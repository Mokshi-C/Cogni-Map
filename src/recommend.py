"""
CogniMap recommendation pipeline.
Given a student_id already present in data/raw/, computes the 4 model features
for every branch, runs the trained Linear Regression model, and returns a
ranked list of pathway recommendations with an explanation.

Reuses the same feature logic as pathway_scoring.py (kept independent here
so this module has no side effects at import time).
"""
import json
import joblib
import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DATA_RAW = BASE / "data" / "raw"
MODELS = BASE / "models"

FEATURES = json.loads((MODELS / "cognimap_features.json").read_text())
MODEL = joblib.load(MODELS / "linear_regression_baseline.pkl")

students = pd.read_csv(DATA_RAW / "students.csv")
courses = pd.read_csv(DATA_RAW / "courses.csv")
student_course = pd.read_csv(DATA_RAW / "student_course.csv")
branches = pd.read_csv(DATA_RAW / "branches.csv")
branch_reqs = pd.read_csv(DATA_RAW / "branch_course_requirements.csv")
careers = pd.read_csv(DATA_RAW / "careers.csv")
course_skill = pd.read_csv(DATA_RAW / "course_skill.csv")

courses_idx = courses.set_index("course_id")
prereq_map = courses_idx["prerequisite_course_id"].to_dict()

_branch_required_ids = {
    b: set(branch_reqs[(branch_reqs.branch_id == b) &
                        (branch_reqs.requirement_type.isin(["Foundational", "Core"]))]["course_id"])
    for b in branches.branch_id
}
_branch_required_credits = {
    b: int(courses[courses.course_id.isin(ids)]["credits"].sum())
    for b, ids in _branch_required_ids.items()
}
_branch_required_skills = {}
for _, row in branches.iterrows():
    skills = set()
    for cname in row["associated_careers"].split("|"):
        match = careers[careers.career_name == cname]
        if len(match):
            skills |= set(match.iloc[0]["required_skills"].split("|"))
    _branch_required_skills[row["branch_id"]] = skills


def _score_features(completed_ids: set, marks_lookup: dict, student_skills: set,
                     target_branch: str, fallback_avg_marks: float) -> dict:
    """Core scoring formulas — the single source of truth. Used by both the
    existing-student (database lookup) path and the new-student (raw input) path.
    completed_ids: set of course_ids the student has completed.
    marks_lookup: {course_id: marks} for those completed courses.
    student_skills: set of skill name strings.
    fallback_avg_marks: used for academic_fit only if no relevant courses completed yet.
    """
    required_ids = _branch_required_ids[target_branch]
    required_credits = _branch_required_credits[target_branch]
    completed_relevant = completed_ids & required_ids
    earned_credits = int(courses[courses.course_id.isin(completed_relevant)]["credits"].sum())
    credit_completion_pct = round(100 * earned_credits / required_credits, 1) if required_credits else 0.0

    remaining_ids = required_ids - completed_relevant
    needed, satisfied = 0, 0
    for cid in remaining_ids:
        prereq = prereq_map.get(cid)
        if pd.isna(prereq):
            continue
        needed += 1
        if prereq in completed_ids:
            satisfied += 1
    prereq_pct = round(100 * satisfied / needed, 1) if needed else 100.0

    req_skills = _branch_required_skills[target_branch]
    skill_match_pct = round(100 * len(student_skills & req_skills) / len(req_skills), 1) if req_skills else 0.0

    relevant_marks = [marks_lookup[cid] for cid in completed_relevant if cid in marks_lookup]
    academic_fit = round(sum(relevant_marks) / len(relevant_marks), 1) if relevant_marks else round(fallback_avg_marks, 1)

    return dict(
        academic_fit=academic_fit, skill_match_pct=skill_match_pct,
        credit_completion_pct=credit_completion_pct, prerequisite_satisfaction_pct=prereq_pct,
        credits_earned=earned_credits, credits_required=required_credits,
    )


def _compute_features(student_id: str, target_branch: str) -> dict:
    """Existing-student path: looks up completed courses/marks/skills from the database."""
    row = students.set_index("student_id").loc[student_id]
    completed = student_course[(student_course.student_id == student_id) &
                                (student_course.completion_status == "Completed")]
    completed_ids = set(completed.course_id)
    marks_lookup = dict(zip(completed.course_id, completed.marks))
    student_skills = set(str(row["skills"]).split("|")) if pd.notna(row["skills"]) else set()

    return _score_features(completed_ids, marks_lookup, student_skills, target_branch,
                            fallback_avg_marks=float(row["avg_marks"]))


def _explain(feats: dict) -> str:
    """Simple explanation: name the strongest contributing factor(s)."""
    scored = {
        "strong academic performance in relevant courses": feats["academic_fit"],
        "skill alignment": feats["skill_match_pct"],
        "credit completion": feats["credit_completion_pct"],
        "prerequisite readiness": feats["prerequisite_satisfaction_pct"],
    }
    top_factor = max(scored, key=scored.get)
    return (f"Driven mainly by {top_factor} "
            f"({feats['credits_earned']}/{feats['credits_required']} relevant credits already completed).")


def recommend(student_id: str, top_n: int = 3) -> list[dict]:
    """Returns top_n branch recommendations for a student, ranked by predicted score."""
    if student_id not in set(students.student_id):
        raise ValueError(f"student_id '{student_id}' not found in data/raw/students.csv")

    results = []
    for branch_id in branches.branch_id:
        feats = _compute_features(student_id, branch_id)
        x = pd.DataFrame([[feats[f] for f in FEATURES]], columns=FEATURES)
        predicted_score = round(float(MODEL.predict(x)[0]), 1)
        results.append(dict(
            branch_id=branch_id,
            branch_name=branches.set_index("branch_id").loc[branch_id, "branch_name"],
            predicted_score=predicted_score,
            **feats,
            explanation=_explain(feats),
        ))

    results.sort(key=lambda r: r["predicted_score"], reverse=True)
    return results[:top_n]


def recommend_new_student(completed_courses: dict, skills: list, top_n: int = 3) -> list[dict]:
    """New-student path: same model, same _score_features formulas, fed from
    submitted data instead of a database row. completed_courses: {course_id: marks}.
    No fallback avg_marks available (no history), so academic_fit falls back to 0.0
    for branches where the student has completed no relevant courses."""
    completed_ids = set(completed_courses.keys())
    student_skills = set(skills)

    results = []
    for branch_id in branches.branch_id:
        feats = _score_features(completed_ids, completed_courses, student_skills, branch_id,
                                 fallback_avg_marks=0.0)
        x = pd.DataFrame([[feats[f] for f in FEATURES]], columns=FEATURES)
        predicted_score = round(float(MODEL.predict(x)[0]), 1)
        results.append(dict(
            branch_id=branch_id,
            branch_name=branches.set_index("branch_id").loc[branch_id, "branch_name"],
            predicted_score=predicted_score,
            **feats,
            explanation=_explain(feats),
        ))

    results.sort(key=lambda r: r["predicted_score"], reverse=True)
    return results[:top_n]


if __name__ == "__main__":
    sample_id = students.iloc[0]["student_id"]
    for r in recommend(sample_id):
        print(r["branch_name"], "->", r["predicted_score"], "|", r["explanation"])
