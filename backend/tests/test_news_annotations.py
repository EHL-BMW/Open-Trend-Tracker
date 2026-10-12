import json
from types import SimpleNamespace

from app.services import news_annotations


def test_demo_annotations_work_without_api_key(tmp_path, monkeypatch):
    trends = tmp_path / "trends.json"
    trends.write_text(json.dumps({"topics": [{
        "id": "solid_state",
        "label_en": "Solid-state batteries",
        "headlines": [{"title": "固态电池", "source": "Example", "link": "https://example.com/1"}],
    }]}), encoding="utf-8")
    notes = tmp_path / "notes.json"
    notes.write_text(json.dumps({"solid_state": {"固态电池": {
        "titleEn": "Solid-state batteries",
        "featureSummary": "The story covers solid-state batteries.",
    }}}), encoding="utf-8")
    monkeypatch.setattr(news_annotations, "TRENDS_FILE", trends)
    monkeypatch.setattr(news_annotations, "DEMO_NOTES_FILE", notes)
    monkeypatch.setattr(news_annotations, "get_openai_api_key", lambda: None)

    result = news_annotations.annotate_topic("solid_state")

    assert result["items"][0]["title_en"] == "Solid-state batteries"
    assert result["items"][0]["feature_summary"] == "The story covers solid-state batteries."


def test_topic_annotations_are_feature_focused_and_cached(tmp_path, monkeypatch):
    trends = tmp_path / "trends.json"
    trends.write_text(json.dumps({"topics": [{
        "id": "solid_state",
        "label_en": "Solid-state batteries",
        "headlines": [{"title": "固态电池尚未形成销售收入", "source": "Example", "link": "https://example.com/1"}],
    }]}), encoding="utf-8")
    monkeypatch.setattr(news_annotations, "TRENDS_FILE", trends)
    monkeypatch.setattr(news_annotations, "CACHE_DIR", tmp_path / "cache")
    monkeypatch.setattr(news_annotations, "get_openai_api_key", lambda: "test-key")

    calls = []

    def create(**kwargs):
        calls.append(kwargs)
        return SimpleNamespace(output_text=json.dumps({"items": [{
            "index": 0,
            "title_en": "Solid-state batteries have not generated sales revenue",
            "feature_summary": "The company says solid-state batteries have not yet generated sales revenue.",
        }]}))

    monkeypatch.setattr(news_annotations, "OpenAI", lambda **kwargs: SimpleNamespace(
        responses=SimpleNamespace(create=create)
    ))

    first = news_annotations.annotate_topic("solid_state")
    second = news_annotations.annotate_topic("solid_state")

    assert first == second
    assert len(calls) == 1
    assert "Solid-state batteries" in calls[0]["input"]
    assert first["basis"] == "headline"
    assert first["items"][0]["link"] == "https://example.com/1"
