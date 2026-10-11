"""Category and subcategory sales-impact view for the Forecast tab.

The numeric scenarios come from the same Chinese-200 forecast artifact and
planning-prior model used by ``official_sales.plot_feature_forecast``.  News
topics are attached as recent signals only: they do not receive an invented
sales effect until a comparable legacy feature is available.
"""
from __future__ import annotations

import csv
import json
from functools import cache
from pathlib import Path

from app.analysis.official_sales import CATEGORY_IMPACT_PRIORS, FORECAST_SATURATION, YEARS
from app.paths import DATA_DIR, ROOT_DIR


DEFAULT_FORECAST_FILE = DATA_DIR / "analysis" / "chinese_200" / "feature_sales_impact_4_year_forecast.csv"
DEFAULT_NEWS_FILE = ROOT_DIR / "frontend" / "src" / "content" / "china_tech_trends.json"

# A stable layer between the broad technical category and a concrete feature.
# A legacy feature belongs to one subcategory; news IDs are the canonical IDs
# already used by Feature Radar.
SUBCATEGORY_TAXONOMY = (
    {
        "id": "battery_range",
        "label": "Battery & range",
        "category": "Energy & Charging",
        "legacy": ("900V system + 102 kWh battery",),
        "news": ("solid_state", "sodium_ion"),
    },
    {
        "id": "charging_replenishment",
        "label": "Charging & replenishment",
        "category": "Energy & Charging",
        "legacy": ("Charging + battery-swap station network",),
        "news": ("ultra_charging", "battery_swap", "v2g"),
    },
    {
        "id": "high_voltage_powertrain",
        "label": "High-voltage powertrain",
        "category": "Energy & Charging",
        "legacy": (),
        "news": ("hv_800v",),
    },
    {
        "id": "assisted_driving",
        "label": "Assisted driving",
        "category": "Driving Assistance",
        "legacy": ("World-model ADAS + point-to-point navigation",),
        "news": ("urban_noa", "e2e_vla", "l3_autonomy"),
    },
    {
        "id": "perception_compute",
        "label": "Perception & driving compute",
        "category": "Driving Assistance",
        "legacy": (),
        "news": ("lidar", "adas_chips"),
    },
    {
        "id": "autonomous_mobility",
        "label": "Autonomous mobility",
        "category": "Driving Assistance",
        "legacy": (),
        "news": ("robotaxi",),
    },
    {
        "id": "cockpit_intelligence",
        "label": "Cockpit intelligence",
        "category": "Digital Cockpit & AI",
        "legacy": (),
        "news": ("cockpit_llm",),
    },
    {
        "id": "vehicle_compute",
        "label": "Vehicle compute & E/E",
        "category": "Digital Cockpit & AI",
        "legacy": ("5 nm automotive SoC + full-domain E/E architecture",),
        "news": ("central_compute",),
    },
    {
        "id": "software_lifecycle",
        "label": "Software lifecycle & OTA",
        "category": "Connected Ecosystem",
        "legacy": (),
        "news": ("ota",),
    },
    {
        "id": "cross_device_ecosystem",
        "label": "Cross-device ecosystem",
        "category": "Connected Ecosystem",
        "legacy": (),
        "news": ("phone_car_eco",),
    },
    {
        "id": "seating_comfort",
        "label": "Seating & occupant comfort",
        "category": "Smart Cabin",
        "legacy": (
            "Dual cushion airbags + seat-integrated belts",
            "Second-row zero-gravity seats + leg support",
            "Six-/seven-seat cabin configuration",
        ),
        "news": ("smart_seats",),
    },
    {
        "id": "cabin_entertainment",
        "label": "Cabin entertainment & audio",
        "category": "Smart Cabin",
        "legacy": (
            "Integrated cabin display + audio entertainment",
            "Roof center speaker + Dirac RRM audio",
        ),
        "news": (),
    },
    {
        "id": "ride_body_control",
        "label": "Ride & body control",
        "category": "Vehicle Dynamics",
        "legacy": (
            "CDC dampers + hydraulic rear-subframe bushings",
            "Software-controlled active chassis system",
        ),
        "news": ("active_suspension",),
    },
    {
        "id": "by_wire_controls",
        "label": "Steer/brake-by-wire controls",
        "category": "Vehicle Dynamics",
        "legacy": (),
        "news": ("steer_by_wire",),
    },
    {
        "id": "body_manufacturing",
        "label": "Body structure & manufacturing",
        "category": "Vehicle Dynamics",
        "legacy": (),
        "news": ("giga_casting",),
    },
    {
        "id": "lighting_visibility",
        "label": "Lighting & visibility",
        "category": "Smart Exterior",
        "legacy": ("ADB matrix headlights + Double-Dash DRL",),
        "news": ("smart_lighting",),
    },
    {
        "id": "exterior_personalization",
        "label": "Exterior personalization",
        "category": "Smart Exterior",
        "legacy": ("New Moon Silver paint + 21-inch wheels",),
        "news": (),
    },
)


def _trajectory(prior: float) -> list[dict]:
    return [
        {"year": year, "impact_pct": round(prior * FORECAST_SATURATION[year], 3)}
        for year in YEARS
    ]


def _load_legacy(path: Path) -> dict[str, dict]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    output = {}
    for row in rows:
        name = row["display_name"]
        output[name] = {
            "name": name,
            "category": row["category"],
            "models": json.loads(row["models"]),
            "pair_count": int(row["pair_count"]),
            "impact_by_year": [
                {
                    "year": year,
                    "impact_pct": round(float(row[f"estimated_sales_impact_year_{year}_pct"]), 3),
                    "lower_pct": round(float(row[f"lower_year_{year}_pct"]), 3),
                    "upper_pct": round(float(row[f"upper_year_{year}_pct"]), 3),
                }
                for year in YEARS
            ],
        }
    return output


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


def _mean_legacy_trajectory(features: list[dict]) -> list[dict] | None:
    if not features:
        return None
    return [
        {
            "year": year,
            "impact_pct": round(sum(f["impact_by_year"][year - 1]["impact_pct"] for f in features) / len(features), 3),
            "lower_pct": round(sum(f["impact_by_year"][year - 1]["lower_pct"] for f in features) / len(features), 3),
            "upper_pct": round(sum(f["impact_by_year"][year - 1]["upper_pct"] for f in features) / len(features), 3),
        }
        for year in YEARS
    ]


def build_impact_taxonomy(forecast_path: Path, news_path: Path) -> dict:
    legacy_by_name = _load_legacy(forecast_path)
    news_source, news_by_id = _load_news(news_path)
    categories: dict[str, dict] = {}
    used_legacy: set[str] = set()
    used_news: set[str] = set()

    for definition in SUBCATEGORY_TAXONOMY:
        category = definition["category"]
        if category not in categories:
            prior = CATEGORY_IMPACT_PRIORS[category]
            categories[category] = {
                "id": category.lower().replace(" & ", "-").replace(" ", "-"),
                "label": category,
                "impact_by_year": _trajectory(prior),
                "subcategories": [],
            }
        legacy = [legacy_by_name[name] for name in definition["legacy"] if name in legacy_by_name]
        news = [news_by_id[item] for item in definition["news"] if item in news_by_id]
        used_legacy.update(item["name"] for item in legacy)
        used_news.update(item["id"] for item in news)
        categories[category]["subcategories"].append({
            "id": definition["id"],
            "label": definition["label"],
            "impact_by_year": _mean_legacy_trajectory(legacy),
            "legacy_features": legacy,
            "news_features": news,
        })

    missing_legacy = sorted(set(legacy_by_name) - used_legacy)
    missing_news = sorted(set(news_by_id) - used_news)
    if missing_legacy or missing_news:
        raise ValueError(
            "subcategory taxonomy is incomplete: "
            f"legacy={missing_legacy or 'none'}, news={missing_news or 'none'}"
        )

    return {
        "title": "Sales Impact Forecast",
        "as_of": news_source["generated_at"],
        "horizon_years": list(YEARS),
        "categories": list(categories.values()),
        "legacy_feature_count": len(legacy_by_name),
        "news_feature_count": len(news_by_id),
        "method": "category planning prior × adoption saturation; subcategory is the mean of mapped Chinese-200 feature scenarios",
        "status": "scenario_estimate_not_sales_fitted",
        "caveat": "Planning scenario, not a causal or sales-fitted prediction. Recent news signals are mapped for context and do not receive an independent sales effect.",
        "source_plot": "data/analysis/chinese/plots/feature_sales_impact_4_year_forecast.pdf",
    }


@cache
def impact_taxonomy() -> dict:
    return build_impact_taxonomy(DEFAULT_FORECAST_FILE, DEFAULT_NEWS_FILE)
