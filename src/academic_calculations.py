"""
Academic calculations — additive and read-only.

Computes semester GPA (SGPA), cumulative GPA (CGPA), and total completed
credits from the existing student_course.csv (using its semester_taken
column) and courses.csv. Uses the exact grade-point mapping already defined
in generate.py — not a new/invented scale.

Does not modify, import, or affect recommend.py, the model, or any scoring
logic in any way.
"""
from pathlib import Path

import pandas as pd

DATA_RAW = Path(__file__).resolve().parent.parent / "data" / "raw"

# Official university grading scale, confirmed 2026-08-19.
GRADE_POINTS = {"O": 10, "A+": 9, "A": 8, "B+": 7, "B": 6, "C+": 5, "C": 4, "D+": 3, "D": 2, "F": 0}

_student_course = pd.read_csv(DATA_RAW / "student_course.csv")
_courses = pd.read_csv(DATA_RAW / "courses.csv")
_credits_by_course = _courses.set_index("course_id")["credits"].to_dict()


def _completed(student_id: str) -> pd.DataFrame:
    return _student_course[
        (_student_course.student_id == student_id) &
        (_student_course.completion_status == "Completed")
    ]


def calculate_sgpa(student_id: str) -> dict:
    """Credit-weighted GPA per semester: sum(grade_point * credits_earned) / sum(credits_earned)."""
    completed = _completed(student_id)
    sgpa = {}
    for sem, group in completed.groupby("semester_taken"):
        gp = group.grade.map(GRADE_POINTS)
        weighted = (gp * group.credits_earned).sum()
        credits = group.credits_earned.sum()
        sgpa[int(sem)] = round(weighted / credits, 2) if credits else 0.0
    return dict(sorted(sgpa.items()))


def calculate_cgpa(student_id: str) -> float:
    """Cumulative credit-weighted GPA across all completed courses (same
    formula generate.py used to produce students.csv's cgpa column)."""
    completed = _completed(student_id)
    if not len(completed):
        return 0.0
    gp = completed.grade.map(GRADE_POINTS)
    weighted = (gp * completed.credits_earned).sum()
    credits = completed.credits_earned.sum()
    return round(weighted / credits, 2) if credits else 0.0


def calculate_total_credits(student_id: str) -> int:
    """Total credits earned across all completed courses."""
    return int(_completed(student_id).credits_earned.sum())


def summarize_new_student_history(semesters: list[dict]) -> dict:
    """New-student path (no student_id / no database row yet).

    Same GRADE_POINTS map and same credit-weighted formula as
    calculate_sgpa/calculate_cgpa above — this is NOT a second GPA system,
    just fed from submitted {course_id, grade} pairs instead of a database
    lookup, mirroring how recommend.py already has both an existing-student
    and a new-student path for its own scoring.

    semesters: [{"semester_number": int, "courses": [{"course_id": str, "grade": str}, ...]}, ...]
    Credits are always looked up from courses.csv — never taken from the input.

    Returns:
      {
        "sgpa_by_semester": {semester_number: sgpa, ...},
        "cgpa": float,
        "total_credits": int,
        "semesters": [ {semester_number, sgpa, credits, courses:[{course_id, credits, grade, grade_point}]} ]
      }
    """
    sgpa_by_semester = {}
    detailed_semesters = []
    total_weighted = 0.0
    total_credits = 0

    for sem in semesters:
        sem_num = int(sem["semester_number"])
        sem_weighted = 0.0
        sem_credits = 0
        courses_detail = []

        for c in sem["courses"]:
            course_id = c["course_id"]
            grade = c["grade"]
            if grade not in GRADE_POINTS:
                raise ValueError(f"Unknown grade '{grade}' for course {course_id}")
            if course_id not in _credits_by_course:
                raise ValueError(f"Unknown course_id '{course_id}'")

            credits = int(_credits_by_course[course_id])
            grade_point = GRADE_POINTS[grade]
            sem_weighted += grade_point * credits
            sem_credits += credits
            courses_detail.append(dict(course_id=course_id, credits=credits, grade=grade, grade_point=grade_point))

        sgpa = round(sem_weighted / sem_credits, 2) if sem_credits else 0.0
        sgpa_by_semester[sem_num] = sgpa
        total_weighted += sem_weighted
        total_credits += sem_credits
        detailed_semesters.append(dict(semester_number=sem_num, sgpa=sgpa, credits=sem_credits, courses=courses_detail))

    cgpa = round(total_weighted / total_credits, 2) if total_credits else 0.0
    detailed_semesters.sort(key=lambda s: s["semester_number"])

    return dict(
        sgpa_by_semester=dict(sorted(sgpa_by_semester.items())),
        cgpa=cgpa,
        total_credits=total_credits,
        semesters=detailed_semesters,
    )


if __name__ == "__main__":
    sid = "S00001"
    print(f"Student {sid}")
    print("SGPA by semester:", calculate_sgpa(sid))
    print("CGPA:", calculate_cgpa(sid))
    print("Total completed credits:", calculate_total_credits(sid))

    # Cross-check against students.csv's existing stored cgpa/completed_credits
    students = pd.read_csv(DATA_RAW / "students.csv")
    row = students.set_index("student_id").loc[sid]
    print()
    print("students.csv stored cgpa:", row["cgpa"], "| computed:", calculate_cgpa(sid))
    print("students.csv stored completed_credits:", row["completed_credits"],
          "| computed:", calculate_total_credits(sid))
