"""Minimal API layer. Wraps src/recommend.py — no ML/scoring logic here."""
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from recommend import recommend, recommend_new_student, students, courses, course_skill, branches  # noqa: E402
from academic_calculations import summarize_new_student_history  # noqa: E402
from personalized_scoring import get_hybrid_recommendation  # noqa: E402

app = FastAPI(title="CogniMap AI API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.get("/students")
def list_students():
    return students[["student_id", "name", "current_branch", "semester", "cgpa"]].to_dict(orient="records")


@app.get("/recommend/{student_id}")
def get_recommendations(student_id: str, top_n: int = 3):
    try:
        recs = get_hybrid_recommendation(student_id, completed_courses={}, skills=[])
        return recs[:top_n]
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/courses")
def list_courses():
    return courses[["course_id", "course_name", "credits", "semester"]].to_dict(orient="records")


@app.get("/skills")
def list_skills():
    return sorted(course_skill["skill_name"].unique().tolist())


@app.get("/branches")
def list_branches():
    return branches[["branch_id", "branch_name"]].to_dict(orient="records")


class HistoryCourse(BaseModel):
    course_id: str
    grade: str


class HistorySemester(BaseModel):
    semester_number: int
    courses: list[HistoryCourse]


class AcademicHistoryRequest(BaseModel):
    semesters: list[HistorySemester]


@app.post("/academic-history/summary")
def academic_history_summary(payload: AcademicHistoryRequest):
    """New-student SGPA/CGPA/credit summary. Reuses academic_calculations.py's
    GRADE_POINTS + formula — no separate GPA logic here."""
    try:
        semesters = [s.model_dump() for s in payload.semesters]
        return summarize_new_student_history(semesters)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


class CompletedCourse(BaseModel):
    course_id: str
    marks: float


class NewStudentProfile(BaseModel):
    completed_courses: list[CompletedCourse]
    skills: list[str]
    skill_proficiency: dict[str, str] = {}
    interests: dict = {}
    career_goals: list[str] = []
    pg_preference: str = "Undecided"
    top_n: int = 3


@app.post("/recommend/new")
def recommend_new(profile: NewStudentProfile):
    completed = {c.course_id: c.marks for c in profile.completed_courses}
    recs = get_hybrid_recommendation(
        student_id="",
        completed_courses=completed,
        skills=profile.skills,
        skill_proficiency=profile.skill_proficiency,
        interests=profile.interests,
        career_goals=profile.career_goals,
        pg_preference=profile.pg_preference
    )
    return recs[:profile.top_n]
