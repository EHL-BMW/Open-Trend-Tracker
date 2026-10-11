"""OpenTT planner API (docs/API.md) on real data instead of the frontend mocks.

Candidates are the selected Chinese-derived features. The four sources score or describe them:

  sales     BMW 2030 volume x conservative (lower-bound) year-4 uplift = extra units/year (scenario)
  customer  keyword-quantified BMW customer comments: pain = negative, praise = positive mentions
  trends    Chinese-derived sales-impact trend, year 1 -> year 4 after launch (assumption)
  features  BMW option-list availability of the matching taxonomy attributes (context, not weighted)

The scoring and texts follow frontend/src/mocks/engine.ts, the reference implementation of the contract.
No observed sales response exists for these features yet, so sales specs are marked as assumption
and every recommendation carries a flag saying so; assumptionShare stays the trends share as in the contract.
"""
from __future__ import annotations

import hashlib
import json
import re
import uuid
from datetime import datetime, timezone
from functools import cache

from app.paths import RUNTIME_DIR
from app.services.decision_dashboard import _internal_comments, quantify_comments
from app.services.forecast import engineering_comparison, forecast_catalog

RUNS_DIR = RUNTIME_DIR / "planner-runs"
FORECAST_YEAR = 2030
DEFAULT_WEIGHTS = {"sales": 30, "customer": 45, "trends": 25}
WEIGHTED = ["sales", "customer", "trends"]
NAMES = {"sales": "Sales", "customer": "Customer", "trends": "Trends / Competition", "features": "Product"}
CHIPS = {"sales": "Sales", "customer": "Customer", "trends": "Trends", "features": "Product"}
COMMENT_VEHICLES = ["F70", "G60", "G70"]
CATALOG_VEHICLES = ["G60", "G70"]
# Chinese-derived feature -> BMW taxonomy attributes that describe the same customer function
BMW_ATTRIBUTES = {
    "900V system + 102 kWh battery": ["hv_battery", "electric_range"],
    "Charging + battery-swap station network": ["charging"],
    "World-model ADAS + point-to-point navigation": ["driving_assistance", "navigation"],
    "5 nm automotive SoC + full-domain E/E architecture": ["operating_concept", "connected_services"],
    "CDC dampers + hydraulic rear-subframe bushings": ["handling_ride"],
    "Software-controlled active chassis system": ["handling_ride", "driving_modes"],
    "Dual cushion airbags + seat-integrated belts": ["safety_overall"],
    "Integrated cabin display + audio entertainment": ["rear_entertainment", "displays"],
    "Roof center speaker + Dirac RRM audio": ["audio"],
    "Second-row zero-gravity seats + leg support": ["seat_features", "rear_space"],
    "Six-/seven-seat cabin configuration": ["versatility", "interior_space"],
    "ADB matrix headlights + Double-Dash DRL": ["exterior_lighting"],
    "New Moon Silver paint + 21-inch wheels": ["exterior_styling", "wheels_tires"],
}
PREFIX = {"sales": "S", "customer": "C", "features": "F", "trends": "T"}


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.casefold()).strip("-")


def pc(value: float, digits: int = 0) -> str:
    return f"{value * 100:.{digits}f}%"


def uniq(values) -> list:
    return list(dict.fromkeys(values))


@cache
def tables() -> dict:
    """All source records, built once per process from the backend data."""
    catalog = forecast_catalog()
    features = catalog["features"]
    history = catalog["bmw_sales_history"]
    candidates = {slug(row["feature"]): row["feature"] for row in features}
    markets = {}
    sales, customer, product, trends = [], [], [], []
    for row in features:
        c = slug(row["feature"])
        trends.append({"c": c, "v": row["estimate"][3] / 100, "now": row["estimate"][0] / 100,
                       "low": row["lower"][3] / 100, "technology": c, "pairs": row["pairs"]})
        for line, by_market in history.items():
            for market, item in by_market.items():
                units = round(item[str(FORECAST_YEAR)] * row["lower"][3] / 100)
                if market == "Global" or units <= 0:
                    continue
                markets[market] = item["label"]
                sales.append({"c": c, "v": units, "line": line, "market": market, "market_label": item["label"]})
    for vehicle in COMMENT_VEHICLES:
        comments = _internal_comments(vehicle)
        for row in features:
            summary = quantify_comments(row["feature"], comments)
            for signal, key in (("pain", "negative"), ("praise", "positive")):
                if summary[key]:
                    customer.append({"c": slug(row["feature"]), "v": summary[key], "vehicle": vehicle,
                                     "signal": signal, "area": row["category"]})
    for vehicle in CATALOG_VEHICLES:
        items = {item["feature_id"]: item for item in engineering_comparison(vehicle)["items"]}
        for row in features:
            for attribute in BMW_ATTRIBUTES.get(row["feature"], []):
                item = items[attribute]
                product.append({"c": slug(row["feature"]), "v": 1, "vehicle": vehicle,
                                "attribute": item["feature"], "availability": item["availability"]})
    data = {"candidates": candidates, "markets": markets, "sales": sales, "customer": customer,
            "features": product, "trends": trends, "lines": list(history)}
    data["version"] = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()[:12]
    return data


def options(pairs) -> list[dict]:
    return [{"value": value, "label": label} for value, label in pairs]


def catalog() -> dict:
    t = tables()
    names = t["candidates"]
    return {
        "dataVersion": t["version"],
        "forecastYear": FORECAST_YEAR,
        "defaultWeights": DEFAULT_WEIGHTS,
        "categories": {
            "sales": {"recordCount": len(t["sales"]), "filters": [
                {"key": "line", "label": "Line", "options": options((x, x) for x in t["lines"])},
                {"key": "market", "label": "Market", "options": options(t["markets"].items())},
            ]},
            "customer": {"recordCount": len(t["customer"]), "filters": [
                {"key": "vehicle", "label": "Feedback from", "options": options((v, v) for v in COMMENT_VEHICLES)},
                {"key": "signal", "label": "Signal", "options": options([("pain", "Pain points"), ("praise", "Praise")])},
            ]},
            "features": {"recordCount": len(t["features"]), "filters": [
                {"key": "vehicle", "label": "Vehicle", "heading": "Existing BMW cars (option lists)",
                 "options": options((v, v) for v in CATALOG_VEHICLES)},
            ]},
            "trends": {"recordCount": len(t["trends"]), "filters": [
                {"key": "technology", "label": "Feature", "heading": "China EV market (official release pairs)",
                 "options": options(names.items())},
            ]},
        },
        "trendForecast": [{"technology": r["technology"], "label": names[r["c"]], "currentShare": r["now"],
                           "forecastShare": r["v"]} for r in t["trends"]],
        "trendForecastLabels": {
            "title": "Sales-impact trend",
            "description": "Estimated sales uplift of each Chinese-derived feature, year 1 and year 4 after launch.",
            "current": "Year 1",
            "forecast": "Year 4",
        },
    }


def fingerprint(req: dict) -> str:
    """Hash of the normalised request, mirroring requestKey() in frontend/src/domain/settings.ts."""
    filters = {k: {g: sorted(v) for g, v in sorted(req["filters"].get(k, {}).items())}
               for k in ["sales", "customer", "features", "trends"]}
    canon = json.dumps({"d": req["dataVersion"], "n": req["topN"], "w": [req["weights"][k] for k in WEIGHTED],
                        "e": [req["enabled"][k] for k in WEIGHTED], "f": filters}, sort_keys=True)
    return hashlib.sha256(canon.encode()).hexdigest()[:8]


def record_label(key: str, r: dict, names: dict) -> str:
    if key == "sales":
        return f"{r['line']} · {r['market_label']} · +{r['v']:,} units/yr"
    if key == "customer":
        return f"{'Pain points' if r['signal'] == 'pain' else 'Praise'} · {r['vehicle']} feedback · {r['v']} mentions"
    if key == "trends":
        return f"{names[r['c']]} · {pc(r['now'], 1)} year 1 → {pc(r['v'], 1)} year 4 · {r['pairs']} source pairs"
    return f"{r['vehicle']} · {r['attribute']} · {r['availability'].replace('_', ' ')}"


def phrase(key: str, rows: list[dict]) -> str:
    if key == "sales":
        units = sum(r["v"] for r in rows)
        lines = ", ".join(uniq(r["line"] for r in rows))
        return f"about {units:,} extra BMW units per year across {lines} in the conservative scenario"
    if key == "customer":
        pain = sum(r["v"] for r in rows if r["signal"] == "pain")
        praise = sum(r["v"] for r in rows if r["signal"] == "praise")
        return f"{pain} customer pain-point mentions" if pain >= praise else f"{praise} customer praise mentions"
    return "; ".join(f"estimated sales uplift of {pc(r['now'], 1)} in year 1 rising to {pc(r['v'], 1)} in year 4"
                     for r in rows)


def analyse(req: dict) -> dict:
    t = tables()
    names = t["candidates"]
    f, on = req["filters"], req["enabled"]
    active = sum(req["weights"][k] for k in WEIGHTED if on[k])
    eff = {k: req["weights"][k] / active if on[k] and active > 0 else 0.0 for k in WEIGHTED}
    pick = lambda key, group: set(f.get(key, {}).get(group, []))
    rows = {
        "sales": [r for r in t["sales"] if r["line"] in pick("sales", "line") and r["market"] in pick("sales", "market")],
        "customer": [r for r in t["customer"]
                     if r["vehicle"] in pick("customer", "vehicle") and r["signal"] in pick("customer", "signal")],
        "trends": [r for r in t["trends"] if r["technology"] in pick("trends", "technology")],
    }
    rows = {k: v if on[k] else [] for k, v in rows.items()}
    product = [r for r in t["features"] if r["vehicle"] in pick("features", "vehicle")]
    ids = list(names)
    raw = {k: {c: sum(r["v"] for r in rows[k] if r["c"] == c) for c in ids} for k in WEIGHTED}
    best = {k: max(raw[k].values(), default=0) for k in WEIGHTED}

    def rank_text(key: str, c: str) -> str:
        better = sum(raw[key][x] > raw[key][c] for x in ids)
        return f"the strongest of all {len(ids)} candidates" if better == 0 else f"#{better + 1} of {len(ids)} candidates"

    scored = []
    for c in ids:
        parts = {}
        for k in WEIGHTED:
            score = 100 * raw[k][c] / best[k] if best[k] > 0 else 0.0
            parts[k] = {"own": [r for r in rows[k] if r["c"] == c], "score": score, "points": eff[k] * score}
        scored.append((c, parts, sum(p["points"] for p in parts.values())))
    # ties broken by candidate id so the order never depends on runtime quirks
    scored.sort(key=lambda s: (-s[2], s[0]))
    top = [s for s in scored if s[2] > 0][:req["topN"]]

    recommendations = []
    for rank, (c, parts, total) in enumerate(top, start=1):
        cust = parts["customer"]["own"]
        pain = sum(r["v"] for r in cust if r["signal"] == "pain")
        praise = sum(r["v"] for r in cust if r["signal"] == "praise")
        assumption = parts["trends"]["points"] / total
        scenario = (parts["sales"]["points"] + parts["trends"]["points"]) / total
        own_product = [r for r in product if r["c"] == c]

        contributions = []
        for k in WEIGHTED:
            if not on[k]:
                continue
            p = parts[k]
            weight_sum = sum(r["v"] for r in p["own"]) or 1
            contributions.append({
                "category": k, "points": round(p["points"], 1), "categoryScore": round(p["score"], 1),
                "weight": eff[k],
                "summary": f"{phrase(k, p['own'])[:1].upper()}{phrase(k, p['own'])[1:]}: {rank_text(k, c)} in this source."
                if p["own"] else "No matching records, so this source adds nothing.",
                "records": [{"id": f"{PREFIX[k]}-{t[k].index(r) + 1:03d}", "label": record_label(k, r, names),
                             "share": r["v"] / weight_sum} for r in p["own"]],
            })
        context = [{
            "category": "features",
            "summary": "BMW option lists: " + "; ".join(record_label("features", r, names) for r in own_product) + ".",
            "records": [{"id": f"F-{t['features'].index(r) + 1:03d}", "label": record_label("features", r, names),
                         "share": 1 / len(own_product)} for r in own_product],
        }] if own_product else []

        specs = []
        if on["sales"]:
            own = parts["sales"]["own"]
            specs.append({"category": "sales", "label": CHIPS["sales"], "kind": "assumption" if own else "missing",
                          "text": f"{', '.join(uniq(r['line'] for r in own))} · +{sum(r['v'] for r in own):,} units/yr (scenario)"
                          if own else "No volume in the selected lines and markets"})
        if on["customer"]:
            text = " · ".join(x for x in (pain and f"{pain} pain-point mentions", praise and f"{praise} praise mentions") if x)
            specs.append({"category": "customer", "label": CHIPS["customer"], "kind": "evidence" if cust else "missing",
                          "text": f"{text} · {', '.join(uniq(r['vehicle'] for r in cust))}" if cust else "No evidence"})
        if own_product:
            specs.append({"category": "features", "label": CHIPS["features"], "kind": "context",
                          "text": " · ".join(uniq(f"{r['vehicle']} {r['availability'].replace('_', ' ')}" for r in own_product))})
        own_trends = parts["trends"]["own"]
        if on["trends"] and own_trends:
            specs.append({"category": "trends", "label": CHIPS["trends"], "kind": "assumption",
                          "text": " · ".join(f"{pc(r['now'], 1)} → {pc(r['v'], 1)} uplift, year 1 → 4" for r in own_trends)})

        drivers = sorted((k for k in WEIGHTED if parts[k]["points"] > 0), key=lambda k: -parts[k]["points"])
        lead = drivers[0]
        verdict = (f"Ranks #{rank} with {total:.1f} of 100. The biggest driver is {NAMES[lead]} "
                   f"({parts[lead]['points']:.1f} pts): {phrase(lead, parts[lead]['own'])}, {rank_text(lead, c)}.")
        if len(drivers) > 1:
            others = [f"{NAMES[k]} ({parts[k]['points']:.1f} pts)" for k in drivers[1:]]
            listing = others[0] if len(others) == 1 else f"{', '.join(others[:-1])} and {others[-1]}"
            verdict += f" Also supported by {listing}."
        verdict += (f" {pc(assumption)} of the score rests on trend assumptions." if assumption > 0.005
                    else " No part of the score rests on trend assumptions.")
        if parts["sales"]["points"] > 0:
            verdict += " Sales points are a BMW volume × uplift scenario, not observed sales."

        flags = []
        if pain and praise:
            flags.append({"severity": "warning", "message": f"Mixed customer signal: praised {praise} times, "
                          f"criticised {pain} times. Read the examples before changing it."})
        if praise > pain:
            flags.append({"severity": "ok", "message": "Customers praise this. Protect it rather than replacing it."})
        if on["customer"] and not cust:
            flags.append({"severity": "warning", "message": "No customer comments support this recommendation."})
        if scenario > 0.3:
            flags.append({"severity": "warning", "message": "More than 30% of the score comes from sales scenarios "
                          "and trends. Treat it as a hypothesis to validate."})
        if parts["sales"]["own"] or own_trends:
            flags.append({"severity": "info", "message": "Sales impact is a planning scenario from Chinese official "
                          "release pairs (category prior × feature multiplier), not a fitted or causal estimate."})

        recommendations.append({
            "id": c, "rank": rank, "title": names[c], "score": round(total, 1), "keep": praise > pain,
            "assumptionShare": assumption, "specs": specs,
            "reasoning": {
                "verdict": verdict,
                "confidence": "evidence-led" if assumption < 0.2 else "mixed" if assumption < 0.5 else "assumption-led",
                "evidenceShare": 1 - assumption, "contributions": contributions, "context": context, "flags": flags,
            },
        })

    run = {
        "id": uuid.uuid4().hex,
        "createdAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "fingerprint": fingerprint(req),
        "dataVersion": t["version"],
        "request": req,
        "effectiveWeights": eff,
        "recommendations": recommendations,
    }
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    (RUNS_DIR / f"{run['id']}.json").write_text(json.dumps(run, ensure_ascii=False) + "\n", encoding="utf-8")
    return run


def get_run(run_id: str) -> dict:
    path = RUNS_DIR / f"{run_id}.json"
    if not re.fullmatch(r"[0-9a-f]{32}", run_id) or not path.exists():
        raise KeyError(run_id)
    return json.loads(path.read_text(encoding="utf-8"))


def list_runs(limit: int) -> list[dict]:
    runs = [json.loads(p.read_text(encoding="utf-8")) for p in RUNS_DIR.glob("*.json")] if RUNS_DIR.exists() else []
    runs.sort(key=lambda r: r["createdAt"], reverse=True)
    return [{"id": r["id"], "createdAt": r["createdAt"], "fingerprint": r["fingerprint"],
             "effectiveWeights": r["effectiveWeights"], "enabled": r["request"]["enabled"],
             "topTitles": [x["title"] for x in r["recommendations"]]} for r in runs[:limit]]
