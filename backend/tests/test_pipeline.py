"""End-to-end checks on the real internal data plus the example external feed."""
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app import api
from app.external import ev_market
from app.mapping import Mapper
from app.paths import EXTERNAL_DIR, INTERNAL_DIR
from app.unify import build, collect

EXAMPLES = Path(__file__).resolve().parents[1] / "examples"
pytestmark = pytest.mark.skipif(not (INTERNAL_DIR / "sales_volumes.xlsx").exists(), reason="internal data missing")


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


EV_MARKET = sorted(EXTERNAL_DIR.glob("top_500_ev_phev_europe*.csv"))


@pytest.mark.skipif(not EV_MARKET, reason="EV market table missing")
def test_ev_market_table():
    obs = ev_market(EV_MARKET[0])
    Mapper().apply(obs)
    assert all(o.attribute for o in obs), {o.raw_label for o in obs if not o.attribute}
    own = [o for o in obs if o.competitor is None]
    assert {o.vehicle for o in own} == {"G60", "G70"}  # F70 has no EV/PHEV variant
    assert not any(o.competitor and o.competitor.startswith(("BMW", "MINI")) for o in obs)
    i5 = [o for o in own if o.vehicle == "G60" and o.metric == "wltp_range_bev"]
    assert i5 and all(0 < o.norm <= 1 for o in i5)  # percentile within E-segment BEVs
    assert not any(o.metric == "charging_time_10_80_phev" and o.competitor is None for o in obs)


def test_recommendation_pipeline(tmp_path, monkeypatch):
    from app import pipeline

    mapper = Mapper()
    features = pipeline.feature_catalog(mapper)
    existing = pipeline.existing_features(mapper, features)
    # package contents count: the G60 head-up display only appears inside the Innovationspaket
    assert "BMW Live Cockpit Professional inkl. BMW Head-Up Display" in set(existing["item"])
    monkeypatch.setattr(pipeline, "SYNTHETIC_DIR", tmp_path)
    trends, news = pipeline.external_inputs(mapper, features)
    assert set(trends.columns) >= {"month", "feature", "popularity", "sales"} and (trends["sales"] > 0).all()
    fc = pipeline.forecast(trends, news)
    assert fc["sales_growth_fc"].abs().max() < 1  # no exploding growth from near-zero history
    rec = pipeline.recommend(features, existing, pipeline.comment_summary(pipeline.comments(mapper, features)),
                             fc, pipeline.engineering_filter(features))
    g60 = rec[rec["car"] == "G60"]
    assert g60["score"].is_monotonic_decreasing or g60[g60["feasible"]]["score"].is_monotonic_decreasing
    assert g60[~g60["feasible"]]["score"].isna().all()  # engineering "off" features are never scored
    assert (g60[g60["feasible"]]["score"].between(0, 1)).all()
