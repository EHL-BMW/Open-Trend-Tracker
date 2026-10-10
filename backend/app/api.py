"""Read-only API over the unified output (run `python -m app.unify` first).

    uv run uvicorn app.api:app --reload
"""
import json
from functools import cache

from fastapi import FastAPI, HTTPException

from app.paths import UNIFIED_DIR

app = FastAPI(title="Open-Trend-Tracker")


@cache
def vehicle(code: str) -> dict:
    path = UNIFIED_DIR / f"{code}.json"
    if not path.exists():
        raise HTTPException(404, f"no unified data for vehicle {code}")
    return json.loads(path.read_text())


@cache
def observations() -> dict[str, dict]:
    path = UNIFIED_DIR / "observations.jsonl"
    if not path.exists():
        raise HTTPException(503, "no unified data yet; run `python -m app.unify`")
    return {o["id"]: o for o in map(json.loads, path.open())}


@app.get("/api/vehicles")
def list_vehicles():
    codes = sorted(p.stem for p in UNIFIED_DIR.glob("*.json") if p.stem != "coverage")
    return [{"vehicle": c, "line": vehicle(c)["line"], "markets": list(vehicle(c)["markets"])} for c in codes]


@app.get("/api/vehicles/{code}")
def get_vehicle(code: str):
    return vehicle(code)


@app.get("/api/vehicles/{code}/markets/{market}")
def get_market(code: str, market: str):
    markets = vehicle(code)["markets"]
    if market not in markets:
        raise HTTPException(404, f"{code} has no data for market {market}")
    return markets[market]


@app.get("/api/observations/{obs_id}")
def get_observation(obs_id: str):
    """Unified -> raw: an observation carries its RawRef (file + sheet/row or page)."""
    if obs_id not in observations():
        raise HTTPException(404, f"unknown observation {obs_id}")
    return observations()[obs_id]


@app.get("/api/observations")
def find_observations(vehicle: str, attribute: str | None = None, market: str | None = None,
                      metric: str | None = None, limit: int = 100):
    """Raw -> unified and evidence browsing: filter observations by where they landed in the tree."""
    hits = [o for o in observations().values()
            if o["vehicle"] == vehicle and attribute in (None, o["attribute"])
            and market in (None, "ALL", o["market"]) and metric in (None, o["metric"])]
    return {"total": len(hits), "items": hits[:limit]}


@app.get("/api/coverage")
def get_coverage():
    return json.loads((UNIFIED_DIR / "coverage.json").read_text())
