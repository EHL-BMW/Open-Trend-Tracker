import io
import zipfile

import pytest

from app.services.customer_input import complaint_rows, extract_text, process_document
from app.services.decision_dashboard import decision_dashboard, quantify_comments, save_override
from app.services.forecast import engineering_comparison, price_forecast, sales_forecast


def test_customer_text_is_mapped_to_complaint_data_and_plot(tmp_path, monkeypatch):
    from app.services import customer_input

    monkeypatch.setattr(customer_input, "RUNTIME_DIR", tmp_path)
    result = process_document(
        "feedback.txt",
        b"The touchscreen is confusing and slow.\nI want better seat comfort.\nI love the ambient lighting.",
    )
    assert result["statement_count"] == 3
    assert result["sentiment_counts"] == {"difficult_to_use": 1, "want": 1, "like": 1}
    assert any(row["feature_id"] == "touchscreen" for row in result["complaints"])
    assert (tmp_path / "customer-input" / result["document_id"] / "complaints.png").stat().st_size > 0
    assert (tmp_path / "customer-input" / result["document_id"] / "result.json").stat().st_size > 0


def test_docx_text_extraction_uses_standard_library():
    body = b'''<?xml version="1.0" encoding="UTF-8"?>
    <w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
      <w:body><w:p><w:r><w:t>Charging is difficult.</w:t></w:r></w:p></w:body>
    </w:document>'''
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("word/document.xml", body)
    assert extract_text("input.docx", buffer.getvalue()) == "Charging is difficult."


def test_customer_rows_keep_unclassified_text():
    rows = complaint_rows("A completely novel customer idea.")
    assert rows[0]["feature"] == "Unclassified"
    assert rows[0]["complaint"] == "A completely novel customer idea."


def test_forecast_services_are_frontend_ready():
    result = sales_forecast("G60/G68", "Global", ["900V system + 102 kWh battery"])
    assert result["years"] == [2030, 2031, 2032, 2033]
    assert len(result["baseline"]) == len(result["estimate"]) == 4
    assert result["estimate"][0] > result["baseline"][0]

    prices = price_forecast("G60", target_year=2030, annual_rate=0.025)
    assert prices["items"]
    assert all(row["forecast_price_eur"] > row["current_price_eur"] for row in prices["items"])

    engineering = engineering_comparison("G60")
    assert engineering["items"]
    assert {row["availability"] for row in engineering["items"]} <= {"standard", "optional", "not_listed"}


def test_chinese_features_join_quantified_comments_and_manual_overrides(tmp_path, monkeypatch):
    from app.services import decision_dashboard as service

    comments = [
        {"id": "1", "text": "Charging is slow and difficult.", "sentiment": "negative", "source": "test"},
        {"id": "2", "text": "I love the charging network.", "sentiment": "positive", "source": "test"},
        {"id": "3", "text": "Great paint colour.", "sentiment": "positive", "source": "test"},
    ]
    summary = quantify_comments("Charging + battery-swap station network", comments)
    assert summary["mentions"] == 2
    assert summary["mention_rate"] == 2 / 3
    assert summary["need_share"] == 0.5

    monkeypatch.setattr(service, "OVERRIDES_FILE", tmp_path / "overrides.json")
    saved = save_override("G60", "Charging + battery-swap station network", {
        "display_name": "Fast charging ecosystem", "selected": True, "priority": 1,
        "engineering_status": "approved", "note": "Use in concept.",
    })
    assert saved["engineering_status"] == "approved"
    dashboard = decision_dashboard("G60")
    row = next(item for item in dashboard["features"] if item["source_feature"] == "Charging + battery-swap station network")
    assert row["display_name"] == "Fast charging ecosystem"
    assert row["comments"]["total_comments"] > 0
    assert row["sales_impact_trend"]["estimate_pct"] == [2.3, 3.312, 4.048, 4.6]
    with pytest.raises(ValueError, match="document_id"):
        decision_dashboard("G60", "../../private")


def test_planner_contract_ranks_news_features_from_real_sources(tmp_path, monkeypatch):
    from fastapi.testclient import TestClient

    from app.api import app
    from app.services import planner

    monkeypatch.setattr(planner, "RUNS_DIR", tmp_path)
    client = TestClient(app)
    catalog = client.get("/api/v1/catalog").json()
    assert len(catalog["trendForecast"]) == len(planner.tables()["candidates"]) == 21
    assert catalog["impactCoverage"]["collectionTarget"] == 200
    assert catalog["impactCoverage"]["validPairCount"] == 200
    assert all([point["year"] for point in row["impactByYear"]] == [1, 2, 3, 4]
               for row in catalog["trendForecast"])
    assert any(point["impact"] < 0 for row in catalog["trendForecast"] for point in row["impactByYear"])
    assert [o["value"] for o in catalog["categories"]["sales"]["filters"][0]["options"]] == ["CN", "EU", "US"]
    everything = {key: {group["key"]: [o["value"] for o in group["options"]] for group in source["filters"]}
                  for key, source in catalog["categories"].items()}
    request = {"dataVersion": catalog["dataVersion"], "topN": 5, "weights": catalog["defaultWeights"],
               "enabled": {"sales": True, "customer": True, "trends": True}, "filters": everything}
    first = client.post("/api/v1/analyses", json=request).json()
    again = client.post("/api/v1/analyses", json=request).json()
    titles = [row["title"] for row in first["recommendations"]]
    assert titles == [row["title"] for row in again["recommendations"]]
    assert first["fingerprint"] == again["fingerprint"]
    assert set(titles) <= set(planner.tables()["candidates"].values())
    top = first["recommendations"][0]
    assert {spec["category"]: spec["kind"] for spec in top["specs"]}["sales"] == "assumption"
    assert abs(top["assumptionShare"] - top["reasoning"]["contributions"][2]["points"] / top["score"]) < 0.01
    cited = [r for item in top["reasoning"]["contributions"] + top["reasoning"]["context"] for r in item["records"]]
    assert cited and all(r["url"] for r in cited)
    assert any(r["url"].startswith("https://") for r in top["reasoning"]["contributions"][2]["records"])

    customer_only = {**request, "enabled": {"sales": False, "customer": True, "trends": False}}
    run = client.post("/api/v1/analyses", json=customer_only).json()
    assert all(row["assumptionShare"] == 0 for row in run["recommendations"])
    assert client.get(f"/api/v1/analyses/{run['id']}").json()["id"] == run["id"]
    assert len(client.get("/api/v1/analyses?limit=2").json()["items"]) == 2
    assert client.post("/api/v1/analyses", json={**request, "dataVersion": "old"}).status_code == 409
    assert client.get("/api/v1/analyses/unknown").json()["error"]["code"] == "not_found"
