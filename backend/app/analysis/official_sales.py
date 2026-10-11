"""Compare version sales and associate newly added features with sales changes.

This module reports observational associations, not causal effects. Input is the
flat CSV written by an official-site grabber. For reliable ordering, an
optional integer ``version_order`` column can be supplied; otherwise release
date and input-row order are used.

Run from ``backend/``::

    uv run python -m app.analysis.official_sales \
      ../data/external/chinese_official_20_pairs.csv \
      --output-dir ../data/analysis/chinese
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
import statistics
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from app.paths import DATA_DIR, EXTERNAL_DIR


DEFAULT_INPUT = EXTERNAL_DIR / "chinese_official_20_pairs.csv"
DEFAULT_OUTPUT_DIR = DATA_DIR / "analysis"
YEARS = range(1, 5)
# Planning priors for a relative cumulative-sales uplift versus an otherwise
# identical version without the feature. These are deliberately conservative,
# editable assumptions - not coefficients learned from the current dataset.
CATEGORY_IMPACT_PRIORS = {
    "Energy & Charging": 4.0,
    "Driving Assistance": 3.6,
    "Digital Cockpit & AI": 3.0,
    "Vehicle Dynamics": 2.7,
    "Smart Cabin": 2.3,
    "Connected Ecosystem": 1.8,
    "Smart Exterior": 1.2,
    "General & Services": 0.8,
    "Unclassified": 1.0,
}
FORECAST_SATURATION = {1: 0.50, 2: 0.72, 3: 0.88, 4: 1.00}
FEATURE_COLUMNS = ["feature", "transition_count"] + [
    column
    for year in YEARS
    for column in (
        f"comparable_year_{year}", f"mean_sales_diff_year_{year}",
        f"median_sales_diff_year_{year}", f"mean_sales_diff_pct_year_{year}",
        f"positive_share_year_{year}",
    )
] + [
    "comparable_transition_count", "mean_sales_diff_pct_all_horizons", "association", "interpretation",
]


def _number(value: str | int | float | None) -> float | None:
    if value is None or value == "":
        return None
    number = float(value)
    return number if math.isfinite(number) else None


def _features(value: str) -> set[str]:
    if not value:
        return set()
    parsed = json.loads(value)
    if not isinstance(parsed, list) or not all(isinstance(item, str) for item in parsed):
        raise ValueError("newly_released_features must be a JSON array of strings")
    return {item.strip() for item in parsed if item.strip()}


def _release_sort(value: str) -> tuple[int, int, int]:
    """Sort YYYY-MM, YYYY-Qn and YYYY-MM-DD without pretending equal precision."""
    try:
        if "-Q" in value:
            year, quarter = value.split("-Q", 1)
            return int(year), (int(quarter) - 1) * 3 + 1, 0
        parts = [int(part) for part in value.split("-")]
        return parts[0], parts[1] if len(parts) > 1 else 1, parts[2] if len(parts) > 2 else 0
    except (ValueError, IndexError) as exc:
        raise ValueError(f"invalid release_date {value!r}") from exc


@dataclass
class VersionRecord:
    pair_id: str | None
    car_model: str
    version: str
    release_date: str
    input_order: int
    version_order: int | None
    features: set[str]
    feature_categories: dict[str, str]
    cumulative_sales: dict[int, float | None]


def _feature_category_map(row: dict[str, str]) -> dict[str, str]:
    raw = row.get("feature_evidence", "")
    if not raw:
        return {}
    parsed = json.loads(raw)
    if not isinstance(parsed, list):
        raise ValueError("feature_evidence must be a JSON array")
    output = {}
    for item in parsed:
        if isinstance(item, dict) and isinstance(item.get("name"), str) and isinstance(item.get("category"), str):
            output[item["name"].strip()] = item["category"].strip()
    return output


def read_versions(path: Path) -> list[VersionRecord]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        required = {"car_model", "version", "release_date", "newly_released_features"} | {
            f"cumulative_sales_year_{year}" for year in YEARS
        }
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            missing = sorted(required - set(reader.fieldnames or []))
            raise ValueError(f"input CSV is missing columns: {missing}")
        records = []
        for index, row in enumerate(reader):
            order = int(row["version_order"]) if row.get("version_order") else None
            records.append(VersionRecord(
                pair_id=row.get("pair_id") or None,
                car_model=row["car_model"].strip(),
                version=row["version"].strip(),
                release_date=row["release_date"].strip(),
                input_order=index,
                version_order=order,
                features=_features(row["newly_released_features"]),
                feature_categories=_feature_category_map(row),
                cumulative_sales={year: _number(row[f"cumulative_sales_year_{year}"]) for year in YEARS},
            ))
    return records


def _ordered(records: Iterable[VersionRecord]) -> list[VersionRecord]:
    return sorted(records, key=lambda row: (
        row.version_order is None,
        row.version_order if row.version_order is not None else 0,
        _release_sort(row.release_date),
        row.input_order,
    ))


def version_sales_differences(records: Iterable[VersionRecord]) -> list[dict]:
    """Compare every version with the previous version of the same car model."""
    grouped: dict[str, list[VersionRecord]] = defaultdict(list)
    for record in records:
        grouped[record.pair_id or record.car_model].append(record)

    output = []
    for group in sorted(grouped):
        ordered = _ordered(grouped[group])
        for sequence, (previous, current) in enumerate(zip(ordered, ordered[1:]), start=2):
            # Rows from one launch page are often simultaneous trims rather than
            # generations. Only compare equal-date rows when the input explicitly
            # supplies their intended version sequence.
            if (previous.version_order is None or current.version_order is None) and \
                    _release_sort(previous.release_date) == _release_sort(current.release_date):
                continue
            row: dict[str, object] = {
                "pair_id": current.pair_id or "",
                "car_model": current.car_model,
                "version_sequence": sequence,
                "version": current.version,
                "previous_version": previous.version,
                "release_date": current.release_date,
                "previous_release_date": previous.release_date,
                "added_features": json.dumps(sorted(current.features - previous.features), ensure_ascii=False),
                "removed_features": json.dumps(sorted(previous.features - current.features), ensure_ascii=False),
                "added_feature_categories": json.dumps({
                    feature: current.feature_categories.get(feature, "Unclassified")
                    for feature in sorted(current.features - previous.features)
                }, ensure_ascii=False),
            }
            comparable = 0
            for year in YEARS:
                current_sales = current.cumulative_sales[year]
                previous_sales = previous.cumulative_sales[year]
                difference = current_sales - previous_sales if current_sales is not None and previous_sales is not None else None
                pct = difference / previous_sales * 100 if difference is not None and previous_sales else None
                row[f"current_sales_year_{year}"] = current_sales
                row[f"previous_sales_year_{year}"] = previous_sales
                row[f"sales_diff_year_{year}"] = difference
                row[f"sales_diff_pct_year_{year}"] = pct
                comparable += difference is not None
            row["comparison_status"] = "complete" if comparable == len(YEARS) else (
                "partial" if comparable else "missing_sales"
            )
            output.append(row)
    return output


def feature_sales_associations(comparisons: Iterable[dict], min_transitions: int = 2) -> list[dict]:
    """Aggregate sales changes for transitions where each feature was newly added.

    A feature is labelled positive/negative only when it appears in at least
    ``min_transitions`` comparable version changes. This avoids presenting a
    one-off launch as general evidence.
    """
    feature_rows: dict[str, list[dict]] = defaultdict(list)
    for comparison in comparisons:
        for feature in json.loads(str(comparison["added_features"])):
            feature_rows[feature].append(comparison)

    output = []
    for feature, rows in feature_rows.items():
        result: dict[str, object] = {"feature": feature, "transition_count": len(rows)}
        all_pct: list[float] = []
        comparable_transitions: set[tuple[str, str]] = set()
        for year in YEARS:
            diffs = [float(row[f"sales_diff_year_{year}"]) for row in rows if row[f"sales_diff_year_{year}"] is not None]
            pcts = [float(row[f"sales_diff_pct_year_{year}"]) for row in rows if row[f"sales_diff_pct_year_{year}"] is not None]
            all_pct.extend(pcts)
            comparable_transitions.update(
                (str(row["car_model"]), str(row["version"]))
                for row in rows if row[f"sales_diff_year_{year}"] is not None
            )
            result[f"comparable_year_{year}"] = len(diffs)
            result[f"mean_sales_diff_year_{year}"] = statistics.fmean(diffs) if diffs else None
            result[f"median_sales_diff_year_{year}"] = statistics.median(diffs) if diffs else None
            result[f"mean_sales_diff_pct_year_{year}"] = statistics.fmean(pcts) if pcts else None
            result[f"positive_share_year_{year}"] = sum(value > 0 for value in diffs) / len(diffs) if diffs else None

        n_comparable = len(comparable_transitions)
        mean_pct = statistics.fmean(all_pct) if all_pct else None
        result["comparable_transition_count"] = n_comparable
        result["mean_sales_diff_pct_all_horizons"] = mean_pct
        if n_comparable < min_transitions or mean_pct is None:
            result["association"] = "insufficient_evidence"
        elif mean_pct > 0:
            result["association"] = "positive_association"
        elif mean_pct < 0:
            result["association"] = "negative_association"
        else:
            result["association"] = "neutral_association"
        result["interpretation"] = "observational association; does not establish that the feature caused the sales change"
        output.append(result)
    return sorted(output, key=lambda row: (
        row["association"] == "insufficient_evidence",
        -(row["mean_sales_diff_pct_all_horizons"] or 0),
        row["feature"],
    ))


def _feature_multiplier(feature: str) -> float:
    text = feature.casefold()
    high_value = (
        "lidar", "autonomous", "driver assistance", "automated", "parking", "aeb", "aes",
        "charging", "battery", "electric range", "range of", "artificial intelligence", "voice assistant",
    )
    presentation_only = ("paint", "colour", "color", "wheel design", "trim", "appearance")
    if any(keyword in text for keyword in high_value):
        return 1.15
    if any(keyword in text for keyword in presentation_only):
        return 0.80
    return 1.00


def _feature_display_name(feature: str) -> str:
    text = feature.casefold()
    labels = (
        (("900v", "high-voltage"), "900V system + 102 kWh battery"),
        (("5c", "battery"), "5C fast-charging battery"),
        (("100kwh", "battery"), "100 kWh liquid-cooled battery"),
        (("worldmodel",), "World-model ADAS + point-to-point navigation"),
        (("dual orin",), "Dual Orin-X assisted-driving stack"),
        (("voice assistant",), "AI voice assistant"),
        (("digital architecture",), "5 nm automotive SoC + full-domain E/E architecture"),
        (("steering wheel", "column shifter"), "Redesigned steering controls"),
        (("steering wheel",), "Redesigned steering controls"),
        (("tailor-made", "acoustic fabric"), "Premium acoustic speaker fabric"),
        (("roof-mounted center speaker",), "Roof center speaker + Dirac RRM audio"),
        (("second living room",), "Second Living Room cabin"),
        (("six- and seven-seater",), "Six-/seven-seat cabin configuration"),
        (("zero-gravity", "rotat"), "Rotating zero-gravity seats"),
        (("zero-gravity seat",), "Second-row zero-gravity seats + leg support"),
        (("premium seat platform",), "Premium seat platform"),
        (("11-layer comfort structure",), "11-layer comfort seats"),
        (("reclining safety seat",), "Reclining safety seats"),
        (("reclining safety system",), "Dual cushion airbags + seat-integrated belts"),
        (("four executive seats",), "Executive-seat layout"),
        (("seat comfort",), "Comfort seats"),
        (("smart restraint system",), "Smart restraint system"),
        (("lounge seat",), "Lounge Seat"),
        (("dual motor four-wheel drive",), "Dual-motor all-wheel drive"),
        (("matrix headlights", "adaptive driving beam"), "ADB matrix headlights + Double-Dash DRL"),
        (("adb headlight",), "ADB matrix headlights + Double-Dash DRL"),
        (("lidar", "headlight"), "LiDAR-adaptive headlights"),
        (("lidar", "lighting system"), "LiDAR-adaptive headlights"),
        (("double-dash drl",), "3D daytime-running lights"),
        (("new moon silver",), "New Moon Silver paint + 21-inch wheels"),
        (("panocinema",), "PanoCinema digital cockpit"),
        (("heads-up display",), "Head-up display"),
        (("head-up display",), "Head-up display"),
        (("upgraded chassis",), "Upgraded chassis"),
        (("intelligent chassis",), "Software-controlled active chassis system"),
        (("suspension components", "upgraded"), "CDC dampers + hydraulic rear-subframe bushings"),
        (("suspension mount",), "CDC dampers + hydraulic rear-subframe bushings"),
        (("dual-chamber air suspension",), "Dual-chamber air suspension"),
        (("find my car",), "Find My Car"),
        (("range-extension",), "Upgraded range-extension system"),
        (("magic carpet", "suspension"), "Magic Carpet air suspension"),
        (("automated parking",), "Automated parking"),
        (("lidar", "aeb"), "LiDAR-assisted active safety"),
        (("electric drive",), "High-efficiency electric drive"),
        (("recharging",), "Charging + battery-swap station network"),
        (("surround sound",), "Surround-sound cabin audio"),
        (("cabin entertainment",), "Integrated cabin display + audio entertainment"),
        (("screen", "display"), "Multi-screen digital cockpit"),
        (("seat", "massage"), "Massage seats"),
    )
    for keywords, label in labels:
        if all(keyword in text for keyword in keywords):
            return label
    compact = re.sub(r"^(?:the|a|an)\s+", "", feature, flags=re.I).strip()
    return compact if len(compact) <= 58 else compact[:55].rstrip() + "..."


def _is_forecastable_feature(feature: str, category: str) -> bool:
    text = feature.casefold()
    noise = ("price", "rmb", "press release", "media contact", "started a new chapter",
             "in addition to the state-of-the-art", "delivery will", "pre-order", "over 180 improvements",
             "measuring 5,280", "6-seater all-around smart electric flagship",
             "powered by industry-leading ev technologies")
    if any(term in text for term in noise):
        return False
    if category == "Unclassified":
        return True
    concrete = (
        "battery", "charging", "range", "lidar", "autonomous", "assistance", "parking", "aeb", "aes",
        "suspension", "chassis", "steering", "cockpit", "display", "screen", "voice", "assistant", "seat",
        "cabin", "audio", "climate", "radar", "camera", "processor", "chip", "architecture", "platform",
        "drive", "motor", "lighting", "headlight", "door", "connected", "software", "app", "5g",
    )
    return any(term in text for term in concrete)


def _looks_like_feature_label(source: str, display_name: str) -> bool:
    """Reject article prose that keyword extraction mistook for a feature."""
    text = re.sub(r"\s+", " ", source).strip()
    words = text.split()
    sentence_starts = {
        "a", "as", "at", "backed", "built", "by", "during", "first", "in", "inside",
        "it", "launched", "meanwhile", "offering", "on", "respective", "setting", "the",
        "this", "through", "together", "with",
    }
    if words and words[0].casefold().strip("•\"'") in sentence_starts and len(words) > 5:
        return False
    if re.search(r"\b(?:is|are|was|were)\s+(?:powered|equipped|designed|built)\s+by\b", text, re.I):
        return False
    # Canonicalization converts long evidence sentences into a stable feature
    # label. Unmapped long prose is not suitable for a ranked feature chart.
    compact = re.sub(r"^(?:the|a|an)\s+", "", text, flags=re.I).strip()
    was_canonicalized = display_name != compact and not display_name.endswith("...")
    return was_canonicalized or (len(words) <= 7 and not re.search(r"[.;:]", text))


def _canonical_category(feature: str, display_name: str, detected: str) -> str:
    text = display_name.casefold()
    rules = (
        ("Energy & Charging", ("5c", "900v", "battery", "charging", "electric drive", "range-extension")),
        ("Driving Assistance", ("worldmodel", "world-model", "orin-x", "autonomous", "automated parking", "aeb", "aes")),
        ("Connected Ecosystem", ("find my car", "connected", "software upgrade")),
        ("Digital Cockpit & AI", ("voice assistant", "digital architecture", "e/e architecture", "automotive soc", "digital cockpit", "head-up display")),
        ("Smart Cabin", ("seat", "cabin entertainment", "audio entertainment", "speaker", "surround sound", "second living room", "massage", "restraint")),
        ("Vehicle Dynamics", ("chassis", "suspension", "steering", "all-wheel drive", "four-wheel drive")),
        ("Smart Exterior", ("headlight", "daytime-running", "drl", "exterior color")),
    )
    for category, keywords in rules:
        if any(keyword in text for keyword in keywords):
            return category
    return detected


def feature_impact_forecast(comparisons: Iterable[dict]) -> list[dict]:
    """Create a transparent four-year planning scenario when observed sales are absent.

    The estimate combines an editable category prior, a small keyword multiplier,
    and a four-year saturation curve. A +/-50% interval communicates model risk.
    It must not be interpreted as a fitted causal effect.
    """
    groups: dict[tuple[str, str], dict[str, object]] = {}
    all_pairs = {
        str(comparison.get("pair_id") or f"{comparison['car_model']}:{comparison['version']}")
        for comparison in comparisons
    }
    for comparison in comparisons:
        categories = json.loads(str(comparison.get("added_feature_categories", "{}")))
        for feature in json.loads(str(comparison["added_features"])):
            category = categories.get(feature, "Unclassified")
            if _is_forecastable_feature(feature, category):
                display_name = _feature_display_name(feature)
                if not _looks_like_feature_label(feature, display_name):
                    continue
                category = _canonical_category(feature, display_name, category)
                group = groups.setdefault((display_name, category), {"count": 0, "features": set()})
                group["count"] = int(group["count"]) + 1
                group["features"].add(feature)
                group.setdefault("pairs", set()).add(str(
                    comparison.get("pair_id") or f"{comparison['car_model']}:{comparison['version']}"
                ))
                group.setdefault("models", set()).add(str(comparison["car_model"]))

    output = []
    for (display_name, category), group in groups.items():
        source_features = sorted(group["features"])
        count = int(group["count"])
        pair_count = len(group["pairs"])
        models = sorted(group["models"])
        prior = CATEGORY_IMPACT_PRIORS.get(category, CATEGORY_IMPACT_PRIORS["Unclassified"])
        multiplier = max(_feature_multiplier(feature) for feature in source_features)
        year4 = prior * multiplier
        uncertainty = max(0.35, 0.60 / math.sqrt(max(pair_count, 1)))
        row: dict[str, object] = {
            "feature": display_name,
            "display_name": display_name,
            "category": category,
            "transition_count": count,
            "pair_count": pair_count,
            "pair_coverage_pct": pair_count / len(all_pairs) * 100 if all_pairs else 0,
            "model_count": len(models),
            "models": json.dumps(models, ensure_ascii=False),
            "source_feature_examples": json.dumps(source_features[:5], ensure_ascii=False),
            "category_prior_year_4_pct": prior,
            "feature_multiplier": multiplier,
            "uncertainty_pct": uncertainty * 100,
        }
        for year in YEARS:
            estimate = year4 * FORECAST_SATURATION[year]
            row[f"estimated_sales_impact_year_{year}_pct"] = estimate
            row[f"lower_year_{year}_pct"] = estimate * (1 - uncertainty)
            row[f"upper_year_{year}_pct"] = estimate * (1 + uncertainty)
        row["analysis_scope"] = "general_across_all_models"
        row["forecast_status"] = "scenario_estimate_not_sales_fitted"
        row["method"] = "canonical category prior x feature multiplier x adoption saturation; uncertainty narrows with independent pair coverage"
        output.append(row)
    return sorted(output, key=lambda row: (-float(row["estimated_sales_impact_year_4_pct"]), str(row["feature"])))


def feature_catalog(forecast: Iterable[dict]) -> list[dict]:
    return sorted(({
        "category": row["category"],
        "feature": row["feature"],
        "pair_count": row["pair_count"],
        "pair_coverage_pct": row["pair_coverage_pct"],
        "model_count": row["model_count"],
        "models": row["models"],
        "source_feature_examples": row["source_feature_examples"],
    } for row in forecast), key=lambda row: (str(row["category"]), str(row["feature"])))


def _write_csv(rows: list[dict], path: Path, fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    columns = fieldnames or (list(rows[0]) if rows else [])
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        if not columns:
            return
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def _empty_plot(ax, title: str, message: str) -> None:
    ax.set_title(title, loc="left", fontsize=15, fontweight="bold")
    ax.text(0.5, 0.52, message, ha="center", va="center", transform=ax.transAxes,
            fontsize=12, color="#53657a", linespacing=1.5)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)


def plot_analysis(comparisons: list[dict], associations: list[dict], output_dir: Path) -> dict[str, str]:
    """Create presentation-ready PNG and PDF plots for both analyses."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    output_dir.mkdir(parents=True, exist_ok=True)
    version_base = output_dir / "version_sales_differences"
    feature_base = output_dir / "feature_sales_associations"

    fig, ax = plt.subplots(figsize=(11, 6.5), constrained_layout=True)
    plotted = 0
    for row in comparisons:
        values = [row[f"sales_diff_pct_year_{year}"] for year in YEARS]
        points = [(year, value) for year, value in zip(YEARS, values) if value is not None]
        if not points:
            continue
        x, y = zip(*points)
        label = f"{row['car_model']}: {row['version']} vs {row['previous_version']}"
        ax.plot(x, y, marker="o", linewidth=2, label=label)
        plotted += 1
    if plotted:
        ax.axhline(0, color="#56616f", linewidth=1)
        ax.set_title("Sales change versus previous model version", loc="left", fontsize=15, fontweight="bold")
        ax.set_xlabel("Years after release")
        ax.set_ylabel("Cumulative sales difference (%)")
        ax.set_xticks(list(YEARS))
        ax.grid(axis="y", alpha=0.25)
        ax.legend(loc="best", fontsize=8)
    else:
        _empty_plot(ax, "Sales change versus previous model version",
                    "No comparable year 1-4 sales data.\nAdd chronological versions and official cumulative sales.")
    fig.savefig(version_base.with_suffix(".png"), dpi=180)
    fig.savefig(version_base.with_suffix(".pdf"))
    plt.close(fig)

    comparable_features = [row for row in associations if row["mean_sales_diff_pct_all_horizons"] is not None]
    comparable_features = sorted(
        comparable_features,
        key=lambda row: float(row["mean_sales_diff_pct_all_horizons"]),
    )[-20:]
    height = max(5.5, 0.38 * len(comparable_features) + 2.2)
    fig, ax = plt.subplots(figsize=(11, height), constrained_layout=True)
    if comparable_features:
        names = [str(row["feature"])[:70] for row in comparable_features]
        values = [float(row["mean_sales_diff_pct_all_horizons"]) for row in comparable_features]
        colors = ["#16856b" if value > 0 else "#d14b4b" if value < 0 else "#8492a6" for value in values]
        ax.barh(names, values, color=colors)
        ax.axvline(0, color="#56616f", linewidth=1)
        ax.set_title("New feature association with cumulative sales change", loc="left",
                     fontsize=15, fontweight="bold")
        ax.set_xlabel("Mean sales difference across available year 1-4 horizons (%)")
        ax.grid(axis="x", alpha=0.25)
        ax.text(0, -0.13, "Association only; this analysis does not establish causation.",
                transform=ax.transAxes, fontsize=9, color="#53657a")
    else:
        _empty_plot(ax, "New feature association with cumulative sales change",
                    "No feature transitions with comparable sales data.\nResults will appear after official sales are supplied.")
    fig.savefig(feature_base.with_suffix(".png"), dpi=180)
    fig.savefig(feature_base.with_suffix(".pdf"))
    plt.close(fig)

    return {
        "version_sales_png": str(version_base.with_suffix(".png")),
        "version_sales_pdf": str(version_base.with_suffix(".pdf")),
        "feature_sales_png": str(feature_base.with_suffix(".png")),
        "feature_sales_pdf": str(feature_base.with_suffix(".pdf")),
    }


def plot_feature_forecast(forecast: list[dict], output_dir: Path) -> dict[str, str]:
    """Plot category trajectories and the top feature-level year-four scenarios."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    output_dir.mkdir(parents=True, exist_ok=True)
    base = output_dir / "feature_sales_impact_4_year_forecast"
    fig, (ax_lines, ax_rank) = plt.subplots(
        1, 2, figsize=(15, 8.5), gridspec_kw={"width_ratios": [1.0, 1.35]},
    )

    categories = [category for category in CATEGORY_IMPACT_PRIORS if category != "Unclassified"]
    for category in categories:
        prior = CATEGORY_IMPACT_PRIORS[category]
        values = [prior * FORECAST_SATURATION[year] for year in YEARS]
        ax_lines.plot(list(YEARS), values, marker="o", linewidth=2, label=category)
    ax_lines.set_title("Category planning priors", loc="left", fontsize=14, fontweight="bold")
    ax_lines.set_xlabel("Years after release")
    ax_lines.set_ylabel("Estimated cumulative-sales uplift (%)")
    ax_lines.set_xticks(list(YEARS))
    ax_lines.grid(axis="y", alpha=0.25)
    ax_lines.legend(fontsize=8, loc="upper left")

    top = forecast[:15][::-1]
    if top:
        labels = [f"{row['display_name']}\n[{row['category']}]" for row in top]
        values = [float(row["estimated_sales_impact_year_4_pct"]) for row in top]
        lower = [float(row["lower_year_4_pct"]) for row in top]
        upper = [float(row["upper_year_4_pct"]) for row in top]
        errors = [[value - low for value, low in zip(values, lower)],
                  [high - value for value, high in zip(values, upper)]]
        positions = list(range(len(top)))
        ax_rank.errorbar(values, positions, xerr=errors, fmt="o", color="#176b87",
                         ecolor="#8aa8b5", capsize=3, markersize=6)
        ax_rank.set_yticks(positions, labels)
        ax_rank.set_xlabel("Estimated general year-4 cumulative-sales uplift (%)")
        ax_rank.grid(axis="x", alpha=0.25)
    else:
        _empty_plot(ax_rank, "Top feature scenarios", "No newly added features were detected.")
    ax_rank.set_title("Top feature scenarios at year 4", loc="left", fontsize=14, fontweight="bold")
    fig.suptitle("General four-year feature sales-impact scenario", x=0.01, ha="left", fontsize=17, fontweight="bold")
    fig.subplots_adjust(left=0.06, right=0.98, bottom=0.14, top=0.86, wspace=0.95)
    fig.text(
        0.01, 0.025,
        "Market-wide planning estimate, not a fitted causal forecast. Whiskers show 35%-60% ranges based on pair coverage.",
        fontsize=9, color="#53657a",
    )
    fig.savefig(base.with_suffix(".png"), dpi=180)
    fig.savefig(base.with_suffix(".pdf"))
    plt.close(fig)
    return {"feature_forecast_png": str(base.with_suffix(".png")),
            "feature_forecast_pdf": str(base.with_suffix(".pdf"))}


def plot_full_ranked_feature_forecast(forecast: list[dict], output_dir: Path) -> str:
    """Plot every forecast feature, ranked, with category-colored row bands."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch

    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / "full_ranked_feature_impact_by_category.png"
    category_colors = {
        "Energy & Charging": "#2F78A7",
        "Driving Assistance": "#A353A3",
        "Digital Cockpit & AI": "#E08332",
        "Vehicle Dynamics": "#397C5A",
        "Smart Cabin": "#B85C68",
        "Connected Ecosystem": "#5E6FC2",
        "Smart Exterior": "#8A733E",
        "General & Services": "#66717D",
        "Unclassified": "#7B7B7B",
    }
    ranked = sorted(
        forecast,
        key=lambda row: (
            float(row["estimated_sales_impact_year_4_pct"]),
            int(row.get("pair_count", 0)),
            str(row["display_name"]),
        ),
    )
    height = max(8.0, 0.39 * len(ranked) + 2.8)
    fig, ax = plt.subplots(figsize=(14, height))
    if not ranked:
        _empty_plot(ax, "Full ranked feature impact", "No forecastable features were detected.")
    else:
        for position, row in enumerate(ranked):
            category = str(row["category"])
            color = category_colors.get(category, category_colors["Unclassified"])
            ax.axhspan(position - 0.48, position + 0.48, color=color, alpha=0.105, linewidth=0)
            value = float(row["estimated_sales_impact_year_4_pct"])
            low = float(row["lower_year_4_pct"])
            high = float(row["upper_year_4_pct"])
            ax.errorbar(
                value, position, xerr=[[value - low], [high - value]], fmt="o",
                color=color, ecolor=color, alpha=0.95, capsize=2.5, markersize=5,
            )
            ax.text(high + 0.08, position, f"{value:.1f}% · {int(row.get('pair_count', 0))} pairs",
                    va="center", fontsize=8.5, color="#354052")

        total = len(ranked)
        labels = [
            f"{total - index}. {row['display_name']}"
            for index, row in enumerate(ranked)
        ]
        ax.set_yticks(range(total), labels)
        max_upper = max(float(row["upper_year_4_pct"]) for row in ranked)
        ax.set_xlim(0, max_upper * 1.35)
        ax.set_xlabel("Estimated general cumulative-sales impact after 4 years (%)")
        ax.set_ylabel("Feature rank")
        ax.set_title("Full ranked feature-impact forecast", loc="left", fontsize=16, fontweight="bold")
        ax.grid(axis="x", alpha=0.22)
        ax.set_axisbelow(True)
        handles = [Patch(facecolor=color, alpha=0.28, label=category)
                   for category, color in category_colors.items()
                   if any(str(row["category"]) == category for row in ranked)]
        ax.legend(handles=handles, title="Technology category", loc="lower right", fontsize=8,
                  title_fontsize=9, frameon=True)
        fig.subplots_adjust(left=0.29, right=0.985, top=0.93, bottom=0.14)
        fig.text(
            0.29, 0.035,
            "Ranked planning scenario—not a sales-fitted causal estimate. Whiskers are the model uncertainty range; labels show estimate and source-pair count.",
            fontsize=9, color="#53657a", va="bottom",
        )
    fig.savefig(output, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return str(output)


def analyze(input_path: Path, output_dir: Path = DEFAULT_OUTPUT_DIR, min_transitions: int = 2) -> dict:
    records = read_versions(input_path)
    differences = version_sales_differences(records)
    associations = feature_sales_associations(differences, min_transitions=min_transitions)
    forecast = feature_impact_forecast(differences)
    differences_path = output_dir / "version_sales_differences.csv"
    features_path = output_dir / "feature_sales_associations.csv"
    summary_path = output_dir / "official_sales_analysis_summary.json"
    forecast_path = output_dir / "feature_sales_impact_4_year_forecast.csv"
    catalog_path = output_dir / "feature_catalog_by_category.csv"

    difference_columns = [
        "pair_id", "car_model", "version_sequence", "version", "previous_version", "release_date",
        "previous_release_date", "added_features", "removed_features", "added_feature_categories",
    ]
    for year in YEARS:
        difference_columns += [f"current_sales_year_{year}", f"previous_sales_year_{year}",
                               f"sales_diff_year_{year}", f"sales_diff_pct_year_{year}"]
    difference_columns.append("comparison_status")
    _write_csv(differences, differences_path, difference_columns)
    _write_csv(associations, features_path, FEATURE_COLUMNS)
    _write_csv(forecast, forecast_path)
    _write_csv(feature_catalog(forecast), catalog_path)
    plots = plot_analysis(differences, associations, output_dir / "plots")
    forecast_plots = plot_feature_forecast(forecast, output_dir / "plots")

    comparable = sum(row["comparison_status"] != "missing_sales" for row in differences)
    summary = {
        "input": str(input_path),
        "version_records": len(records),
        "version_comparisons": len(differences),
        "comparisons_with_sales": comparable,
        "features_analyzed": len(associations),
        "positive_associations": sum(row["association"] == "positive_association" for row in associations),
        "negative_associations": sum(row["association"] == "negative_association" for row in associations),
        "insufficient_evidence": sum(row["association"] == "insufficient_evidence" for row in associations),
        "scenario_features_forecast": len(forecast),
        "forecast_method": "general cross-model planning priors with four-year saturation and coverage-based uncertainty; not fitted to sales",
        "caveat": "Feature results are observational associations, not causal estimates.",
        "outputs": {
            "version_differences": str(differences_path),
            "feature_associations": str(features_path),
            "feature_impact_forecast": str(forecast_path),
            "feature_catalog": str(catalog_path),
            **plots,
            **forecast_plots,
        },
    }
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--min-transitions", type=int, default=2)
    args = parser.parse_args()
    if args.min_transitions < 1:
        parser.error("--min-transitions must be positive")
    summary = analyze(args.input, args.output_dir, args.min_transitions)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
