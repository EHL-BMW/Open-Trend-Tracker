"""Exploratory, NOT publication-gated: sales association of launch bundles that contain an item.

Same independent trajectories and market adjustment as ``chinese_pairs``, but the item is not separated
from the rest of its launch bundle: no peer-item or bundle-size controls and no interval-width gate.
Controls kept: intercept, NEV, standardized log baseline, calendar-year dummies and data-quality flags.
Uncertainty is CR1 clustered by nameplate. Kept gates: 5 treated and 5 control nameplates, 8 residual dof.

Two panels of complete four-year trajectories:
  strict  publication-eligible only (single source series, full baseline, no successor overlap)
  broad   every complete trajectory; quality flags enter as controls

Read the result as "launches that included X sold this much better or worse", not as the effect of X.
"""
from __future__ import annotations

import math

import numpy as np

from app.analysis.chinese_pairs import (
    MIN_NAMEPLATES, MIN_RESIDUAL_DOF, SUBCATEGORIES, YEARS, _column_basis, _pct,
)

PANELS = ("strict", "broad")
LEVELS = ("category", "subcategory", "feature")


def association(panel: list[dict], level: str, target: str, year: int) -> dict | None:
    """Clustered OLS coefficient of 'bundle contains target' on market-adjusted log sales change."""
    x = np.array([target in o["items"][level] for o in panel], dtype=float)
    with_models = {o["car_model"] for o, v in zip(panel, x, strict=True) if v}
    without_models = {o["car_model"] for o, v in zip(panel, x, strict=True) if not v}
    if len(with_models) < MIN_NAMEPLATES or len(without_models) < MIN_NAMEPLATES:
        return None
    baseline = np.log([float(o["baseline_sales"]) for o in panel])
    controls = [np.ones(len(panel)), np.array([o["powertrain"] == "NEV" for o in panel], dtype=float),
                (baseline - baseline.mean()) / (baseline.std() or 1.0)]
    calendar = sorted({int(o[f"year_{year}"]) for o in panel})
    controls += [np.array([int(o[f"year_{year}"]) == c for o in panel], dtype=float) for c in calendar[1:]]
    flags = sorted(set().union(*(o["quality"][year] for o in panel)))
    controls += [np.array([f in o["quality"][year] for o in panel], dtype=float) for f in flags]
    basis, rank = _column_basis(np.column_stack(controls))
    x_resid = x - basis @ (basis.T @ x)
    information = float(x_resid @ x_resid)
    dof = len(panel) - rank - 1
    if information < 1e-8 or dof < MIN_RESIDUAL_DOF:
        return None
    y = np.array([float(o[f"excess_log_year_{year}"]) for o in panel])
    y_resid = y - basis @ (basis.T @ y)
    beta = float(x_resid @ y_resid / information)
    resid = y_resid - beta * x_resid
    clusters = sorted({o["car_model"] for o in panel})
    scores = [float(np.sum((x_resid * resid)[[o["car_model"] == c for o in panel]])) for c in clusters]
    correction = len(clusters) / (len(clusters) - 1) * (len(panel) - 1) / dof
    se = math.sqrt(correction * sum(s * s for s in scores)) / information
    return {"impact_pct": _pct(beta), "lower_pct": _pct(beta - 1.96 * se), "upper_pct": _pct(beta + 1.96 * se),
            "se_log": round(se, 4), "excludes_zero": abs(beta) > 1.96 * se,
            "nameplates_with": len(with_models), "nameplates_without": len(without_models)}


def bundle_rows(observations: list[dict], parents: dict) -> list[dict]:
    complete = [o for o in observations if all(o[f"status_year_{k}"] == "observed" for k in YEARS)]
    panels = {"strict": [o for o in complete if o["publication_eligible"]], "broad": complete}
    rows = []
    for panel_id, panel in panels.items():
        panel_nameplates = len({o["car_model"] for o in panel})
        for level in LEVELS:
            for name in sorted(set().union(set(), *(o["items"][level] for o in panel))):
                for year in YEARS:
                    result = association(panel, level, name, year)
                    if result:
                        rows.append({"panel": panel_id, "panel_nameplates": panel_nameplates, "level": level,
                                     "name": name,
                                     "label": SUBCATEGORIES[name][0] if level == "subcategory" else name,
                                     "subcategory": parents[(level, name)][0],
                                     "category": parents[(level, name)][1], "year": year, **result})
    return rows
