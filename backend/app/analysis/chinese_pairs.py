"""Sales change after Chinese version launches and the feature impact estimated from it.

Inputs are curated by hand in ``data/external/chinese_pairs/`` (every row carries a source URL):

- ``pairs.csv``        one row per version change: previous -> current version of one nameplate, with the
                       nameplate's first China launch (YYYY-MM) to detect a partial baseline year
- ``features.csv``     features new in the current version: detail, feature, subcategory, category
- ``model_sales.csv``  annual China sales per nameplate and source ``series``; a nameplate may have several
                       series (e.g. wholesale and registrations), and every change is taken within one series
- ``market_sales.csv`` annual China passenger-car retail (CPCA), total and NEV

Year alignment (annual data): a version launched in Jan-Mar sells in its launch year, so that is
year 1; a later launch makes the launch year a mixed year, so year 1 is the next calendar year.
The baseline is the calendar year before the launch year (previous version only). Year k is
year 1 + k - 1 and is observable when that calendar year is complete in ``market_sales.csv``
and the pair has a numeric baseline plus four annual observations. Partial baseline years and
later successor launches are retained as quality flags rather than silently dropping points.

Sales change is market-adjusted: excess = ln(S_k / S_base) - ln(M_k / M_base), with M the NEV
or ICE passenger market. The impact of an item (feature, subcategory or category) in year k is
the mean excess of pairs that added it minus the mean excess of pairs that did not, with a 95%
normal interval. These are observational associations, not causal effects.

Run from ``backend/``::

    uv run python -m app.analysis.chinese_pairs
"""
from __future__ import annotations

import csv
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from app.paths import DATA_DIR, EXTERNAL_DIR

INPUT_DIR = EXTERNAL_DIR / "chinese_pairs"
OUTPUT_DIR = DATA_DIR / "analysis" / "chinese_pairs"
YEARS = (1, 2, 3, 4)
MIN_PAIRS = 5  # an item needs this many pairs with sales in a year to get an estimate

CATEGORIES = (
    "Energy & Charging", "Driving Assistance", "Digital Cockpit & AI", "Vehicle Dynamics",
    "Smart Cabin", "Connected Ecosystem", "Smart Exterior", "General & Services",
)
# Middle layer between category and feature. Ids are shared with the news topics in
# app/services/impact_forecast.py.
SUBCATEGORIES = {
    "battery_range": ("Battery & range", "Energy & Charging"),
    "charging_replenishment": ("Charging & replenishment", "Energy & Charging"),
    "high_voltage_powertrain": ("High-voltage powertrain", "Energy & Charging"),
    "hybrid_powertrain": ("Hybrid & range-extender powertrain", "Energy & Charging"),
    "assisted_driving": ("Assisted driving", "Driving Assistance"),
    "perception_compute": ("Perception & driving compute", "Driving Assistance"),
    "autonomous_mobility": ("Autonomous mobility", "Driving Assistance"),
    "cockpit_intelligence": ("Cockpit intelligence", "Digital Cockpit & AI"),
    "displays_hmi": ("Displays & HMI", "Digital Cockpit & AI"),
    "vehicle_compute": ("Vehicle compute & E/E", "Digital Cockpit & AI"),
    "software_lifecycle": ("Software lifecycle & OTA", "Connected Ecosystem"),
    "cross_device_ecosystem": ("Cross-device ecosystem", "Connected Ecosystem"),
    "seating_comfort": ("Seating & occupant comfort", "Smart Cabin"),
    "cabin_entertainment": ("Cabin entertainment & audio", "Smart Cabin"),
    "passive_safety": ("Passive safety", "Smart Cabin"),
    "powertrain_performance": ("Powertrain & performance", "Vehicle Dynamics"),
    "ride_body_control": ("Ride & body control", "Vehicle Dynamics"),
    "by_wire_controls": ("Steer/brake-by-wire controls", "Vehicle Dynamics"),
    "body_manufacturing": ("Body structure & manufacturing", "Vehicle Dynamics"),
    "lighting_visibility": ("Lighting & visibility", "Smart Exterior"),
    "exterior_personalization": ("Exterior design & personalization", "Smart Exterior"),
    "ownership_services": ("Ownership & services", "General & Services"),
}


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def first_sales_year(launch: str) -> int:
    year, month = int(launch[:4]), int(launch[5:7])
    return year if month <= 3 else year + 1


def load(input_dir: Path = INPUT_DIR) -> tuple[list[dict], list[dict], dict, dict]:
    pairs = read_csv(input_dir / "pairs.csv")
    features = read_csv(input_dir / "features.csv")
    ids = [p["pair_id"] for p in pairs]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate pair_id in pairs.csv")
    for f in features:
        if f["pair_id"] not in ids:
            raise ValueError(f"feature for unknown pair {f['pair_id']}: {f['detail']}")
        if f["subcategory"] not in SUBCATEGORIES:
            raise ValueError(f"unknown subcategory {f['subcategory']!r} for {f['detail']}")
        if SUBCATEGORIES[f["subcategory"]][1] != f["category"]:
            raise ValueError(f"{f['subcategory']} belongs to {SUBCATEGORIES[f['subcategory']][1]}, not {f['category']}")
    sales: dict[str, dict[str, dict[int, int]]] = defaultdict(lambda: defaultdict(dict))
    for row in read_csv(input_dir / "model_sales.csv"):
        sales[row["car_model"]][row["series"]][int(row["year"])] = int(row["units"])
    market = {int(r["year"]): {"NEV": int(r["nev_retail"]), "ICE": int(r["total_retail"]) - int(r["nev_retail"])}
              for r in read_csv(input_dir / "market_sales.csv")}
    return pairs, features, sales, market


def pick_series(by_series: dict[str, dict[int, int]], base_year: int, years: list[int]) -> str:
    """The series that has the baseline year and the most of the given years ('' if none has the baseline)."""
    covering = [(sum(y in values for y in years), name) for name, values in by_series.items() if base_year in values]
    return max(covering, key=lambda c: c[0])[1] if covering else ""


def pair_sales(pairs: list[dict], sales: dict, market: dict) -> list[dict]:
    """Baseline and year 1-4 sales of each pair, raw and market-adjusted."""
    last_year = max(market)
    launches = defaultdict(list)
    for p in pairs:
        launches[p["car_model"]].append(p["current_launch"])
    rows = []
    for p in pairs:
        model, segment = p["car_model"], p["powertrain"]
        first = first_sales_year(p["current_launch"])
        base_year = int(p["current_launch"][:4]) - 1
        later = sorted(d for d in launches[model] if d > p["current_launch"])
        # a nameplate first sold after February of the baseline year has no full baseline year
        partial = p["nameplate_launch"][:7] > f"{base_year}-02"
        years = [first + k - 1 for k in YEARS if first + k - 1 <= last_year]
        series = pick_series(sales[model], base_year, years)
        chosen = sales[model].get(series, {})
        base = chosen.get(base_year)
        row = {"pair_id": p["pair_id"], "brand": p["brand"], "car_model": model, "powertrain": segment,
               "change_type": p["change_type"], "current_version": p["current_version"],
               "current_launch": p["current_launch"], "successor_launch": later[0] if later else "",
               "nameplate_launch": p["nameplate_launch"], "sales_series": series,
               "baseline_year": base_year, "baseline_sales": base}
        for k in YEARS:
            year = first + k - 1
            units = chosen.get(year) if year <= last_year else None
            superseded = bool(later and int(later[0][:4]) <= year)
            # the year exists only in another series: a change across series (e.g. wholesale vs
            # registrations) is not a sales change
            broken = units is None and any(year in v for v in sales[model].values()) and \
                any(base_year in v for v in sales[model].values())
            change = excess = None
            if units and base and year in market and base_year in market:
                change = units / base - 1
                excess = math.log(units / base) - math.log(market[year][segment] / market[base_year][segment])
            row[f"year_{k}"] = year
            row[f"sales_year_{k}"] = units
            row[f"change_pct_year_{k}"] = None if change is None else round(change * 100, 2)
            row[f"excess_log_year_{k}"] = None if excess is None else round(excess, 4)
            row[f"status_year_{k}"] = ("not_yet_observable" if year > last_year else
                                       "series_break" if broken else
                                       "missing_sales" if excess is None else "observed")
            flags = []
            if partial:
                flags.append("partial_baseline")
            if superseded:
                flags.append("successor_overlap")
            if series == "four_year_nameplate":
                flags.append("provider_change")
            row[f"quality_year_{k}"] = ";".join(flags)
        row["valid_four_year_pair"] = all(row[f"status_year_{k}"] == "observed" for k in YEARS)
        rows.append(row)
    return rows


def _pct(log_value: float) -> float:
    return round((math.exp(log_value) - 1) * 100, 2)


def contrast(with_item: list[float], without: list[float]) -> dict | None:
    if len(with_item) < MIN_PAIRS or len(without) < MIN_PAIRS:
        return None
    diff = statistics.fmean(with_item) - statistics.fmean(without)
    se = math.sqrt(statistics.variance(with_item) / len(with_item) + statistics.variance(without) / len(without))
    return {"impact_pct": _pct(diff), "lower_pct": _pct(diff - 1.96 * se), "upper_pct": _pct(diff + 1.96 * se),
            "n_with": len(with_item), "n_without": len(without)}


def impact(pair_rows: list[dict], features: list[dict]) -> list[dict]:
    """Market-adjusted sales impact per feature, subcategory and category for each year."""
    items: dict[tuple[str, str], set[str]] = defaultdict(set)
    parents: dict[tuple[str, str], tuple[str, str]] = {}
    for f in features:
        items[("feature", f["feature"])].add(f["pair_id"])
        items[("subcategory", f["subcategory"])].add(f["pair_id"])
        items[("category", f["category"])].add(f["pair_id"])
        parents[("feature", f["feature"])] = (f["subcategory"], f["category"])
        parents[("subcategory", f["subcategory"])] = (f["subcategory"], f["category"])
        parents[("category", f["category"])] = ("", f["category"])
    by_pair = {r["pair_id"]: r for r in pair_rows}
    output = []
    for (level, name), pair_ids in sorted(items.items()):
        subcategory, category = parents[(level, name)]
        row = {"level": level, "name": name,
               "label": SUBCATEGORIES[name][0] if level == "subcategory" else name,
               "subcategory": subcategory, "category": category, "pair_count": len(pair_ids),
               "models": json.dumps(sorted({by_pair[i]["car_model"] for i in pair_ids}), ensure_ascii=False)}
        for k in YEARS:
            observed = [r for r in pair_rows if r[f"excess_log_year_{k}"] is not None]
            result = contrast([r[f"excess_log_year_{k}"] for r in observed if r["pair_id"] in pair_ids],
                              [r[f"excess_log_year_{k}"] for r in observed if r["pair_id"] not in pair_ids])
            for key in ("impact_pct", "lower_pct", "upper_pct", "n_with", "n_without"):
                row[f"{key}_year_{k}"] = result[key] if result else None
        output.append(row)
    return output


def plot(impact_rows: list[dict], path: Path) -> None:
    rows = [r for r in impact_rows if r["level"] == "subcategory" and r["impact_pct_year_1"] is not None]
    rows.sort(key=lambda r: r["impact_pct_year_1"])
    fig, ax = plt.subplots(figsize=(8, 0.35 * len(rows) + 1.6))
    for i, r in enumerate(rows):
        ax.plot([r["lower_pct_year_1"], r["upper_pct_year_1"]], [i, i], color="#7b8794", lw=1.5)
        ax.plot(r["impact_pct_year_1"], i, "o", color="#2f78a7")
    ax.axvline(0, color="#333", lw=0.8)
    ax.set_yticks(range(len(rows)), [f"{r['label']} (n={r['n_with_year_1']})" for r in rows], fontsize=8)
    ax.set_xlabel("Year-1 market-adjusted sales change vs pairs without it (%), 95% interval")
    ax.set_title("Chinese version changes: sales impact by subcategory (observational)", fontsize=10)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
    plt.close(fig)


def run(input_dir: Path = INPUT_DIR, output_dir: Path = OUTPUT_DIR) -> dict:
    pairs, features, sales, market = load(input_dir)
    pair_rows = pair_sales(pairs, sales, market)
    impact_rows = impact(pair_rows, features)
    write_csv(pair_rows, output_dir / "pair_sales.csv")
    write_csv(features, output_dir / "feature_log.csv")
    write_csv(impact_rows, output_dir / "impact.csv")
    plot(impact_rows, output_dir / "plots" / "impact_by_subcategory.pdf")
    summary = {
        "pairs": len(pairs),
        "brands": len({p["brand"] for p in pairs}),
        "launch_range": [min(p["current_launch"] for p in pairs), max(p["current_launch"] for p in pairs)],
        "features": len(features),
        "observed_pairs_by_year": {k: sum(r[f"status_year_{k}"] == "observed" for r in pair_rows) for k in YEARS},
        "valid_four_year_pairs": sum(r["valid_four_year_pair"] for r in pair_rows),
        "collection_target": 200,
        "estimated_items": {level: sum(r["level"] == level and r["impact_pct_year_1"] is not None for r in impact_rows)
                            for level in ("feature", "subcategory", "category")},
        "last_full_sales_year": max(market),
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
