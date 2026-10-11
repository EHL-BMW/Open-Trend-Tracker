"""OpenTT planner API (docs/API.md) on real data instead of the frontend mocks.

Candidates are the new Chinese features tracked in the newsletter (potential improvements). The sources:

  trends    news signal of the new feature + its estimated sales uplift, year 1 -> year 4, taken from the
            related old (Chinese-200) features of the same subcategory, or the category prior if none exists
  sales     BMW 2030 volume in CN, EU and US x the estimated year-4 uplift = extra units/year (scenario)
  customer  G70 problems identified from the feedback workbook in Feature Radar (mentions per problem)
  features  BMW option-list availability of the attributes behind the related old features (context, not weighted)

The scoring and texts follow frontend/src/mocks/engine.ts, the reference implementation of the contract.
No observed sales response exists for these features yet, so sales specs are marked as assumption
and every recommendation carries a flag saying so; assumptionShare stays the trends share as in the contract.
Every cited record carries a `url` back to its source (news article, Feature Radar problem, Impact tab, option list).
"""
from __future__ import annotations

import hashlib
import json
import re
import uuid
from datetime import datetime, timezone
from functools import cache

from app.paths import RUNTIME_DIR
from app.services.forecast import engineering_comparison, forecast_catalog
from app.services.impact_forecast import impact_taxonomy
from app.services.problem_identification import OUTPUT_FILE as PROBLEM_FILE

RUNS_DIR = RUNTIME_DIR / "planner-runs"
FORECAST_YEAR = 2030
DEFAULT_WEIGHTS = {"sales": 30, "customer": 45, "trends": 25}
WEIGHTED = ["sales", "customer", "trends"]
NAMES = {"sales": "Sales", "customer": "Customer", "trends": "Trends / Competition", "features": "Product"}
CHIPS = {"sales": "Sales", "customer": "Customer", "trends": "Trends", "features": "Product"}
MARKETS = {"CN": "China", "EU": "Europe", "US": "USA"}
CATALOG_VEHICLES = ["G60", "G70"]
IMPACT_URL = "/sales-impact-forecast"
# Old Chinese-derived feature -> BMW taxonomy attributes that describe the same customer function
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


def pc(value: float, digits: int = 0) -> str:
    return f"{value * 100:.{digits}f}%"


def uniq(values) -> list:
    return list(dict.fromkeys(values))


def saved_problems() -> list[dict]:
    """The latest problem list saved from Feature Radar; empty until a workbook was analysed."""
    if not PROBLEM_FILE.exists():
        return []
    return json.loads(PROBLEM_FILE.read_text(encoding="utf-8"))["problems"]


def tables() -> dict:
    """All source records. Rebuilt when Feature Radar saves a new problem list."""
    return _tables(PROBLEM_FILE.stat().st_mtime if PROBLEM_FILE.exists() else 0.0)


@cache
def _tables(_problems_mtime: float) -> dict:
    history = forecast_catalog()["bmw_sales_history"]
    option_lists = {v: {item["feature_id"]: item for item in engineering_comparison(v)["items"]} for v in CATALOG_VEHICLES}
    candidates, sales, customer, product, trends = {}, [], [], [], []
    for category in impact_taxonomy()["categories"]:
        for sub in category["subcategories"]:
            old = sub["legacy_features"]
            estimate = sub["impact_by_year"] or category["impact_by_year"]
            uplift = estimate[-1]["impact_pct"] / 100
            for news in sub["news_features"]:
                c = news["id"]
                candidates[c] = news["label"]
                trends.append({"c": c, "v": uplift, "now": estimate[0]["impact_pct"] / 100, "technology": c,
                               "priority": news["priority"] or 0.0, "signal": news["signal"] or "Tracked",
                               "articles": news["volume_recent"], "url": news["headline_url"],
                               "category": category["label"], "basis": [f["name"] for f in old]})
                for line, by_market in history.items():
                    for market, label in MARKETS.items():
                        units = round(by_market[market][str(FORECAST_YEAR)] * uplift)
                        if units > 0:
                            sales.append({"c": c, "v": units, "line": line, "market": market, "market_label": label})
                for vehicle, items in option_lists.items():
                    for attribute in uniq(a for f in old for a in BMW_ATTRIBUTES[f["name"]]):
                        item = items[attribute]
                        product.append({"c": c, "v": 1, "vehicle": vehicle,
                                        "attribute": item["feature"], "availability": item["availability"]})
    problems = saved_problems()
    for problem in problems:
        for c in problem["possible_feature_ids"]:
            if c in candidates:
                customer.append({"c": c, "v": problem["mention_count"], "problem": problem["id"],
                                 "name": problem["name"], "severity": problem["severity"]})
    data = {"candidates": candidates, "problems": [(p["id"], p["name"]) for p in problems], "sales": sales,
            "customer": customer, "features": product, "trends": trends}
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
                {"key": "market", "label": "Market", "options": options((m, f"{m} · {label}") for m, label in MARKETS.items())},
            ]},
            "customer": {"recordCount": len(t["customer"]), "filters": [
                {"key": "problem", "label": "Problem", "heading": "G70 problem list (Feature Radar)",
                 "options": options(t["problems"])},
            ]},
            "features": {"recordCount": len(t["features"]), "filters": [
                {"key": "vehicle", "label": "Vehicle", "heading": "Existing BMW cars (option lists)",
                 "options": options((v, v) for v in CATALOG_VEHICLES)},
            ]},
            "trends": {"recordCount": len(t["trends"]), "filters": [
                {"key": "technology", "label": "Feature", "heading": "New features in China news (newsletter)",
                 "options": options(names.items())},
            ]},
        },
        "trendForecast": [{"technology": r["technology"], "label": names[r["c"]], "currentShare": r["now"],
                           "forecastShare": r["v"]} for r in t["trends"]],
        "trendForecastLabels": {
            "title": "Estimated sales impact",
            "description": "Sales uplift of each new feature, estimated from its related old (Chinese-200) features, "
                           "or the category prior when none exists. Year 1 and year 4 after launch.",
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


def market_list(rows: list[dict]) -> list[str]:
    return [m for m in MARKETS if any(r["market"] == m for r in rows)]


def basis_text(r: dict) -> str:
    return ", ".join(r["basis"]) if r["basis"] else f"the {r['category']} category prior"


def record_label(key: str, r: dict, names: dict) -> str:
    if key == "sales":
        return f"{r['line']} · {r['market_label']} · +{r['v']:,} units/yr"
    if key == "customer":
        return f"{r['name']} · {r['v']} mentions · {r['severity']}"
    return f"{r['vehicle']} · {r['attribute']} · {r['availability'].replace('_', ' ')}"


def records(key: str, rows: list[dict], t: dict) -> list[dict]:
    """Cited records with a link back to their source; shares split each source's signal."""
    names = t["candidates"]
    if key == "trends":
        out = []
        for r in rows:
            rid = f"T-{t['trends'].index(r) + 1:03d}"
            out.append({"id": rid, "label": f"News · {names[r['c']]} · {r['signal']} · priority {r['priority']:.1f} · "
                                            f"{r['articles']:,} articles", "url": r["url"]})
            estimate = f"{pc(r['now'], 1)} year 1 → {pc(r['v'], 1)} year 4"
            basis = [f"Old feature · {name} · {estimate}" for name in r["basis"]]
            out += [{"id": f"{rid}.{j}", "label": label, "url": IMPACT_URL}
                    for j, label in enumerate(basis or [f"Category prior · {r['category']} · {estimate}"], start=1)]
        return [{**x, "share": 1 / len(out)} for x in out]
    total = sum(r["v"] for r in rows) or 1
    out = []
    for r in rows:
        url = {"sales": IMPACT_URL, "customer": f"/feature-trends#problem-{r.get('problem')}",
               "features": f"/api/engineering/features/{r.get('vehicle')}"}[key]
        out.append({"id": f"{PREFIX[key]}-{t[key].index(r) + 1:03d}", "label": record_label(key, r, names),
                    "url": url, "share": r["v"] / total})
    return out


def phrase(key: str, rows: list[dict]) -> str:
    if key == "sales":
        units = sum(r["v"] for r in rows)
        markets = ", ".join(market_list(rows))
        return f"about {units:,} extra BMW units per year in {markets} in the scenario"
    if key == "customer":
        return f"{sum(r['v'] for r in rows)} mentions across {len(rows)} G70 problem{'s' if len(rows) != 1 else ''}"
    return "; ".join(f"{r['signal'].lower()} in China news, with an estimated sales uplift of {pc(r['now'], 1)} in year 1 "
                     f"rising to {pc(r['v'], 1)} in year 4 (from {basis_text(r)})" for r in rows)


def analyse(req: dict) -> dict:
    t = tables()
    names = t["candidates"]
    f, on = req["filters"], req["enabled"]
    active = sum(req["weights"][k] for k in WEIGHTED if on[k])
    eff = {k: req["weights"][k] / active if on[k] and active > 0 else 0.0 for k in WEIGHTED}
    pick = lambda key, group: set(f.get(key, {}).get(group, []))
    rows = {
        "sales": [r for r in t["sales"] if r["market"] in pick("sales", "market")],
        "customer": [r for r in t["customer"] if r["problem"] in pick("customer", "problem")],
        "trends": [r for r in t["trends"] if r["technology"] in pick("trends", "technology")],
    }
    rows = {k: v if on[k] else [] for k, v in rows.items()}
    product = [r for r in t["features"] if r["vehicle"] in pick("features", "vehicle")]
    ids = list(names)
    priority = {r["c"]: r["priority"] for r in t["trends"]}
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
    # features sharing one uplift estimate tie often: the stronger news signal goes first, then the id
    scored.sort(key=lambda s: (-round(s[2], 6), -priority[s[0]], s[0]))
    top = [s for s in scored if s[2] > 0][:req["topN"]]

    recommendations = []
    for rank, (c, parts, total) in enumerate(top, start=1):
        cust = parts["customer"]["own"]
        mentions = sum(r["v"] for r in cust)
        assumption = parts["trends"]["points"] / total
        scenario = (parts["sales"]["points"] + parts["trends"]["points"]) / total
        own_product = [r for r in product if r["c"] == c]
        own_trends = parts["trends"]["own"]

        contributions = []
        for k in WEIGHTED:
            if not on[k]:
                continue
            p = parts[k]
            contributions.append({
                "category": k, "points": round(p["points"], 1), "categoryScore": round(p["score"], 1),
                "weight": eff[k],
                "summary": f"{phrase(k, p['own'])[:1].upper()}{phrase(k, p['own'])[1:]}: {rank_text(k, c)} in this source."
                if p["own"] else "No matching records, so this source adds nothing.",
                "records": records(k, p["own"], t),
            })
        context = [{
            "category": "features",
            "summary": "BMW option lists: " + "; ".join(record_label("features", r, names) for r in own_product) + ".",
            "records": records("features", own_product, t),
        }] if own_product else []

        specs = []
        if on["sales"]:
            own = parts["sales"]["own"]
            specs.append({"category": "sales", "label": CHIPS["sales"], "kind": "assumption" if own else "missing",
                          "text": f"{', '.join(market_list(own))} · +{sum(r['v'] for r in own):,} units/yr (scenario)"
                          if own else "No volume in the selected markets"})
        if on["customer"]:
            specs.append({"category": "customer", "label": CHIPS["customer"], "kind": "evidence" if cust else "missing",
                          "text": f"{len(cust)} G70 problem{'s' if len(cust) != 1 else ''} · {mentions} mentions"
                          if cust else "No problem in the selected list"})
        if own_product:
            specs.append({"category": "features", "label": CHIPS["features"], "kind": "context",
                          "text": " · ".join(uniq(f"{r['vehicle']} {r['availability'].replace('_', ' ')}" for r in own_product))})
        if on["trends"] and own_trends:
            specs.append({"category": "trends", "label": CHIPS["trends"], "kind": "assumption",
                          "text": " · ".join(f"{r['signal']} · {pc(r['now'], 1)} → {pc(r['v'], 1)} uplift, year 1 → 4"
                                             for r in own_trends)})

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
        if on["customer"] and not cust:
            flags.append({"severity": "warning", "message": "No G70 customer problem supports this recommendation."})
        if scenario > 0.3:
            flags.append({"severity": "warning", "message": "More than 30% of the score comes from sales scenarios "
                          "and trends. Treat it as a hypothesis to validate."})
        if any(not r["basis"] for r in own_trends):
            flags.append({"severity": "warning", "message": "No comparable old feature exists yet: the uplift is the "
                          "category planning prior, not a feature-level estimate."})
        if parts["sales"]["own"] or own_trends:
            flags.append({"severity": "info", "message": "Sales impact is a planning scenario (category prior × "
                          "feature multiplier from Chinese official release pairs), not a fitted or causal estimate."})

        recommendations.append({
            "id": c, "rank": rank, "title": names[c], "score": round(total, 1), "keep": False,
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
