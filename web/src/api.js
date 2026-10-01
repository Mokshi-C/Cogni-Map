const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

export async function fetchStudents() {
  const res = await fetch(`${API_BASE}/students`)
  if (!res.ok) throw new Error('Failed to load students')
  return res.json()
}

export async function fetchRecommendations(studentId, topN) {
  const res = await fetch(`${API_BASE}/recommend/${studentId}?top_n=${topN}`)
  if (!res.ok) throw new Error('Failed to load recommendations')
  return res.json()
}

export async function fetchCourses() {
  const res = await fetch(`${API_BASE}/courses`)
  if (!res.ok) throw new Error('Failed to load courses')
  return res.json()
}

export async function fetchSkills() {
  const res = await fetch(`${API_BASE}/skills`)
  if (!res.ok) throw new Error('Failed to load skills')
  return res.json()
}

export async function fetchNewStudentRecommendations(completedCourses, skills, topN, skillProficiency = {}, interests = {}, careerGoals = [], pgPreference = 'Undecided') {
  const res = await fetch(`${API_BASE}/recommend/new`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      completed_courses: completedCourses,
      skills,
      skill_proficiency: skillProficiency,
      interests,
      career_goals: careerGoals,
      pg_preference: pgPreference,
      top_n: topN
    }),
  })
  if (!res.ok) throw new Error('Failed to load recommendations')
  return res.json()
}

export async function fetchBranches() {
  const res = await fetch(`${API_BASE}/branches`)
  if (!res.ok) throw new Error('Failed to load branches')
  return res.json()
}

export async function fetchAcademicHistorySummary(semesters) {
  const res = await fetch(`${API_BASE}/academic-history/summary`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ semesters }),
  })
  if (!res.ok) throw new Error('Failed to calculate SGPA/CGPA')
  return res.json()
}
