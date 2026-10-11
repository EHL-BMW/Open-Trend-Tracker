"""Backend API for unified evidence, forecasts, engineering input, and uploads.

    uv run uvicorn app.api:app --reload
"""
import json
from functools import cache

from fastapi import FastAPI, File, HTTPException, Query, Request, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from typing import Literal

from app.paths import RUNTIME_DIR, UNIFIED_DIR, get_openai_api_key, get_openai_model
from app.services.customer_input import process_document
from app.services.decision_dashboard import decision_dashboard, save_override
from app.services.feature_extraction import FeatureExtractionInput, extract_features
from app.services.forecast import engineering_comparison, forecast_catalog, price_forecast, sales_forecast
from app.services.impact_forecast import impact_taxonomy
from app.services.problem_identification import get_saved_g70_problems, identify_uploaded_problems
from app.services import gap_agent, planner

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


@app.get("/api/v1/forecast/impact-taxonomy")
def get_impact_taxonomy():
    """Category → subcategory → legacy and recent-news feature forecast view."""
    try:
        return impact_taxonomy()
    except (FileNotFoundError, KeyError, ValueError, json.JSONDecodeError) as exc:
        raise HTTPException(503, f"impact forecast inputs are not ready: {exc}") from exc


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


# ---------- planner contract v1 (docs/API.md) ----------

class Weights(BaseModel):
    sales: float
    customer: float
    trends: float


class Enabled(BaseModel):
    sales: bool
    customer: bool
    trends: bool


class Filters(BaseModel):
    sales: dict[str, list[str]]
    customer: dict[str, list[str]]
    features: dict[str, list[str]]
    trends: dict[str, list[str]]


class AnalysisRequest(BaseModel):
    dataVersion: str
    topN: int = Field(ge=1, le=20)
    weights: Weights
    enabled: Enabled
    filters: Filters


def v1_error(status: int, code: str, message: str, details=None) -> JSONResponse:
    return JSONResponse({"error": {"code": code, "message": message, "details": details}}, status_code=status)


@app.exception_handler(RequestValidationError)
async def invalid_request(request: Request, exc: RequestValidationError):
    if request.url.path.startswith("/api/v1/"):
        return v1_error(400, "invalid_request", "The analysis request is invalid.", jsonable(exc.errors()))
    return await request_validation_exception_handler(request, exc)


def jsonable(value):
    return json.loads(json.dumps(value, default=str))


@app.get("/api/v1/catalog")
def v1_catalog():
    return planner.catalog()


@app.post("/api/v1/analyses", status_code=201)
def v1_run_analysis(body: AnalysisRequest):
    if body.dataVersion != planner.tables()["version"]:
        return v1_error(409, "stale_data_version", "The data was updated. Reload the page to get the latest filters.")
    return planner.analyse(body.model_dump())


@app.get("/api/v1/analyses")
def v1_list_runs(limit: int = Query(20, ge=1, le=100)):
    return {"items": planner.list_runs(limit)}


@app.get("/api/v1/analyses/{run_id}")
def v1_get_run(run_id: str):
    try:
        return planner.get_run(run_id)
    except KeyError:
        return v1_error(404, "not_found", "That run doesn't exist.")


# ---------- AI Competitor Gap Analysis Agent ----------

class AgentAnalysisRequest(BaseModel):
    vehicle: str = "G60"
    domain: str | None = None
    domains: list[str] | None = None
    focus_competitor: str | None = None
    custom_instruction: str | None = None


class AgentReviewRequest(BaseModel):
    status: Literal["approved", "rejected", "challenged"]
    pm_notes: str | None = None


@app.post("/api/v1/agent/feature-extraction")
def v1_extract_features(req: FeatureExtractionInput):
    """Extract canonical, traceable China-market vehicle features from one source."""
    try:
        return extract_features(req)
    except RuntimeError as exc:
        raise HTTPException(503, str(exc)) from exc
    except (ValueError, json.JSONDecodeError) as exc:
        raise HTTPException(502, f"feature extraction returned invalid structured output: {exc}") from exc


@app.post("/api/v1/agent/problems/identify", status_code=201)
async def v1_identify_g70_problems(document: UploadFile = File(...)):
    """Identify problems in an uploaded workbook, save the list, and render its figure."""
    try:
        return identify_uploaded_problems(document.filename or "feedback.xlsx", await document.read())
    except FileNotFoundError as exc:
        raise HTTPException(404, str(exc)) from exc
    except (ValueError, json.JSONDecodeError) as exc:
        raise HTTPException(502, f"problem identification returned invalid structured output: {exc}") from exc


@app.get("/api/v1/agent/problems")
def v1_get_g70_problems():
    """Return the latest persisted G70 problem analysis for downstream feature views."""
    try:
        return get_saved_g70_problems()
    except FileNotFoundError as exc:
        raise HTTPException(404, str(exc)) from exc


@app.get("/api/v1/agent/status")
def v1_agent_status():
    key = get_openai_api_key()
    return {
        "configured": bool(key),
        "model": get_openai_model(),
        "provider": "OpenAI",
        "domains": list(gap_agent.DOMAIN_MAPPING.keys()),
        "domain_options": [
            {"key": k, "label": v["label"]}
            for k, v in gap_agent.DOMAIN_MAPPING.items()
        ],
    }


@app.post("/api/v1/agent/gap-analysis", status_code=201)
def v1_run_gap_analysis(req: AgentAnalysisRequest):
    return gap_agent.run_gap_analysis(
        vehicle=req.vehicle,
        domain=req.domain,
        domains=req.domains,
        focus_competitor=req.focus_competitor,
        custom_instruction=req.custom_instruction,
    )


@app.get("/api/v1/agent/gap-analyses")
def v1_list_gap_analyses(limit: int = Query(20, ge=1, le=100)):
    return {"items": gap_agent.list_gap_analyses(limit)}


@app.get("/api/v1/agent/gap-analyses/{analysis_id}")
def v1_get_gap_analysis(analysis_id: str):
    try:
        return gap_agent.get_gap_analysis(analysis_id)
    except KeyError:
        return v1_error(404, "not_found", f"Gap analysis {analysis_id} not found.")


@app.post("/api/v1/agent/gap-analyses/{analysis_id}/review")
def v1_review_gap_analysis(analysis_id: str, req: AgentReviewRequest):
    try:
        return gap_agent.review_gap_analysis(analysis_id, req.status, req.pm_notes)
    except KeyError:
        return v1_error(404, "not_found", f"Gap analysis {analysis_id} not found.")


class AgentChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str


class AgentChatRequest(BaseModel):
    messages: list[AgentChatMessage]
    vehicle: str = "G60"
    focus_company: str | None = None
    domain: str | None = None
    domains: list[str] | None = None


@app.get("/api/v1/agent/trend-markers")
def v1_get_trend_markers(
    company: str | None = None,
    domain: str | None = None,
    domains: list[str] | None = Query(None),
    q: str | None = None,
):
    return gap_agent.query_trend_markers(
        company=company,
        domain=domain,
        domains=domains,
        query=q,
    )


@app.post("/api/v1/agent/chat")
def v1_agent_chat(req: AgentChatRequest):
    return gap_agent.chat_with_agent(
        messages=[m.model_dump() for m in req.messages],
        target_vehicle=req.vehicle,
        focus_company=req.focus_company,
        domain=req.domain,
        domains=req.domains,
    )


