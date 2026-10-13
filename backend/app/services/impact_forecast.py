"""Conditional category, subcategory and feature sales effects for the Impact tab.

The numbers come from the balanced event-study in ``app.analysis.chinese_pairs``. Duplicate trim
trajectories are collapsed and every target is conditioned on supported peers, bundle size,
powertrain, baseline scale, calendar year and recorded quality flags. Exact feature values are
withheld when a feature cannot be separated from its launch bundle or uncertainty is too large.
News topics are attached to a subcategory as recent signals only: they get no sales effect of
their own. ``exploratory`` carries the bundle-level associations from
``app.analysis.bundle_exploratory``: labelled exploratory and never mixed into the gated values.
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
    """Only expose a complete four-year series that passed every publication gate."""
    if row.get("identification_status") != "identified":
        return []
    return [
        {"year": year,
         "impact_pct": float(row[f"impact_pct_year_{year}"]),
         "lower_pct": float(row[f"lower_pct_year_{year}"]),
         "upper_pct": float(row[f"upper_pct_year_{year}"]),
         "incremental_units": int(float(row[f"incremental_units_year_{year}"])),
         "lower_units": int(float(row[f"lower_units_year_{year}"])),
         "upper_units": int(float(row[f"upper_units_year_{year}"])),
         "observations": int(float(row[f"n_with_year_{year}"])),
         "nameplates": int(float(row[f"nameplates_with_year_{year}"])),
         "pairs": int(float(row[f"nameplates_with_year_{year}"]))}
        for year in YEARS if _number(row[f"impact_pct_year_{year}"]) is not None
    ]


def _direction(by_panel: dict[str, dict]) -> str:
    """Sign agreement of the strict and broad panels over the years both estimate."""
    years = [{p["year"]: p["impact_pct"] for p in by_panel[panel]["by_year"]} for panel in ("strict", "broad")
             if panel in by_panel]
    shared = sorted(set(years[0]) & set(years[1])) if len(years) == 2 else []
    if not shared:
        return "single_panel"
    signs = {value > 0 for panel in years for year, value in panel.items() if year in shared}
    return "mixed" if len(signs) == 2 else ("up" if signs.pop() else "down")


def _exploratory(path: Path) -> dict | None:
    if not path.exists():
        return None
    with path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    items: dict[tuple[str, str], dict] = {}
    panel_sizes: dict[str, int] = {}
    for row in rows:
        panel_sizes[row["panel"]] = int(row["panel_nameplates"])
        item = items.setdefault((row["level"], row["name"]), {
            "level": row["level"], "id": row["name"], "label": row["label"], "category": row["category"],
            "subcategory": row["subcategory"], "panels": {}})
        panel = item["panels"].setdefault(row["panel"], {
            "nameplates_with": int(row["nameplates_with"]), "nameplates_without": int(row["nameplates_without"]),
            "by_year": []})
        panel["by_year"].append({"year": int(row["year"]), "impact_pct": float(row["impact_pct"]),
                                 "lower_pct": float(row["lower_pct"]), "upper_pct": float(row["upper_pct"]),
                                 "excludes_zero": row["excludes_zero"] == "True"})
    # category row, then each subcategory followed by its features
    subcategory_order = {name: i for i, name in enumerate(SUBCATEGORIES)}
    ordered = sorted(items.values(), key=lambda i: (
        CATEGORIES.index(i["category"]), subcategory_order.get(i["subcategory"], -1), i["level"] == "feature",
        i["label"]))
    for item in ordered:
        item["direction"] = _direction(item["panels"])
    return {
        "panels": [
            {"id": "strict", "label": "Strict", "nameplates": panel_sizes.get("strict", 0),
             "description": "publication-eligible trajectories only: one sales source, full baseline year, "
                            "no successor update inside the four years"},
            {"id": "broad", "label": "Broad", "nameplates": panel_sizes.get("broad", 0),
             "description": "every complete four-year trajectory, including mixed-source series and "
                            "overlapping updates; these quality flags enter as controls"},
        ],
        "items": ordered,
        "estimate_count": len(rows),
        "excludes_zero_count": sum(row["excludes_zero"] == "True" for row in rows),
        "method": "launches whose bundle contained the item vs launches whose bundle did not; market-adjusted "
                  "log sales change controlled for powertrain, baseline scale, calendar year and data-quality "
                  "flags; 95% interval clustered by nameplate",
        "caveat": "Exploratory, not publication-grade: the item is not separated from what launched with it, "
                  "and no interval-width gate is applied. OEMs often refresh models that are already declining, "
                  "so a negative value can reflect which models got the update rather than harm from it. "
                  "With many estimates about 1 in 20 intervals excludes zero by chance; trust a direction "
                  "only when both panels and several years agree.",
    }


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
         "models": json.loads(row["models"]), "pair_count": int(row["pair_count"]),
         "independent_count": int(row["independent_count"]),
         "independent_nameplates": int(row["independent_nameplates"]),
         "identification_status": row["identification_status"],
         "identification_reason": row["identification_reason"], "impact_by_year": _series(row)}
        for row in rows if row["level"] == "feature"
    ]
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
                "independent_count": int(row["independent_count"]) if row else 0,
                "independent_nameplates": int(row["independent_nameplates"]) if row else 0,
                "identification_status": row["identification_status"] if row else "not_identified",
                "identification_reason": row["identification_reason"] if row else "no historical feature evidence",
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
                "independent_count": int(row["independent_count"]) if row else 0,
                "independent_nameplates": int(row["independent_nameplates"]) if row else 0,
                "identification_status": row["identification_status"] if row else "not_identified",
                "identification_reason": row["identification_reason"] if row else "no historical feature evidence",
                "impact_by_year": _series(row) if row else [],  # empty: too few pairs for an estimate
                "subcategories": subcategories,
            })

    return {
        "title": "Sales Impact Forecast",
        "as_of": news_source["generated_at"],
        "horizon_years": list(YEARS),
        "categories": categories,
        "legacy_feature_count": len(features),
        "isolated_feature_count": sum(bool(feature["impact_by_year"]) for feature in features),
        "news_feature_count": len(news_by_id),
        "valid_pair_count": summary.get("valid_four_year_pairs", 0),
        "collection_target": summary.get("collection_target", 200),
        "independent_observation_count": summary.get("independent_observations", 0),
        "complete_observation_count": summary.get("complete_four_year_observations", 0),
        "independent_nameplate_count": summary.get("independent_nameplates", 0),
        "complete_nameplate_count": summary.get("complete_four_year_nameplates", 0),
        "method": "balanced four-year, market-adjusted event study; duplicate trim trajectories collapsed; target "
                  "feature partialled from supported peer features, bundle size, powertrain, baseline scale, calendar "
                  "year and recorded quality flags; uncertainty clustered by nameplate",
        "status": "conditional_counterfactual" if any(c["impact_by_year"] for c in categories)
                  else "insufficient_independent_data",
        "caveat": "No value is published unless all four years pass treated/control nameplate, residual-variation, "
                  "degrees-of-freedom, leverage and clustered-uncertainty gates. This controls observed differences but "
                  "does not prove causality; price, incentives, supply and unrecorded redesign changes may remain.",
        "source_plot": "data/analysis/chinese_pairs/plots/impact_by_subcategory.pdf",
        "exploratory": _exploratory(impact_path.with_name("bundle_exploratory.csv")),
    }


@cache
def impact_taxonomy() -> dict:
    return build_impact_taxonomy(DEFAULT_IMPACT_FILE, DEFAULT_NEWS_FILE)
