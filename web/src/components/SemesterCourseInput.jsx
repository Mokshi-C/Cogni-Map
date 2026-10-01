// Converts a letter grade to a representative marks value for the existing
// recommend/new model input — presentation-layer only, unrelated to GPA.
// The actual grade-point scale (used for SGPA/CGPA) lives in
// src/academic_calculations.py's GRADE_POINTS; this list is kept in sync
// with it so every grade the student can pick here also has a marks value.
export const GRADE_TO_MARKS = {
  O: 98, 'A+': 93, A: 85, 'B+': 75, B: 65, 'C+': 55, C: 48, 'D+': 38, D: 28, F: 10,
}
const GRADES = Object.keys(GRADE_TO_MARKS)

/** Shows only the COMPLETED semesters (1 .. currentSemester - 1), grouped by
 * the course catalog's own semester field. Selecting a grade marks a course
 * as completed; credits always come from the course dataset (read-only) —
 * never manually entered, and GPA is never entered either — it's calculated
 * from these grades by the backend (academic_calculations.py). */
export default function SemesterCourseInput({ courses, currentSemester, selectedGrades, onGradeChange }) {
  const bySemester = {}
  for (const c of courses) {
    if (c.semester >= currentSemester) continue
    ;(bySemester[c.semester] ??= []).push(c)
  }
  const semesters = Object.keys(bySemester).map(Number).sort((a, b) => a - b)

  if (semesters.length === 0) {
    return <p className="cm-muted">No completed semesters yet — nothing to enter.</p>
  }

  return (
    <div>
      {semesters.map((sem) => (
        <div key={sem} className="cm-semester-block">
          <div className="cm-semester-heading">Semester {sem}</div>
          <div className="cm-checklist">
            {bySemester[sem].map((c) => (
              <div className="cm-checklist-row" key={c.course_id}>
                <span>
                  {c.course_name} <span className="cm-muted">({c.credits} cr)</span>
                </span>
                <select
                  className="cm-grade-select"
                  value={selectedGrades[c.course_id] || ''}
                  onChange={(e) => onGradeChange(c.course_id, e.target.value)}
                >
                  <option value="">Not taken</option>
                  {GRADES.map((g) => <option key={g} value={g}>{g}</option>)}
                </select>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}
