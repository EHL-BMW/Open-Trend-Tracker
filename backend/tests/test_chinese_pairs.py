import csv
import math

import pytest

from app.analysis.chinese_pairs import first_sales_year, run
from app.services.impact_forecast import build_impact_taxonomy, impact_taxonomy


def _write(path, rows):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _fixture(tmp_path):
    pairs, features, sales = [], [], []
    for i in range(10):
        model = f"Car {i}"
        pairs.append({"pair_id": f"P{i}", "brand": "B", "car_model": model, "powertrain": "NEV",
                      "change_type": "facelift", "nameplate_launch": "2021-05", "previous_version": "v1", "previous_launch": "2021-05",
                      "current_version": "v2", "current_launch": "2023-02-10", "source_url": "https://example.com"})
        charging = i < 5
        if charging:
            features.append({"pair_id": f"P{i}", "detail": "5C LFP battery", "feature": "5C fast charging",
                             "subcategory": "charging_replenishment", "category": "Energy & Charging",
                             "evidence": "quote", "source_url": "https://example.com"})
        features.append({"pair_id": f"P{i}", "detail": "15.6-inch screen", "feature": "Larger centre screen",
                         "subcategory": "displays_hmi", "category": "Digital Cockpit & AI",
                         "evidence": "quote", "source_url": "https://example.com"})
        # charging pairs double, the others grow with the market (x1.5)
        growth = 2.0 + 0.01 * i if charging else 1.5 + 0.01 * i
        sales += [{"car_model": model, "year": 2022, "units": 10000},
                  {"car_model": model, "year": 2023, "units": round(10000 * growth)}]
    _write(tmp_path / "pairs.csv", pairs)
    _write(tmp_path / "features.csv", features)
    _write(tmp_path / "model_sales.csv", [{**r, "series": "retail", "source": "s", "url": "u"} for r in sales])
    _write(tmp_path / "market_sales.csv", [
        {"year": 2022, "total_retail": 20_000_000, "nev_retail": 4_000_000, "source": "s", "url": "u"},
        {"year": 2023, "total_retail": 21_000_000, "nev_retail": 6_000_000, "source": "s", "url": "u"},
    ])


def test_first_sales_year_skips_mixed_launch_year():
    assert first_sales_year("2024-03-31") == 2024
    assert first_sales_year("2024-04") == 2025


def test_run_estimates_market_adjusted_contrast(tmp_path):
    (tmp_path / "in").mkdir()
    _fixture(tmp_path / "in")
    summary = run(tmp_path / "in", tmp_path / "out")
    assert summary["pairs"] == 10
    assert summary["observed_pairs_by_year"] == {1: 10, 2: 0, 3: 0, 4: 0}

    with (tmp_path / "out" / "pair_sales.csv").open(encoding="utf-8") as stream:
        first = next(csv.DictReader(stream))
    # Car 0 doubled while the NEV market grew 1.5x: excess = ln(2 / 1.5)
    assert float(first["excess_log_year_1"]) == pytest.approx(math.log(2 / 1.5), abs=1e-4)
    assert first["status_year_2"] == "not_yet_observable"

    with (tmp_path / "out" / "impact.csv").open(encoding="utf-8") as stream:
        rows = {(r["level"], r["name"]): r for r in csv.DictReader(stream)}
    charging = rows[("subcategory", "charging_replenishment")]
    assert float(charging["impact_pct_year_1"]) == pytest.approx((2.02 / 1.57 - 1) * 100, abs=0.5)
    assert float(charging["lower_pct_year_1"]) < float(charging["impact_pct_year_1"]) < float(charging["upper_pct_year_1"])
    # every pair added a screen, so there is no comparison group
    assert rows[("feature", "Larger centre screen")]["impact_pct_year_1"] == ""
    assert (tmp_path / "out" / "plots" / "impact_by_subcategory.pdf").stat().st_size > 0

    news = tmp_path / "news.json"
    news.write_text('{"generated_at": "2026-10-01", "topics": []}', encoding="utf-8")
    taxonomy = build_impact_taxonomy(tmp_path / "out" / "impact.csv", news)
    energy = next(c for c in taxonomy["categories"] if c["label"] == "Energy & Charging")
    assert [p["year"] for p in energy["impact_by_year"]] == [1]
    sub = next(s for s in energy["subcategories"] if s["id"] == "charging_replenishment")
    assert sub["legacy_features"][0]["name"] == "5C fast charging"


def test_changes_stay_within_one_sales_series(tmp_path):
    _fixture(tmp_path)
    with (tmp_path / "model_sales.csv").open("a", encoding="utf-8", newline="") as stream:
        # Car 0 also has a wholesale series without the baseline year, and Car 1 a wholesale-only 2024
        stream.write("Car 0,2023,99999,wholesale,s,u\nCar 1,2024,50000,wholesale,s,u\n")
    with (tmp_path / "market_sales.csv").open("a", encoding="utf-8", newline="") as stream:
        stream.write("2024,22000000,8000000,s,u\n")
    run(tmp_path, tmp_path / "out")
    with (tmp_path / "out" / "pair_sales.csv").open(encoding="utf-8") as stream:
        rows = {r["pair_id"]: r for r in csv.DictReader(stream)}
    assert rows["P0"]["sales_series"] == "retail" and rows["P0"]["sales_year_1"] == "20000"
    assert rows["P1"]["status_year_2"] == "series_break"
    assert rows["P2"]["status_year_2"] == "missing_sales"


def test_sales_after_a_successor_launch_are_retained_with_a_quality_flag(tmp_path):
    _fixture(tmp_path)
    with (tmp_path / "pairs.csv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    rows.append({**rows[0], "pair_id": "P10", "previous_version": "v2", "current_version": "v3",
                 "previous_launch": "2023-02-10", "current_launch": "2024-08-01"})
    _write(tmp_path / "pairs.csv", rows)
    with (tmp_path / "features.csv").open(encoding="utf-8", newline="") as stream:
        features = list(csv.DictReader(stream))
    features.append({**features[0], "pair_id": "P10"})
    _write(tmp_path / "features.csv", features)
    with (tmp_path / "model_sales.csv").open("a", encoding="utf-8", newline="") as stream:
        stream.write("Car 0,2024,25000,retail,s,u\n")
    with (tmp_path / "market_sales.csv").open("a", encoding="utf-8", newline="") as stream:
        stream.write("2024,22000000,8000000,s,u\n")

    run(tmp_path, tmp_path / "out")

    with (tmp_path / "out" / "pair_sales.csv").open(encoding="utf-8") as stream:
        pair_rows = {r["pair_id"]: r for r in csv.DictReader(stream)}
    assert pair_rows["P0"]["successor_launch"] == "2024-08-01"
    assert pair_rows["P0"]["status_year_2"] == "observed"
    assert pair_rows["P0"]["quality_year_2"] == "successor_overlap"
    assert pair_rows["P0"]["excess_log_year_2"] != ""


def test_feature_rows_must_use_known_subcategory(tmp_path):
    _fixture(tmp_path)
    with (tmp_path / "features.csv").open("a", encoding="utf-8", newline="") as stream:
        stream.write("P0,x,y,fast_charging,Energy & Charging,q,u\n")
    with pytest.raises(ValueError, match="unknown subcategory"):
        run(tmp_path, tmp_path / "out")


def test_live_impact_taxonomy_maps_every_news_topic():
    result = impact_taxonomy()
    assert result["status"] == "observational_sales_association"
    assert result["news_feature_count"] == 21
    assert any(c["impact_by_year"] for c in result["categories"])
    news = {n["id"] for c in result["categories"] for sub in c["subcategories"] for n in sub["news_features"]}
    assert len(news) == 21
