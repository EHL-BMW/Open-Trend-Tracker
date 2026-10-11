"""Feature recommendation pipeline: from raw inputs to one ranked feature list per car.

    uv run python -m app.pipeline

Steps (each writes data/pipeline/<n>_<name>.csv and a figure in data/pipeline/plots/):
 1 existing features   option-list PDFs -> car, item, feature, category, standard/optional, price
 2 comments            customer feedback -> feature, category, sentiment, source comment
 3 external trends     month, feature, popularity, sales            (SYNTHETIC for now, see app/dummy.py)
 4 news               date, feature, headline, impact              (SYNTHETIC for now)
 5 forecast            sales history + popularity trend + news -> popularity and sales growth in 12 months
 6 engineering filter  engineer's on/off per feature (backend/engineering_filter.csv)
 7 recommendation      joint score per car and feature, highest first

The "LLM processing" of steps 1 and 2 is LLM-free for now: rule-based parsing plus the curated
taxonomy.json produce the same table shape an LLM step would (see CLAUDE.md).
"""
import numpy as np
import pandas as pd

from app import dummy, external, internal, plots
from app.mapping import Mapper
from app.paths import BACKEND_DIR, DATA_DIR, EXTERNAL_DIR, INTERNAL_DIR

OUT_DIR = DATA_DIR / "pipeline"
SYNTHETIC_DIR = EXTERNAL_DIR / "synthetic"
FILTER_FILE = BACKEND_DIR / "engineering_filter.csv"
# taxonomy categories that are outcomes or market facts, not features a car can add
NOT_FEATURES = {"overall", "market", "value_brand", "quality"}
CARS = ["F70", "G60", "G70"]
HORIZON = 12  # forecast months
WEIGHTS = {"trend": 0.25, "market": 0.25, "comment": 0.30, "gap": 0.20}
SENTIMENTS = ["like", "want", "difficult_to_use", "defect"]
NOT_LISTED_GAP = 0.75


def feature_catalog(mapper: Mapper) -> dict[str, dict]:
    return {a: {"name": info["name"], "category": info["category"],
                "category_name": mapper.categories[info["category"]]}
            for a, info in mapper.attributes.items() if info["category"] not in NOT_FEATURES}


def _describe(df: pd.DataFrame, features: dict) -> pd.DataFrame:
    df["feature_name"] = df["feature"].map(lambda f: features[f]["name"] if f in features else None)
    df["category"] = df["feature"].map(lambda f: features[f]["category_name"] if f in features else None)
    return df


# --- 1 existing features -----------------------------------------------------------------

def existing_features(mapper: Mapper, features: dict) -> pd.DataFrame:
    rows = []
    for pdf in sorted(INTERNAL_DIR.glob("*_OptionList.PDF")):
        car = pdf.name.split("_")[0]
        option_rows = internal.option_rows(pdf)
        n_variants = max(r["standard"] + r["optional"] for r in option_rows)
        for r in option_rows:
            fid, _ = mapper.lookup(r["name"])
            rows.append({"car": car, "item": r["name"], "code": r["code"], "package": r["package"], "feature": fid,
                         "standard_share": r["standard"] / n_variants, "optional_share": r["optional"] / n_variants,
                         "price_eur": r["price"], "source": f"{pdf.name} page {r['page']}"})
    df = _describe(pd.DataFrame(rows), features)
    return df[df["feature"].isin(features)].reset_index(drop=True)


def gap(existing: pd.DataFrame, car: str, fid: str) -> float:
    """0 = standard on every variant, 0.5 = optional on every variant, NaN = the car has no option list.
    Per item: offered = standard share + half the optional share; the best item counts.
    Not listed = 0.75, not 1: a price list omits some standard equipment, so absence is weak evidence."""
    if car not in set(existing["car"]):
        return np.nan
    items = existing[(existing["car"] == car) & (existing["feature"] == fid)]
    return NOT_LISTED_GAP if items.empty else 1 - (items["standard_share"] + 0.5 * items["optional_share"]).max()


# --- 2 comments --------------------------------------------------------------------------

def comments(mapper: Mapper, features: dict) -> pd.DataFrame:
    obs = internal.feedback()
    mapper.apply(obs)
    rows = [{"car": o.vehicle, "market": o.market, "country": o.country, "feature": o.attribute,
             "sentiment": o.metric, "comment": o.text, "source": f"{o.raw.file} {o.raw.locator}"}
            for o in obs if o.attribute in features and o.metric in SENTIMENTS]
    return _describe(pd.DataFrame(rows), features)


def comment_summary(com: pd.DataFrame) -> pd.DataFrame:
    """Per car and feature: counts, need share (want + difficult + defect) and a volume-weighted comment score."""
    s = com.pivot_table(index=["car", "feature"], columns="sentiment", values="comment", aggfunc="count",
                        fill_value=0).reindex(columns=SENTIMENTS, fill_value=0)
    s["mentions"] = s[SENTIMENTS].sum(axis=1)
    s["need_share"] = (s["want"] + s["difficult_to_use"] + s["defect"]) / s["mentions"]
    s["net_sentiment"] = (s["like"] - s["difficult_to_use"] - s["defect"]) / s["mentions"]
    volume = s["mentions"] / s.groupby("car")["mentions"].transform("max")
    s["comment_score"] = s["need_share"] * np.sqrt(volume)  # many people asking or complaining -> high
    return s.reset_index()


# --- 3 + 4 external trends and news ------------------------------------------------------

def popularity_anchors(mapper: Mapper) -> dict[str, float]:
    """Share (0-100) of competitor models in the EV market table that list each feature."""
    paths = sorted(EXTERNAL_DIR.glob("top_500_ev_phev_europe*.csv"))
    if not paths:
        return {}
    obs = [o for o in external.ev_market(paths[0]) if o.metric == "has_feature" and o.competitor]
    mapper.apply(obs)
    models = {o.competitor for o in obs}
    listed = pd.DataFrame([(o.attribute, o.competitor) for o in obs if o.attribute], columns=["f", "m"])
    return (listed.drop_duplicates().groupby("f")["m"].count() / len(models) * 100).clip(10, 90).to_dict()


def external_inputs(mapper: Mapper, features: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    trends_file, news_file = SYNTHETIC_DIR / "feature_trends.csv", SYNTHETIC_DIR / "news.csv"
    if not (trends_file.exists() and news_file.exists()):
        SYNTHETIC_DIR.mkdir(parents=True, exist_ok=True)
        tr = dummy.trends(features, popularity_anchors(mapper))
        tr.to_csv(trends_file, index=False)
        dummy.news(features, tr).to_csv(news_file, index=False)
    return pd.read_csv(trends_file), pd.read_csv(news_file)


# --- 5 forecast --------------------------------------------------------------------------

def _slope(y: np.ndarray) -> float:
    return np.polyfit(np.arange(len(y)), y, 1)[0]


def forecast(trends: pd.DataFrame, news: pd.DataFrame) -> pd.DataFrame:
    """Per feature, 12 months ahead:
    sales growth  = log-linear trend of the last 24 months of sales      + 5 % per unit of recent news impact
    popularity    = mean of (linear popularity trend, popularity scaled by sales growth) + 10 points per unit of news
    Recent news impact = sum of impacts, each decayed with a 6-month time constant, over the last 12 months."""
    now = pd.Period(trends["month"].max(), freq="M")
    age = news.assign(age=lambda d: [(now - pd.Period(x, freq="M")).n for x in d["date"]])
    age = age[age["age"] <= 12]
    news_impact = (age["impact"] * np.exp(-age["age"] / 6)).groupby(age["feature"]).sum()
    rows = []
    for fid, g in trends.groupby("feature"):
        pop, sales = g["popularity"].to_numpy()[-24:], g["sales"].to_numpy()[-24:].astype(float)
        sales_growth_hist = np.exp(HORIZON * _slope(np.log(np.maximum(sales, 1)))) - 1
        impact = news_impact.get(fid, 0.0)
        sales_growth = sales_growth_hist + 0.05 * impact
        pop_trend = pop[-1] + HORIZON * _slope(pop)
        pop_from_sales = pop[-1] * (1 + sales_growth_hist)
        pop_fc = float(np.clip((pop_trend + pop_from_sales) / 2 + 10 * impact, 0, 100))
        rows.append({"feature": fid, "popularity_now": pop[-1], "popularity_trend_fc": pop_trend,
                     "popularity_from_sales_fc": pop_from_sales, "news_impact": impact,
                     "popularity_fc": pop_fc, "popularity_change": pop_fc - pop[-1],
                     "sales_now": sales[-1], "sales_growth_hist": sales_growth_hist,
                     "sales_growth_fc": sales_growth})
    return pd.DataFrame(rows)


# --- 6 engineering filter ----------------------------------------------------------------

def engineering_filter(features: dict) -> pd.DataFrame:
    """Engineer's manual on/off per feature; a feature missing from the file counts as on."""
    df = pd.read_csv(FILTER_FILE) if FILTER_FILE.exists() else pd.DataFrame(columns=["feature", "feasible", "engineer", "note"])
    df = pd.DataFrame({"feature": list(features)}).merge(df, on="feature", how="left")
    df["feasible"] = df["feasible"].fillna("on").str.lower().eq("on")
    return _describe(df.fillna({"engineer": "", "note": ""}), features)


# --- 7 joint score -----------------------------------------------------------------------

def _minmax(s: pd.Series) -> pd.Series:
    return (s - s.min()) / (s.max() - s.min()) if s.max() > s.min() else s * 0 + 0.5


def recommend(features: dict, existing: pd.DataFrame, com_sum: pd.DataFrame, fc: pd.DataFrame,
              filt: pd.DataFrame) -> pd.DataFrame:
    out = []
    for car in CARS:
        df = pd.DataFrame({"car": car, "feature": list(features)})
        df = df.merge(fc, on="feature", how="left").merge(filt[["feature", "feasible", "note"]], on="feature")
        df = df.merge(com_sum[com_sum["car"] == car].drop(columns="car"), on="feature", how="left")
        df[["mentions", "comment_score"]] = df[["mentions", "comment_score"]].fillna(0)
        df["gap_raw"] = [gap(existing, car, f) for f in df["feature"]]
        ok = df["feasible"]
        df.loc[ok, "trend"] = _minmax(df.loc[ok, "popularity_change"])
        df.loc[ok, "market"] = 0.5 * _minmax(df.loc[ok, "popularity_now"]) + 0.5 * _minmax(df.loc[ok, "sales_growth_fc"])
        df.loc[ok, "comment"] = _minmax(df.loc[ok, "comment_score"])
        df.loc[ok, "gap"] = df.loc[ok, "gap_raw"].fillna(0.5)  # no option list -> neutral
        for k, w in WEIGHTS.items():
            df[f"w_{k}"] = w * df[k]
        df["score"] = df[[f"w_{k}" for k in WEIGHTS]].sum(axis=1, min_count=1)
        df = df.sort_values(["feasible", "score"], ascending=False, ignore_index=True)
        df["rank"] = np.where(df["feasible"], np.arange(1, len(df) + 1), np.nan)
        out.append(_describe(df, features))
    cols = ["car", "rank", "feature", "feature_name", "category", "score", *[f"w_{k}" for k in WEIGHTS],
            *WEIGHTS, "feasible", "note", "popularity_now", "popularity_fc", "popularity_change",
            "sales_growth_fc", "news_impact", "mentions", "like", "want", "difficult_to_use", "defect",
            "need_share", "gap_raw"]
    return pd.concat(out, ignore_index=True)[cols]


def main() -> None:
    mapper = Mapper()
    features = feature_catalog(mapper)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    existing = existing_features(mapper, features)
    com = comments(mapper, features)
    com_sum = comment_summary(com)
    trends, news = external_inputs(mapper, features)
    fc = forecast(trends, news)
    filt = engineering_filter(features)
    rec = recommend(features, existing, com_sum, fc, filt)

    for name, df in [("1_existing_features", existing), ("2_comments", com), ("2_comment_summary", com_sum),
                     ("3_external_trends", trends), ("4_news", news), ("5_forecast", fc),
                     ("6_engineering_filter", filt), ("7_recommendations", rec)]:
        df.to_csv(OUT_DIR / f"{name}.csv", index=False)
    plots.all_steps(OUT_DIR / "plots", features, existing, com_sum, trends, news, fc, filt, rec, WEIGHTS)

    print(f"features: {len(features)} | existing items: {len(existing)} | comments: {len(com)} | "
          f"news: {len(news)} | engineering off: {(~filt['feasible']).sum()}")
    for car in CARS:
        top = rec[(rec["car"] == car) & rec["feasible"]].head(5)
        print(f"{car} top 5: " + ", ".join(f"{n} ({s:.2f})" for n, s in zip(top["feature_name"], top["score"])))
    print(f"-> {OUT_DIR}")


if __name__ == "__main__":
    main()
