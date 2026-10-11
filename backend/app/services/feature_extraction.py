"""Canonical vehicle-feature extraction for China-market source material."""

from __future__ import annotations

import json

from openai import OpenAI
from pydantic import BaseModel, Field

from app.paths import get_openai_api_key, get_openai_model


class FeatureExtractionInput(BaseModel):
    source_title: str
    source_url: str
    source_date: str
    vehicle_info: str = "Unknown"
    existing_features: list[str] = Field(default_factory=list)
    source_text: str


class FeatureEvidence(BaseModel):
    quote: str
    source_url: str


class ExtractedFeature(BaseModel):
    canonical_name: str
    category: str
    customer_capability: str
    customer_problem: str
    vehicle_scope: list[str]
    evidence: FeatureEvidence


class FeatureExtractionOutput(BaseModel):
    features: list[ExtractedFeature]


FEATURE_EXTRACTION_SYSTEM_PROMPT = """You are a Vehicle Feature Extraction Agent for BMW's China market. Read the supplied source material, extract concrete and traceable vehicle features, and map them into a unified feature repository.

Definition of a Feature
A Feature is a vehicle function or item of equipment that a customer can use or experience and that a product manager can independently decide whether to offer. Use cross-brand generic names, never automaker marketing names.

Granularity rules
- Keep features at the level of "in-car refrigerator", "seat massage", "automated parking", "rear-wheel steering", or "head-up display".
- Do not split one function by specification, implementation, or marketing name. For example, "cooling refrigerator", "heating refrigerator", and "8-litre refrigerator" must all map to "in-car refrigerator"; cooling, heating, and capacity are attributes, not separate features.
- Split capabilities only when the customer experience is different and each capability can be configured independently. For example, "seat heating" and "seat massage" are separate features.
- "Smart cockpit", "energy replenishment", and "comfort" are categories, not features.

Repository matching
- If the same feature already exists in the repository, match the existing canonical entry and add evidence. Do not create a synonym or duplicate entry.
- Extract only functions explicitly supported by the supplied material.
- Do not infer that every model, model year, powertrain, or trim offers the feature.

Output requirements
- Return JSON only, with a top-level "features" array.
- canonical_name must be a unified Chinese feature name.
- category must be a technology category, not another feature.
- customer_capability must state in one sentence what the customer can specifically do.
- customer_problem must state the likely usage problem the feature addresses.
- vehicle_scope must contain only brands explicitly supported by the source.
- evidence must include a short verbatim quote and the supplied source URL.
- If the source supports no qualifying feature, return {"features": []}.
"""


def build_feature_extraction_messages(source: FeatureExtractionInput) -> list[dict[str, str]]:
    """Build the English extraction prompt while preserving Chinese canonical output names."""
    payload = {
        "source_title": source.source_title,
        "source_url": source.source_url,
        "source_date": source.source_date,
        "vehicle_info": source.vehicle_info,
        "existing_features": source.existing_features,
        "source_text": source.source_text,
    }
    return [
        {"role": "system", "content": FEATURE_EXTRACTION_SYSTEM_PROMPT},
        {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
    ]


def extract_features(source: FeatureExtractionInput) -> dict:
    """Extract and validate canonical features with the configured OpenAI model."""
    api_key = get_openai_api_key()
    if not api_key:
        raise RuntimeError("OpenAI is not configured; set OPENAI_API_KEY to run feature extraction")

    response = OpenAI(api_key=api_key).chat.completions.create(
        model=get_openai_model(),
        response_format={"type": "json_object"},
        temperature=0.0,
        seed=42,
        messages=build_feature_extraction_messages(source),
    )
    content = response.choices[0].message.content or '{"features": []}'
    return FeatureExtractionOutput.model_validate_json(content).model_dump()

