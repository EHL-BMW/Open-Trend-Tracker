"""Tests for the AI Competitor Gap Analysis Agent, Future Trend Markers DB, and AI Chat."""
import pytest
from fastapi.testclient import TestClient

from app.api import app
from app.services import gap_agent


@pytest.fixture
def client():
    return TestClient(app)


def test_agent_status_endpoint(client):
    response = client.get("/api/v1/agent/status")
    assert response.status_code == 200
    data = response.json()
    assert "configured" in data
    assert "model" in data
    assert "domains" in data
    # Assert all 7 MECE domains are present
    expected_7_domains = [
        "energy_charging",
        "driving_assistance",
        "digital_cockpit",
        "connected_ecosystem",
        "smart_cabin",
        "vehicle_dynamics",
        "smart_exterior",
    ]
    for d in expected_7_domains:
        assert d in data["domains"], f"Missing domain {d} in agent status"
    assert len(data["domains"]) == 7


def test_deterministic_offline_gap_synthesis_all_7_domains():
    expected_7_domains = [
        "energy_charging",
        "driving_assistance",
        "digital_cockpit",
        "connected_ecosystem",
        "smart_cabin",
        "vehicle_dynamics",
        "smart_exterior",
    ]
    for dom in expected_7_domains:
        synthesis = gap_agent._build_offline_synthesis("G60", dom)
        assert synthesis.target_vehicle == "G60"
        assert synthesis.domain == dom
        assert len(synthesis.competitor_benchmarks) >= 2
        assert len(synthesis.recommended_requirements) >= 1
        assert synthesis.review_status == "pending_review"
        assert len(synthesis.pm_challenge_prompts) >= 1


def test_domain_aliases_resolution():
    assert gap_agent.normalize_domain("smart_driving") == "driving_assistance"
    assert gap_agent.normalize_domain("chassis_dynamics") == "vehicle_dynamics"
    assert gap_agent.normalize_domain("energy_and_charging") == "energy_charging"
    assert gap_agent.normalize_domain("connected_ecosystem") == "connected_ecosystem"
    assert gap_agent.normalize_domain("smart_exterior") == "smart_exterior"


def test_future_trend_markers_db(client):
    # 1. Query all
    res = client.get("/api/v1/agent/trend-markers")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 20
    companies = [c["id"] for c in data["companies"]]
    assert "nio" in companies
    assert "aito" in companies
    assert "xiaomi" in companies
    assert "li_auto" in companies
    assert "zeekr" in companies
    assert "xpeng" in companies

    # 2. Filter by company
    res_xiaomi = client.get("/api/v1/agent/trend-markers?company=xiaomi")
    assert res_xiaomi.status_code == 200
    items = res_xiaomi.json()["items"]
    assert len(items) >= 2
    assert all(item["company_id"] == "xiaomi" for item in items)

    # 3. Filter by newly added MECE domains
    res_connected = client.get("/api/v1/agent/trend-markers?domain=connected_ecosystem")
    assert res_connected.status_code == 200
    conn_items = res_connected.json()["items"]
    assert len(conn_items) >= 2

    res_exterior = client.get("/api/v1/agent/trend-markers?domain=smart_exterior")
    assert res_exterior.status_code == 200
    ext_items = res_exterior.json()["items"]
    assert len(ext_items) >= 2

    # 4. Search query
    res_search = client.get("/api/v1/agent/trend-markers?q=Golden+Battery")
    assert res_search.status_code == 200
    search_items = res_search.json()["items"]
    assert len(search_items) >= 1
    assert search_items[0]["company_id"] == "zeekr"


def test_agent_chat_endpoint_with_connected_domain(client):
    res = client.post("/api/v1/agent/chat", json={
        "vehicle": "G60",
        "focus_company": "aito",
        "domain": "connected_ecosystem",
        "messages": [
            {"role": "user", "content": "How does AITO MagLink and underground garage BLE link solve My BMW App timeouts?"}
        ]
    })
    assert res.status_code == 200
    data = res.json()
    assert data["role"] == "assistant"
    assert len(data["content"]) > 50
    assert "referenced_markers" in data


def test_agent_gap_analyses_lifecycle(client):
    # 1. Run or retrieve analysis
    res = client.post("/api/v1/agent/gap-analysis", json={
        "vehicle": "G60",
        "domain": "smart_exterior",
        "focus_competitor": "Zeekr",
    })
    assert res.status_code == 201
    analysis = res.json()
    analysis_id = analysis["analysis_id"]
    assert analysis["target_vehicle"] == "G60"
    assert analysis["domain"] == "smart_exterior"
    assert len(analysis["recommended_requirements"]) > 0

    # 2. Get by ID
    get_res = client.get(f"/api/v1/agent/gap-analyses/{analysis_id}")
    assert get_res.status_code == 200
    assert get_res.json()["analysis_id"] == analysis_id

    # 3. List
    list_res = client.get("/api/v1/agent/gap-analyses")
    assert list_res.status_code == 200
    items = list_res.json()["items"]
    assert any(item["analysis_id"] == analysis_id for item in items)

    # 4. Review decision
    review_res = client.post(f"/api/v1/agent/gap-analyses/{analysis_id}/review", json={
        "status": "approved",
        "pm_notes": "Reviewed and approved by PM test suite",
    })
    assert review_res.status_code == 200
    updated = review_res.json()
    assert updated["review_status"] == "approved"
    assert updated["pm_notes"] == "Reviewed and approved by PM test suite"


def test_multi_domain_normalization():
    assert gap_agent.normalize_domains("all") == list(gap_agent.DOMAIN_MAPPING.keys())
    assert gap_agent.normalize_domains(["all"]) == list(gap_agent.DOMAIN_MAPPING.keys())
    assert gap_agent.normalize_domains(["energy_charging", "smart_driving"]) == ["energy_charging", "driving_assistance"]
    assert gap_agent.normalize_domains("energy_charging,connected_ecosystem") == ["energy_charging", "connected_ecosystem"]
    assert gap_agent.normalize_domains([]) == ["energy_charging"]


def test_multi_domain_gap_analysis_and_trend_markers(client):
    # Test 2 domains (e.g. Energy + Connected Ecosystem)
    res_2 = client.post("/api/v1/agent/gap-analysis", json={
        "vehicle": "G60",
        "domains": ["energy_charging", "connected_ecosystem"],
        "focus_competitor": "All",
    })
    assert res_2.status_code == 201
    analysis_2 = res_2.json()
    assert analysis_2["domains"] == ["energy_charging", "connected_ecosystem"]
    assert "Energy & Charging" in analysis_2["domain_label"]
    assert "Connected Ecosystem" in analysis_2["domain_label"]
    assert len(analysis_2["recommended_requirements"]) >= 2

    # Test 3 domains (Digital Cockpit + Smart Cabin + Smart Exterior)
    res_3 = client.post("/api/v1/agent/gap-analysis", json={
        "vehicle": "G70",
        "domains": ["digital_cockpit", "smart_cabin", "smart_exterior"],
    })
    assert res_3.status_code == 201
    analysis_3 = res_3.json()
    assert analysis_3["domains"] == ["digital_cockpit", "smart_cabin", "smart_exterior"]
    assert len(analysis_3["recommended_requirements"]) >= 3

    # Test trend markers filtered across multiple domains
    tm_res = client.get("/api/v1/agent/trend-markers?domains=energy_charging&domains=smart_exterior")
    assert tm_res.status_code == 200
    tm_data = tm_res.json()
    assert tm_data["total"] >= 4
    domains_present = {gap_agent.normalize_domain(m["domain"]) for m in tm_data["items"]}
    assert domains_present.issubset({"energy_charging", "smart_exterior"})

    # Test multi-domain chat endpoint
    chat_res = client.post("/api/v1/agent/chat", json={
        "vehicle": "G60",
        "domains": ["energy_charging", "connected_ecosystem"],
        "messages": [
            {"role": "user", "content": "How do energy charging and subterranean connected ecosystem trade-offs interact?"}
        ]
    })
    assert chat_res.status_code == 200
    assert len(chat_res.json()["content"]) > 50

