"""
CogniMap synthetic dataset generator.
Produces 7 linked CSV tables with logically-consistent (non-random) relationships:
  branches.csv, courses.csv, branch_course_requirements.csv, course_skill.csv,
  careers.csv, students.csv, student_course.csv
"""
import random
import numpy as np
import pandas as pd
from reference_data import BRANCHES, BRANCH_IDS, SKILLS, COMMON_CORE, BRANCH_COURSES, CAREERS

random.seed(42)
np.random.seed(42)

N_STUDENTS = 2000

# ---------------------------------------------------------------------------
# 1. COURSES + BRANCH_COURSE_REQUIREMENTS
# ---------------------------------------------------------------------------
courses = []
course_name_to_id = {}
branch_reqs = []  # (branch_id, course_id, requirement_type)

def add_course(name, credits, semester, prereq_name, skills, difficulty, category):
    if name in course_name_to_id:
        return course_name_to_id[name]
    cid = f"C{len(courses)+1:04d}"
    course_name_to_id[name] = cid
    courses.append(dict(
        course_id=cid, course_name=name, credits=credits, semester=semester,
        prerequisite_course_id=None,  # filled in second pass
        prerequisite_course_name=prereq_name,
        course_category=category, difficulty=difficulty,
    ))
    return cid

# Common core -> required for every branch as "Foundational"
for name, credits, sem, prereq, skills, diff in COMMON_CORE:
    cid = add_course(name, credits, sem, prereq, skills, diff, "Foundational")
    for b in BRANCH_IDS:
        branch_reqs.append((b, cid, "Foundational"))
    globals().setdefault("_course_skills", []).extend([(cid, s) for s in skills])

# Branch-specific
for branch_id, clist in BRANCH_COURSES.items():
    for name, credits, sem, prereq, skills, diff, req_type in clist:
        cid = add_course(name, credits, sem, prereq, skills, diff,
                          "Branch-Core" if req_type == "core" else "Elective")
        branch_reqs.append((branch_id, cid, "Core" if req_type == "core" else "Elective"))
        globals()["_course_skills"].extend([(cid, s) for s in skills])

# resolve prerequisite names -> ids
for c in courses:
    pname = c.pop("prerequisite_course_name")
    c["prerequisite_course_id"] = course_name_to_id.get(pname) if pname else None

courses_df = pd.DataFrame(courses)
branch_reqs_df = pd.DataFrame(branch_reqs, columns=["branch_id", "course_id", "requirement_type"]).drop_duplicates()

# ---------------------------------------------------------------------------
# 2. COURSE_SKILL
# ---------------------------------------------------------------------------
course_skill_rows = []
seen = set()
for cid, skill in globals()["_course_skills"]:
    key = (cid, skill)
    if key in seen:
        continue
    seen.add(key)
    course_skill_rows.append(dict(course_id=cid, skill_name=skill,
                                   skill_weight=round(random.uniform(0.5, 1.0), 2)))
course_skill_df = pd.DataFrame(course_skill_rows)

# ---------------------------------------------------------------------------
# 3. BRANCHES (with required_credits computed from Foundational+Core requirement rows)
# ---------------------------------------------------------------------------
branches_out = []
for b in BRANCHES:
    req_course_ids = branch_reqs_df[(branch_reqs_df.branch_id == b["branch_id"]) &
                                     (branch_reqs_df.requirement_type.isin(["Foundational", "Core"]))]["course_id"]
    req_credits = courses_df[courses_df.course_id.isin(req_course_ids)]["credits"].sum()
    elective_ids = branch_reqs_df[(branch_reqs_df.branch_id == b["branch_id"]) &
                                   (branch_reqs_df.requirement_type == "Elective")]["course_id"]
    assoc_careers = [c["career_name"] for c in CAREERS if b["branch_id"] in c["related_specializations"]]
    branches_out.append(dict(
        branch_id=b["branch_id"], branch_name=b["branch_name"], description=b["description"],
        core_domains=b["core_domains"],
        required_credits=int(req_credits),
        required_course_ids="|".join(sorted(req_course_ids)),
        elective_course_ids="|".join(sorted(elective_ids)),
        min_elective_credits=6,
        associated_careers="|".join(assoc_careers),
    ))
branches_df = pd.DataFrame(branches_out)

# ---------------------------------------------------------------------------
# 4. CAREERS
# ---------------------------------------------------------------------------
careers_out = []
for i, c in enumerate(CAREERS, start=1):
    preferred_course_ids = course_skill_df[course_skill_df.skill_name.isin(c["required_skills"])]["course_id"].unique()
    careers_out.append(dict(
        career_id=f"CR{i:03d}", career_name=c["career_name"],
        required_skills="|".join(c["required_skills"]),
        preferred_course_ids="|".join(sorted(preferred_course_ids)[:8]),
        related_specializations="|".join(c["related_specializations"]),
        demand_score=c["demand_score"],
    ))
careers_df = pd.DataFrame(careers_out)

# ---------------------------------------------------------------------------
# 5. STUDENTS  (with branch-correlated skills/interests/CGPA — generated AFTER
#    student_course so CGPA/credits reflect actual course performance)
# ---------------------------------------------------------------------------
FIRST_NAMES = ["Aditi","Arjun","Kavya","Rohan","Sneha","Vikram","Ananya","Karthik","Priya","Suresh",
               "Divya","Rahul","Meera","Sanjay","Pooja","Aravind","Nisha","Vivek","Lakshmi","Manoj",
               "Deepa","Kiran","Swathi","Naveen","Ritu","Harish","Anjali","Gokul","Shreya","Prakash"]
LAST_NAMES = ["Kumar","Sharma","Reddy","Iyer","Nair","Gupta","Menon","Rao","Patel","Krishnan",
              "Pillai","Varma","Chandran","Mehta","Subramaniam","Das","Bose","Singh","Verma","Raman"]

branch_weights = {"CSE": 0.22, "AIML": 0.20, "AIDS": 0.15, "IT": 0.16,
                   "CYSEC": 0.12, "CSBS": 0.08, "IOT": 0.07}

students = []
for i in range(1, N_STUDENTS + 1):
    sid = f"S{i:05d}"
    branch = np.random.choice(list(branch_weights.keys()), p=list(branch_weights.values()))
    semester = int(np.random.choice(range(3, 9), p=[0.22,0.20,0.16,0.14,0.14,0.14]))  # weighted toward mid-program
    gender = random.choice(["Male", "Female"])
    age = 17 + (semester + 1) // 2 + random.choice([0, 0, 1])
    # latent "academic aptitude" drives marks generation later; keep here for interest/skill correlation
    aptitude = np.clip(np.random.normal(70, 12), 35, 98)
    students.append(dict(
        student_id=sid, name=f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
        gender=gender, age=int(age), current_branch=branch, semester=semester,
        _aptitude=aptitude,
    ))
students_df = pd.DataFrame(students)

# ---------------------------------------------------------------------------
# 6. STUDENT_COURSE
#    For each student: enroll in every Foundational/Core course whose semester
#    <= student's current semester - 1 (i.e., already offered), plus a couple
#    of electives. Marks correlate with the student's aptitude AND a branch-fit
#    bonus (higher marks in courses matching their declared branch).
# ---------------------------------------------------------------------------
courses_df["semester"] = courses_df["semester"].astype(int)
branch_course_set = {b: set(branch_reqs_df[branch_reqs_df.branch_id == b]["course_id"])
                      for b in BRANCH_IDS}

def grade_from_marks(m):
    if m >= 90: return "A+"
    if m >= 80: return "A"
    if m >= 70: return "B+"
    if m >= 60: return "B"
    if m >= 50: return "C"
    if m >= 40: return "D"
    return "F"

student_course_rows = []
for _, s in students_df.iterrows():
    sid, branch, sem, aptitude = s.student_id, s.current_branch, s.semester, s._aptitude
    own_reqs = branch_course_set[branch]
    # eligible courses: offered at or before (semester - 1), i.e. already completed terms
    eligible = courses_df[courses_df.semester <= max(sem - 1, 1)]
    for _, c in eligible.iterrows():
        cid = c.course_id
        is_own_branch_relevant = cid in own_reqs
        # not every eligible course is necessarily taken (electives selective; some foundational skipped rarely)
        take_prob = 0.97 if c.course_category == "Foundational" else (0.9 if is_own_branch_relevant else 0.15)
        if random.random() > take_prob:
            continue
        base = aptitude + (6 if is_own_branch_relevant else 0) - (c.difficulty - 3) * 3
        marks = np.clip(np.random.normal(base, 8), 25, 100)
        completion_status = "Completed" if marks >= 40 else "Failed"
        credits_earned = c.credits if completion_status == "Completed" else 0
        student_course_rows.append(dict(
            student_id=sid, course_id=cid, marks=round(float(marks), 1),
            grade=grade_from_marks(marks), credits_attempted=c.credits,
            credits_earned=credits_earned, completion_status=completion_status,
        ))

student_course_df = pd.DataFrame(student_course_rows)

# ---------------------------------------------------------------------------
# 7. Finish STUDENTS: compute CGPA, completed_credits, skills, interests,
#    projects, certifications, career_interest, preferred_specialization,
#    learning_preference — all correlated with actual course performance.
# ---------------------------------------------------------------------------
GRADE_POINTS = {"O": 10, "A+": 9, "A": 8, "B+": 7, "B": 6, "C+": 5, "C": 4, "D+": 3, "D": 2, "F": 0}
PROJECTS_BY_DOMAIN = {
    "CSE": ["E-commerce Web App", "Compiler Mini-Project", "OS Scheduler Simulation"],
    "AIML": ["Image Classification Model", "Chatbot using Transformers", "Sentiment Analysis Tool"],
    "AIDS": ["Sales Forecasting Dashboard", "Customer Segmentation Analysis", "ETL Pipeline for Retail Data"],
    "IT": ["Cloud-hosted Inventory System", "Network Monitoring Tool", "Enterprise CRM App"],
    "CYSEC": ["Vulnerability Scanner", "Phishing Detection Tool", "Secure File Sharing System"],
    "CSBS": ["ERP Dashboard for SMEs", "Business Analytics Report Tool", "Market Trend Predictor"],
    "IOT": ["Smart Home Automation", "Weather Monitoring IoT Node", "Wearable Health Tracker"],
}
LEARNING_PREFS = ["Project-based", "Theory-focused", "Hands-on Labs", "Self-paced Online", "Mentor-guided"]
CERT_POOL = {
    "AIML": ["TensorFlow Developer Certificate", "Deep Learning Specialization"],
    "AIDS": ["Google Data Analytics Certificate", "IBM Data Science Certificate"],
    "IT": ["AWS Cloud Practitioner", "CompTIA Network+"],
    "CYSEC": ["Certified Ethical Hacker (CEH) - Foundation", "CompTIA Security+"],
    "CSE": ["Java Programming Certificate", "DSA Specialization"],
    "CSBS": ["Google Business Analytics Certificate", "PMP Foundation"],
    "IOT": ["Embedded Systems Certificate", "IoT Fundamentals (Cisco)"],
}
sc_by_student = student_course_df.groupby("student_id")

final_students = []
for _, s in students_df.iterrows():
    sid, branch, sem, aptitude = s.student_id, s.current_branch, s.semester, s._aptitude
    if sid in sc_by_student.groups:
        g = sc_by_student.get_group(sid)
        completed = g[g.completion_status == "Completed"]
        total_earned = int(completed.credits_earned.sum())
        gp = completed.grade.map(GRADE_POINTS)
        cgpa = round(float((gp * completed.credits_earned).sum() / max(completed.credits_earned.sum(), 1)), 2) if len(completed) else 0.0
        avg_marks = round(float(completed.marks.mean()), 1) if len(completed) else 0.0
    else:
        total_earned, cgpa, avg_marks = 0, 0.0, 0.0

    # skills self-reported: derived from courses actually completed (via course_skill),
    # NOT from branch label directly -> avoids the "domain==target" leakage seen earlier
    if sid in sc_by_student.groups:
        completed_ids = set(sc_by_student.get_group(sid).query("completion_status=='Completed'")["course_id"])
    else:
        completed_ids = set()
    derived_skills = sorted(set(course_skill_df[course_skill_df.course_id.isin(completed_ids)]["skill_name"]))
    # student self-reports a noisy subset (not perfect self-awareness) of derived skills, occasionally +1 unrelated skill
    reported_skills = [sk for sk in derived_skills if random.random() < 0.8]
    if random.random() < 0.15 and len(SKILLS) > 0:
        extra = random.choice(SKILLS)
        if extra not in reported_skills:
            reported_skills.append(extra)
    if not reported_skills:
        reported_skills = random.sample(SKILLS, k=2)

    prog_langs = [s for s in reported_skills if s in ("Python", "Java", "C++", "C", "JavaScript")]
    if not prog_langs:
        prog_langs = [random.choice(["Python", "Java", "C++"])]

    # interest: mostly aligned with branch domain, but with real noise (not deterministic)
    domain_pool = [d.strip() for b in BRANCHES if b["branch_id"] == branch for d in b["core_domains"].split("|")]
    other_domains = [d.strip() for b in BRANCHES for d in b["core_domains"].split("|") if b["branch_id"] != branch]
    if random.random() < 0.75:
        interest = random.choice(domain_pool)
    else:
        interest = random.choice(other_domains)  # genuine cross-domain interest, not just branch label

    # career interest: correlated with branch's associated careers but ~20% explore other branches' careers
    branch_careers = [c["career_name"] for c in CAREERS if branch in c["related_specializations"]]
    other_careers = [c["career_name"] for c in CAREERS if branch not in c["related_specializations"]]
    career_interest = random.choice(branch_careers) if random.random() < 0.8 else random.choice(other_careers)

    preferred_spec = branch if random.random() < 0.85 else random.choice([b for b in BRANCH_IDS if b != branch])

    n_certs = np.random.choice([0, 1, 2], p=[0.5, 0.35, 0.15])
    certs = "|".join(random.sample(CERT_POOL.get(branch, []), k=min(n_certs, len(CERT_POOL.get(branch, [])))))
    n_proj = np.random.choice([0, 1, 2, 3], p=[0.15, 0.35, 0.35, 0.15])
    projects = "|".join(random.sample(PROJECTS_BY_DOMAIN.get(branch, []), k=min(n_proj, len(PROJECTS_BY_DOMAIN.get(branch, [])))))

    final_students.append(dict(
        student_id=sid, name=s["name"], gender=s.gender, age=s.age,
        current_branch=branch, semester=sem, cgpa=cgpa, avg_marks=avg_marks,
        completed_credits=total_earned,
        skills="|".join(reported_skills), programming_languages="|".join(sorted(set(prog_langs))),
        interests=interest, preferred_domain=interest,
        project_experience=projects, certifications=certs,
        career_interest=career_interest, preferred_specialization=preferred_spec,
        learning_preference=random.choice(LEARNING_PREFS),
    ))

students_final_df = pd.DataFrame(final_students)

# ---------------------------------------------------------------------------
# SAVE
# ---------------------------------------------------------------------------
out = "/home/claude/cognimap_data"
branches_df.to_csv(f"{out}/branches.csv", index=False)
courses_df.to_csv(f"{out}/courses.csv", index=False)
branch_reqs_df.to_csv(f"{out}/branch_course_requirements.csv", index=False)
course_skill_df.to_csv(f"{out}/course_skill.csv", index=False)
careers_df.to_csv(f"{out}/careers.csv", index=False)
students_final_df.to_csv(f"{out}/students.csv", index=False)
student_course_df.to_csv(f"{out}/student_course.csv", index=False)

print("Branches:", branches_df.shape)
print("Courses:", courses_df.shape)
print("Branch-Course Requirements:", branch_reqs_df.shape)
print("Course-Skill:", course_skill_df.shape)
print("Careers:", careers_df.shape)
print("Students:", students_final_df.shape)
print("Student-Course:", student_course_df.shape)
