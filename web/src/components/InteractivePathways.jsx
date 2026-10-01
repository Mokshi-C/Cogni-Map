import { useState } from 'react'

export function TechStackConstellation({ targetBranch }) {
  const [selectedNode, setSelectedNode] = useState(null)

  // Map pathways to specific custom tech stacks
  const stackData = {
    'AIML': [
      { id: 'python', label: 'Python', desc: 'Core language for ML algorithms and scripting.', level: 'Advanced', x: 150, y: 30 },
      { id: 'numpy', label: 'NumPy', desc: 'Matrix manipulation and numerical calculations.', level: 'Intermediate', x: 80, y: 100 },
      { id: 'pandas', label: 'Pandas', desc: 'Data cleaning, analytics, and frame operations.', level: 'Intermediate', x: 220, y: 100 },
      { id: 'ml', label: 'Machine Learning', desc: 'Supervised and unsupervised models (Scikit-Learn).', level: 'Advanced', x: 150, y: 180 },
      { id: 'tensorflow', label: 'TensorFlow', desc: 'Production-ready deep learning frameworks.', level: 'Beginner', x: 80, y: 250 },
      { id: 'pytorch', label: 'PyTorch', desc: 'Flexible dynamic computation graphs for research.', level: 'Beginner', x: 220, y: 250 }
    ],
    'CYSEC': [
      { id: 'linux', label: 'Linux OS', desc: 'Operating system internals, bash scripting, permissions.', level: 'Advanced', x: 150, y: 30 },
      { id: 'networks', label: 'TCP/IP Networks', desc: 'Protocols, packet analysis, Wireshark utilities.', level: 'Advanced', x: 80, y: 100 },
      { id: 'cryptography', label: 'Cryptography', desc: 'Asymmetric cryptography, hashes, and secure handshakes.', level: 'Intermediate', x: 220, y: 100 },
      { id: 'pentesting', label: 'Penetration Testing', desc: 'Vulnerability assessment, exploit framing, security scanning.', level: 'Intermediate', x: 150, y: 180 },
      { id: 'soc', label: 'SOC Operations', desc: 'Security information and event logging analysis.', level: 'Beginner', x: 80, y: 250 },
      { id: 'cloudsec', label: 'Cloud Security', desc: 'IAM architecture, network rules, virtual firewalls.', level: 'Beginner', x: 220, y: 250 }
    ],
    'default': [
      { id: 'python', label: 'Python', desc: 'General programming and system scripts.', level: 'Advanced', x: 150, y: 30 },
      { id: 'sql', label: 'SQL DB', desc: 'Relational data query design and indexing.', level: 'Advanced', x: 80, y: 100 },
      { id: 'git', label: 'Git & VCS', desc: 'Collaborative development and trunk-based deployment workflows.', level: 'Intermediate', x: 220, y: 100 },
      { id: 'algorithms', label: 'Data Structures', desc: 'Searching, sorting, tree/graph logic, complexity scaling.', level: 'Advanced', x: 150, y: 180 },
      { id: 'cloud', label: 'Cloud Systems', desc: 'Containerized deployment, virtual compute hosts.', level: 'Beginner', x: 150, y: 250 }
    ]
  }

  const nodes = stackData[targetBranch] || stackData['default']

  // Define connection lines between matching node coordinates
  const connections = nodes.length === 6 ? [
    { from: 'python', to: 'numpy' },
    { from: 'python', to: 'pandas' },
    { from: 'numpy', to: 'ml' },
    { from: 'pandas', to: 'ml' },
    { from: 'ml', to: 'tensorflow' },
    { from: 'ml', to: 'pytorch' }
  ] : [
    { from: 'python', to: 'sql' },
    { from: 'python', to: 'git' },
    { from: 'sql', to: 'algorithms' },
    { from: 'git', to: 'algorithms' },
    { from: 'algorithms', to: 'cloud' }
  ]

  return (
    <div className="cm-semester-block" style={{ marginTop: '28px' }}>
      <div className="cm-semester-heading" style={{ fontSize: '1.25rem' }}>Tech Stack to Master</div>
      <p className="cm-muted" style={{ marginBottom: '16px' }}>
        Interact with the technology constellation below to inspect critical core stacks.
      </p>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', alignItems: 'center' }}>
        <div style={{ position: 'relative', width: '300px', height: '280px', background: 'var(--cream)', borderRadius: '12px', border: '1px solid var(--line)' }}>
          {/* Connection lines */}
          <svg style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', pointerEvents: 'none' }}>
            {connections.map((c, idx) => {
              const fromNode = nodes.find(n => n.id === c.from)
              const toNode = nodes.find(n => n.id === c.to)
              if (!fromNode || !toNode) return null
              return (
                <line
                  key={idx}
                  x1={fromNode.x}
                  y1={fromNode.y}
                  x2={toNode.x}
                  y2={toNode.y}
                  stroke="var(--sage)"
                  strokeWidth="2.5"
                  strokeDasharray="4,3"
                />
              )
            })}
          </svg>

          {/* Technology Nodes */}
          {nodes.map(n => {
            const isSelected = selectedNode?.id === n.id
            return (
              <button
                key={n.id}
                type="button"
                onClick={() => setSelectedNode(n)}
                style={{
                  position: 'absolute',
                  left: `${n.x - 45}px`,
                  top: `${n.y - 18}px`,
                  width: '90px',
                  height: '36px',
                  borderRadius: '18px',
                  background: isSelected ? 'var(--coral)' : '#fff',
                  color: isSelected ? '#fff' : 'var(--ink)',
                  border: `2px solid ${isSelected ? 'var(--coral-dark)' : 'var(--sage)'}`,
                  fontSize: '0.82rem',
                  fontWeight: '600',
                  cursor: 'pointer',
                  zIndex: 5,
                  boxShadow: '0 4px 8px rgba(0,0,0,0.05)',
                  transition: 'all 0.25s cubic-bezier(0.4, 0, 0.2, 1)'
                }}
              >
                {n.label}
              </button>
            )
          })}
        </div>

        {/* Selected Tech Card */}
        {selectedNode ? (
          <div className="cm-card fade-in-slide" style={{ padding: '16px', borderLeftColor: 'var(--amber)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
              <strong style={{ fontSize: '1.05rem', color: 'var(--coral-dark)' }}>{selectedNode.label}</strong>
              <span className="cm-rank-badge" style={{ background: 'var(--sage)', fontSize: '0.72rem' }}>{selectedNode.level}</span>
            </div>
            <p style={{ margin: '0 0 8px 0', fontSize: '0.88rem', color: 'var(--ink)', lineHeight: '1.4' }}>
              {selectedNode.desc}
            </p>
          </div>
        ) : (
          <div style={{ textAlign: 'center', fontSize: '0.85rem', color: 'var(--sage-dark)', fontStyle: 'italic', padding: '10px' }}>
            💡 Click on any node above to review course relevance.
          </div>
        )}
      </div>
    </div>
  )
}

export function LearningRoadmap({ targetBranch }) {
  const roadmaps = {
    'AIML': [
      { step: 'Python Fundamentals', status: 'Completed', detail: 'Learn programming fundamentals, variables, loops, functions, lists.' },
      { step: 'Data Analysis & Libraries', status: 'Current', detail: 'Learn data analysis using pandas and vector math with NumPy.' },
      { step: 'Statistics & Probability', status: 'Upcoming', detail: 'Understand descriptive statistics, Bayes theorem, distributions.' },
      { step: 'Machine Learning Models', status: 'Upcoming', detail: 'Supervised learning regressions, classification trees, random forests.' }
    ],
    'CYSEC': [
      { step: 'Networks & Protocols', status: 'Completed', detail: 'Understand DNS resolution, IP routing, subnet masks, packets.' },
      { step: 'Linux Internals & Scripting', status: 'Current', detail: 'Use command line bash utilities, process hooks, shell scripts.' },
      { step: 'Secure Infrastructure Design', status: 'Upcoming', detail: 'Configure access rules, SSL, load balancers, database firewalls.' },
      { step: 'Incident Response & Analysis', status: 'Upcoming', detail: 'Review syslog outputs, detect brute force, set security blocks.' }
    ],
    'default': [
      { step: 'Core Programming', status: 'Completed', detail: 'Variable assignments, iterations, control logs, modular functions.' },
      { step: 'Database Engineering', status: 'Current', detail: 'Write relational SQL queries, table indexing, connection pools.' },
      { step: 'Data Structures', status: 'Upcoming', detail: 'List traversals, queue structures, complexity scale models.' },
      { step: 'Production Deployment', status: 'Upcoming', detail: 'Deploy services on virtual host platforms, configure HTTPS rules.' }
    ]
  }

  const steps = roadmaps[targetBranch] || roadmaps['default']

  return (
    <div className="cm-semester-block" style={{ marginTop: '28px' }}>
      <div className="cm-semester-heading" style={{ fontSize: '1.25rem' }}>Learning Roadmap</div>
      <p className="cm-muted" style={{ marginBottom: '18px' }}>
        A progressive view of critical modules required to reach your target career.
      </p>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', position: 'relative', paddingLeft: '24px' }}>
        <div style={{ position: 'absolute', top: '10px', bottom: '10px', left: '8px', width: '2px', background: 'var(--sage)' }} />

        {steps.map((s, idx) => {
          let badgeColor = '#6E8F7B'
          let bulletChar = '○'
          if (s.status === 'Completed') {
            badgeColor = 'var(--sage)'
            bulletChar = '✓'
          } else if (s.status === 'Current') {
            badgeColor = 'var(--coral)'
            bulletChar = '●'
          } else {
            badgeColor = 'var(--amber)'
          }

          return (
            <div key={idx} className="fade-in-slide" style={{ position: 'relative' }}>
              {/* Bullet node on timeline */}
              <div 
                style={{
                  position: 'absolute',
                  left: '-23px',
                  top: '2px',
                  width: '16px',
                  height: '16px',
                  borderRadius: '50%',
                  background: '#fff',
                  border: `2px solid ${badgeColor}`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '0.68rem',
                  fontWeight: 'bold',
                  color: badgeColor,
                  zIndex: 2
                }}
              >
                {bulletChar}
              </div>

              <div>
                <div style={{ display: 'flex', gap: '10px', alignItems: 'center', marginBottom: '2px' }}>
                  <strong style={{ fontSize: '0.95rem' }}>{s.step}</strong>
                  <span style={{ fontSize: '0.7rem', padding: '2px 8px', borderRadius: '10px', background: 'var(--cream)', color: badgeColor, fontWeight: 'bold', border: `1px solid ${badgeColor}` }}>
                    {s.status}
                  </span>
                </div>
                <p style={{ margin: 0, fontSize: '0.85rem', color: 'var(--sage-dark)', lineHeight: '1.4' }}>
                  {s.detail}
                </p>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
