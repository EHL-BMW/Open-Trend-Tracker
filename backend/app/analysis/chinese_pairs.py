"""Market-adjusted four-year event-study estimates for Chinese vehicle features.

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
or ICE passenger market. SRNI-CAR observations use the total market aggregated from the same
monthly source, avoiding a denominator/provider mismatch. Repeated trim rows that reuse the same nameplate sales trajectory are
collapsed before estimation. On the balanced four-year panel, the coefficient for an item is
estimated after partialling out supported peer items, bundle size, powertrain, baseline scale,
calendar year and recorded data-quality flags. Standard errors are clustered by nameplate.

This is a dynamic, regression-adjusted difference-in-differences association. It is suitable for
screening observational product data, but it is not a causal claim: price, incentives, supply,
distribution, brand strength and unrecorded redesign changes may remain confounded.

Run from ``backend/``::

    uv run python -m app.analysis.chinese_pairs
"""
from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from app.paths import DATA_DIR, EXTERNAL_DIR
from app.analysis.srni_panel import SRNI_SERIES

INPUT_DIR = EXTERNAL_DIR / "chinese_pairs"
OUTPUT_DIR = DATA_DIR / "analysis" / "chinese_pairs"
YEARS = (1, 2, 3, 4)
MIN_NAMEPLATES = 5
MIN_CLUSTERS = 10
MIN_RESIDUAL_DOF = 8
MIN_RESIDUAL_INFORMATION = 0.5
MAX_LOG_STANDARD_ERROR = 0.35
MAX_LEVERAGE = 0.8

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
    market = {int(r["year"]): {"NEV": int(r["nev_retail"]),
                               "ICE": int(r["total_retail"]) - int(r["nev_retail"]),
                               "TOTAL": int(r["total_retail"])}
              for r in read_csv(input_dir / "market_sales.csv")}
    srni_market_path = input_dir / "srni_market_sales.csv"
    if srni_market_path.exists():
        for row in read_csv(srni_market_path):
            market.setdefault(int(row["year"]), {})["SRNI_TOTAL"] = int(row["total_units"])
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
        market_segment = "SRNI_TOTAL" if series == SRNI_SERIES else segment
        row = {"pair_id": p["pair_id"], "brand": p["brand"], "car_model": model, "powertrain": segment,
               "change_type": p["change_type"], "current_version": p["current_version"],
               "current_launch": p["current_launch"], "successor_launch": later[0] if later else "",
               "nameplate_launch": p["nameplate_launch"], "sales_series": series,
               "market_denominator": market_segment,
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
            if (units and base and year in market and base_year in market
                    and market_segment in market[year] and market_segment in market[base_year]):
                change = units / base - 1
                excess = math.log(units / base) - math.log(
                    market[year][market_segment] / market[base_year][market_segment]
                )
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
        row["publication_eligible"] = (
            row["valid_four_year_pair"] and series != "four_year_nameplate" and not partial
            and not any("successor_overlap" in row[f"quality_year_{k}"] for k in YEARS)
        )
        rows.append(row)
    return rows


def _pct(log_value: float) -> float:
    """Convert a bounded log coefficient to a percentage without overflowing."""
    return round((math.exp(max(-20.0, min(20.0, log_value))) - 1) * 100, 2)


def independent_observations(pair_rows: list[dict], features: list[dict]) -> tuple[list[dict], dict]:
    """Collapse trim rows that reuse exactly the same annual nameplate trajectory."""
    membership: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    parents: dict[tuple[str, str], tuple[str, str]] = {}
    for feature in features:
        pair_id = feature["pair_id"]
        for level, column in (("feature", "feature"), ("subcategory", "subcategory"), ("category", "category")):
            membership[pair_id][level].add(feature[column])
        parents[("feature", feature["feature"])] = (feature["subcategory"], feature["category"])
        parents[("subcategory", feature["subcategory"])] = (feature["subcategory"], feature["category"])
        parents[("category", feature["category"])] = ("", feature["category"])

    identity_fields = ["car_model", "powertrain", "sales_series", "market_denominator",
                       "baseline_year", "baseline_sales"]
    for year in YEARS:
        identity_fields.extend((f"year_{year}", f"sales_year_{year}"))
    grouped: dict[tuple, dict] = {}
    for pair in pair_rows:
        key = tuple(pair[field] for field in identity_fields)
        observation = grouped.setdefault(key, {
            "brand": pair["brand"], "car_model": pair["car_model"], "powertrain": pair["powertrain"],
            "sales_series": pair["sales_series"], "baseline_year": pair["baseline_year"],
            "market_denominator": pair["market_denominator"],
            "baseline_sales": pair["baseline_sales"], "pair_ids": set(),
            "publication_eligible": True,
            "items": defaultdict(set), "quality": defaultdict(set),
        })
        observation["publication_eligible"] = (
            observation["publication_eligible"] and pair["publication_eligible"]
        )
        observation["pair_ids"].add(pair["pair_id"])
        for level in ("feature", "subcategory", "category"):
            observation["items"][level].update(membership[pair["pair_id"]][level])
        for year in YEARS:
            for field in ("year", "sales_year", "change_pct_year", "excess_log_year", "status_year"):
                observation[f"{field}_{year}"] = pair[f"{field}_{year}"]
            observation["quality"][year].update(filter(None, pair[f"quality_year_{year}"].split(";")))

    observations = []
    for index, observation in enumerate(grouped.values(), 1):
        observation["observation_id"] = f"OBS{index:03d}"
        observations.append(observation)
    return observations, parents


def serializable_observations(observations: list[dict]) -> list[dict]:
    """Flatten analysis-only sets for the auditable CSV output."""
    rows = []
    for observation in observations:
        row = {
            "observation_id": observation["observation_id"], "brand": observation["brand"],
            "car_model": observation["car_model"], "powertrain": observation["powertrain"],
            "sales_series": observation["sales_series"], "pair_count": len(observation["pair_ids"]),
            "market_denominator": observation["market_denominator"],
            "publication_eligible": observation["publication_eligible"],
            "pair_ids": json.dumps(sorted(observation["pair_ids"])),
            "categories": json.dumps(sorted(observation["items"]["category"]), ensure_ascii=False),
            "subcategories": json.dumps(sorted(observation["items"]["subcategory"]), ensure_ascii=False),
            "features": json.dumps(sorted(observation["items"]["feature"]), ensure_ascii=False),
            "baseline_year": observation["baseline_year"], "baseline_sales": observation["baseline_sales"],
        }
        for year in YEARS:
            for field in ("year", "sales_year", "change_pct_year", "excess_log_year", "status_year"):
                row[f"{field}_{year}"] = observation[f"{field}_{year}"]
            row[f"quality_year_{year}"] = ";".join(sorted(observation["quality"][year]))
        rows.append(row)
    return rows


def _column_basis(matrix: np.ndarray) -> tuple[np.ndarray, int]:
    """Orthonormal basis for a possibly rank-deficient control matrix."""
    u, singular, _ = np.linalg.svd(matrix, full_matrices=False)
    if not len(singular) or singular[0] == 0:
        return np.empty((len(matrix), 0)), 0
    tolerance = max(matrix.shape) * np.finfo(float).eps * singular[0]
    rank = int(np.sum(singular > tolerance))
    return u[:, :rank], rank


def _unit_effect(log_effect: float, observations: list[dict], year: int) -> tuple[int, int]:
    """Average and sample-total counterfactual units, counting each nameplate once."""
    by_nameplate: dict[str, list[float]] = defaultdict(list)
    multiplier = 1 - math.exp(max(-20.0, min(20.0, -log_effect)))
    for observation in observations:
        by_nameplate[observation["car_model"]].append(float(observation[f"sales_year_{year}"]) * multiplier)
    per_nameplate = [float(np.mean(values)) for values in by_nameplate.values()]
    return round(float(np.mean(per_nameplate))), round(float(np.sum(per_nameplate)))


def isolated_effect(observations: list[dict], level: str, target: str, names: list[str], year: int) -> dict:
    """FWL event-study coefficient with nameplate-clustered uncertainty on a balanced panel."""
    balanced = [o for o in observations if o["publication_eligible"]
                and all(o[f"status_year_{k}"] == "observed" for k in YEARS)]
    target_values = np.array([target in o["items"][level] for o in balanced], dtype=float)
    treated = [o for o, value in zip(balanced, target_values, strict=True) if value]
    untreated = [o for o, value in zip(balanced, target_values, strict=True) if not value]
    treated_models = {o["car_model"] for o in treated}
    untreated_models = {o["car_model"] for o in untreated}
    clusters = {o["car_model"] for o in balanced}
    result = {
        "n_with": len(treated), "n_without": len(untreated),
        "nameplates_with": len(treated_models), "nameplates_without": len(untreated_models),
        "cluster_count": len(clusters), "residual_dof": None, "residual_information": None,
        "max_leverage": None, "status": "not_identified", "reason": "",
    }
    reasons = []
    if len(treated_models) < MIN_NAMEPLATES:
        reasons.append(f"fewer than {MIN_NAMEPLATES} treated nameplates")
    if len(untreated_models) < MIN_NAMEPLATES:
        reasons.append(f"fewer than {MIN_NAMEPLATES} control nameplates")
    if len(clusters) < MIN_CLUSTERS:
        reasons.append(f"fewer than {MIN_CLUSTERS} nameplate clusters")
    if not balanced:
        result["reason"] = "; ".join(["no complete four-year trajectories", *reasons])
        return result

    baseline = np.log(np.array([float(o["baseline_sales"]) for o in balanced]))
    baseline = (baseline - baseline.mean()) / (baseline.std() or 1.0)
    bundle_size = np.array([len(o["items"][level] - {target}) for o in balanced], dtype=float)
    bundle_size = (bundle_size - bundle_size.mean()) / (bundle_size.std() or 1.0)
    controls = [np.ones(len(balanced)), np.array([o["powertrain"] == "NEV" for o in balanced], dtype=float),
                baseline, bundle_size]
    calendar_years = sorted({int(o[f"year_{year}"]) for o in balanced})
    controls.extend(np.array([int(o[f"year_{year}"]) == value for o in balanced], dtype=float)
                    for value in calendar_years[1:])
    quality_flags = sorted(set().union(*(o["quality"][year] for o in balanced)))
    controls.extend(np.array([flag in o["quality"][year] for o in balanced], dtype=float) for flag in quality_flags)

    # Rare peer indicators are disclosed as part of the bundle but not assigned unstable coefficients.
    observed_models = {o["car_model"] for o in balanced}
    supported_peers = []
    for name in names:
        if name == target:
            continue
        with_name = {o["car_model"] for o in balanced if name in o["items"][level]}
        if len(with_name) >= MIN_NAMEPLATES and len(observed_models - with_name) >= MIN_NAMEPLATES:
            supported_peers.append(name)
    controls.extend(np.array([name in o["items"][level] for o in balanced], dtype=float)
                    for name in supported_peers)
    control_matrix = np.column_stack(controls)
    basis, control_rank = _column_basis(control_matrix)
    target_residual = target_values - basis @ (basis.T @ target_values)
    information = float(target_residual @ target_residual)
    full_rank = control_rank + (1 if information > 1e-10 else 0)
    dof = len(balanced) - full_rank
    result["residual_dof"] = dof
    result["residual_information"] = round(information, 4)
    if information < MIN_RESIDUAL_INFORMATION:
        reasons.append("feature is confounded with the launch bundle")
    if dof < MIN_RESIDUAL_DOF:
        reasons.append(f"fewer than {MIN_RESIDUAL_DOF} residual degrees of freedom")
    if reasons:
        result["reason"] = "; ".join(dict.fromkeys(reasons))
        return result

    outcome = np.array([float(o[f"excess_log_year_{year}"]) for o in balanced])
    outcome_residual = outcome - basis @ (basis.T @ outcome)
    coefficient = float(target_residual @ outcome_residual / information)
    residual = outcome_residual - coefficient * target_residual
    leverage = np.sum(basis ** 2, axis=1) + target_residual ** 2 / information
    result["max_leverage"] = round(float(np.max(leverage)), 4)
    if np.max(leverage) >= MAX_LEVERAGE:
        result["reason"] = "high-leverage observations prevent stable inference"
        return result

    # One-parameter FWL form of the CR1 nameplate-clustered covariance estimator.
    cluster_scores = []
    for cluster in sorted(clusters):
        mask = np.array([o["car_model"] == cluster for o in balanced])
        cluster_scores.append(float(np.sum(target_residual[mask] * residual[mask])))
    correction = len(clusters) / (len(clusters) - 1) * (len(balanced) - 1) / dof
    variance = correction * sum(score ** 2 for score in cluster_scores) / information ** 2
    standard_error = math.sqrt(max(0.0, variance))
    result["standard_error_log"] = round(standard_error, 4)
    if standard_error > MAX_LOG_STANDARD_ERROR:
        result["reason"] = "95% interval is too wide for publication"
        return result

    lower_log, upper_log = coefficient - 1.96 * standard_error, coefficient + 1.96 * standard_error
    mean_units, sample_units = _unit_effect(coefficient, treated, year)
    lower_units, lower_sample_units = _unit_effect(lower_log, treated, year)
    upper_units, upper_sample_units = _unit_effect(upper_log, treated, year)
    result.update({
        "status": "identified", "reason": "", "impact_pct": _pct(coefficient),
        "lower_pct": _pct(lower_log), "upper_pct": _pct(upper_log),
        "incremental_units": mean_units, "lower_units": lower_units, "upper_units": upper_units,
        "sample_incremental_units": sample_units,
        "sample_lower_units": lower_sample_units, "sample_upper_units": upper_sample_units,
    })
    return result


def impact(observations: list[dict], parents: dict) -> list[dict]:
    """Conditional market-adjusted estimates from independent, complete four-year trajectories."""
    output = []
    for level in ("category", "subcategory", "feature"):
        names = sorted(set().union(*(observation["items"][level] for observation in observations)))
        for name in names:
            subcategory, category = parents[(level, name)]
            with_item = [o for o in observations if name in o["items"][level]]
            pair_ids = set().union(*(o["pair_ids"] for o in with_item))
            row = {
                "level": level, "name": name,
                "label": SUBCATEGORIES[name][0] if level == "subcategory" else name,
                "subcategory": subcategory, "category": category,
                "pair_count": len(pair_ids), "independent_count": len(with_item),
                "independent_nameplates": len({o["car_model"] for o in with_item}),
                "models": json.dumps(sorted({o["car_model"] for o in with_item}), ensure_ascii=False),
            }
            results = []
            for year in YEARS:
                result = isolated_effect(observations, level, name, names, year)
                results.append(result)
                for key in (
                    "impact_pct", "lower_pct", "upper_pct", "incremental_units", "lower_units", "upper_units",
                    "sample_incremental_units", "sample_lower_units", "sample_upper_units", "n_with", "n_without",
                    "nameplates_with", "nameplates_without", "cluster_count", "residual_dof",
                    "residual_information", "max_leverage", "standard_error_log",
                ):
                    row[f"{key}_year_{year}"] = result.get(key)
            row["identification_status"] = "identified" if all(r["status"] == "identified" for r in results) \
                else "not_identified"
            row["identification_reason"] = "; ".join(dict.fromkeys(
                reason for result in results for reason in result["reason"].split("; ") if reason
            ))
            output.append(row)
    return output


def plot(impact_rows: list[dict], path: Path) -> None:
    rows = [r for r in impact_rows if r["level"] == "subcategory" and r["impact_pct_year_1"] is not None]
    rows.sort(key=lambda r: r["impact_pct_year_1"])
    fig, ax = plt.subplots(figsize=(8, 0.35 * len(rows) + 1.6))
    if not rows:
        ax.text(0.5, 0.5, "No subcategory estimate passed the identification and uncertainty gates",
                ha="center", va="center", transform=ax.transAxes)
        ax.set_axis_off()
    for i, r in enumerate(rows):
        ax.plot([r["lower_pct_year_1"], r["upper_pct_year_1"]], [i, i], color="#7b8794", lw=1.5)
        ax.plot(r["impact_pct_year_1"], i, "o", color="#2f78a7")
    ax.axvline(0, color="#333", lw=0.8)
    ax.set_yticks(range(len(rows)), [f"{r['label']} ({r['nameplates_with_year_1']} nameplates)" for r in rows],
                  fontsize=8)
    ax.set_xlabel("Year-1 conditional market-adjusted sales effect (%), clustered 95% interval")
    ax.set_title("Independent Chinese sales trajectories: conditional subcategory effect", fontsize=10)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
    plt.close(fig)


def run(input_dir: Path = INPUT_DIR, output_dir: Path = OUTPUT_DIR) -> dict:
    pairs, features, sales, market = load(input_dir)
    pair_rows = pair_sales(pairs, sales, market)
    observations, parents = independent_observations(pair_rows, features)
    observation_rows = serializable_observations(observations)
    impact_rows = impact(observations, parents)
    write_csv(pair_rows, output_dir / "pair_sales.csv")
    write_csv(observation_rows, output_dir / "independent_observations.csv")
    write_csv(features, output_dir / "feature_log.csv")
    write_csv(impact_rows, output_dir / "impact.csv")
    from app.analysis.bundle_exploratory import bundle_rows  # imports this module's constants
    bundle = bundle_rows(observations, parents)
    if bundle:
        write_csv(bundle, output_dir / "bundle_exploratory.csv")
    else:
        (output_dir / "bundle_exploratory.csv").unlink(missing_ok=True)
    plot(impact_rows, output_dir / "plots" / "impact_by_subcategory.pdf")
    summary = {
        "pairs": len(pairs),
        "brands": len({p["brand"] for p in pairs}),
        "launch_range": [min(p["current_launch"] for p in pairs), max(p["current_launch"] for p in pairs)],
        "features": len(features),
        "observed_pairs_by_year": {k: sum(r[f"status_year_{k}"] == "observed" for r in pair_rows) for k in YEARS},
        "valid_four_year_pairs": sum(r["valid_four_year_pair"] for r in pair_rows),
        "collection_target": 200,
        "independent_observations": len(observations),
        "independent_nameplates": len({o["car_model"] for o in observations}),
        "complete_four_year_observations": sum(all(o[f"status_year_{k}"] == "observed" for k in YEARS)
                                               for o in observations),
        "complete_four_year_nameplates": len({o["car_model"] for o in observations
                                               if all(o[f"status_year_{k}"] == "observed" for k in YEARS)}),
        "publication_eligible_observations": sum(bool(o["publication_eligible"]) for o in observations),
        "publication_eligible_nameplates": len({o["car_model"] for o in observations
                                                if o["publication_eligible"]}),
        "estimated_items": {level: sum(r["level"] == level and r["identification_status"] == "identified"
                                               for r in impact_rows)
                            for level in ("feature", "subcategory", "category")},
        "last_full_sales_year": max(market),
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
