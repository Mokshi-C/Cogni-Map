# CogniMap — Dataset Architecture & Credit-Aware Recommendation Design

## 1. Overview

Seven linked tables model a realistic academic ecosystem across 7 CSE-allied
specializations (CSE, AIML, AIDS, IT, Cyber Security, CSBS, IoT & Embedded
Systems). All relationships are **logically constructed, not randomly assigned**:
branch-relevant courses genuinely correlate with branch-relevant skills and
careers, prerequisite chains are real and semester-consistent, and several
courses are **deliberately shared across branches** (e.g. "Introduction to
Machine Learning" is Core for AIML, Core for AIDS, and Elective for CSBS) so
that credit-overlap logic has real cases to work with — this was the whole
point of the pivot away from the public Kaggle datasets, which had either no
signal or fake deterministic signal (see Section 6).

**Scale generated:** 2,000 students · 59 courses · 7 branches · 29 careers ·
148 branch-course requirement links · 109 course-skill mappings · 27,923
student-course enrollment records.

## 2. Entity-Relationship Structure

```
BRANCHES (1) ──< BRANCH_COURSE_REQUIREMENTS >── (1) COURSES
   │                                                  │
   │                                                  ├──< COURSE_SKILL >── SKILLS (taxonomy, not a table)
   │                                                  │
   │                                                  └──< STUDENT_COURSE >── (1) STUDENTS
   │                                                                              │
   └──< associated_careers (text list) >── CAREERS ──< required_skills ──────────┘
                                              (also required_skills ~ skills taxonomy)
```

- **BRANCHES → COURSES**: many-to-many, via `BRANCH_COURSE_REQUIREMENTS`
  (a course can be Foundational/Core for one branch and Elective — or absent
  — for another; this junction table is what makes the design "credit-aware,"
  since it's what lets CogniMap recognize a completed course as relevant to a
  *different* branch than the student's current one).
- **COURSES → STUDENT_COURSE**: one-to-many (each enrollment record ties one
  student to one course, with grade/marks/credit outcome).
- **COURSES → COURSE_SKILL**: one-to-many (each course teaches multiple
  skills, each with a weight).
- **CAREERS**: references skills (text list, matched against the skill
  taxonomy) and branches (`related_specializations`), and cross-references
  `preferred_course_ids` computed from courses that teach its required skills.
- **STUDENTS**: `skills`, `certifications`, `career_interest`, and
  `preferred_specialization` are all **derived with realistic noise** from
  actual completed coursework, not copied from `current_branch` — this is
  the specific fix for the leakage pattern found in the earlier Kaggle
  dataset (where "Interested Domain" was a near-exact paraphrase of the
  target).

## 3. Full Schema

### 3.1 `branches.csv` (7 rows)
| Column | Type | Description |
|---|---|---|
| branch_id | str | Primary key, e.g. `AIML` |
| branch_name | str | Full name |
| description | str | One-line description |
| core_domains | str (pipe-delimited) | Domain tags used for interest matching |
| required_credits | int | Sum of credits across Foundational+Core courses for this branch |
| required_course_ids | str (pipe-delimited) | Course IDs that are Foundational/Core |
| elective_course_ids | str (pipe-delimited) | Course IDs available as electives |
| min_elective_credits | int | Minimum elective credits needed (fixed at 6) |
| associated_careers | str (pipe-delimited) | Career names linked to this branch |

**Sample row:** `AIML, Artificial Intelligence and Machine Learning, ..., 65, C0001|C0002|...|C0021, C0025|C0026, 6, Machine Learning Engineer|AI Research Engineer|...`

### 3.2 `courses.csv` (59 rows)
| Column | Type | Description |
|---|---|---|
| course_id | str | Primary key, e.g. `C0015` |
| course_name | str | e.g. "Introduction to Machine Learning" |
| credits | int | 2-4 |
| semester | int | 1-8, when the course is offered |
| prerequisite_course_id | str or null | FK to `courses.course_id`; null = no prerequisite |
| course_category | str | `Foundational` \| `Branch-Core` \| `Elective` |
| difficulty | int | 1 (easy) - 5 (hard) |

### 3.3 `branch_course_requirements.csv` (148 rows) — junction table
| Column | Type | Description |
|---|---|---|
| branch_id | str | FK to `branches.branch_id` |
| course_id | str | FK to `courses.course_id` |
| requirement_type | str | `Foundational` \| `Core` \| `Elective` |

*This table is the credit-overlap engine — a course appearing under multiple
`branch_id`s with `requirement_type in (Foundational, Core)` is exactly what
lets a completed course count toward more than one branch's requirements.*

### 3.4 `course_skill.csv` (109 rows) — junction table
| Column | Type | Description |
|---|---|---|
| course_id | str | FK to `courses.course_id` |
| skill_name | str | One of 32 taxonomy skills |
| skill_weight | float | 0.5-1.0, relative importance of this skill within the course |

### 3.5 `careers.csv` (29 rows)
| Column | Type | Description |
|---|---|---|
| career_id | str | Primary key, e.g. `CR006` |
| career_name | str | e.g. "Machine Learning Engineer" |
| required_skills | str (pipe-delimited) | Skills needed for this career |
| preferred_course_ids | str (pipe-delimited) | Courses that teach ≥1 required skill (auto-derived) |
| related_specializations | str (pipe-delimited) | Branch IDs this career maps to |
| demand_score | int | 1-10, illustrative market-demand weight |

### 3.6 `students.csv` (2,000 rows)
| Column | Type | Description |
|---|---|---|
| student_id | str | Primary key |
| name | str | Synthetic name |
| gender | str | Male/Female |
| age | int | 17-24 |
| current_branch | str | FK to `branches.branch_id` |
| semester | int | 3-8 (only students past semester 2 included, so there's course history) |
| cgpa | float | 0-10, computed from actual completed grades (credit-weighted) |
| avg_marks | float | Average marks across completed courses |
| completed_credits | int | Total credits earned to date |
| skills | str (pipe-delimited) | Derived (noisily, 80% recall) from completed courses' `course_skill` mappings |
| programming_languages | str (pipe-delimited) | Subset of `skills` restricted to languages |
| interests | str | A domain tag — 75% aligned to current branch, 25% genuinely cross-domain |
| preferred_domain | str | Mirrors `interests` (kept as a separate column per your spec; same value by design) |
| project_experience | str (pipe-delimited) | 0-3 branch-flavored project titles |
| certifications | str (pipe-delimited, may be empty) | 0-2 branch-relevant certifications |
| career_interest | str | 80% a career linked to current branch, 20% a genuine cross-branch interest |
| preferred_specialization | str | 85% same as `current_branch`, 15% a different branch (students considering a switch) |
| learning_preference | str | One of 5 categorical styles |

**⚠️ Note on empty-string fields:** `certifications` and `project_experience`
read back as `NaN` in pandas when a student has zero of them — this is
expected (not a data quality bug); handle with `.fillna('')`.

### 3.7 `student_course.csv` (27,923 rows)
| Column | Type | Description |
|---|---|---|
| student_id | str | FK to `students.student_id` |
| course_id | str | FK to `courses.course_id` |
| marks | float | 25-100, generated from a latent aptitude + branch-relevance bonus + course difficulty penalty + noise |
| grade | str | A+/A/B+/B/C/D/F, derived from marks |
| credits_attempted | int | = course credits |
| credits_earned | int | = course credits if `completion_status=='Completed'` (marks ≥ 40), else 0 |
| completion_status | str | `Completed` \| `Failed` |

Only courses offered at or before `semester - 1` are eligible per student
(i.e., only courses that would realistically already have been taken), so
there's no temporal leakage of "future" coursework into a student's current
profile.

## 4. Credit-Aware Scoring Methodology

For a student and a **target branch** (which may differ from their current
branch — this is the whole point):

**Credit Completion %** = (credits earned in courses that are Foundational/Core
for the target branch) ÷ (target branch's `required_credits`)

**Prerequisite Satisfaction %** = (prerequisites-of-remaining-required-courses
that are already completed) ÷ (total prerequisites needed for remaining
required courses)

**Skill Match %** = (student's derived skills ∩ union of required_skills across
the target branch's associated careers) ÷ (that union's size)

**Academic Fit** = average marks in target-branch-relevant courses already
completed (falls back to overall average if none taken yet)

**Pathway Compatibility Score** = `0.35×Academic Fit + 0.20×Skill Match% +
0.25×Credit Completion% + 0.20×Prerequisite Satisfaction%`

These weights are a documented starting point — not fitted to data — and
should be tuned during the qualitative validation step in Phase 7 of the
project roadmap (e.g., checking that the ranking feels sensible to actual
students/faculty). **Reference implementation:** `pathway_scoring.py`
(included). Worked example output for a real generated student:

```
Student S00009 | current branch: AIDS | semester 7 | CGPA 8.34

Target AIDS  -> Academic Fit 77.2 | Skill Match 66.7% | Credit Completion 95.6% (65/68 credits) | Prereq Satisfaction 100.0% -> Score 84.3
Target AIML  -> Academic Fit 78.9 | Skill Match 37.5% | Credit Completion 81.5% (53/65 credits) | Prereq Satisfaction  50.0% -> Score 65.5
Target CYSEC -> Academic Fit 80.2 | Skill Match 20.0% | Credit Completion 75.4% (49/65 credits) | Prereq Satisfaction  40.0% -> Score 58.9
```

This is the exact kind of statement you asked CogniMap to be able to produce:
*"AIML is a viable secondary pathway for this student — 81.5% of required
credits and half of the prerequisite chain are already satisfied via
overlapping coursework with their current AIDS branch."*

## 5. Data Generation Logic (how realism was engineered, not randomized)

1. **Courses first**, with hand-authored prerequisite chains and skill
   mappings per branch, including deliberately shared courses across
   branches with overlapping domains (ML-adjacent branches share the ML
   course; CSBS shares statistics with AIDS; IoT shares Robotics with AIML).
2. **Students assigned a branch** (weighted, not uniform — CSE/AIML larger
   cohorts, IoT/CSBS smaller, matching typical enrollment skew) and a latent
   **aptitude** value (`Normal(70, 12)`), which is *never stored directly* —
   it only drives downstream marks generation, so it can't leak as a feature.
3. **Enrollment records generated per student**, restricted to courses
   already offered by their current semester, with take-probability higher
   for Foundational (97%) and own-branch Core (90%) courses than unrelated
   electives (15%) — mirroring real course-selection behavior.
4. **Marks = aptitude + branch-relevance bonus (+6) − difficulty penalty +
   noise (σ=8)** — this is what produces the "real but noisy" signal
   verified in Section 6, rather than either extreme.
5. **CGPA, completed_credits derived from actual `student_course` outcomes**
   (credit-weighted grade points) — not assigned independently, so it's
   internally consistent (a student can't have high CGPA with low completed
   credits, etc.).
6. **Skills derived from completed courses' `course_skill` mappings**, with
   80% self-report recall (real people under-report skills) plus a 15%
   chance of one unrelated bonus skill (genuine noise).
7. **Interests / career_interest / preferred_specialization** each carry
   deliberate cross-branch noise (75%/80%/85% aligned respectively) so
   they're realistic signals, not a repeated copy of `current_branch` —
   this directly avoids the "Interested Domain ≈ target label" leakage
   found in the Kaggle dataset evaluated earlier in this project.

## 6. Data Quality Verification (already run — see `generate.py` + checks)

- **No missing values** outside the expected empty-string-for-zero-items
  case in `students.certifications` / `students.project_experience`.
- **No duplicate rows** in any table; no duplicate (student_id, course_id)
  pairs in `student_course`.
- **No prerequisite-semester violations** (every prerequisite is offered in
  an earlier semester than the course requiring it) — verified after fixing
  one bug found during QA (Computer Networks originally listed Operating
  Systems, same-semester, as a prerequisite).
- **Real-but-noisy branch signal, verified quantitatively:** on the shared
  "Introduction to Machine Learning" course, AIML students average 73.8
  marks vs. 65-71 for other branches — a genuine, learnable difference, but
  with std of 13-19, so nowhere near deterministic. Compare this to the two
  public Kaggle CS-career datasets rejected earlier in this project: one had
  *zero* separation between classes (labels statistically independent of
  features — unlearnable), the other had near-*complete* separation via a
  templated pattern (leakage — trivially "solvable" but meaningless). This
  dataset sits in the realistic middle, which is what a genuine ML problem
  needs.
- **Genuine credit overlap confirmed:** AIDS students average ~41 of 65
  AIML-required credits already completed (range 19-60), confirming the
  cross-branch overlap scenario the credit-aware logic depends on actually
  exists in the data.

## 7. Leakage Guidance — What NOT to Use as a Direct Model Feature

| Column | Why it's risky | Correct usage |
|---|---|---|
| `preferred_specialization` | Near-target by construction (85% equals `current_branch`, itself close to any "recommended branch" label) | Use only as a **validation/comparison signal** after generating recommendations — never as an input feature |
| `career_interest` | Similarly close to a career-level target if you build a career-prediction layer | Same — validation only, not a feature |
| `current_branch` | If your target is "which branch should this student be in," their *current* branch is definitionally close to the answer for students who haven't switched | Fine to use for **already-enrolled-elsewhere pathway comparison** (as shown in the worked example), but exclude it if you're building a "which branch fits a brand-new student" cold-start model |
| `interests` / `preferred_domain` | Same text value duplicated across two columns by design; using both is pseudo-double-counting one signal | Treat as a single feature, not two |
| `cgpa` computed post-hoc from `student_course` | Not leakage exactly, but don't also feed in individual course marks used to compute it as separate features unless you're intentionally doing so for interpretability — it's redundant information | Pick one representation (aggregate CGPA *or* per-relevant-course marks), document which |

**Target definition for modeling:** don't predict `current_branch` (that's
just recovering an assigned label). Predict `pathway_compatibility_score`
(regression) for a given (student, candidate-branch) pair, or rank all 7
branches by score for a student and evaluate top-1/top-3 against
`preferred_specialization` **only as a held-out qualitative check**, not as
training signal.

## 8. Build Order

1. `branches.csv`, `courses.csv`, `branch_course_requirements.csv`,
   `course_skill.csv` — the static curriculum backbone (build/validate this
   first; everything else depends on it being internally consistent, as the
   prerequisite-semester bug above demonstrates).
2. `careers.csv` — depends on `course_skill` (for `preferred_course_ids`).
3. `students.csv` (branch/semester/aptitude assignment only, skills/CGPA
   left for step 5).
4. `student_course.csv` — depends on `students` + `courses`.
5. Finish `students.csv` (CGPA, completed_credits, skills, interests,
   career_interest, etc.) — depends on `student_course`.
6. `pathway_scoring.py` — depends on all tables; this is your feature
   engineering + recommendation layer for the ML phase.

## 9. Feeding into the CogniMap ML Model

- **Row-level modeling unit:** (student, candidate_branch) pairs — each
  student generates 7 rows (one per branch), with features = credit
  completion %, prerequisite satisfaction %, skill match %, academic fit,
  and the label = a validated pathway compatibility score (or, for a
  classification framing, whether that branch is in the student's
  eventual/actual chosen specialization — if you later collect real
  outcome data).
- This reshapes the recommendation problem into a **learning-to-rank**
  setup: for each student, rank their 7 candidate-branch rows by predicted
  score, return top-3. This is the same architecture discussed in the
  earlier roadmap (Phase 4-6), now with real, internally-consistent
  features to train on instead of a synthetic single-target classification
  problem.
- Explainability (Phase 8) becomes direct: the four component scores *are*
  the explanation ("recommended because of 81.5% credit completion and
  strong academic fit"), no separate SHAP step strictly required, though
  it's still a nice addition for the component weights themselves.

## 10. Files Delivered

| File | Contents |
|---|---|
| `branches.csv` | 7 branches |
| `courses.csv` | 59 courses |
| `branch_course_requirements.csv` | 148 branch↔course links |
| `course_skill.csv` | 109 course↔skill links |
| `careers.csv` | 29 careers |
| `students.csv` | 2,000 students |
| `student_course.csv` | 27,923 enrollment records |
| `reference_data.py` | Hand-authored branch/skill/career/course definitions (edit this to change the curriculum) |
| `generate.py` | Full generator script (re-run after editing `reference_data.py`) |
| `pathway_scoring.py` | Credit-aware scoring reference implementation + worked example |
