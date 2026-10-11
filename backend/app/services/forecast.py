"""Backend-only forecast, price, and engineering-comparison services.

The frontend receives display-ready series from this module. It must not repeat
forecast formulas or infer BMW availability from raw files.
"""
from __future__ import annotations

from functools import cache
from statistics import median

from app.analysis.interactive_feature_plot import (
    DEFAULT_BMW_SALES,
    DEFAULT_INPUT,
    build_snapshots,
    estimate_bmw_sales,
    load_bmw_sales_history,
)
from app.mapping import Mapper
from app.pipeline import existing_features, feature_catalog

DEFAULT_ANNUAL_PRICE_RATE = 0.025
DEFAULT_PRICE_BASE_YEAR = 2026


@cache
def forecast_catalog() -> dict:
    """Return feature trajectories and BMW series for the forecast page."""
    snapshots = build_snapshots(DEFAULT_INPUT)
    if not snapshots:
        raise ValueError(f"no comparable version pairs in {DEFAULT_INPUT}")
    latest_year = max(snapshots)
    history = load_bmw_sales_history(DEFAULT_BMW_SALES)
    return {
        "as_of_year": latest_year,
        "horizon_years": [1, 2, 3, 4],
        "features": snapshots[latest_year],
        "categories": sorted({row["category"] for row in snapshots[latest_year]}),
        "bmw_sales_history": history,
        "method": "category prior × feature multiplier × adoption saturation",
        "status": "scenario_estimate_not_sales_fitted",
        "caveat": "Planning scenario, not a causal or sales-fitted prediction.",
    }


def sales_forecast(model: str, market: str, selected_names: list[str]) -> dict:
    """Return a display-ready BMW sales forecast for selected feature names."""
    catalog = forecast_catalog()
    history = catalog["bmw_sales_history"]
    if model not in history:
        raise KeyError(f"unknown BMW model {model!r}")
    if market not in history[model]:
        raise KeyError(f"unknown market {market!r} for {model}")
    by_name = {row["feature"]: row for row in catalog["features"]}
    unknown = sorted(set(selected_names) - set(by_name))
    if unknown:
        raise KeyError(f"unknown forecast features: {', '.join(unknown)}")
    selected = [by_name[name] for name in selected_names]
    result = estimate_bmw_sales(history, model, market, selected)
    return {
        "model": model,
        "market": market,
        "selected_features": selected_names,
        **result,
        "status": catalog["status"],
        "caveat": catalog["caveat"],
    }


@cache
def _bmw_option_prices() -> list[dict]:
    mapper = Mapper()
    features = feature_catalog(mapper)
    rows = existing_features(mapper, features)
    priced = rows[rows["price_eur"].fillna(0) > 0]
    output = []
    for (vehicle, feature), group in priced.groupby(["car", "feature"]):
        values = [float(value) for value in group["price_eur"]]
        output.append({
            "vehicle": vehicle,
            "feature_id": feature,
            "feature": features[feature]["name"],
            "category": features[feature]["category_name"],
            "current_price_eur": round(median(values), 2),
            "source_price_count": len(values),
            "sources": sorted(set(group["source"])),
        })
    return sorted(output, key=lambda row: (row["vehicle"], row["category"], row["feature"]))


def price_forecast(
    vehicle: str,
    target_year: int = 2030,
    annual_rate: float = DEFAULT_ANNUAL_PRICE_RATE,
) -> dict:
    """Inflate catalog option-price evidence to a target year.

    This is a transparent planning estimate. It deliberately does not invent a
    cost for features with no positive option price in the BMW source PDFs.
    """
    if target_year < DEFAULT_PRICE_BASE_YEAR:
        raise ValueError(f"target_year must be >= {DEFAULT_PRICE_BASE_YEAR}")
    if not -0.5 < annual_rate < 1:
        raise ValueError("annual_rate must be between -0.5 and 1")
    rows = [dict(row) for row in _bmw_option_prices() if row["vehicle"] == vehicle]
    factor = (1 + annual_rate) ** (target_year - DEFAULT_PRICE_BASE_YEAR)
    for row in rows:
        row["forecast_price_eur"] = round(row["current_price_eur"] * factor, 2)
    return {
        "vehicle": vehicle,
        "base_year": DEFAULT_PRICE_BASE_YEAR,
        "target_year": target_year,
        "annual_rate": annual_rate,
        "items": rows,
        "method": "median positive BMW option-list price × compound annual price rate",
        "caveat": "Reference option-price scenario, not a BOM, margin, or supplier-cost forecast.",
    }


@cache
def engineering_comparison(vehicle: str) -> dict:
    """Convert the existing BMW catalog into editable engineering input rows."""
    mapper = Mapper()
    features = feature_catalog(mapper)
    rows = existing_features(mapper, features)
    vehicle_rows = rows[rows["car"] == vehicle]
    items = []
    for feature_id, info in features.items():
        matches = vehicle_rows[vehicle_rows["feature"] == feature_id]
        if matches.empty:
            availability = "not_listed"
            standard_share = optional_share = 0.0
            sources = []
        else:
            standard_share = float(matches["standard_share"].max())
            optional_share = float(matches["optional_share"].max())
            availability = "standard" if standard_share > 0 else "optional"
            sources = sorted(set(matches["source"]))
        items.append({
            "feature_id": feature_id,
            "feature": info["name"],
            "category": info["category_name"],
            "availability": availability,
            "standard_share": standard_share,
            "optional_share": optional_share,
            "engineering_input": availability != "standard",
            "sources": sources,
        })
    return {
        "vehicle": vehicle,
        "items": items,
        "method": "BMW option-list parser + canonical taxonomy mapping",
        "note": "engineering_input=true means the feature is optional or not listed; an engineer must still confirm feasibility.",
    }
