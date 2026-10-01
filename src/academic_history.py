"""
Academic history query layer — additive and read-only.

Provides the Student -> Semester -> Course -> Grade view by joining the
existing student_course.csv (with its new semester_taken column) against
courses.csv. Does not modify, import, or affect recommend.py, the model,
or any scoring logic in any way.
"""
from pathlib import Path

import pandas as pd

DATA_RAW = Path(__file__).resolve().parent.parent / "data" / "raw"

_student_course = pd.read_csv(DATA_RAW / "student_course.csv")
_courses = pd.read_csv(DATA_RAW / "courses.csv")


def get_academic_history(student_id: str) -> dict:
    """Returns {semester: [ {course_id, course_name, credits, grade}, ... ]}
    for every course the student has a record for (completed or failed)."""
    rows = _student_course[_student_course.student_id == student_id].merge(
        _courses[["course_id", "course_name", "credits"]], on="course_id", how="left"
    )

    history = {}
    for _, row in rows.sort_values(["semester_taken", "course_id"]).iterrows():
        sem = int(row["semester_taken"])
        history.setdefault(sem, []).append(dict(
            course_id=row["course_id"],
            course_name=row["course_name"],
            credits=int(row["credits"]),
            grade=row["grade"],
        ))
    return history


if __name__ == "__main__":
    history = get_academic_history("S00001")
    for sem in sorted(history):
        print(f"Semester {sem}:")
        for c in history[sem]:
            print(f"  {c['course_id']} — {c['course_name']} ({c['credits']} cr) — Grade: {c['grade']}")
