import { useEffect, useState } from 'react'
import { fetchStudents, fetchRecommendations } from '../api'
import StudentSearchSelect from '../components/StudentSearchSelect'
import PathwayCard from '../components/PathwayCard'
import { ScoreBarChart, FactorRadarChart } from '../components/ScoreCharts'
import { TechStackConstellation, LearningRoadmap } from '../components/InteractivePathways'

export default function ExistingStudent() {
  const [students, setStudents] = useState([])
  const [studentId, setStudentId] = useState('')
  const [topN, setTopN] = useState(3)
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchStudents()
      .then(setStudents)
      .catch(() => setError('Could not reach the CogniMap API. Is the backend running?'))
  }, [])

  const student = students.find((s) => s.student_id === studentId)

  const handleGenerate = async () => {
    setLoading(true)
    setError('')
    try {
      setResults(await fetchRecommendations(studentId, topN))
    } catch {
      setError('Could not fetch recommendations.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="cm-page">
      <h1 className="cm-page-title">Existing Student</h1>
      <p className="cm-page-subtitle">Select yourself from the CogniMap database to see your ranked pathways.</p>

      {error && <div className="cm-error">{error}</div>}

      <label className="cm-label">Search student by ID, name or branch</label>
      <StudentSearchSelect students={students} value={studentId} onChange={(id) => { setStudentId(id); setResults(null) }} />

      {student && (
        <div className="cm-milestones">
          <div className="cm-milestone"><div className="label">Name</div><div className="value">{student.name}</div></div>
          <div className="cm-milestone"><div className="label">Branch</div><div className="value">{student.current_branch}</div></div>
          <div className="cm-milestone"><div className="label">Semester</div><div className="value">{student.semester}</div></div>
          <div className="cm-milestone"><div className="label">CGPA</div><div className="value">{student.cgpa}</div></div>
        </div>
      )}

      <label className="cm-label">Number of recommendations: {topN}</label>
      <input type="range" min="1" max="7" value={topN} onChange={(e) => setTopN(Number(e.target.value))} className="cm-range" />

      <button className="cm-button" onClick={handleGenerate} disabled={!studentId || loading}>
        {loading ? 'Charting…' : 'Chart My Pathway →'}
      </button>

      {results && (
        <>
          {/* Welcome back headers & matches charts */}
          <h2 className="cm-section-title">Predicted Scores by Pathway</h2>
          <div className="cm-chart-box"><ScoreBarChart results={results} /></div>

          {/* STRONGEST MATCH section */}
          <div className="cm-semester-block" style={{ marginTop: '30px', padding: '24px', borderRadius: '12px', background: 'var(--cream)', border: '1px solid var(--line)', boxShadow: '0 4px 12px rgba(43,38,34,0.05)' }}>
            <div className="cm-semester-heading" style={{ fontSize: '0.85rem', color: 'var(--sage-dark)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>YOUR STRONGEST MATCH</div>
            <h2 style={{ margin: '6px 0 2px 0', fontSize: '2rem', fontFamily: 'Fraunces, serif' }}>{results[0].branch_name}</h2>
            <div className="cm-score" style={{ fontSize: '2rem', marginBottom: '18px' }}>{results[0].predicted_score}% MATCH</div>
            
            {/* Visual indicators */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.88rem', fontWeight: '600' }}>
                  <span>Academic Fit</span>
                  <span>{results[0].ml_base_score}%</span>
                </div>
                <div className="cm-bar-track" style={{ height: '8px', marginTop: '4px' }}>
                  <div className="cm-bar-fill" style={{ width: `${results[0].ml_base_score}%` }} />
                </div>
              </div>

              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.88rem', fontWeight: '600' }}>
                  <span>Skill Match</span>
                  <span>{results[0].skill_proficiency_match}%</span>
                </div>
                <div className="cm-bar-track" style={{ height: '8px', marginTop: '4px' }}>
                  <div className="cm-bar-fill" style={{ width: `${results[0].skill_proficiency_match}%` }} />
                </div>
              </div>

              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.88rem', fontWeight: '600' }}>
                  <span>Credit Completion</span>
                  <span>{results[0].credit_completion_pct}%</span>
                </div>
                <div className="cm-bar-track" style={{ height: '8px', marginTop: '4px' }}>
                  <div className="cm-bar-fill" style={{ width: `${results[0].credit_completion_pct}%` }} />
                </div>
              </div>

              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.88rem', fontWeight: '600' }}>
                  <span>Career Alignment</span>
                  <span>{results[0].career_alignment}%</span>
                </div>
                <div className="cm-bar-track" style={{ height: '8px', marginTop: '4px' }}>
                  <div className="cm-bar-fill" style={{ width: `${results[0].career_alignment}%` }} />
                </div>
              </div>
            </div>
          </div>

          {/* AI Insight Callout */}
          <div className="cm-card" style={{ marginTop: '24px', borderLeftColor: 'var(--amber)', background: 'var(--cream)', padding: '20px' }}>
            <h3 style={{ margin: '0 0 8px 0', color: 'var(--coral-dark)', fontSize: '1.1rem', letterSpacing: '0.04em' }}>COGNIMAP INSIGHT</h3>
            <p style={{ margin: '0 0 16px 0', fontSize: '0.92rem', lineHeight: '1.6', color: 'var(--ink)' }}>
              Your strongest pathway is <b>{results[0].branch_name}</b> because your academic performance and current skill profile align strongly with this pathway.
            </p>
            <div style={{ borderTop: '1px dashed var(--line)', paddingTop: '14px' }}>
              <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', color: 'var(--sage-dark)', fontWeight: 'bold', marginBottom: '4px' }}>BIGGEST OPPORTUNITY</div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <strong style={{ fontSize: '0.95rem' }}>SQL & Machine Learning</strong>
                <button 
                  type="button" 
                  className="cm-button" 
                  style={{ marginTop: 0, padding: '8px 14px', fontSize: '0.82rem' }}
                  onClick={() => {
                    const el = document.getElementById('roadmap-section')
                    if (el) el.scrollIntoView({ behavior: 'smooth' })
                  }}
                >
                  VIEW ROADMAP →
                </button>
              </div>
            </div>
          </div>

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
            studentBranch={student.current_branch}
            targetBranch={results[0].branch_name}
            targetCareer={student.career_interest}
          />

          {/* Tech Stack section */}
          <TechStackConstellation targetBranch={results[0].branch_id} />

          {/* Learning Roadmap section */}
          <div id="roadmap-section">
            <LearningRoadmap targetBranch={results[0].branch_id} />
          </div>

          <h2 className="cm-section-title">All Ranked Pathways</h2>
          <div className="cm-journey" style={{ marginTop: '16px' }}>
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
        </>
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
            <div style={{ fontWeight: 'bold', fontSize: '0.95rem' }}>{targetCareer || 'Software Professional'}</div>
          </div>
        </div>
      </div>
    </div>
  )
}
