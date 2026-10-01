"""
Academic Domain Strength — additive and read-only.

Pipeline:
    student completed courses + grades
        -> courses.csv (credits)
        -> course_skill.csv (skill_name + skill_weight)
        -> skill_domain_map.csv (domain + domain_weight)
        -> grade points (reused from academic_calculations.GRADE_POINTS)
        -> normalized Academic Domain Strength (0-100) per domain

For a completed course, each of its skills contributes to one or more
domains (via skill_domain_map.csv). A course's contribution to a domain is
weighted by:
  - how strongly the course teaches that skill      (skill_weight)
  - how strongly that skill belongs to the domain    (domain_weight)
  - how many credits the course carries              (credits)
and scored by how well the student actually performed in it (grade_point,
0-10, same scale as GRADE_POINTS in academic_calculations.py).

Domain strength = (points actually earned) / (points possible if every
contributing course had been graded 'O') * 100, i.e. a credit- and
skill-relevance-weighted performance percentage, per domain.

Does not modify, import, or affect recommend.py, the model, SGPA/CGPA
calculations, or any existing scoring logic. Only reads existing
student_course.csv / courses.csv / course_skill.csv and the newly added
skill_domain_map.csv (data/raw/skill_domain_map.csv — this file did not
exist anywhere in the project and was created as part of this feature).
"""
from pathlib import Path

import pandas as pd

from academic_calculations import GRADE_POINTS  # reuse, do not redefine

DATA_RAW = Path(__file__).resolve().parent.parent / "data" / "raw"
MAX_GRADE_POINT = max(GRADE_POINTS.values())  # 10, i.e. grade "O"

_student_course = pd.read_csv(DATA_RAW / "student_course.csv")
_courses = pd.read_csv(DATA_RAW / "courses.csv")
_course_skill = pd.read_csv(DATA_RAW / "course_skill.csv")
_skill_domain_map = pd.read_csv(DATA_RAW / "skill_domain_map.csv")

ALL_DOMAINS = sorted(_skill_domain_map["domain"].unique().tolist())

# Pre-join course -> skill -> domain once (static, independent of any student)
_course_skill_domain = _course_skill.merge(_skill_domain_map, on="skill_name", how="inner")


def _completed(student_id: str) -> pd.DataFrame:
    return _student_course[
        (_student_course.student_id == student_id) &
        (_student_course.completion_status == "Completed")
    ]


def _domain_strength_from_courses(course_grades: dict) -> dict:
    """Shared core: course_grades = {course_id: grade}. Credits are always
    looked up from courses.csv, never taken from the caller, mirroring the
    pattern in academic_calculations.summarize_new_student_history."""
    earned = {d: 0.0 for d in ALL_DOMAINS}
    possible = {d: 0.0 for d in ALL_DOMAINS}
    contributing_courses = {d: set() for d in ALL_DOMAINS}

    credits_by_course = _courses.set_index("course_id")["credits"].to_dict()

    for course_id, grade in course_grades.items():
        if course_id not in credits_by_course or grade not in GRADE_POINTS:
            continue  # unknown course/grade silently skipped (defensive; callers validate upstream)

        credits = credits_by_course[course_id]
        grade_point = GRADE_POINTS[grade]

        rows = _course_skill_domain[_course_skill_domain.course_id == course_id]
        for _, row in rows.iterrows():
            weight = row["skill_weight"] * row["domain_weight"] * credits
            domain = row["domain"]
            earned[domain] += grade_point * weight
            possible[domain] += MAX_GRADE_POINT * weight
            contributing_courses[domain].add(course_id)

    strengths = {}
    for domain in ALL_DOMAINS:
        if possible[domain] > 0:
            strengths[domain] = round(100 * earned[domain] / possible[domain], 2)
        else:
            strengths[domain] = None  # no completed course touches this domain yet

    return dict(
        domain_strength=strengths,
        domain_courses_considered={d: len(c) for d, c in contributing_courses.items()},
    )


def calculate_domain_strength(student_id: str) -> dict:
    """Academic Domain Strength (0-100) per domain for an existing student,
    computed from their completed courses in student_course.csv."""
    completed = _completed(student_id)
    course_grades = dict(zip(completed.course_id, completed.grade))
    return _domain_strength_from_courses(course_grades)


def calculate_domain_strength_new_student(semesters: list[dict]) -> dict:
    """Same calculation for a new student who has no student_id / database
    row yet — fed from submitted {course_id, grade} pairs instead, mirroring
    academic_calculations.summarize_new_student_history.

    semesters: [{"semester_number": int, "courses": [{"course_id": str, "grade": str}, ...]}, ...]
    """
    course_grades = {}
    for sem in semesters:
        for c in sem["courses"]:
            course_id, grade = c["course_id"], c["grade"]
            if grade not in GRADE_POINTS:
                raise ValueError(f"Unknown grade '{grade}' for course {course_id}")
            if course_id not in _courses.course_id.values:
                raise ValueError(f"Unknown course_id '{course_id}'")
            course_grades[course_id] = grade
    return _domain_strength_from_courses(course_grades)


if __name__ == "__main__":
    sid = "S00001"
    result = calculate_domain_strength(sid)
    print(f"Academic Domain Strength — {sid}")
    for domain in ALL_DOMAINS:
        score = result["domain_strength"][domain]
        n = result["domain_courses_considered"][domain]
        label = f"{score:5.2f}" if score is not None else "  n/a"
        print(f"  {domain:<42} {label}   ({n} course(s))")
