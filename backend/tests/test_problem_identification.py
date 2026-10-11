"""Tests for G70 problem identification and Feature Radar linkage."""

from openpyxl import Workbook

from app.services.problem_identification import _deterministic_problems, _read_candidates


def test_problem_candidates_exclude_likes_and_keep_traceable_evidence(tmp_path):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Feedback_Explorer"
    sheet.append([
        "ID", "Source", "Brand", "Sales Description", "Country", "Derivate (e-code)",
        "Engine Type", "Feedback Type", "Customer Feedback", "Vfc level2 3 Name",
        "Vfc level2 Name", "Vfc level3 Name",
    ])
    sheet.append(["G70-1", "A", "BMW", "7 Series", "US", "G70", "BEV", "Difficult to Use", "The touch screen menus are confusing.", "", "Touch screen, operation", "Not user-friendly"])
    sheet.append(["G70-2", "A", "BMW", "7 Series", "US", "G70", "BEV", "Likes", "The touch screen looks great.", "", "Touch screen, operation", "Like: function"])
    source = tmp_path / "feedback.xlsx"
    workbook.save(source)

    candidates = _read_candidates(source)

    assert candidates[0]["mention_count"] == 1
    assert candidates[0]["evidence"][0]["feedback_id"] == "G70-1"


def test_deterministic_problem_uses_eight_category_taxonomy_and_feature_id():
    problem = _deterministic_problems([
        {
            "label": "Touch screen, operation",
            "mention_count": 14,
            "feedback_types": {"Difficult to Use": 14},
            "evidence": [{"feedback_id": "G70-1", "feedback_type": "Difficult to Use", "quote": "Menus are confusing."}],
        }
    ])[0]

    assert problem.category == "Digital Experience"
    assert problem.affected_feature_ids == ["cockpit_llm"]
    assert "cockpit_llm" in problem.possible_feature_ids
    assert problem.mention_count == 14
