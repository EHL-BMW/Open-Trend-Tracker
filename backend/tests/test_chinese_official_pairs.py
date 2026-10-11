import csv
import json

from app.grabbers.chinese_official_pairs import DEFAULT_FALLBACK, DEFAULT_SEEDS, _feature_payload, _official
from app.grabbers.bmw_official import TECHNOLOGY_DOMAINS


def test_manifest_contains_twenty_complete_consecutive_pairs():
    with DEFAULT_SEEDS.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 20
    assert len({row["pair_id"] for row in rows}) == 20
    assert all(row["previous_version"] and row["current_version"] for row in rows)
    assert all(row["previous_release_date"] < row["current_release_date"] for row in rows)
    assert all(_official(row[side]) for row in rows for side in ("previous_url", "current_url"))


def test_official_fallback_covers_every_li_auto_source():
    with DEFAULT_SEEDS.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    fallback = json.loads(DEFAULT_FALLBACK.read_text(encoding="utf-8"))
    li_urls = {
        row[side]
        for row in rows
        if row["brand"] == "Li Auto"
        for side in ("previous_url", "current_url")
    }
    assert li_urls <= fallback.keys()


def test_fallback_features_use_only_methodology_categories():
    fallback = json.loads(DEFAULT_FALLBACK.read_text(encoding="utf-8"))
    for blocks in fallback.values():
        _, categories, _ = _feature_payload(blocks)
        assert set(json.loads(categories)) <= set(TECHNOLOGY_DOMAINS)
