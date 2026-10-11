"""Compose Chinese feature evidence, BMW comments, sales trends, and PM overrides."""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

import pandas as pd

from app.paths import INTERNAL_DIR, RUNTIME_DIR
from app.services.forecast import forecast_catalog

FEATURE_PATTERNS = {
    "900V system + 102 kWh battery": (r"\b(?:800|900)\s*v\b", r"high[- ]voltage", r"battery", r"electric range"),
    "Charging + battery-swap station network": (r"charg", r"wallbox", r"charging station", r"charging network", r"charging cable"),
    "World-model ADAS + point-to-point navigation": (r"driving assist", r"highway assist", r"adaptive cruise", r"lane ", r"parking assist", r"navigation"),
    "5 nm automotive SoC + full-domain E/E architecture": (r"operating system", r"connecteddrive", r"software", r"touchscreen", r"cockpit", r"display", r"voice control"),
    "CDC dampers + hydraulic rear-subframe bushings": (r"suspension", r"damper", r"damping", r"shock absorber", r"ride comfort"),
    "Software-controlled active chassis system": (r"chassis", r"driving dynamics", r"handling", r"active steering", r"active roll"),
    "Dual cushion airbags + seat-integrated belts": (r"airbag", r"seat ?belt", r"safety belt", r"restraint"),
    "Integrated cabin display + audio entertainment": (r"rear.?seat entertainment", r"theatre screen", r"display", r"infotainment", r"sound system", r"audio"),
    "Roof center speaker + Dirac RRM audio": (r"speaker", r"sound system", r"bowers", r"surround sound", r"audio"),
    "Second-row zero-gravity seats + leg support": (r"seat comfort", r"reclin", r"lounge seat", r"leg support", r"comfortable seat"),
    "Six-/seven-seat cabin configuration": (r"six[- ]seat", r"seven[- ]seat", r"third row", r"seating capacity"),
    "ADB matrix headlights + Double-Dash DRL": (r"headlight", r"high.?beam", r"exterior light", r"daytime.?running"),
    "New Moon Silver paint + 21-inch wheels": (r"paint", r"exterior colou?r", r"wheel", r"rim", r"tyre", r"tire"),
}
OVERRIDES_FILE = RUNTIME_DIR / "decision-dashboard-overrides.json"


def _sentiment(feedback_type: str) -> str:
    value = feedback_type.strip().casefold()
    if value == "likes":
        return "positive"
    if value in {"wants", "difficult to use", "defect"}:
        return "negative"
    return "neutral"


def _internal_comments(vehicle: str) -> list[dict]:
    path = INTERNAL_DIR / f"{vehicle}_feedback_hackathon.xlsx"
    if not path.exists():
        return []
    frame = pd.read_excel(path).fillna("")
    frame = frame.drop_duplicates(subset=["ID", "Customer Feedback", "Feedback Type"])
    return [{
        "id": str(row["ID"]),
        "text": str(row["Customer Feedback"]),
        "sentiment": _sentiment(str(row["Feedback Type"])),
        "source": path.name,
    } for row in frame.to_dict("records") if str(row["Customer Feedback"]).strip()]


def _uploaded_comments(document_id: str) -> list[dict]:
    if not re.fullmatch(r"[0-9a-f]{16}", document_id):
        raise ValueError("document_id must be the 16-character ID returned by customer-input processing")
    path = RUNTIME_DIR / "customer-input" / document_id / "result.json"
    if not path.exists():
        raise FileNotFoundError(f"unknown processed document {document_id}")
    result = json.loads(path.read_text(encoding="utf-8"))
    return [{
        "id": str(row["id"]),
        "text": row["complaint"],
        "sentiment": "positive" if row["sentiment"] == "like" else (
            "negative" if row["sentiment"] in {"want", "difficult_to_use", "defect"} else "neutral"
        ),
        "source": result["filename"],
    } for row in result["complaints"]]


def quantify_comments(feature: str, comments: list[dict]) -> dict:
    patterns = FEATURE_PATTERNS.get(feature, (re.escape(feature),))
    matches = [row for row in comments if any(re.search(pattern, row["text"], re.I) for pattern in patterns)]
    counts = Counter(row["sentiment"] for row in matches)
    mentioned = len(matches)
    need = counts["negative"] / mentioned if mentioned else 0.0
    net = (counts["positive"] - counts["negative"]) / mentioned if mentioned else None
    return {
        "total_comments": len(comments),
        "mentions": mentioned,
        "mention_rate": mentioned / len(comments) if comments else 0.0,
        "positive": counts["positive"],
        "negative": counts["negative"],
        "neutral": counts["neutral"],
        "need_share": need,
        "net_sentiment": net,
        "examples": matches[:3],
    }


def _read_overrides() -> dict:
    if not OVERRIDES_FILE.exists():
        return {}
    return json.loads(OVERRIDES_FILE.read_text(encoding="utf-8"))


def save_override(vehicle: str, feature: str, values: dict) -> dict:
    catalog_names = {row["feature"] for row in forecast_catalog()["features"]}
    if feature not in catalog_names:
        raise KeyError(f"unknown Chinese-derived feature {feature!r}")
    overrides = _read_overrides()
    key = f"{vehicle}:{feature}"
    allowed = {"display_name", "selected", "priority", "engineering_status", "note"}
    overrides[key] = {name: value for name, value in values.items() if name in allowed and value is not None}
    OVERRIDES_FILE.parent.mkdir(parents=True, exist_ok=True)
    OVERRIDES_FILE.write_text(json.dumps(overrides, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return overrides[key]


def decision_dashboard(vehicle: str, document_id: str | None = None) -> dict:
    catalog = forecast_catalog()
    comments = _uploaded_comments(document_id) if document_id else _internal_comments(vehicle)
    overrides = _read_overrides()
    features = []
    for rank, source in enumerate(catalog["features"], start=1):
        feature = source["feature"]
        default = {
            "display_name": feature,
            "selected": rank <= 5,
            "priority": rank,
            "engineering_status": "review",
            "note": "",
        }
        manual = overrides.get(f"{vehicle}:{feature}", {})
        features.append({
            "source_feature": feature,
            "category": source["category"],
            "pair_count": source["pairs"],
            "model_count": source["models"],
            "sales_impact_trend": {
                "years_after_release": [1, 2, 3, 4],
                "estimate_pct": source["estimate"],
                "lower_pct": source["lower"],
                "upper_pct": source["upper"],
            },
            "comments": quantify_comments(feature, comments),
            **default,
            **manual,
        })
    features.sort(key=lambda row: (not row["selected"], row["priority"], row["source_feature"]))
    return {
        "vehicle": vehicle,
        "comment_source": {"type": "uploaded_document" if document_id else "bmw_internal", "document_id": document_id},
        "features": features,
        "method": "Chinese-derived feature forecast joined to keyword-quantified customer comments; PM edits are stored as overrides.",
        "caveat": "Sales impact is a planning scenario and comment matching is deterministic; both require product-manager review.",
    }
