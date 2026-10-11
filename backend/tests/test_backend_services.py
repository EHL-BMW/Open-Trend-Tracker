import io
import zipfile

from app.services.customer_input import complaint_rows, extract_text, process_document
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
