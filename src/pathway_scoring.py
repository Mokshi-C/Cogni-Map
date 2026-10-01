"""
CogniMap — Credit-aware Pathway Compatibility Scoring (reference implementation)

Computes, for a given student and a given TARGET branch (which may or may not be
their current branch), four component scores and a weighted composite:

  1. Academic Fit        - how well the student's marks-in-relevant-courses compare
                            to the target branch's requirements
  2. Skill Match          - overlap between student's derived skills and the
                            target branch's associated career skill requirements
  3. Credit Completion %  - completed relevant credits / total required credits
  4. Prerequisite Satisfaction % - fraction of prerequisites-for-remaining-courses
                            that are already completed

Composite = 0.35*Academic Fit + 0.20*Skill Match + 0.25*Credit Completion
            + 0.20*Prerequisite Satisfaction

Weights are a documented starting point, not derived from data -- tune them
via the qualitative validation step described in the roadmap (Phase 7).
"""
import pandas as pd

DATA = "/home/claude/cognimap_data"
students = pd.read_csv(f"{DATA}/students.csv")
courses = pd.read_csv(f"{DATA}/courses.csv")
student_course = pd.read_csv(f"{DATA}/student_course.csv")
branches = pd.read_csv(f"{DATA}/branches.csv")
branch_reqs = pd.read_csv(f"{DATA}/branch_course_requirements.csv")
course_skill = pd.read_csv(f"{DATA}/course_skill.csv")
careers = pd.read_csv(f"{DATA}/careers.csv")

courses_idx = courses.set_index("course_id")


def credit_completion_pct(student_id, target_branch):
    req = branch_reqs[(branch_reqs.branch_id == target_branch) &
                       (branch_reqs.requirement_type.isin(["Foundational", "Core"]))]
    required_ids = set(req.course_id)
    required_credits = courses_idx.loc[list(required_ids), "credits"].sum()

    completed = student_course[(student_course.student_id == student_id) &
                                (student_course.completion_status == "Completed")]
    completed_relevant = completed[completed.course_id.isin(required_ids)]
    earned_credits = completed_relevant.credits_earned.sum()

    pct = round(100 * earned_credits / required_credits, 1) if required_credits else 0.0
    remaining_ids = required_ids - set(completed_relevant.course_id)
    return pct, earned_credits, required_credits, remaining_ids


def prerequisite_satisfaction_pct(student_id, remaining_course_ids):
    if not remaining_course_ids:
        return 100.0
    completed_ids = set(student_course[(student_course.student_id == student_id) &
                                        (student_course.completion_status == "Completed")].course_id)
    needed_prereqs, satisfied = 0, 0
    for cid in remaining_course_ids:
        prereq = courses_idx.loc[cid, "prerequisite_course_id"]
        if pd.isna(prereq):
            continue
        needed_prereqs += 1
        if prereq in completed_ids:
            satisfied += 1
    if needed_prereqs == 0:
        return 100.0
    return round(100 * satisfied / needed_prereqs, 1)


def skill_match_pct(student_id, target_branch):
    student_skills = set(str(students.set_index("student_id").loc[student_id, "skills"]).split("|"))
    branch_career_names = branches.set_index("branch_id").loc[target_branch, "associated_careers"].split("|")
    required_skills = set()
    for cname in branch_career_names:
        row = careers[careers.career_name == cname]
        if len(row):
            required_skills |= set(row.iloc[0]["required_skills"].split("|"))
    if not required_skills:
        return 0.0
    overlap = student_skills & required_skills
    return round(100 * len(overlap) / len(required_skills), 1)


def academic_fit_score(student_id, target_branch, remaining_ids_reference=None):
    """Average marks in courses relevant to the target branch that the student
    has already taken (foundational + any target-branch core already completed),
    normalized to 0-100. Falls back to overall avg_marks if no relevant courses taken."""
    req = branch_reqs[(branch_reqs.branch_id == target_branch) &
                       (branch_reqs.requirement_type.isin(["Foundational", "Core"]))]
    required_ids = set(req.course_id)
    taken = student_course[(student_course.student_id == student_id) &
                            (student_course.course_id.isin(required_ids)) &
                            (student_course.completion_status == "Completed")]
    if len(taken):
        return round(taken.marks.mean(), 1)
    return float(students.set_index("student_id").loc[student_id, "avg_marks"])


def pathway_compatibility(student_id, target_branch,
                           w_academic=0.35, w_skill=0.20, w_credit=0.25, w_prereq=0.20):
    credit_pct, earned, required, remaining_ids = credit_completion_pct(student_id, target_branch)
    prereq_pct = prerequisite_satisfaction_pct(student_id, remaining_ids)
    skill_pct = skill_match_pct(student_id, target_branch)
    academic = academic_fit_score(student_id, target_branch)

    composite = (w_academic * academic + w_skill * skill_pct +
                 w_credit * credit_pct + w_prereq * prereq_pct)

    return dict(
        student_id=student_id, target_branch=target_branch,
        academic_fit=academic, skill_match_pct=skill_pct,
        credit_completion_pct=credit_pct, credits_earned=int(earned), credits_required=int(required),
        prerequisite_satisfaction_pct=prereq_pct,
        remaining_courses=len(remaining_ids),
        pathway_compatibility_score=round(composite, 1),
    )


if __name__ == "__main__":
    # Worked example: an AIDS student evaluated against AIML as a target pathway
    sample = students[(students.current_branch == "AIDS") & (students.semester >= 6)].iloc[0]
    sid = sample.student_id
    print(f"Student {sid} | current branch: {sample.current_branch} | semester {sample.semester} | "
          f"CGPA {sample.cgpa}\n")

    for target in ["AIDS", "AIML", "CYSEC"]:
        result = pathway_compatibility(sid, target)
        print(f"--- Target pathway: {target} ---")
        for k, v in result.items():
            print(f"  {k}: {v}")
        print()
