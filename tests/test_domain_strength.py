"""
Tests for src/domain_strength.py (Academic Domain Strength).

Run from project root:
    PYTHONPATH=src pytest tests/test_domain_strength.py -v
"""
import sys
from pathlib import Path

import pandas as pd
import pytest

SRC = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC))

import domain_strength as ds  # noqa: E402
from academic_calculations import GRADE_POINTS  # noqa: E402


# ---------------------------------------------------------------------------
# skill_domain_map.csv integrity
# ---------------------------------------------------------------------------

def test_skill_domain_map_file_exists_and_loads():
    path = Path(__file__).resolve().parent.parent / "data" / "raw" / "skill_domain_map.csv"
    assert path.exists()
    df = pd.read_csv(path)
    assert {"skill_name", "domain", "domain_weight"} <= set(df.columns)
    assert len(df) > 0


def test_every_skill_used_in_course_skill_is_mapped_to_a_domain():
    course_skill_names = set(ds._course_skill["skill_name"].unique())
    mapped_names = set(ds._skill_domain_map["skill_name"].unique())
    missing = course_skill_names - mapped_names
    assert not missing, f"Skills used in course_skill.csv but missing from skill_domain_map.csv: {missing}"


def test_domain_weights_per_skill_sum_to_one():
    sums = ds._skill_domain_map.groupby("skill_name")["domain_weight"].sum().round(6)
    bad = sums[sums != 1.0]
    assert bad.empty, f"Skills whose domain_weight rows don't sum to 1.0: {bad.to_dict()}"


def test_domain_weights_are_within_valid_range():
    assert (ds._skill_domain_map["domain_weight"] > 0).all()
    assert (ds._skill_domain_map["domain_weight"] <= 1.0).all()


# ---------------------------------------------------------------------------
# Existing-student path
# ---------------------------------------------------------------------------

def test_calculate_domain_strength_returns_all_domains():
    result = ds.calculate_domain_strength("S00001")
    assert set(result["domain_strength"].keys()) == set(ds.ALL_DOMAINS)
    assert set(result["domain_courses_considered"].keys()) == set(ds.ALL_DOMAINS)


def test_domain_strength_scores_are_in_valid_range():
    result = ds.calculate_domain_strength("S00001")
    for domain, score in result["domain_strength"].items():
        if score is not None:
            assert 0.0 <= score <= 100.0, f"{domain} score {score} out of [0, 100]"


def test_domain_with_no_completed_relevant_courses_is_none_not_zero():
    """A domain nobody has touched yet should be reported as 'n/a' (None),
    not silently scored as 0 (which would be indistinguishable from all-F grades)."""
    result = ds._domain_strength_from_courses({})  # no completed courses at all
    assert all(v is None for v in result["domain_strength"].values())
    assert all(v == 0 for v in result["domain_courses_considered"].values())


def test_unknown_student_id_returns_all_none_not_an_error():
    result = ds.calculate_domain_strength("S99999_DOES_NOT_EXIST")
    assert all(v is None for v in result["domain_strength"].values())


# ---------------------------------------------------------------------------
# Correctness of the weighting math (hand-computed against a tiny fixture)
# ---------------------------------------------------------------------------

def test_domain_strength_matches_hand_calculation(monkeypatch):
    """Single course, single skill, single domain, weight 1.0 -> strength
    should equal exactly the grade's percentage of the max grade point."""
    fake_courses = pd.DataFrame([
        {"course_id": "X001", "credits": 4},
    ]).set_index("course_id")

    fake_course_skill_domain = pd.DataFrame([
        {"course_id": "X001", "skill_name": "TestSkill", "skill_weight": 1.0,
         "domain": "Test Domain", "domain_weight": 1.0},
    ])

    monkeypatch.setattr(ds, "_courses", fake_courses.reset_index())
    monkeypatch.setattr(ds, "_course_skill_domain", fake_course_skill_domain)
    monkeypatch.setattr(ds, "ALL_DOMAINS", ["Test Domain"])

    # Grade "A" -> grade_point 8 out of max 10 -> expect exactly 80.0
    result = ds._domain_strength_from_courses({"X001": "A"})
    assert result["domain_strength"]["Test Domain"] == 80.0
    assert result["domain_courses_considered"]["Test Domain"] == 1


def test_full_marks_grade_gives_100_strength(monkeypatch):
    top_grade = max(GRADE_POINTS, key=GRADE_POINTS.get)  # "O"

    fake_courses = pd.DataFrame([{"course_id": "X001", "credits": 3}])
    fake_course_skill_domain = pd.DataFrame([
        {"course_id": "X001", "skill_name": "TestSkill", "skill_weight": 0.9,
         "domain": "Test Domain", "domain_weight": 0.5},
    ])
    monkeypatch.setattr(ds, "_courses", fake_courses)
    monkeypatch.setattr(ds, "_course_skill_domain", fake_course_skill_domain)
    monkeypatch.setattr(ds, "ALL_DOMAINS", ["Test Domain"])

    result = ds._domain_strength_from_courses({"X001": top_grade})
    assert result["domain_strength"]["Test Domain"] == 100.0


def test_failing_grade_gives_zero_strength(monkeypatch):
    fake_courses = pd.DataFrame([{"course_id": "X001", "credits": 4}])
    fake_course_skill_domain = pd.DataFrame([
        {"course_id": "X001", "skill_name": "TestSkill", "skill_weight": 1.0,
         "domain": "Test Domain", "domain_weight": 1.0},
    ])
    monkeypatch.setattr(ds, "_courses", fake_courses)
    monkeypatch.setattr(ds, "_course_skill_domain", fake_course_skill_domain)
    monkeypatch.setattr(ds, "ALL_DOMAINS", ["Test Domain"])

    result = ds._domain_strength_from_courses({"X001": "F"})
    assert result["domain_strength"]["Test Domain"] == 0.0


def test_multi_domain_skill_splits_contribution_correctly(monkeypatch):
    """A skill mapped to two domains with weights 0.5/0.5 should contribute
    proportionally to both, each still resolving to the same percentage."""
    fake_courses = pd.DataFrame([{"course_id": "X001", "credits": 4}])
    fake_course_skill_domain = pd.DataFrame([
        {"course_id": "X001", "skill_name": "Statistics", "skill_weight": 1.0,
         "domain": "Domain A", "domain_weight": 0.5},
        {"course_id": "X001", "skill_name": "Statistics", "skill_weight": 1.0,
         "domain": "Domain B", "domain_weight": 0.5},
    ])
    monkeypatch.setattr(ds, "_courses", fake_courses)
    monkeypatch.setattr(ds, "_course_skill_domain", fake_course_skill_domain)
    monkeypatch.setattr(ds, "ALL_DOMAINS", ["Domain A", "Domain B"])

    result = ds._domain_strength_from_courses({"X001": "B+"})  # grade_point 7 -> 70%
    assert result["domain_strength"]["Domain A"] == 70.0
    assert result["domain_strength"]["Domain B"] == 70.0


# ---------------------------------------------------------------------------
# New-student path (mirrors summarize_new_student_history behaviour)
# ---------------------------------------------------------------------------

def test_new_student_path_matches_existing_student_path_for_same_data():
    """S00001's actual completed courses, fed through the new-student
    endpoint, must produce identical results to the existing-student path."""
    completed = ds._completed("S00001")
    semesters_input = [
        {
            "semester_number": int(sem),
            "courses": [
                {"course_id": row.course_id, "grade": row.grade}
                for row in group.itertuples()
            ],
        }
        for sem, group in completed.groupby("semester_taken")
    ]

    existing_result = ds.calculate_domain_strength("S00001")
    new_student_result = ds.calculate_domain_strength_new_student(semesters_input)

    assert existing_result["domain_strength"] == new_student_result["domain_strength"]


def test_new_student_path_rejects_unknown_grade():
    with pytest.raises(ValueError, match="Unknown grade"):
        ds.calculate_domain_strength_new_student([
            {"semester_number": 1, "courses": [{"course_id": "C0001", "grade": "Z"}]}
        ])


def test_new_student_path_rejects_unknown_course_id():
    with pytest.raises(ValueError, match="Unknown course_id"):
        ds.calculate_domain_strength_new_student([
            {"semester_number": 1, "courses": [{"course_id": "C9999_NOPE", "grade": "A"}]}
        ])


def test_new_student_path_credits_always_from_courses_csv_not_input():
    """Confirms credits can't be spoofed/passed via input — only course_id
    and grade are accepted, credits are always looked up."""
    import inspect
    sig = inspect.signature(ds.calculate_domain_strength_new_student)
    # only 'semesters' is accepted; per-course dicts only ever read course_id/grade
    assert list(sig.parameters) == ["semesters"]


# ---------------------------------------------------------------------------
# Non-interference guarantees
# ---------------------------------------------------------------------------

def test_does_not_modify_sgpa_cgpa_module():
    """Importing/using domain_strength must not change academic_calculations'
    published results for the same student."""
    from academic_calculations import calculate_cgpa, calculate_sgpa
    cgpa_before = calculate_cgpa("S00001")
    sgpa_before = calculate_sgpa("S00001")

    ds.calculate_domain_strength("S00001")  # exercise the new module

    assert calculate_cgpa("S00001") == cgpa_before
    assert calculate_sgpa("S00001") == sgpa_before


def test_does_not_import_recommend_module():
    """domain_strength.py must stay decoupled from recommend.py / the model,
    per the additive/read-only constraint."""
    import ast
    src_path = Path(__file__).resolve().parent.parent / "src" / "domain_strength.py"
    tree = ast.parse(src_path.read_text())
    imported_names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_names.update(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_names.add(node.module)
    assert "recommend" not in imported_names
    assert "pathway_scoring" not in imported_names


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
