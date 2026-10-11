"""One PDF per pipeline step (data/pipeline/plots/). Colours follow a fixed, colour-blind-checked order."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.backends.backend_pdf import PdfPages  # noqa: E402

SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3de"
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]  # categorical slots 1-4, always in this order
UP, DOWN, NEUTRAL = "#2a78d6", "#e34948", "#c3c2b7"   # diverging poles + neutral
GOOD, CRITICAL = "#0ca30c", "#d03b3b"                 # status: always with a label
SYNTHETIC_NOTE = "SYNTHETIC placeholder data (app/dummy.py), not real market data"

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
    "text.color": INK, "font.size": 9, "axes.titlesize": 10, "axes.titleweight": "bold",
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": GRID,
    "grid.linewidth": 0.6, "axes.axisbelow": True, "legend.frameon": False, "pdf.fonttype": 42,
})


def _title(fig, title: str, subtitle: str = "") -> None:
    fig.suptitle(title, x=0.01, y=0.995, ha="left", va="top", fontsize=13, fontweight="bold")
    if subtitle:
        fig.text(0.01, 0.995 - 0.3 / fig.get_figheight(), subtitle, ha="left", va="top", color=INK2, fontsize=9)


def _hbar_stack(ax, labels, parts: list[np.ndarray], names: list[str]) -> None:
    left = np.zeros(len(labels))
    for i, (vals, name) in enumerate(zip(parts, names)):
        ax.barh(labels, vals, left=left, color=SERIES[i], height=0.7, label=name,
                edgecolor=SURFACE, linewidth=1)  # 1pt surface gap between segments
        left += vals
    ax.invert_yaxis()
    ax.grid(axis="y", visible=False)


# --- 1 existing features -----------------------------------------------------------------

def existing(pdf: PdfPages, existing: pd.DataFrame) -> None:
    cars = sorted(existing["car"].unique())
    order = existing.sort_values(["category", "feature_name"])["feature_name"].unique()
    fig, axes = plt.subplots(1, len(cars), figsize=(11, 0.22 * len(order) + 1.8), sharey=True)
    for ax, car in zip(np.atleast_1d(axes), cars):
        d = existing[existing["car"] == car]
        std = d[d["standard_share"] > 0].groupby("feature_name").size().reindex(order, fill_value=0)
        opt = d[d["standard_share"] == 0].groupby("feature_name").size().reindex(order, fill_value=0)
        _hbar_stack(ax, order, [std.to_numpy(), opt.to_numpy()], ["standard on some variant", "optional only"])
        ax.set_title(car, loc="left")
        ax.set_xlabel("option-list items")
    np.atleast_1d(axes)[0].legend(loc="lower right")
    _title(fig, "Step 1 · Existing features per car", "Option-list PDF items mapped to features (rule-based parse + taxonomy)")
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    pdf.savefig(fig)
    plt.close(fig)


# --- 2 comments --------------------------------------------------------------------------

def comments(pdf: PdfPages, com_sum: pd.DataFrame, features: dict) -> None:
    names = ["like", "want", "difficult_to_use", "defect"]
    for car, d in com_sum.groupby("car"):
        d = d.sort_values("mentions", ascending=False).head(20)
        labels = [features[f]["name"] for f in d["feature"]]
        fig, ax = plt.subplots(figsize=(10, 6.5))
        _hbar_stack(ax, labels, [d[n].to_numpy() for n in names], ["like", "want", "difficult to use", "defect"])
        for y, (total, need) in enumerate(zip(d["mentions"], d["need_share"])):
            ax.text(total, y, f"  {total}  ·  {need:.0%} need", va="center", color=INK2, fontsize=8)
        ax.set_xlabel("customer comments")
        ax.set_xlim(0, d["mentions"].max() * 1.25)
        ax.legend(loc="lower right", ncols=4)
        _title(fig, f"Step 2 · Customer comments by feature · {car}",
               "Top 20 features by mentions. need = (want + difficult + defect) / mentions")
        fig.tight_layout(rect=(0, 0, 1, 0.93))
        pdf.savefig(fig)
        plt.close(fig)


# --- 3 external trends -------------------------------------------------------------------

def trends(pdf: PdfPages, trends: pd.DataFrame, features: dict) -> None:
    top = trends.groupby("feature")["popularity"].last().sort_values(ascending=False).index[:16]
    for col, label in [("popularity", "popularity index (0-100)"), ("sales", "cars sold with feature (k / month)")]:
        fig, axes = plt.subplots(4, 4, figsize=(11, 8), sharex=True, sharey=True)
        for ax, fid in zip(axes.flat, top):
            g = trends[trends["feature"] == fid]
            x = pd.PeriodIndex(g["month"], freq="M").to_timestamp()
            y = g[col] / (1000 if col == "sales" else 1)
            ax.plot(x, y, color=SERIES[0] if col == "popularity" else SERIES[1], linewidth=1.5)
            ax.set_title(features[fid]["name"], loc="left", fontsize=8.5)
        for ax in axes[:, 0]:
            ax.set_ylabel(label, fontsize=7.5)
        for ax in axes.flat:
            ax.xaxis.set_major_locator(mdates.YearLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        _title(fig, f"Step 3 · External trends · {col}", f"Top 16 features by current popularity. {SYNTHETIC_NOTE}")
        fig.tight_layout(rect=(0, 0, 1, 0.93))
        pdf.savefig(fig)
        plt.close(fig)


# --- 4 news ------------------------------------------------------------------------------

def news(pdf: PdfPages, news: pd.DataFrame, features: dict) -> None:
    d = news.assign(date=pd.to_datetime(news["date"]), name=news["feature"].map(lambda f: features[f]["name"]))
    order = d.groupby("name")["impact"].sum().sort_values().index
    fig, ax = plt.subplots(figsize=(10, 0.35 * len(order) + 1.8))
    for sign, color, label in [(1, UP, "positive news"), (-1, DOWN, "negative news")]:
        s = d[np.sign(d["impact"]) == sign]
        ax.scatter(s["date"], s["name"].map({n: i for i, n in enumerate(order)}), s=30 + 220 * s["impact"].abs(),
                   color=color, alpha=0.85, edgecolor=SURFACE, linewidth=1.5, label=label)
    ax.set_yticks(range(len(order)), order)
    ax.set_ylim(-0.7, len(order) - 0.3)
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncols=2, markerscale=0.6)
    ax.set_xlabel("date (dot size = |impact|)")
    _title(fig, "Step 4 · News signals per feature", SYNTHETIC_NOTE)
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    pdf.savefig(fig)
    plt.close(fig)


# --- 5 forecast --------------------------------------------------------------------------

def forecast(pdf: PdfPages, trends: pd.DataFrame, fc: pd.DataFrame, features: dict) -> None:
    top = fc.reindex(fc["popularity_change"].abs().sort_values(ascending=False).index).head(12)
    fig, axes = plt.subplots(3, 4, figsize=(11, 7), sharex=True, sharey=True)
    for ax, (_, r) in zip(axes.flat, top.iterrows()):
        g = trends[trends["feature"] == r["feature"]].tail(36)
        x = pd.PeriodIndex(g["month"], freq="M").to_timestamp()
        end = x[-1] + pd.DateOffset(months=12)
        ax.plot(x, g["popularity"], color=SERIES[0], linewidth=1.5)
        ax.plot([x[-1], end], [r["popularity_now"], r["popularity_fc"]], color=SERIES[0], linewidth=1.5,
                linestyle=(0, (3, 2)))
        ax.scatter([end], [r["popularity_fc"]], color=SERIES[0], s=24, zorder=3, edgecolor=SURFACE, linewidth=1.5)
        ax.text(end, r["popularity_fc"], f" {r['popularity_change']:+.1f}", va="center", fontsize=8, color=INK2)
        ax.set_title(features[r["feature"]]["name"], loc="left", fontsize=8.5)
    for ax in axes[:, 0]:
        ax.set_ylabel("popularity", fontsize=8)
    for ax in axes.flat:
        ax.xaxis.set_major_locator(mdates.YearLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    _title(fig, "Step 5 · Popularity forecast, 12 months (dashed)",
           "Largest forecast changes. Forecast = mean(popularity trend, sales-implied popularity) + news impact")
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    pdf.savefig(fig)
    plt.close(fig)

    d = fc.assign(name=fc["feature"].map(lambda f: features[f]["name"]))
    fig, axes = plt.subplots(1, 2, figsize=(11, 0.2 * len(d) + 1.8), sharey=False)
    for ax, col, label, scale in [(axes[0], "popularity_change", "popularity change (index points)", 1),
                                  (axes[1], "sales_growth_fc", "sales growth forecast (%)", 100)]:
        s = d.sort_values(col)
        ax.barh(s["name"], s[col] * scale, color=[UP if v >= 0 else DOWN for v in s[col]], height=0.7)
        ax.axvline(0, color=INK2, linewidth=0.8)
        ax.set_xlabel(label)
        ax.grid(axis="y", visible=False)
        ax.tick_params(axis="y", labelsize=7)
    _title(fig, "Step 5 · Forecast per feature, 12 months", "Blue = up, red = down. " + SYNTHETIC_NOTE)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    pdf.savefig(fig)
    plt.close(fig)


# --- 6 engineering filter ----------------------------------------------------------------

def engineering(pdf: PdfPages, filt: pd.DataFrame) -> None:
    d = filt.sort_values(["feasible", "category", "feature_name"], ascending=[True, True, True], ignore_index=True)
    fig, ax = plt.subplots(figsize=(10, 0.22 * len(d) + 1.4))
    ax.set_axis_off()
    for i, r in d.iterrows():
        y = len(d) - i
        mark, color, word = ("✓", GOOD, "on") if r["feasible"] else ("✗", CRITICAL, "off")
        ax.text(0.00, y, mark, color=color, fontsize=10, fontweight="bold", va="center")
        ax.text(0.03, y, word, color=INK, va="center", fontweight="bold" if not r["feasible"] else "normal")
        ax.text(0.08, y, r["feature_name"], va="center")
        ax.text(0.31, y, r["category"], va="center", color=INK2)
        ax.text(0.56, y, r["note"], va="center", color=INK2, fontsize=8)
    ax.set_ylim(0, len(d) + 1)
    ax.set_xlim(0, 1)
    _title(fig, "Step 6 · Engineering feasibility filter",
           f"{(~d['feasible']).sum()} of {len(d)} features switched off. Manual labels in backend/engineering_filter.csv (DUMMY)")
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    pdf.savefig(fig)
    plt.close(fig)


# --- 7 recommendation --------------------------------------------------------------------

def recommendation(pdf: PdfPages, rec: pd.DataFrame, weights: dict) -> None:
    names = list(weights)
    for car, d in rec.groupby("car", sort=False):
        ok, off = d[d["feasible"]], d[~d["feasible"]]
        labels = [f"{int(r):>2}. {n}" for r, n in zip(ok["rank"], ok["feature_name"])]
        fig, ax = plt.subplots(figsize=(10, 0.24 * len(ok) + 2.4))
        _hbar_stack(ax, labels, [ok[f"w_{k}"].to_numpy() for k in names],
                    [f"{k} (w={w:.2f})" for k, w in weights.items()])
        for y, s in enumerate(ok["score"]):
            ax.text(s, y, f" {s:.2f}", va="center", fontsize=8, color=INK2)
        ax.set_xlim(0, ok["score"].max() * 1.12)
        ax.set_xlabel("score = Σ weight × component (each component scaled 0-1 across features)")
        ax.legend(loc="lower right", ncols=2)
        ax.tick_params(axis="y", labelsize=8)
        excluded = ", ".join(off["feature_name"])
        _title(fig, f"Step 7 · Feature recommendation · {car}",
               f"Excluded by engineering filter: {excluded}")
        fig.tight_layout(rect=(0, 0, 1, 0.95))
        pdf.savefig(fig)
        plt.close(fig)


def all_steps(out_dir: Path, features, existing_df, com_sum, trends_df, news_df, fc, filt, rec, weights) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    jobs = [("1_existing_features", lambda p: existing(p, existing_df)),
            ("2_comments", lambda p: comments(p, com_sum, features)),
            ("3_external_trends", lambda p: trends(p, trends_df, features)),
            ("4_news", lambda p: news(p, news_df, features)),
            ("5_forecast", lambda p: forecast(p, trends_df, fc, features)),
            ("6_engineering_filter", lambda p: engineering(p, filt)),
            ("7_recommendation", lambda p: recommendation(p, rec, weights))]
    for name, job in jobs:
        with PdfPages(out_dir / f"{name}.pdf") as pdf:
            job(pdf)
