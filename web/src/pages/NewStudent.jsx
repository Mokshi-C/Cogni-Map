import { useEffect, useState } from 'react'
import {
  fetchCourses, fetchSkills, fetchNewStudentRecommendations,
  fetchBranches, fetchAcademicHistorySummary,
} from '../api'
import PathwayCard from '../components/PathwayCard'
import { ScoreBarChart, FactorRadarChart } from '../components/ScoreCharts'
import SemesterCourseInput, { GRADE_TO_MARKS } from '../components/SemesterCourseInput'
import { INTEREST_LEVELS, INTEREST_DOMAINS, INTEREST_DOMAIN_NAMES } from '../interestTaxonomy'

const PROFICIENCY_LEVELS = ['Beginner', 'Intermediate', 'Advanced']

const CAREER_OPTIONS = [
  'Software Engineer',
  'Backend Developer',
  'Systems Engineer',
  'DevOps Engineer',
  'Software Architect',
  'Machine Learning Engineer',
  'AI Research Engineer',
  'Computer Vision Engineer',
  'NLP Engineer',
  'Robotics Engineer',
  'Data Scientist',
  'Data Analyst',
  'Business Intelligence Analyst',
  'Data Engineer',
  'IT Support Engineer',
  'Network Administrator',
  'Systems Administrator',
  'Database Administrator',
  'Cloud Engineer',
  'Cybersecurity Analyst',
  'Penetration Tester',
  'Security Architect',
  'SOC Analyst',
  'Product Manager (Tech)',
  'Business Systems Analyst',
  'IT Consultant',
  'IoT Solutions Engineer',
  'Embedded Systems Engineer',
  'Firmware Engineer'
]

const PG_OPTIONS = ['M.Tech', 'M.E.', 'M.Sc.', 'MS', 'Undecided']

export default function NewStudent() {
  const [courses, setCourses] = useState([])
  const [allSkills, setAllSkills] = useState([])
  const [branches, setBranches] = useState([])

  const [ugBranch, setUgBranch] = useState('')
  const [currentYear, setCurrentYear] = useState(1)
  const [currentSemester, setCurrentSemester] = useState(1)
  const [selectedGrades, setSelectedGrades] = useState({}) // course_id -> letter grade
  const [selectedSkills, setSelectedSkills] = useState(new Set())
  const [topN, setTopN] = useState(3)

  // Self-reported skill proficiency — separate from selectedSkills above
  // (which feeds the recommendation model) and from academic domain strength
  // (which is derived from courses/grades, not self-reported).
  const [skillProficiency, setSkillProficiency] = useState({}) // { skill_name: 'Beginner'|'Intermediate'|'Advanced' }

  // Interests: domain -> { level, subtopics: [] }. Separate from skillProficiency
  // above and from academic domain strength — self-reported interest signal only,
  // not integrated into the recommendation model yet.
  const [interests, setInterests] = useState({})

  // Career Goals and PG Preference
  const [careerGoals, setCareerGoals] = useState([])
  const [pgPreference, setPgPreference] = useState('Undecided')

  const [summary, setSummary] = useState(null) // { sgpa_by_semester, cgpa, total_credits, semesters }
  const [summaryError, setSummaryError] = useState('')

  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchCourses().then(setCourses).catch(() => setError('Could not reach the CogniMap API.'))
    fetchSkills().then(setAllSkills).catch(() => {})
    fetchBranches().then(setBranches).catch(() => {})
  }, [])

  // Live SGPA/CGPA — recalculated via the backend (academic_calculations.py)
  // every time a grade changes. Group by each course's own catalog semester,
  // same grouping SemesterCourseInput already uses to display them.
  useEffect(() => {
    const entries = Object.entries(selectedGrades)
    if (entries.length === 0) {
      setSummary(null)
      return
    }
    const bySemester = {}
    for (const [course_id, grade] of entries) {
      const course = courses.find((c) => c.course_id === course_id)
      if (!course) continue
      ;(bySemester[course.semester] ??= []).push({ course_id, grade })
    }
    const payload = Object.entries(bySemester).map(([semester_number, courses]) => ({
      semester_number: Number(semester_number), courses,
    }))
    if (payload.length === 0) return

    fetchAcademicHistorySummary(payload)
      .then((data) => { setSummary(data); setSummaryError('') })
      .catch(() => setSummaryError('Could not calculate SGPA/CGPA.'))
  }, [selectedGrades, courses])

  const handleGradeChange = (courseId, grade) => {
    setSelectedGrades((prev) => {
      const next = { ...prev }
      if (grade === '') delete next[courseId]
      else next[courseId] = grade
      return next
    })
  }

  // If the current semester moves back down, drop grades entered for
  // semesters that are no longer "completed" so SGPA/CGPA stays accurate.
  const handleCurrentSemesterChange = (sem) => {
    setCurrentSemester(sem)
    setSelectedGrades((prev) => {
      const next = {}
      for (const [courseId, grade] of Object.entries(prev)) {
        const course = courses.find((c) => c.course_id === courseId)
        if (course && course.semester < sem) next[courseId] = grade
      }
      return next
    })
  }

  const toggleSkill = (skill) => {
    setSelectedSkills((prev) => {
      const next = new Set(prev)
      if (next.has(skill)) {
        next.delete(skill)
        setSkillProficiency((sp) => {
          const nextSp = { ...sp }
          delete nextSp[skill]
          return nextSp
        })
      } else {
        next.add(skill)
        setSkillProficiency((sp) => ({ ...sp, [skill]: 'Beginner' }))
      }
      return next
    })
  }

  const addSkillProficiency = (skill) => {
    if (!skill || skillProficiency[skill]) return
    setSkillProficiency((prev) => ({ ...prev, [skill]: 'Beginner' }))
    setSelectedSkills((prev) => {
      const next = new Set(prev)
      next.add(skill)
      return next
    })
  }

  const changeSkillProficiency = (skill, level) => {
    setSkillProficiency((prev) => ({ ...prev, [skill]: level }))
  }

  const removeSkillProficiency = (skill) => {
    setSkillProficiency((prev) => {
      const next = { ...prev }
      delete next[skill]
      return next
    })
    setSelectedSkills((prev) => {
      const next = new Set(prev)
      next.delete(skill)
      return next
    })
  }

  const addCareerGoal = (career) => {
    if (!career || careerGoals.includes(career)) return
    setCareerGoals((prev) => [...prev, career])
  }

  const removeCareerGoal = (career) => {
    setCareerGoals((prev) => prev.filter((c) => c !== career))
  }

  const addInterestDomain = (domain) => {
    if (!domain || interests[domain]) return
    setInterests((prev) => ({ ...prev, [domain]: { level: 'Medium', subtopics: [] } }))
  }

  const changeInterestLevel = (domain, level) => {
    setInterests((prev) => ({ ...prev, [domain]: { ...prev[domain], level } }))
  }

  const toggleInterestSubtopic = (domain, subtopic) => {
    setInterests((prev) => {
      const current = prev[domain]
      if (!current) return prev
      const has = current.subtopics.includes(subtopic)
      const subtopics = has
        ? current.subtopics.filter((s) => s !== subtopic)
        : [...current.subtopics, subtopic]
      return { ...prev, [domain]: { ...current, subtopics } }
    })
  }

  const removeInterestDomain = (domain) => {
    setInterests((prev) => {
      const next = { ...prev }
      delete next[domain] // drops level + subtopics together, safely
      return next
    })
  }



  const [step, setStep] = useState(1)
  const [analysisPhase, setAnalysisPhase] = useState(0)

  const handleGenerate = async () => {
    setLoading(true)
    setError('')
    setAnalysisPhase(1)
    
    // Simulate interactive analysis phases for presentation
    await new Promise(r => setTimeout(r, 800))
    setAnalysisPhase(2)
    await new Promise(r => setTimeout(r, 800))
    setAnalysisPhase(3)
    await new Promise(r => setTimeout(r, 800))

    try {
      const completed = Object.entries(selectedGrades).map(([course_id, grade]) => ({
        course_id, marks: GRADE_TO_MARKS[grade],
      }))
      const data = await fetchNewStudentRecommendations(
        completed,
        Array.from(selectedSkills),
        topN,
        skillProficiency,
        interests,
        careerGoals,
        pgPreference
      )
      setResults(data)
    } catch {
      setError('Could not fetch recommendations.')
    } finally {
      setLoading(false)
      setAnalysisPhase(0)
    }
  }

  const stepNames = ['Academic Profile', 'Skills & Tech', 'Interests & Subtopics', 'Goals & Target']

  return (
    <div className="cm-page">
      <h1 className="cm-page-title">New Student Profile</h1>
      <p className="cm-page-subtitle">
        Not in the CogniMap database yet? Enter your academic history semester by semester —
        the same trained model and scoring formulas are used, just on your input.
      </p>

      {error && <div className="cm-error">{error}</div>}

      {/* Step Indicator Header */}
      {!results && (
        <div className="cm-onboarding-steps">
          {stepNames.map((name, idx) => {
            const stepNum = idx + 1
            const isCompleted = step > stepNum
            const isActive = step === stepNum
            return (
              <div 
                key={name} 
                className={`cm-step-indicator ${isActive ? 'active' : ''} ${isCompleted ? 'completed' : ''}`}
              >
                {isCompleted ? '✓' : stepNum}. {name}
              </div>
            )
          })}
        </div>
      )}

      {loading && (
        <div className="cm-analyzing-overlay fade-in-slide">
          <div className="cm-loading-title" style={{ color: 'var(--coral-dark)' }}>Analyzing Profile...</div>
          <div style={{ marginTop: '20px' }}>
            <div className={`cm-analysis-step ${analysisPhase >= 1 ? 'done' : ''}`}>
              {analysisPhase >= 2 ? '✓' : '●'} Calculating academic domain strengths...
            </div>
            <div className={`cm-analysis-step ${analysisPhase >= 2 ? 'done' : ''}`}>
              {analysisPhase >= 3 ? '✓' : '●'} Analyzing career and proficiency matches...
            </div>
            <div className={`cm-analysis-step ${analysisPhase >= 3 ? 'done' : ''}`}>
              {analysisPhase >= 4 ? '✓' : '●'} Running Random Forest predictor models...
            </div>
          </div>
        </div>
      )}

      {!loading && !results && (
        <div className="fade-in-slide">
          {/* STEP 1: Academic Profile */}
          {step === 1 && (
            <div>
              <label className="cm-label">UG branch / degree</label>
              <select className="cm-select" value={ugBranch} onChange={(e) => setUgBranch(e.target.value)}>
                <option value="">Select your branch</option>
                {branches.map((b) => (
                  <option key={b.branch_id} value={b.branch_id}>{b.branch_name}</option>
                ))}
              </select>

              <label className="cm-label">Current year</label>
              <select className="cm-select" value={currentYear} onChange={(e) => setCurrentYear(Number(e.target.value))}>
                {[1, 2, 3, 4].map((n) => <option key={n} value={n}>Year {n}</option>)}
              </select>

              <label className="cm-label">Current semester</label>
              <select
                className="cm-select"
                value={currentSemester}
                onChange={(e) => handleCurrentSemesterChange(Number(e.target.value))}
              >
                {[1, 2, 3, 4, 5, 6, 7, 8].map((n) => (
                  <option key={n} value={n}>Semester {n}</option>
                ))}
              </select>

              <label className="cm-label">Your academic history (completed semesters)</label>
              <SemesterCourseInput
                courses={courses}
                currentSemester={currentSemester}
                selectedGrades={selectedGrades}
                onGradeChange={handleGradeChange}
              />

              {summaryError && <div className="cm-error">{summaryError}</div>}
              {summary && (
                <div className="cm-semester-block" style={{ marginTop: '24px' }}>
                  <div className="cm-semester-heading">Your calculated academic performance</div>
                  <div className="cm-checklist">
                    {summary.semesters.map((s) => (
                      <div className="cm-checklist-row" key={s.semester_number}>
                        <span>Semester {s.semester_number} SGPA</span>
                        <span>{s.sgpa} ({s.credits} cr)</span>
                      </div>
                    ))}
                    <div className="cm-checklist-row">
                      <strong>Overall CGPA</strong>
                      <strong>{summary.cgpa}</strong>
                    </div>
                    <div className="cm-checklist-row">
                      <span>Total completed credits</span>
                      <span>{summary.total_credits}</span>
                    </div>
                  </div>
                </div>
              )}

              <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '24px' }}>
                <button type="button" className="cm-button" onClick={() => setStep(2)}>Next Step →</button>
              </div>
            </div>
          )}

          {/* STEP 2: Skills */}
          {step === 2 && (
            <div>
              <label className="cm-label">Select your technical skills</label>
              <p className="cm-muted">Select all skills you have exposure to:</p>
              <div className="cm-chip-wrap" style={{ marginBottom: '20px' }}>
                {allSkills.map((skill) => (
                  <button
                    key={skill} type="button"
                    className={`cm-chip ${selectedSkills.has(skill) ? 'selected' : ''}`}
                    onClick={() => toggleSkill(skill)}
                  >
                    {skill}
                  </button>
                ))}
              </div>

              <label className="cm-label">Self-reported skill proficiency (optional)</label>
              <p className="cm-muted">
                Select proficiency levels for your core skills.
              </p>
              <select
                className="cm-select"
                value=""
                onChange={(e) => addSkillProficiency(e.target.value)}
              >
                <option value="">Add a skill proficiency…</option>
                {allSkills.filter((s) => !skillProficiency[s]).map((s) => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </select>

              {Object.keys(skillProficiency).length > 0 && (
                <div className="cm-checklist" style={{ marginTop: '12px' }}>
                  {Object.entries(skillProficiency).map(([skill, level]) => (
                    <div className="cm-checklist-row" key={skill}>
                      <span>{skill}</span>
                      <span>
                        <select
                          className="cm-grade-select"
                          value={level}
                          onChange={(e) => changeSkillProficiency(skill, e.target.value)}
                        >
                          {PROFICIENCY_LEVELS.map((lvl) => <option key={lvl} value={lvl}>{lvl}</option>)}
                        </select>
                        {' '}
                        <button type="button" className="cm-chip" style={{ padding: '4px 10px' }} onClick={() => removeSkillProficiency(skill)}>
                          Remove
                        </button>
                      </span>
                    </div>
                  ))}
                </div>
              )}

              <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '24px' }}>
                <button type="button" className="cm-button cm-button-secondary" onClick={() => setStep(1)}>← Back</button>
                <button type="button" className="cm-button" onClick={() => setStep(3)}>Next Step →</button>
              </div>
            </div>
          )}

          {/* STEP 3: Interests */}
          {step === 3 && (
            <div>
              <label className="cm-label">Your interests & subtopics (optional)</label>
              <p className="cm-muted">
                Pick a domain, then toggle its subtopics and how strongly you're interested.
              </p>
              <select
                className="cm-select"
                value=""
                onChange={(e) => addInterestDomain(e.target.value)}
                style={{ marginBottom: '14px' }}
              >
                <option value="">Add an interest domain…</option>
                {INTEREST_DOMAIN_NAMES.filter((d) => !interests[d]).map((d) => (
                  <option key={d} value={d}>{d}</option>
                ))}
              </select>

              {Object.entries(interests).map(([domain, { level, subtopics }]) => (
                <div className="cm-semester-block" key={domain} style={{ padding: '14px', border: '1px solid var(--line)', borderRadius: '10px', background: '#fff', marginBottom: '16px' }}>
                  <div className="cm-semester-heading" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span>{domain}</span>
                    <span>
                      <select
                        className="cm-grade-select"
                        value={level}
                        onChange={(e) => changeInterestLevel(domain, e.target.value)}
                      >
                        {INTEREST_LEVELS.map((lvl) => <option key={lvl} value={lvl}>{lvl}</option>)}
                      </select>
                      {' '}
                      <button type="button" className="cm-chip" style={{ padding: '4px 10px' }} onClick={() => removeInterestDomain(domain)}>
                        Remove
                      </button>
                    </span>
                  </div>
                  <div className="cm-chip-wrap" style={{ marginTop: '10px' }}>
                    {INTEREST_DOMAINS[domain].map((subtopic) => (
                      <button
                        key={subtopic} type="button"
                        className={`cm-chip ${subtopics.includes(subtopic) ? 'selected' : ''}`}
                        onClick={() => toggleInterestSubtopic(domain, subtopic)}
                      >
                        {subtopic}
                      </button>
                    ))}
                  </div>
                </div>
              ))}

              <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '24px' }}>
                <button type="button" className="cm-button cm-button-secondary" onClick={() => setStep(2)}>← Back</button>
                <button type="button" className="cm-button" onClick={() => setStep(4)}>Next Step →</button>
              </div>
            </div>
          )}

          {/* STEP 4: Career Goals */}
          {step === 4 && (
            <div>
              <label className="cm-label">Your Career Goals (optional)</label>
              <p className="cm-muted">
                Select one or more career directions you are targeting.
              </p>
              <select
                className="cm-select"
                value=""
                onChange={(e) => addCareerGoal(e.target.value)}
              >
                <option value="">Add a career goal…</option>
                {CAREER_OPTIONS.filter((c) => !careerGoals.includes(c)).map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>

              {careerGoals.length > 0 && (
                <div className="cm-chip-wrap" style={{ marginTop: '8px', marginBottom: '16px' }}>
                  {careerGoals.map((c) => (
                    <span key={c} className="cm-chip selected" style={{ display: 'inline-flex', alignItems: 'center', gap: '8px' }}>
                      {c}
                      <button
                        type="button"
                        style={{ background: 'none', border: 'none', color: 'white', cursor: 'pointer', fontWeight: 'bold', padding: 0, marginLeft: '4px' }}
                        onClick={() => removeCareerGoal(c)}
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              )}

              <label className="cm-label">Your PG / Higher-Study Preference (optional)</label>
              <select
                className="cm-select"
                value={pgPreference}
                onChange={(e) => setPgPreference(e.target.value)}
                style={{ marginBottom: '24px' }}
              >
                {PG_OPTIONS.map((opt) => (
                  <option key={opt} value={opt}>{opt}</option>
                ))}
              </select>

              <label className="cm-label">Number of recommendations: {topN}</label>
              <input type="range" min="1" max="7" value={topN} onChange={(e) => setTopN(Number(e.target.value))} className="cm-range" />

              <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '24px' }}>
                <button type="button" className="cm-button cm-button-secondary" onClick={() => setStep(3)}>← Back</button>
                <button className="cm-button" onClick={handleGenerate}>
                  Chart My Pathway →
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {results && (
        <div className="fade-in-slide">
          <button 
            type="button" 
            className="cm-button cm-button-secondary" 
            style={{ marginBottom: '24px' }}
            onClick={() => { setResults(null); setStep(1); }}
          >
            ← Reset & Create New Profile
          </button>

          <h2 className="cm-section-title">Predicted Scores by Pathway</h2>
          <div className="cm-chart-box"><ScoreBarChart results={results} /></div>

          <h2 className="cm-section-title">Top Pathway — Four Factors</h2>
          <div className="cm-chart-box"><FactorRadarChart rec={results[0]} /></div>

          {results[0] && results[0].domain_strengths && (
            <div className="cm-semester-block" style={{ marginTop: '24px', marginBottom: '24px' }}>
              <div className="cm-semester-heading">Your 11 Academic Domain Strengths</div>
              <p className="cm-muted" style={{ marginBottom: '12px' }}>
                Derived dynamically from your completed courses and grades. Represents academic capability independent of GPA.
              </p>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '12px' }}>
                {Object.entries(results[0].domain_strengths).map(([domain, score]) => (
                  <div key={domain} className="cm-comp" style={{ border: '1px solid #eee', padding: '12px', borderRadius: '6px', background: '#fff' }}>
                    <div className="label" style={{ fontWeight: '600', fontSize: '13px', color: '#333' }}>{domain}</div>
                    <div className="value" style={{ fontSize: '13px', fontWeight: 'bold', color: '#007acc' }}>
                      {score !== null ? `${score}%` : 'N/A'}
                    </div>
                    <div className="cm-bar-track" style={{ height: '6px', marginTop: '6px', backgroundColor: '#e0e0e0' }}>
                      <div 
                        className="cm-bar-fill" 
                        style={{ 
                          width: `${score !== null ? score : 0}%`, 
                          height: '100%', 
                          backgroundColor: score !== null ? '#007acc' : '#ccc' 
                        }} 
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <PathwayFlowchart
            studentBranch={branches.find(b => b.branch_id === ugBranch)?.branch_name || 'CSE'}
            targetBranch={results[0].branch_name}
            targetCareer={careerGoals[0] || 'Software Professional'}
          />

          <h2 className="cm-section-title">All Ranked Recommendations</h2>
          <div className="cm-journey">
            <div className="cm-journey-node cm-journey-endpoint">START</div>
            {results.map((rec, i) => (
              <div key={rec.branch_id}>
                <div className="cm-journey-line" />
                <div className="cm-journey-node">
                  <span className="cm-journey-dot" />
                  <PathwayCard rec={rec} rank={i + 1} />
                </div>
              </div>
            ))}
            <div className="cm-journey-line" />
            <div className="cm-journey-node cm-journey-endpoint">EXPLORE</div>
          </div>
        </div>
      )}
    </div>
  )
}

function PathwayFlowchart({ studentBranch, targetBranch, targetCareer }) {
  return (
    <div className="cm-path-canvas fade-in-slide">
      <h3 className="cm-semester-heading" style={{ textAlign: 'center', marginBottom: '20px', fontSize: '1.2rem' }}>
        Interactive Journey Pathway Map
      </h3>
      <div className="cm-path-flow">
        <svg className="cm-path-connector-svg">
          <line x1="50%" y1="0%" x2="50%" y2="100%" stroke="var(--sage)" strokeWidth="3" strokeDasharray="6,4" />
        </svg>

        <div className="cm-path-node highlight">
          <span style={{ fontSize: '1.2rem' }}>👤</span>
          <div>
            <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', color: 'var(--sage-dark)', fontWeight: '600' }}>Student Profile</div>
            <div style={{ fontWeight: 'bold', fontSize: '0.95rem' }}>{studentBranch} Student</div>
          </div>
        </div>

        <div className="cm-path-node">
          <span style={{ fontSize: '1.2rem' }}>📈</span>
          <div>
            <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', color: 'var(--sage-dark)', fontWeight: '600' }}>Academic Fit</div>
            <div style={{ fontWeight: 'bold', fontSize: '0.95rem' }}>Curriculum Relevance Verified</div>
          </div>
        </div>

        <div className="cm-path-node">
          <span style={{ fontSize: '1.2rem' }}>🛠️</span>
          <div>
            <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', color: 'var(--sage-dark)', fontWeight: '600' }}>Skill Match</div>
            <div style={{ fontWeight: 'bold', fontSize: '0.95rem' }}>Taxonomy Alignment Mapped</div>
          </div>
        </div>

        <div className="cm-path-node highlight" style={{ borderColor: 'var(--amber)' }}>
          <span style={{ fontSize: '1.2rem' }}>🎓</span>
          <div>
            <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', color: 'var(--sage-dark)', fontWeight: '600' }}>Recommended Pathway</div>
            <div style={{ fontWeight: 'bold', fontSize: '0.95rem', color: 'var(--coral-dark)' }}>{targetBranch}</div>
          </div>
        </div>

        <div className="cm-path-node highlight" style={{ borderColor: 'var(--sage)' }}>
          <span style={{ fontSize: '1.2rem' }}>💼</span>
          <div>
            <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', color: 'var(--sage-dark)', fontWeight: '600' }}>Target Career Destination</div>
            <div style={{ fontWeight: 'bold', fontSize: '0.95rem' }}>{targetCareer}</div>
          </div>
        </div>
      </div>
    </div>
  )
}
