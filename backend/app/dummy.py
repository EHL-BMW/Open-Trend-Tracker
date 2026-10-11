"""SYNTHETIC external data, so the pipeline can run end to end before the partner's grabber delivers.

Everything here is made up (fixed seed, so it is reproducible) and marked source="SYNTHETIC".
The one real input: a feature's current popularity level is anchored to how many competitor
models in the EV/PHEV market table list it.

    feature_trends.csv   month, feature, popularity (0-100 index), sales (EU cars sold with the feature)
    news.csv             date, feature, headline, impact (-1 .. +1)
"""
import numpy as np
import pandas as pd

SEED = 7
MONTHS = pd.period_range("2021-01", "2026-09", freq="M")
# yearly popularity growth by category: digital and EV topics move fastest
GROWTH = {"range_charging": 0.15, "assistance_safety": 0.12, "infotainment": 0.10, "hmi": 0.08}
EU_MONTHLY_CARS = 900_000

POSITIVE = ["{c} launches {f} as standard across its range",
            "Survey: buyers rank {f} among their top three purchase reasons",
            "Test magazine names {f} the most-wanted feature of the year",
            "Supplier cuts cost of {f} hardware by a third"]
NEGATIVE = ["Owners report problems with {f} in winter",
            "Regulator questions safety of {f}",
            "Recall at {c} linked to {f} supplier"]
COMPETITORS = ["Mercedes-Benz", "Audi", "Tesla", "Volvo", "BYD", "Hyundai"]


def trends(features: dict[str, dict], anchors: dict[str, float]) -> pd.DataFrame:
    """features: id -> {name, category}; anchors: id -> current popularity (0-100) from real data."""
    rng = np.random.default_rng(SEED)
    years = (np.arange(len(MONTHS)) - (len(MONTHS) - 1)) / 12  # 0 = latest month
    market = EU_MONTHLY_CARS * 1.02 ** years * (1 + 0.08 * np.sin(2 * np.pi * np.arange(len(MONTHS)) / 12))
    rows = []
    for fid, info in features.items():
        level = anchors.get(fid, 30.0)
        growth = GROWTH.get(info["category"], 0.03) + rng.normal(0, 0.06)  # compounding, so it never hits 0
        popularity = np.clip(level * (1 + growth) ** years * rng.normal(1, 0.03, len(MONTHS)), 0, 100)
        take_rate = np.clip(popularity / 100 * rng.normal(1, 0.05, len(MONTHS)), 0, 1)
        sales = (market * take_rate).round()
        rows += [{"month": str(m), "feature": fid, "popularity": round(p, 1), "sales": int(s), "source": "SYNTHETIC"}
                 for m, p, s in zip(MONTHS, popularity, sales)]
    return pd.DataFrame(rows)


def news(features: dict[str, dict], trend_df: pd.DataFrame) -> pd.DataFrame:
    """A few headlines for 14 features; rising features get mostly positive news."""
    rng = np.random.default_rng(SEED + 1)
    last = trend_df.groupby("feature")["popularity"].agg(lambda s: s.iloc[-1] - s.iloc[-13])  # 12-month change
    days = pd.date_range("2025-01-01", "2026-09-30", freq="D")
    rows = []
    for fid in rng.choice(sorted(features), size=14, replace=False):
        p_positive = 0.8 if last[fid] > 0 else 0.35
        for _ in range(rng.integers(1, 5)):
            positive = rng.random() < p_positive
            template = rng.choice(POSITIVE if positive else NEGATIVE)
            impact = round(float(rng.uniform(0.2, 0.9) * (1 if positive else -1)), 2)
            rows.append({"date": str(days[rng.integers(len(days))].date()), "feature": fid,
                         "headline": template.format(c=rng.choice(COMPETITORS), f=features[fid]["name"].lower()),
                         "impact": impact, "source": "SYNTHETIC"})
    return pd.DataFrame(rows).sort_values("date", ignore_index=True)
