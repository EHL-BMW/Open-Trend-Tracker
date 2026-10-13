"""Category, subcategory and feature sales impact for the Impact tab.

The numbers come from ``app.analysis.chinese_pairs``: the market-adjusted China sales change
of version pairs that added a feature, minus that of pairs that did not, per year after launch.
News topics are attached to a subcategory as recent signals only: they get no sales effect of
their own.
"""
from __future__ import annotations

import csv
import json
from functools import cache
from pathlib import Path

from app.analysis.chinese_pairs import CATEGORIES, OUTPUT_DIR, SUBCATEGORIES, YEARS
from app.paths import ROOT_DIR

DEFAULT_IMPACT_FILE = OUTPUT_DIR / "impact.csv"
DEFAULT_NEWS_FILE = ROOT_DIR / "frontend" / "src" / "content" / "china_tech_trends.json"

# News topic ids (Feature Radar) per subcategory.
NEWS_BY_SUBCATEGORY = {
    "battery_range": ("solid_state", "sodium_ion"),
    "charging_replenishment": ("ultra_charging", "battery_swap", "v2g"),
    "high_voltage_powertrain": ("hv_800v",),
    "assisted_driving": ("urban_noa", "e2e_vla", "l3_autonomy"),
    "perception_compute": ("lidar", "adas_chips"),
    "autonomous_mobility": ("robotaxi",),
    "cockpit_intelligence": ("cockpit_llm",),
    "vehicle_compute": ("central_compute",),
    "software_lifecycle": ("ota",),
    "cross_device_ecosystem": ("phone_car_eco",),
    "seating_comfort": ("smart_seats",),
    "ride_body_control": ("active_suspension",),
    "by_wire_controls": ("steer_by_wire",),
    "body_manufacturing": ("giga_casting",),
    "lighting_visibility": ("smart_lighting",),
}


def _number(value: str) -> float | None:
    return float(value) if value not in ("", None) else None


def _series(row: dict) -> list[dict]:
    """Impact points for the years that have an estimate."""
    return [
        {"year": year,
         "impact_pct": float(row[f"impact_pct_year_{year}"]),
         "lower_pct": float(row[f"lower_pct_year_{year}"]),
         "upper_pct": float(row[f"upper_pct_year_{year}"]),
         "pairs": int(float(row[f"n_with_year_{year}"]))}
        for year in YEARS if _number(row[f"impact_pct_year_{year}"]) is not None
    ]


def _load_news(path: Path) -> tuple[dict, dict[str, dict]]:
    source = json.loads(path.read_text(encoding="utf-8"))
    topics = {}
    for topic in source["topics"]:
        topics[topic["id"]] = {
            "id": topic["id"],
            "label": topic["label_en"],
            "label_cn": topic["label_cn"],
            "category": topic["bmw_domain"],
            "priority": topic.get("priority"),
            "signal": topic.get("signal"),
            "momentum_pct_change": topic.get("momentum_pct_change"),
            "volume_recent": topic.get("volume_recent", 0),
            "breadth_outlets": topic.get("breadth_outlets", 0),
            "headline": topic.get("headlines", [{}])[0].get("title", ""),
            "headline_url": topic.get("headlines", [{}])[0].get("link", ""),
        }
    return source, topics


def build_impact_taxonomy(impact_path: Path, news_path: Path, summary_path: Path | None = None) -> dict:
    with impact_path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    news_source, news_by_id = _load_news(news_path)
    summary_file = summary_path or impact_path.with_name("summary.json")
    summary = json.loads(summary_file.read_text(encoding="utf-8")) if summary_file.exists() else {}
    unmapped = sorted(set(news_by_id) - {i for ids in NEWS_BY_SUBCATEGORY.values() for i in ids})
    if unmapped:
        raise ValueError(f"news topics without a subcategory: {unmapped}")

    by_level = {(row["level"], row["name"]): row for row in rows}
    features = [
        {"name": row["name"], "category": row["category"], "subcategory": row["subcategory"],
         "models": json.loads(row["models"]), "pair_count": int(row["pair_count"]), "impact_by_year": _series(row)}
        for row in rows if row["level"] == "feature"
    ]
    features = [f for f in features if f["impact_by_year"]]
    categories = []
    for category in CATEGORIES:
        subcategories = []
        for sub_id, (label, parent) in SUBCATEGORIES.items():
            if parent != category:
                continue
            row = by_level.get(("subcategory", sub_id))
            news = [news_by_id[i] for i in NEWS_BY_SUBCATEGORY.get(sub_id, ()) if i in news_by_id]
            if row is None and not news:
                continue
            subcategories.append({
                "id": sub_id,
                "label": label,
                "pair_count": int(row["pair_count"]) if row else 0,
                "impact_by_year": (_series(row) or None) if row else None,
                "legacy_features": sorted((f for f in features if f["subcategory"] == sub_id),
                                          key=lambda f: -f["pair_count"]),
                "news_features": news,
            })
        row = by_level.get(("category", category))
        if row or subcategories:
            categories.append({
                "id": category.lower().replace(" & ", "-").replace(" ", "-"),
                "label": category,
                "pair_count": int(row["pair_count"]) if row else 0,
                "impact_by_year": _series(row) if row else [],  # empty: too few pairs for an estimate
                "subcategories": subcategories,
            })

    return {
        "title": "Sales Impact Forecast",
        "as_of": news_source["generated_at"],
        "horizon_years": list(YEARS),
        "categories": categories,
        "legacy_feature_count": len(features),
        "news_feature_count": len(news_by_id),
        "valid_pair_count": summary.get("valid_four_year_pairs", 0),
        "collection_target": summary.get("collection_target", 200),
        "method": "market-adjusted China sales change after a version launch: pairs that added the item minus "
                  "pairs that did not, per year after launch",
        "status": "observational_sales_association",
        "caveat": "Observational association from Chinese version pairs, not a causal estimate. A valid pair has a "
                  "numeric baseline and all four annual sales comparisons. Nameplate totals can span successor updates "
                  "or provider changes; those quality flags remain in the research output. News signals are context only.",
        "source_plot": "data/analysis/chinese_pairs/plots/impact_by_subcategory.pdf",
    }


@cache
def impact_taxonomy() -> dict:
    return build_impact_taxonomy(DEFAULT_IMPACT_FILE, DEFAULT_NEWS_FILE)
