import json
import joblib
import pandas as pd
import numpy as np
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DATA_RAW = BASE / "data" / "raw"
MODELS = BASE / "models"

# Load references
students = pd.read_csv(DATA_RAW / "students.csv")
courses = pd.read_csv(DATA_RAW / "courses.csv")
student_course = pd.read_csv(DATA_RAW / "student_course.csv")
branches = pd.read_csv(DATA_RAW / "branches.csv")
branch_reqs = pd.read_csv(DATA_RAW / "branch_course_requirements.csv")
careers = pd.read_csv(DATA_RAW / "careers.csv")
course_skill = pd.read_csv(DATA_RAW / "course_skill.csv")
skill_domain_map = pd.read_csv(DATA_RAW / "skill_domain_map.csv")

# Dynamic mappings
courses_idx = courses.set_index("course_id")
prereq_map = courses_idx["prerequisite_course_id"].to_dict()

# Extract course skills map
_course_skills_dict = {}
for _, row in course_skill.iterrows():
    _course_skills_dict.setdefault(row["course_id"], set()).add(row["skill_name"])

# Load model
RF_MODEL = joblib.load(MODELS / "random_forest_pathway_model.joblib")
RF_FEATURES = json.loads((MODELS / "random_forest_features.json").read_text())

# Weights configuration
ML_WEIGHT = 0.70
CAREER_WEIGHT = 0.10
INTEREST_WEIGHT = 0.10
PROFICIENCY_WEIGHT = 0.10

# PG Alignments
PG_ALIGNMENTS = {
    "M.Tech": {"CSE", "AIML", "IOT"},
    "M.E.": {"CSE", "AIML", "IOT"},
    "M.Sc.": {"AIDS", "AIML", "CSBS"},
    "MS": {"CSE", "AIML", "CYSEC", "IOT"}
}

BRANCH_TO_DOMAINS = {
    "CSE": ["Programming", "AI / Machine Learning", "Operating Systems / Systems", "Software Engineering"],
    "AIML": ["AI / Machine Learning", "Statistics", "Mathematics"],
    "AIDS": ["Data Science", "Statistics", "AI / Machine Learning"],
    "IT": ["Computer Networks", "Database Systems", "Software Engineering", "Cloud / Distributed Systems"],
    "CYSEC": ["Cybersecurity", "Computer Networks", "Operating Systems / Systems"],
    "CSBS": ["Data Science", "Software Engineering"],
    "IOT": ["Operating Systems / Systems", "Computer Networks", "Cloud / Distributed Systems"]
}

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

# Cache student strengths
import domain_strength as ds

def get_hybrid_recommendation(student_id: str, completed_courses: dict, skills: list, 
                               skill_proficiency: dict = None, interests: dict = None, 
                               career_goals: list = None, pg_preference: str = None) -> list[dict]:
    """
    Computes hybrid scores for all 7 branch pathways.
    """
    skill_proficiency = skill_proficiency or {}
    interests = interests or {}
    career_goals = career_goals or []
    pg_preference = pg_preference or "Undecided"

    results = []

    # Get student domain strengths
    if student_id and student_id in students.student_id.values:
        strengths = ds.calculate_domain_strength(student_id)["domain_strength"]
        fallback_avg = float(students.set_index("student_id").loc[student_id, "avg_marks"])
        completed_ids = set(student_course[(student_course.student_id == student_id) & 
                                           (student_course.completion_status == "Completed")].course_id)
        marks_lookup = dict(zip(student_course[student_course.student_id == student_id].course_id, 
                                student_course[student_course.student_id == student_id].marks))
        student_skills = set(str(students.set_index("student_id").loc[student_id, "skills"]).split("|"))
    else:
        # New student
        semesters_input = [{"semester_number": 1, "courses": [{"course_id": cid, "grade": "O"} for cid in completed_courses.keys()]}]
        strengths = ds.calculate_domain_strength_new_student(semesters_input)["domain_strength"]
        fallback_avg = 0.0
        completed_ids = set(completed_courses.keys())
        marks_lookup = completed_courses
        student_skills = set(skills)

    for branch_id in branches.branch_id:
        # 1. Base ML Features
        required_ids = _branch_required_ids[branch_id]
        required_credits = _branch_required_credits[branch_id]
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

        req_skills = _branch_required_skills[branch_id]
        skill_match_pct = round(100 * len(student_skills & req_skills) / len(req_skills), 1) if req_skills else 0.0

        relevant_marks = [marks_lookup[cid] for cid in completed_relevant if cid in marks_lookup]
        academic_fit = round(sum(relevant_marks) / len(relevant_marks), 1) if relevant_marks else round(fallback_avg, 1)

        relevant_domains = BRANCH_TO_DOMAINS.get(branch_id, [])
        vals = [strengths[d] for d in relevant_domains if d in strengths and strengths[d] is not None]
        candidate_domain_strength_avg = round(np.mean(vals), 1) if vals else 0.0

        # Predict ML base score
        x = pd.DataFrame([[academic_fit, credit_completion_pct, prereq_pct, candidate_domain_strength_avg, skill_match_pct]], 
                         columns=RF_FEATURES)
        ml_base_score = np.clip(round(float(RF_MODEL.predict(x)[0]), 1), 0.0, 100.0)

        # 2. Career Alignment
        if career_goals:
            career_alignments = []
            for cg in career_goals:
                match = careers[careers.career_name == cg]
                if len(match):
                    req_skills_c = set(match.iloc[0]["required_skills"].split("|"))
                    branch_skills = _branch_required_skills[branch_id]
                    overlap = req_skills_c & branch_skills
                    ratio = len(overlap) / len(req_skills_c) if req_skills_c else 0.0
                    career_alignments.append(ratio * 100.0)
            career_alignment = round(np.mean(career_alignments), 1) if career_alignments else ml_base_score
        else:
            career_alignment = ml_base_score

        # 3. Interest Alignment
        if interests:
            interest_overlap_scores = []
            for domain, data in interests.items():
                level = data.get("level", "Medium")
                level_weight = {"High": 1.0, "Medium": 0.6, "Low": 0.2}.get(level, 0.6)
                
                subtopics = data.get("subtopics", [])
                for subtopic in subtopics:
                    branch_courses = _branch_required_ids[branch_id]
                    matched = False
                    for cid in branch_courses:
                        course_name = courses_idx.loc[cid, "course_name"]
                        if subtopic.lower() == course_name.lower():
                            matched = True
                            break
                        if cid in _course_skills_dict and subtopic in _course_skills_dict[cid]:
                            matched = True
                            break
                    if matched:
                        interest_overlap_scores.append(level_weight * 10.0)
            
            total_subtopics = sum(len(d.get("subtopics", [])) for d in interests.values())
            if total_subtopics > 0:
                interest_alignment = min(100.0, round(10.0 * sum(interest_overlap_scores) / total_subtopics, 1))
            else:
                interest_alignment = ml_base_score
        else:
            interest_alignment = ml_base_score

        # 4. Skill Proficiency Match
        if skill_proficiency:
            proficiency_score = 0.0
            req_skills = _branch_required_skills[branch_id]
            for sk, lvl in skill_proficiency.items():
                if sk in req_skills:
                    weight = {"Advanced": 1.0, "Intermediate": 0.6, "Beginner": 0.3}.get(lvl, 0.3)
                    proficiency_score += weight
            skill_proficiency_match = round(100.0 * proficiency_score / len(req_skills), 1) if req_skills else ml_base_score
        else:
            skill_proficiency_match = ml_base_score

        # 5. PG Preference Tie-breaker
        aligned_branches = PG_ALIGNMENTS.get(pg_preference, set())
        pg_adjustment = 1.5 if branch_id in aligned_branches else 0.0

        # Calculate final hybrid score
        final_score = round(
            ML_WEIGHT * ml_base_score +
            CAREER_WEIGHT * career_alignment +
            INTEREST_WEIGHT * interest_alignment +
            PROFICIENCY_WEIGHT * skill_proficiency_match +
            pg_adjustment,
            1
        )
        final_score = np.clip(final_score, 0.0, 100.0)

        # Generate deterministic explanation
        strongest_factors = []
        if ml_base_score > 75:
            strongest_factors.append("solid academic core")
        if career_alignment > 75:
            strongest_factors.append("strong career goal match")
        if interest_alignment > 75:
            strongest_factors.append("high subject interest alignment")
        
        factor_str = " and ".join(strongest_factors) if strongest_factors else "academic capability"
        explanation = f"Recommended based on {factor_str} ({earned_credits}/{required_credits} relevant credits completed)."

        results.append({
            "branch_id": branch_id,
            "branch_name": branches.set_index("branch_id").loc[branch_id, "branch_name"],
            "predicted_score": final_score,
            "ml_base_score": ml_base_score,
            "career_alignment": career_alignment,
            "interest_alignment": interest_alignment,
            "skill_proficiency_match": skill_proficiency_match,
            "pg_adjustment": pg_adjustment,
            "final_score": final_score,
            "academic_fit": academic_fit,
            "skill_match_pct": skill_match_pct,
            "credit_completion_pct": credit_completion_pct,
            "prerequisite_satisfaction_pct": prereq_pct,
            "credits_earned": earned_credits,
            "credits_required": required_credits,
            "explanation": explanation,
            "domain_strengths": strengths
        })

    results.sort(key=lambda r: r["final_score"], reverse=True)
    return results
