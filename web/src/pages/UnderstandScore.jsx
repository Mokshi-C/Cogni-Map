import { useState } from 'react'

const FACTORS = [
  {
    name: 'Academic Fit',
    icon: '📈',
    meaning: 'The average marks you scored in courses you\'ve completed that are Foundational or Core requirements for a given pathway.',
    why: 'It reflects how well you\'ve actually performed in the coursework most relevant to that pathway, not just your overall GPA.',
    contributes: 'Your marks in each completed course, filtered to only the ones required for that specific pathway. If you haven\'t completed any relevant courses yet, your overall average marks are used instead.',
    improve: 'Focus on performing well in the Foundational/Core courses tied to the pathway you\'re interested in.',
  },
  {
    name: 'Skill Match',
    icon: '🛠️',
    meaning: 'The percentage overlap between your skills and the skills required by the careers associated with a pathway.',
    why: 'A pathway is more relevant to you if your existing skills already line up with the careers it leads to.',
    contributes: 'Your reported skill list, compared against the union of required_skills across every career linked to that branch.',
    improve: 'Build more of the specific skills tied to careers in that pathway — the required skills for each career are listed in the CogniMap career data.',
  },
  {
    name: 'Credit Completion',
    icon: '🎓',
    meaning: 'The percentage of a pathway\'s required credits (Foundational + Core courses) that you\'ve already earned.',
    why: 'This is the literal, credit-aware core of CogniMap — it tells you concretely how far along you already are toward a pathway, including credits that overlap from a different branch.',
    contributes: 'Credits earned from completed courses that are marked Foundational or Core for that branch, divided by the branch\'s total required credits.',
    improve: 'Complete more of the required courses for that branch — including shared/foundational courses you may have already taken without realizing they count.',
  },
  {
    name: 'Prerequisite Satisfaction',
    icon: '🔑',
    meaning: 'Of the courses you still need for a pathway, the percentage whose prerequisite course you\'ve already completed.',
    why: 'It tells you how ready you are to actually start your remaining coursework, not just how many credits you have.',
    contributes: 'For each required course you haven\'t completed yet, whether its prerequisite (if it has one) is already in your completed courses.',
    improve: 'Finish the prerequisite courses for whatever you still need — this directly unlocks the remaining required courses.',
  },
]

function FactorCard({ f }) {
  const [expanded, setExpanded] = useState(false)
  return (
    <div className="cm-expandable-card">
      <div className="cm-expandable-header" onClick={() => setExpanded(!expanded)}>
        <span style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span style={{ fontSize: '1.25rem' }}>{f.icon}</span>
          <span>{f.name}</span>
        </span>
        <span style={{ transform: expanded ? 'rotate(180deg)' : 'rotate(0deg)', transition: 'transform 0.3s ease', fontSize: '0.8rem', color: 'var(--sage-dark)' }}>▼</span>
      </div>
      {expanded && (
        <div className="cm-expandable-body fade-in-slide">
          <p style={{ margin: '0 0 10px 0', lineHeight: '1.6' }}><b>What it means:</b> {f.meaning}</p>
          <p style={{ margin: '0 0 10px 0', lineHeight: '1.6' }}><b>Why it matters:</b> {f.why}</p>
          <p style={{ margin: '0 0 14px 0', lineHeight: '1.6' }}><b>What contributes to it:</b> {f.contributes}</p>
          <div style={{ padding: '14px 18px', background: 'rgba(110, 143, 123, 0.1)', borderLeft: '4px solid var(--sage)', borderRadius: '8px', fontSize: '0.92rem', lineHeight: '1.5' }}>
            💡 <b>How to improve:</b> {f.improve}
          </div>
        </div>
      )}
    </div>
  )
}

export default function UnderstandScore() {
  return (
    <div className="cm-page">
      <h1 className="cm-page-title">Understand Your Score</h1>
      <p className="cm-page-subtitle">
        CogniMap AI's predicted score comes from a Linear Regression model trained on exactly
        four factors, computed the same way for every student and every pathway. Here's what
        each one actually measures.
      </p>

      <div style={{ marginTop: '20px' }}>
        {FACTORS.map((f) => (
          <FactorCard key={f.name} f={f} />
        ))}
      </div>

      <div className="cm-expandable-card" style={{ marginTop: '24px' }}>
        <div className="cm-expandable-header" style={{ background: 'var(--cream)', pointerEvents: 'none' }}>
          <span>⚖️ How the four combine</span>
        </div>
        <div className="cm-expandable-body">
          <p style={{ margin: 0, lineHeight: '1.6' }}>
            The predicted CogniMap score for each pathway comes directly from the trained
            Linear Regression model, using these four values as its only inputs — the same
            four values shown on every recommendation card. No other information (such as your
            stated career interest or preferred specialization) feeds into the prediction.
          </p>
        </div>
      </div>
    </div>
  )
}
