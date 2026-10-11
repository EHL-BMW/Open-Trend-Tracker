import csv
import json

from app.analysis.official_sales import analyze, feature_impact_forecast, read_versions, version_sales_differences
from openpyxl import Workbook

from app.analysis.interactive_feature_plot import (
    build_snapshots,
    estimate_bmw_sales,
    load_bmw_sales_history,
    render_html,
)


FIELDS = [
    "car_model", "version", "release_date", "version_order", "newly_released_features",
    "cumulative_sales_year_1", "cumulative_sales_year_2", "cumulative_sales_year_3",
    "cumulative_sales_year_4",
]


def _write_input(path):
    rows = [
        ["Car A", "Version 1", "2020-01", 1, '["Feature A"]', 100, 180, 250, 300],
        ["Car A", "Version 2", "2022-01", 2, '["Feature A", "Feature B"]', 120, 220, 310, 380],
        ["Car B", "Version 1", "2020-01", 1, '["Feature A"]', 200, 350, 450, 520],
        ["Car B", "Version 2", "2022-01", 2, '["Feature A", "Feature B"]', 230, 400, 520, 600],
    ]
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(FIELDS)
        writer.writerows(rows)


def test_version_differences_and_feature_association(tmp_path):
    source = tmp_path / "source.csv"
    _write_input(source)
    comparisons = version_sales_differences(read_versions(source))
    assert len(comparisons) == 2
    assert comparisons[0]["previous_version"] == "Version 1"
    assert comparisons[0]["sales_diff_year_1"] == 20
    assert comparisons[0]["sales_diff_year_4"] == 80
    assert json.loads(comparisons[0]["added_features"]) == ["Feature B"]
    forecast = feature_impact_forecast(comparisons)
    assert forecast[0]["forecast_status"] == "scenario_estimate_not_sales_fitted"
    assert forecast[0]["analysis_scope"] == "general_across_all_models"
    assert forecast[0]["estimated_sales_impact_year_1_pct"] < forecast[0]["estimated_sales_impact_year_4_pct"]
    assert forecast[0]["lower_year_4_pct"] < forecast[0]["estimated_sales_impact_year_4_pct"]
    assert forecast[0]["upper_year_4_pct"] > forecast[0]["estimated_sales_impact_year_4_pct"]

    summary = analyze(source, tmp_path / "out")
    assert summary["positive_associations"] == 1
    assert all((tmp_path / "out" / "plots" / name).stat().st_size > 0 for name in (
        "version_sales_differences.png", "version_sales_differences.pdf",
        "feature_sales_associations.png", "feature_sales_associations.pdf",
        "feature_sales_impact_4_year_forecast.png", "feature_sales_impact_4_year_forecast.pdf",
    ))
    assert (tmp_path / "out" / "feature_sales_impact_4_year_forecast.csv").stat().st_size > 0
    assert (tmp_path / "out" / "feature_catalog_by_category.csv").stat().st_size > 0
    with (tmp_path / "out" / "feature_sales_associations.csv").open(encoding="utf-8-sig", newline="") as stream:
        features = list(csv.DictReader(stream))
    assert features[0]["feature"] == "Feature B"
    assert features[0]["association"] == "positive_association"


def test_missing_sales_is_reported_not_invented(tmp_path):
    source = tmp_path / "source.csv"
    _write_input(source)
    rows = list(csv.reader(source.open()))
    rows[2][5:] = ["", "", "", ""]
    with source.open("w", newline="") as stream:
        csv.writer(stream).writerows(rows)
    summary = analyze(source, tmp_path / "out")
    assert summary["comparisons_with_sales"] == 1
    assert summary["positive_associations"] == 0
    assert summary["insufficient_evidence"] == 1


def test_same_date_trims_are_not_treated_as_generations(tmp_path):
    source = tmp_path / "source.csv"
    _write_input(source)
    rows = list(csv.DictReader(source.open()))[:2]
    for row in rows:
        row["release_date"] = "2022-01"
        row["version_order"] = ""
    with source.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    assert version_sales_differences(read_versions(source)) == []
    analyze(source, tmp_path / "out")
    with (tmp_path / "out" / "feature_sales_associations.csv").open(encoding="utf-8-sig") as stream:
        assert stream.readline().startswith("feature,transition_count")


def test_interactive_plot_embeds_category_and_feature_trajectories(tmp_path):
    source = tmp_path / "source.csv"
    _write_input(source)
    snapshots = build_snapshots(source)
    assert list(snapshots) == [2022]
    assert snapshots[2022][0]["feature"] == "Feature B"
    output = tmp_path / "interactive.html"
    history = {"F70": {"Global": {"label": "Global", "2024": 100, "2025": 110, "2030": 150}}}
    render_html(snapshots, output, input_pair_count=2, input_row_count=4, bmw_sales_history=history)
    document = output.read_text(encoding="utf-8")
    assert "plotly.js-dist-min@2.35.2" in document
    assert 'id="category-switches"' in document
    assert 'id="feature-switches"' in document
    assert "Category impact over four years" in document
    assert "Feature impact over four years" in document
    assert "fill:'tonexty'" in document
    assert 'id="year"' not in document
    assert "Calculated from all 2 input pairs (4 version rows)" in document
    assert 'id="bmw-model"' in document
    assert 'id="bmw-market"' in document
    assert 'id="bmw-feature-switches"' in document
    assert 'id="bmw-sales"' in document
    assert "New BMW model sales estimate: 2030–2033" in document


def test_bmw_sales_history_and_multi_feature_estimate(tmp_path):
    source = tmp_path / "sales.xlsx"
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "G60_G68"
    sheet.append(["market", "market_code", "volume_2024", "volume_2025", "volume_2030"])
    sheet.append(["Europe", "EU", 80, 100, 200])
    sheet.append(["China", "CN", 40, 50, 100])
    workbook.save(source)

    history = load_bmw_sales_history(source)
    assert history["G60/G68"]["Global"]["2030"] == 300
    features = [
        {"estimate": [2, 3, 4, 5], "lower": [1, 2, 3, 4], "upper": [3, 4, 5, 6]},
        {"estimate": [3, 4, 5, 6], "lower": [2, 3, 4, 5], "upper": [4, 5, 6, 7]},
    ]
    forecast = estimate_bmw_sales(history, "G60/G68", "Global", features)
    assert forecast["impact"] == [5, 7, 9, 11]
    assert forecast["estimate"][0] == 315
    assert forecast["lower"][0] == 309
    assert forecast["upper"][0] == 321


def test_forecast_uses_concrete_implementation_names():
    comparison = {
        "pair_id": "specific-1",
        "car_model": "NIO ES8",
        "version": "new",
        "added_features": json.dumps([
            "Powered by the 900V full-domain high-voltage architecture and a standard 102 kWh battery",
            "reclining safety system with dual seat airbags",
            "WorldModel driver assistance with point-to-point navigation and parking-lot routing",
        ]),
        "added_feature_categories": json.dumps({
            "Powered by the 900V full-domain high-voltage architecture and a standard 102 kWh battery": "Energy & Charging",
            "reclining safety system with dual seat airbags": "Smart Cabin",
            "WorldModel driver assistance with point-to-point navigation and parking-lot routing": "Driving Assistance",
        }),
    }
    labels = {row["display_name"] for row in feature_impact_forecast([comparison])}
    assert "900V system + 102 kWh battery" in labels
    assert "Dual cushion airbags + seat-integrated belts" in labels
    assert "World-model ADAS + point-to-point navigation" in labels
    assert not any(brand in label for label in labels for brand in ("NIO", "Li Auto", "XPeng"))
