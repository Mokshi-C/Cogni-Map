import { useState } from 'react'

export default function PathwayCard({ rec, rank }) {
  const [expanded, setExpanded] = useState(rank === 1)
  const isPersonalized = rec.ml_base_score !== undefined
  const rankClass = rank <= 3 ? `rank-${rank}` : 'rank-3'

  return (
    <div 
      className={`cm-card ${rankClass}`} 
      style={{ cursor: 'pointer', transition: 'all 0.3s ease' }} 
      onClick={() => setExpanded(!expanded)}
    >
      <div className="cm-card-top" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span className="cm-rank-badge">#{rank}</span>
          <span className="cm-branch-name" style={{ fontSize: '1.3rem' }}>{rec.branch_name}</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div className="cm-score" title="Final Compatibility Score" style={{ fontSize: '1.5rem', color: 'var(--coral-dark)' }}>{rec.predicted_score}</div>
          <span style={{ fontSize: '0.8rem', color: 'var(--sage-dark)', transform: expanded ? 'rotate(180deg)' : 'rotate(0deg)', transition: 'transform 0.3s ease' }}>▼</span>
        </div>
      </div>
      
      {expanded && (
        <div className="fade-in-slide" style={{ marginTop: '16px' }} onClick={(e) => e.stopPropagation()}>
          <div className="cm-why" style={{ borderLeft: '4px solid var(--coral)', background: 'var(--cream)', padding: '12px 16px', borderRadius: '6px', margin: '8px 0 16px 0' }}>
            🧭 <b>Why this pathway?</b> {rec.explanation || "Recommended based on academic compatibility."}
          </div>

          <div className="cm-components">
            {/* Academic / ML Base */}
            <div className="cm-comp">
              <div className="label">Academic / ML Compatibility</div>
              <div className="value">{isPersonalized ? rec.ml_base_score : rec.academic_fit}%</div>
              <div className="cm-bar-track">
                <div className="cm-bar-fill" style={{ width: `${Math.min(isPersonalized ? rec.ml_base_score : rec.academic_fit, 100)}%` }} />
              </div>
            </div>

            {/* Skill Alignment */}
            <div className="cm-comp">
              <div className="label">Skill Alignment / Match</div>
              <div className="value">{isPersonalized ? rec.skill_proficiency_match : rec.skill_match_pct}%</div>
              <div className="cm-bar-track">
                <div className="cm-bar-fill" style={{ width: `${Math.min(isPersonalized ? rec.skill_proficiency_match : rec.skill_match_pct, 100)}%` }} />
              </div>
            </div>

            {/* Career Alignment (if personalized) */}
            {isPersonalized && (
              <div className="cm-comp">
                <div className="label">Career Alignment</div>
                <div className="value">{rec.career_alignment}%</div>
                <div className="cm-bar-track">
                  <div className="cm-bar-fill" style={{ width: `${Math.min(rec.career_alignment, 100)}%` }} />
                </div>
              </div>
            )}

            {/* Interest Alignment (if personalized) */}
            {isPersonalized && (
              <div className="cm-comp">
                <div className="label">Interest Alignment</div>
                <div className="value">{rec.interest_alignment}%</div>
                <div className="cm-bar-track">
                  <div className="cm-bar-fill" style={{ width: `${Math.min(rec.interest_alignment, 100)}%` }} />
                </div>
              </div>
            )}

            {/* PG Preference Alignment (if personalized) */}
            {isPersonalized && rec.pg_adjustment > 0 && (
              <div className="cm-comp">
                <div className="label">PG Preference Alignment</div>
                <div className="value">+{rec.pg_adjustment} pts</div>
                <div className="cm-bar-track">
                  <div className="cm-bar-fill" style={{ width: '100%', backgroundColor: '#4caf50' }} />
                </div>
              </div>
            )}
          </div>

          <div className="cm-improve" style={{ marginTop: '16px', fontSize: '0.88rem' }}>
            💡 Progress: <b>{rec.credits_earned}/{rec.credits_required}</b> relevant credits already completed.
          </div>
        </div>
      )}
    </div>
  )
}
