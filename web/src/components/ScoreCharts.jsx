import {
  BarChart, Bar, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
} from 'recharts'

const COLORS = ['#D9552E', '#E0A62E', '#6E8F7B', '#B8441F', '#556F5F', '#C9A24B', '#8AA894']

export function ScoreBarChart({ results }) {
  const data = results.map((r) => ({ name: r.branch_id, score: r.predicted_score }))
  return (
    <ResponsiveContainer width="100%" height={Math.max(180, results.length * 44)}>
      <BarChart data={data} layout="vertical" margin={{ left: 10, right: 20 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#E4D9C4" horizontal={false} />
        <XAxis type="number" domain={[0, 100]} tick={{ fill: '#556F5F', fontSize: 12 }} />
        <YAxis type="category" dataKey="name" tick={{ fill: '#2B2622', fontSize: 13 }} width={60} />
        <Tooltip contentStyle={{ background: '#FBF5EA', border: '1px solid #E4D9C4', borderRadius: 8 }} />
        <Bar dataKey="score" radius={[0, 6, 6, 0]}>
          {data.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}

export function FactorRadarChart({ rec }) {
  const data = [
    { factor: 'Academic Fit', value: rec.academic_fit },
    { factor: 'Skill Match', value: rec.skill_match_pct },
    { factor: 'Credit Completion', value: rec.credit_completion_pct },
    { factor: 'Prerequisite Satisfaction', value: rec.prerequisite_satisfaction_pct },
  ]
  return (
    <ResponsiveContainer width="100%" height={280}>
      <RadarChart data={data} outerRadius="75%">
        <PolarGrid stroke="#E4D9C4" />
        <PolarAngleAxis dataKey="factor" tick={{ fill: '#2B2622', fontSize: 11 }} />
        <PolarRadiusAxis domain={[0, 100]} tick={{ fill: '#556F5F', fontSize: 10 }} />
        <Radar dataKey="value" stroke="#D9552E" fill="#D9552E" fillOpacity={0.35} />
      </RadarChart>
    </ResponsiveContainer>
  )
}
