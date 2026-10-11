import csv
import json

from app.grabbers.bmw_official import (
    Feature,
    Seed,
    classify_feature,
    cumulative_sales,
    extract_features,
    parse_article,
    published_date,
    release_date,
    versions,
    VehicleVersion,
    write_csv,
)


HTML = """
<html><body><div class="article-detail">
  <h1>The new BMW 5 Series Sedan.</h1>
  <h5><span class="date">Wed May 24 14:00:00 CEST 2023</span></h5>
  <h2>For the first time, the new BMW i5 brings all-electric drive.</h2>
  <p>The market launch of the new BMW 5 Series Sedan will begin in October 2023.</p>
  <p>The innovative BMW Curved Display and new BMW Operating System 8.5 improve operation.</p>
  <p>A latest-generation battery enables a longer electric range and faster charging.</p>
  <p>The BMW i5 eDrive40 and BMW i5 M60 xDrive arrive alongside the BMW 520i, BMW 520d xDrive,
     BMW 530e and BMW 550e xDrive. The BMW i5 M60 is mentioned by its short name later.</p>
</div><div><p>Unrelated footer</p></div></body></html>
"""

SEED = Seed("BMW 5 Series", "https://www.press.bmwgroup.com/example", r"BMW\s+((?:i5\s+(?:eDrive\d+|M\d+)(?:\s+xDrive)?|5\d{2}[a-z]?(?:\s+xDrive)?))")


def test_article_and_target_fields():
    article = parse_article(HTML)
    assert article.title == "The new BMW 5 Series Sedan."
    assert published_date(article.published_text) == "2023-05-24"
    assert release_date(article.blocks, "2023-05-24") == ("2023-10", "month")
    assert versions(" ".join(article.blocks), SEED) == [
        "i5 eDrive40", "i5 M60 xDrive", "520i", "520d xDrive", "530e", "550e xDrive",
    ]


def test_features_use_only_pdf_domains():
    article = parse_article(HTML)
    features = extract_features(article.blocks)
    assert features
    assert all(isinstance(item, Feature) for item in features)
    assert {item.category for item in features} <= {"Digital Cockpit & AI", "Energy & Charging"}
    assert classify_feature("A new automated parking assistant is introduced.") == "Driving Assistance"


def test_sales_are_never_estimated():
    empty, status = cumulative_sales("BMW 5 Series", "2023-10", {})
    assert set(empty.values()) == {None}
    assert "not published" in status
    complete, status = cumulative_sales("BMW 5 Series", "2023-10", {
        "bmw 5 series": {2023: 10, 2024: 20, 2025: 30, 2026: 40, 2027: 50}
    })
    assert complete == {"year_1": 10, "year_2": 30, "year_3": 60, "year_4": 100, "year_5": 150}
    assert status.startswith("computed")
    partial, status = cumulative_sales("BMW 5 Series", "2023-10", {
        "bmw 5 series": {2023: 10, 2024: 20}
    })
    assert partial == {"year_1": 10, "year_2": 30, "year_3": None, "year_4": None, "year_5": None}
    assert "incomplete at 2025" in status


def test_csv_is_one_row_per_version(tmp_path):
    row = VehicleVersion(
        car_model="BMW 5 Series",
        version="BMW i5 eDrive40",
        release_date="2023-10",
        release_date_precision="month",
        newly_released_features=[Feature("BMW Curved Display", "Digital Cockpit & AI", "New display.")],
        cumulative_sales_after_years={"year_1": 10, "year_2": 30, "year_3": None, "year_4": None, "year_5": None},
        sales_status="official sales input is incomplete",
        source_url="https://www.press.bmwgroup.com/example",
        source_title="The new BMW 5 Series.",
        retrieved_at="2026-10-11T00:00:00+00:00",
    )
    output = tmp_path / "result.csv"
    write_csv([row], output)
    with output.open(encoding="utf-8-sig", newline="") as stream:
        saved = list(csv.DictReader(stream))
    assert len(saved) == 1
    assert saved[0]["cumulative_sales_year_2"] == "30"
    assert saved[0]["cumulative_sales_year_3"] == ""
    assert json.loads(saved[0]["newly_released_features"]) == ["BMW Curved Display"]
