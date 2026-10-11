"""Tests for the English China-market feature-extraction prompt."""

import json

from app.services.feature_extraction import (
    FEATURE_EXTRACTION_SYSTEM_PROMPT,
    FeatureExtractionInput,
    build_feature_extraction_messages,
)


def test_prompt_is_english_and_omits_ota_status_instruction():
    assert "You are a Vehicle Feature Extraction Agent" in FEATURE_EXTRACTION_SYSTEM_PROMPT
    assert "计划 OTA 上线" not in FEATURE_EXTRACTION_SYSTEM_PROMPT
    assert "planned OTA" not in FEATURE_EXTRACTION_SYSTEM_PROMPT.lower()
    assert "already available" not in FEATURE_EXTRACTION_SYSTEM_PROMPT.lower()


def test_prompt_preserves_requested_feature_contract():
    source = FeatureExtractionInput(
        source_title="Vehicle launch",
        source_url="https://example.com/launch",
        source_date="2026-10-11",
        vehicle_info="Example Brand, Example EV",
        existing_features=["车载冰箱", "座椅按摩"],
        source_text="The vehicle includes an eight-litre refrigerator with cooling and heating.",
    )
    messages = build_feature_extraction_messages(source)
    payload = json.loads(messages[1]["content"])

    assert payload["existing_features"] == ["车载冰箱", "座椅按摩"]
    assert payload["source_url"] == "https://example.com/launch"
    assert "canonical_name" in messages[0]["content"]
    assert "vehicle_scope" in messages[0]["content"]
    assert "evidence" in messages[0]["content"]

