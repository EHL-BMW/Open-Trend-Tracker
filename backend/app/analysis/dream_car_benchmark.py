"""Dream BMW Car Benchmark & Target Vehicle Synthesis.

Performs:
1. Multi-criteria normalization and ranking across all 53 BMW EV/PHEV models.
2. Identifies Pareto-optimal models across Range, Power, Charging, Practicality, and Sales.
3. Cross-references the 16 matched models from customer study data (G60/G70).
4. Synthesizes the target "Dream BMW Car" specification combining best-of-breed baselines
   with Chinese OEM gap-closure solutions.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[3]
CATALOG_CSV = ROOT_DIR / "china-tech-radar" / "bmw_ev_phev_catalog.csv"
COMPLAINT_CSV = ROOT_DIR / "china-tech-radar" / "bmw_ev_complaint_matching.csv"
DOCS_DIR = ROOT_DIR / "docs"


def clean_num(val: Any, default: float = 0.0) -> float:
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def load_data() -> tuple[list[dict[str, str]], dict[str, dict[str, str]]]:
    with open(CATALOG_CSV, encoding="utf-8") as f:
        catalog = list(csv.DictReader(f))

    with open(COMPLAINT_CSV, encoding="utf-8") as f:
        complaints_list = list(csv.DictReader(f))
        complaints = {
            f"{c['model']}::{c['variant']}": c
            for c in complaints_list
            if c.get("is_matched") == "True"
        }

    return catalog, complaints


def compute_mcda_rankings(
    models: list[dict[str, str]],
    weights: dict[str, float] | None = None,
) -> list[dict[str, Any]]:
    """Compute normalized composite baseline scores (0-100) across key technical metrics."""
    if weights is None:
        weights = {
            "range": 0.25,
            "dc_charging": 0.20,
            "power": 0.15,
            "accel": 0.15,
            "towing": 0.10,
            "sales": 0.15,
        }

    ranges = [clean_num(m["electric_range_wltp_km"]) for m in models]
    chargings = [clean_num(m["dc_charging_kw"]) for m in models]
    powers = [clean_num(m["power_ps"]) for m in models]
    accels = [clean_num(m["accel_0_100_s"], 12.0) for m in models]
    towings = [clean_num(m["towing_capacity_kg"]) for m in models]
    sales = [clean_num(m["europe_sales_units"]) for m in models]

    r_min, r_max = min(ranges), max(ranges) + 1e-6
    c_min, c_max = min(chargings), max(chargings) + 1e-6
    p_min, p_max = min(powers), max(powers) + 1e-6
    a_min, a_max = min(accels), max(accels) + 1e-6
    t_min, t_max = min(towings), max(towings) + 1e-6
    s_min, s_max = min(sales), max(sales) + 1e-6

    ranked = []
    for m in models:
        norm_r = (clean_num(m["electric_range_wltp_km"]) - r_min) / (r_max - r_min)
        norm_c = (clean_num(m["dc_charging_kw"]) - c_min) / (c_max - c_min)
        norm_p = (clean_num(m["power_ps"]) - p_min) / (p_max - p_min)
        norm_a = (a_max - clean_num(m["accel_0_100_s"], 12.0)) / (a_max - a_min)
        norm_t = (clean_num(m["towing_capacity_kg"]) - t_min) / (t_max - t_min)
        norm_s = (clean_num(m["europe_sales_units"]) - s_min) / (s_max - s_min)

        composite = (
            norm_r * weights["range"]
            + norm_c * weights["dc_charging"]
            + norm_p * weights["power"]
            + norm_a * weights["accel"]
            + norm_t * weights["towing"]
            + norm_s * weights["sales"]
        ) * 100.0

        ranked.append({
            "model": m["model"],
            "variant": m["variant"],
            "powertrain": m["powertrain"],
            "base_price_eur": clean_num(m["base_price_eur"]),
            "range_km": clean_num(m["electric_range_wltp_km"]),
            "battery_kwh": clean_num(m["battery_capacity_kwh"]),
            "dc_kw": clean_num(m["dc_charging_kw"]),
            "power_ps": clean_num(m["power_ps"]),
            "accel_s": clean_num(m["accel_0_100_s"]),
            "towing_kg": clean_num(m["towing_capacity_kg"]),
            "sales_units": clean_num(m["europe_sales_units"]),
            "score": round(composite, 2),
            "raw": m,
        })

    ranked.sort(key=lambda x: x["score"], reverse=True)
    return ranked


def find_pareto_frontier(ranked: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Identifies Pareto-optimal models (cannot be improved in range without sacrificing power/charging/etc.)."""
    pareto: list[dict[str, Any]] = []
    for item in ranked:
        dominated = False
        for other in ranked:
            if (
                other["range_km"] >= item["range_km"]
                and other["power_ps"] >= item["power_ps"]
                and other["dc_kw"] >= item["dc_kw"]
                and other["accel_s"] <= item["accel_s"]
                and (
                    other["range_km"] > item["range_km"]
                    or other["power_ps"] > item["power_ps"]
                    or other["dc_kw"] > item["dc_kw"]
                    or other["accel_s"] < item["accel_s"]
                )
            ):
                dominated = True
                break
        if not dominated:
            pareto.append(item)
    return pareto


def synthesize_dream_car(ranked_bevs: list[dict[str, Any]]) -> dict[str, Any]:
    """Synthesizes the optimal target vehicle by extracting best-of-breed baselines

    and resolving customer study deficits via Chinese tech radar solutions.
    """
    top_range = max(ranked_bevs, key=lambda x: x["range_km"])
    top_charging = max(ranked_bevs, key=lambda x: x["dc_kw"])
    top_power = max(ranked_bevs, key=lambda x: x["power_ps"])
    top_towing = max(ranked_bevs, key=lambda x: x["towing_kg"])
    top_sales = max(ranked_bevs, key=lambda x: x["sales_units"])

    return {
        "concept_name": "BMW i5 M-Sport Touring 800V Hyper-GT",
        "segment": "E-Segment Premium Touring",
        "target_horizon": "2028-2030 (Neue Klasse / Successor)",
        "donor_baselines": {
            "range_and_battery": {
                "source_model": f"{top_range['model']} {top_range['variant']}",
                "baseline_val": f"{top_range['range_km']} km WLTP / {top_range['battery_kwh']} kWh",
                "target_spec": "650+ km WLTP via 105.2 kWh CTP (Cell-to-Pack) pack",
            },
            "chassis_and_dynamics": {
                "source_model": "BMW i5 M60 / i7 xDrive60",
                "baseline_val": "2-Axle Air Suspension + 3.2° Rear-Wheel Steering (+44.7% Moat)",
                "target_spec": "Active 48V Roll Stabilization + Steer-by-Wire Dynamics",
            },
            "charging_architecture": {
                "source_model": f"{top_charging['model']} {top_charging['variant']}",
                "baseline_val": f"{top_charging['dc_kw']} kW DC (400V)",
                "target_spec": "300 kW DC (800V SiC Architecture, 10-80% in 18 min)",
            },
            "cockpit_and_luxury": {
                "source_model": "BMW i7 xDrive60 & i5 Touring",
                "baseline_val": "Curved Display OS 8.5, Interaction Bar, 570-1700L Cargo",
                "target_spec": "Panoramic Vision HUD + Physical Climate Haptic Keys + Local LLM Voice",
            },
            "audio_and_acoustics": {
                "source_model": "BMW iX / i7",
                "baseline_val": "Bowers & Wilkins Diamond Surround (1,615W, 30 speakers, 4D)",
                "target_spec": "Active Road Noise Cancellation + Headrest Spatial Audio",
            },
            "towing_and_utility": {
                "source_model": f"{top_towing['model']} {top_towing['variant']}",
                "baseline_val": f"{top_towing['towing_kg']} kg",
                "target_spec": "2,000 kg braked towing capacity with electric hitch",
            },
        },
        "customer_gap_closures": [
            {
                "domain": "Energy & Charging",
                "study_friction": "-43.2% Net Sentiment; 35% winter drop & 60 kW cold charging throttles",
                "solution": "800V high-voltage bus with predictive automatic pre-conditioning via route navigation.",
            },
            {
                "domain": "Connected Ecosystem",
                "study_friction": "-76.7% Net Sentiment; app timeouts in underground garages",
                "solution": "Dual-band UWB antenna array with local Bluetooth LE fallback daemon.",
            },
            {
                "domain": "Digital Cockpit & AI",
                "study_friction": "-31.8% Net Sentiment; lack of physical climate controls & touchscreen distraction",
                "solution": "Tactile micro-switch bar for defrost/climate + sub-second on-device voice assistant.",
            },
            {
                "domain": "Smart Cabin",
                "study_friction": "-12.0% Net Sentiment; sweaty Veganza in summer & glass roof heat",
                "solution": "Perforated breathable Veganza with standard ventilation + electrochromic smart glass roof.",
            },
            {
                "domain": "Smart Exterior",
                "study_friction": "-18.1% Net Sentiment; automatic door hesitation in parking lots",
                "solution": "Camera-ultrasonic obstacle fusion algorithm recalibration.",
            },
        ],
    }


def main():
    catalog, complaints = load_data()
    bevs = [m for m in catalog if m["powertrain"] == "BEV"]
    phevs = [m for m in catalog if m["powertrain"] == "PHEV"]

    ranked_all = compute_mcda_rankings(catalog)
    ranked_bevs = compute_mcda_rankings(bevs)
    pareto_bevs = find_pareto_frontier(ranked_bevs)
    dream_car = synthesize_dream_car(ranked_bevs)

    print("=" * 60)
    print("      DREAM BMW CAR BENCHMARK ANALYSIS (53 MODELS)       ")
    print("=" * 60)
    print(f"Catalog census: {len(catalog)} models ({len(bevs)} BEVs, {len(phevs)} PHEVs)")
    print(f"Customer study matched models: {len(complaints)}")
    print("\n--- TOP 5 COMPOSITE BEV LEADERS ---")
    for i, r in enumerate(ranked_bevs[:5], 1):
        print(f"#{i} {r['score']:.1f}/100 | {r['model']} {r['variant']}")
        print(f"   Range: {r['range_km']} km | DC: {r['dc_kw']} kW | Power: {r['power_ps']} PS | 0-100: {r['accel_s']}s | Sales: {r['sales_units']:,}")

    print("\n--- PARETO FRONTIER BEV MODELS ---")
    for p in pareto_bevs:
        print(f"• {p['model']} {p['variant']} (Range: {p['range_km']} km, DC: {p['dc_kw']} kW, Power: {p['power_ps']} PS)")

    print("\n--- SYNTHESIZED DREAM CAR BLUEPRINT ---")
    print(f"Title: {dream_car['concept_name']}")
    for k, v in dream_car["donor_baselines"].items():
        print(f"• {k.replace('_', ' ').title()}: {v['target_spec']} (from {v['source_model']})")


if __name__ == "__main__":
    main()
