"""Backend API for unified evidence, forecasts, engineering input, and uploads.

    uv run uvicorn app.api:app --reload
"""
import json
from functools import cache

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.paths import RUNTIME_DIR, UNIFIED_DIR
from app.services.customer_input import process_document
from app.services.decision_dashboard import decision_dashboard, save_override
from app.services.forecast import engineering_comparison, forecast_catalog, price_forecast, sales_forecast

app = FastAPI(title="Open-Trend-Tracker")
RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/api/artifacts", StaticFiles(directory=RUNTIME_DIR), name="runtime-artifacts")


class DecisionOverride(BaseModel):
    vehicle: str
    feature: str
    display_name: str | None = None
    selected: bool | None = None
    priority: int | None = Field(default=None, ge=1, le=999)
    engineering_status: str | None = None
    note: str | None = None


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


@app.get("/api/forecast/catalog")
def get_forecast_catalog():
    """Feature-impact trajectories plus available BMW model/market history."""
    try:
        return forecast_catalog()
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(503, f"forecast inputs are not ready: {exc}") from exc


@app.get("/api/forecast/sales")
def get_sales_forecast(
    model: str,
    market: str = "Global",
    feature: list[str] = Query(default=[]),
):
    """BMW 2030-2033 sales series; repeat `feature` for multiple selections."""
    try:
        return sales_forecast(model, market, feature)
    except KeyError as exc:
        raise HTTPException(404, str(exc)) from exc
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(503, f"forecast inputs are not ready: {exc}") from exc


@app.get("/api/forecast/prices/{vehicle}")
def get_price_forecast(vehicle: str, target_year: int = 2030, annual_rate: float = 0.025):
    """BMW option-price reference scenario for a forecast page."""
    try:
        result = price_forecast(vehicle.upper(), target_year, annual_rate)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    if not result["items"]:
        raise HTTPException(404, f"no positive BMW option-price evidence for {vehicle}")
    return result


@app.get("/api/engineering/features/{vehicle}")
def get_engineering_features(vehicle: str):
    """Existing BMW catalog comparison shaped as engineering review input."""
    result = engineering_comparison(vehicle.upper())
    if not any(item["sources"] for item in result["items"]):
        raise HTTPException(404, f"no BMW option-list comparison for {vehicle}")
    return result


@app.post("/api/customer-input/process")
async def process_customer_input(document: UploadFile = File(...)):
    """Convert a customer document into complaint data and a generated figure."""
    try:
        return process_document(document.filename or "upload.txt", await document.read())
    except (ValueError, json.JSONDecodeError) as exc:
        raise HTTPException(422, str(exc)) from exc


@app.get("/api/decision-dashboard/{vehicle}")
def get_decision_dashboard(vehicle: str, document_id: str | None = None):
    """Chinese feature selection joined to comments and sales-impact trends."""
    try:
        return decision_dashboard(vehicle.upper(), document_id)
    except FileNotFoundError as exc:
        raise HTTPException(404, str(exc)) from exc
    except (ValueError, KeyError) as exc:
        raise HTTPException(422, str(exc)) from exc


@app.post("/api/decision-dashboard/overrides")
def update_decision_override(update: DecisionOverride):
    """Persist the product manager's editable layer without changing source evidence."""
    if update.engineering_status not in {None, "review", "approved", "rejected"}:
        raise HTTPException(422, "engineering_status must be review, approved, or rejected")
    try:
        saved = save_override(update.vehicle.upper(), update.feature, update.model_dump(exclude={"vehicle", "feature"}))
    except KeyError as exc:
        raise HTTPException(404, str(exc)) from exc
    return {"vehicle": update.vehicle.upper(), "feature": update.feature, "override": saved}
