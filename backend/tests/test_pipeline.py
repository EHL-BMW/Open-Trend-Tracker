"""End-to-end checks on the real internal data plus the example external feed."""
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app import api
from app.paths import DATA_DIR
from app.unify import build, collect

EXAMPLES = Path(__file__).resolve().parents[1] / "examples"
pytestmark = pytest.mark.skipif(not (DATA_DIR / "sales_volumes.xlsx").exists(), reason="internal data missing")


@pytest.fixture(scope="module")
def pipeline():
    obs, mapper = collect(external_dir=EXAMPLES)
    return obs, mapper, build(obs, mapper)


def test_every_observation_links_to_raw(pipeline):
    obs, _, _ = pipeline
    assert len({o.id for o in obs}) == len(obs)
    assert all(o.raw.file and o.raw.locator for o in obs)


def test_internal_sources_are_almost_fully_mapped(pipeline):
    obs, _, _ = pipeline
    # option lists are excluded: paint, upholstery colours and wheel designs stay unmapped on purpose
    internal = [o for o in obs if o.origin == "internal" and o.metric != "unclassified" and o.source != "options"]
    mapped = [o for o in internal if o.attribute]
    assert len(mapped) / len(internal) > 0.99


def test_option_lists_parse(pipeline):
    obs, _, _ = pipeline
    options = [o for o in obs if o.source == "options"]
    assert {o.vehicle for o in options} == {"G60", "G70"}
    hud = [o for o in options if o.raw_label == "BMW 3D Head-Up Display"]
    assert hud and hud[0].attribute == "displays" and hud[0].raw.locator.startswith("page=")
    prices = [o.value for o in options if o.metric == "option_price"]
    assert prices and all(p >= 0 for p in prices)


def test_study_scales_are_normalized(pipeline):
    obs, _, _ = pipeline
    for o in obs:
        if o.source.startswith("study"):
            assert 0 <= o.norm <= 1


def test_hierarchy_and_traceability(pipeline):
    obs, _, trees = pipeline
    by_id = {o.id: o for o in obs}
    node = trees["G60"].markets["US"].categories["hmi"].attributes["touchscreen"]
    assert node.metrics["study_mean_1_7"].unit == "1-7"
    for oid in node.metrics["like"].obs_ids:
        o = by_id[oid]
        assert (o.vehicle, o.market, o.attribute, o.metric) == ("G60", "US", "touchscreen", "like")


def test_unknown_feature_awareness(pipeline):
    _, _, trees = pipeline
    # China has no internal feedback and the CN study has no voice item -> only the external feed knows it
    assert trees["G68"].markets["CN"].categories["hmi"].attributes["voice_assistant"].status == "external_only"
    assert trees["G60"].markets["US"].categories["infotainment"].attributes["smartphone_integration"].status == "both"
    charging = trees["G60"].markets["EU"].categories["range_charging"].attributes["charging"]
    assert "max_dc_charging_power" in charging.competitors["Example Competitor Sedan"]
    # a feature the taxonomy does not know yet, and an unlabelled comment, are kept and reported
    unmapped = trees["G60"].markets["EU"].unmapped
    assert "Augmented reality windshield projection" in unmapped
    assert "(unlabelled comment)" in unmapped


def test_api(pipeline, tmp_path, monkeypatch):
    obs, _, trees = pipeline
    for v, tree in trees.items():
        (tmp_path / f"{v}.json").write_text(tree.model_dump_json())
    (tmp_path / "observations.jsonl").write_text("\n".join(o.model_dump_json() for o in obs))
    (tmp_path / "coverage.json").write_text(json.dumps({}))
    monkeypatch.setattr(api, "UNIFIED_DIR", tmp_path)
    api.vehicle.cache_clear()
    api.observations.cache_clear()

    client = TestClient(api.app)
    assert {v["vehicle"] for v in client.get("/api/vehicles").json()} >= {"F70", "G60", "G68", "G70"}
    market = client.get("/api/vehicles/G60/markets/US").json()
    oid = market["categories"]["hmi"]["attributes"]["touchscreen"]["metrics"]["like"]["obs_ids"][0]
    assert client.get(f"/api/observations/{oid}").json()["raw"]["file"].endswith("G60_feedback_hackathon.xlsx")
    hits = client.get("/api/observations", params={"vehicle": "G60", "attribute": "touchscreen"}).json()
    assert hits["total"] > 0
    api.vehicle.cache_clear()
    api.observations.cache_clear()
