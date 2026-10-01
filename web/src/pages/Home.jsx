import { useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import mascot from '../assets/mascot.png'

const FEATURES = [
  ['Academic Fit', 'How well your marks in relevant completed courses line up with a pathway.'],
  ['Skill Match', 'How much your skills overlap with what careers in that pathway need.'],
  ['Credit Completion', 'How many of the required credits for that pathway you already have.'],
  ['Prerequisite Satisfaction', 'How many prerequisites for your remaining courses are already done.'],
]

function HeroAnimation() {
  const canvasRef = useRef(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    let animationFrameId

    const resize = () => {
      const parent = canvas.parentElement
      if (!parent) return
      canvas.width = parent.offsetWidth
      canvas.height = parent.offsetHeight || 260
    }
    resize()
    window.addEventListener('resize', resize)

    const nodes = Array.from({ length: 18 }, () => ({
      x: Math.random() * canvas.width,
      y: Math.random() * (canvas.height || 260),
      vx: (Math.random() - 0.5) * 0.4,
      vy: (Math.random() - 0.5) * 0.4,
      r: Math.random() * 3 + 1.5,
    }))

    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      
      nodes.forEach((n) => {
        n.x += n.vx
        n.y += n.vy
        if (n.x < 0 || n.x > canvas.width) n.vx = -n.vx
        if (n.y < 0 || n.y > canvas.height) n.vy = -n.vy
        
        ctx.beginPath()
        ctx.arc(n.x, n.y, n.r, 0, Math.PI * 2)
        ctx.fillStyle = '#6E8F7B'
        ctx.fill()
      })

      ctx.strokeStyle = '#D9552E'
      ctx.lineWidth = 0.5
      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const dx = nodes[i].x - nodes[j].x
          const dy = nodes[i].y - nodes[j].y
          const dist = Math.sqrt(dx * dx + dy * dy)
          if (dist < 90) {
            ctx.beginPath()
            ctx.moveTo(nodes[i].x, nodes[i].y)
            ctx.lineTo(nodes[j].x, nodes[j].y)
            ctx.globalAlpha = 0.18 * (1 - dist / 90)
            ctx.stroke()
          }
        }
      }
      ctx.globalAlpha = 1.0
      animationFrameId = requestAnimationFrame(draw)
    }
    draw()

    return () => {
      window.removeEventListener('resize', resize)
      cancelAnimationFrame(animationFrameId)
    }
  }, [])

  return (
    <canvas 
      ref={canvasRef} 
      style={{ 
        position: 'absolute', 
        top: 0, 
        left: 0, 
        width: '100%', 
        height: '100%', 
        pointerEvents: 'none', 
        zIndex: 0 
      }} 
    />
  )
}

export default function Home() {
  return (
    <div className="cm-page">
      <div className="cm-hero" style={{ position: 'relative', overflow: 'hidden', padding: '40px 20px', borderRadius: '16px', border: '1px solid var(--line)', background: 'var(--cream)', marginBottom: '30px' }}>
        <HeroAnimation />
        <div style={{ position: 'relative', zIndex: 1 }}>
          <img src={mascot} alt="CogniMap mascot" className="cm-hero-mascot" style={{ width: '180px' }} />
          <h1 className="cm-hero-title" style={{ fontSize: '2.8rem' }}>CogniMap AI</h1>
          <p className="cm-hero-tagline" style={{ fontSize: '1.25rem', marginTop: '6px' }}>Your academic path, mapped around YOU.</p>
          <p className="cm-hero-blurb" style={{ fontSize: '0.98rem', maxWidth: '600px', margin: '14px auto 0 auto' }}>
            CogniMap AI looks at what you've actually studied — your marks, your skills, and
            the credits and prerequisites you've already completed — and ranks which CSE-allied
            academic pathways genuinely fit you, using a trained model instead of guesswork.
          </p>
          <div className="cm-hero-buttons" style={{ marginTop: '26px' }}>
            <Link to="/existing-student" className="cm-button">I'm an existing student →</Link>
            <Link to="/new-student" className="cm-button cm-button-secondary">I'm a new student →</Link>
          </div>
        </div>
      </div>

      <h2 className="cm-section-title">Why personalized pathways?</h2>
      <p className="cm-section-text">
        Choosing a specialization is easier with real evidence: which of your completed courses
        already count toward a pathway, which skills you're missing, and how close you are to
        being ready — rather than relying on gut feeling alone.
      </p>

      <h2 className="cm-section-title">How it works</h2>
      <div className="cm-flow" style={{ background: '#fff', border: '1px solid var(--line)', padding: '20px', borderRadius: '12px', justifyContent: 'center' }}>
        {['Student Data', 'Academic & Skill Analysis', 'Four Pathway Factors', 'ML Score Prediction', 'Ranked Pathways'].map((step, i, arr) => (
          <div className="cm-flow-step" key={step}>
            <div className="cm-flow-box" style={{ background: 'var(--parchment)', padding: '12px 18px', border: '1px solid var(--line)' }}>{step}</div>
            {i < arr.length - 1 && <div className="cm-flow-arrow" style={{ fontSize: '1.2rem', color: 'var(--sage)' }}>➔</div>}
          </div>
        ))}
      </div>

      <h2 className="cm-section-title">The four pathway factors</h2>
      <div className="cm-feature-grid">
        {FEATURES.map(([title, desc]) => (
          <div className="cm-feature-card" key={title} style={{ transition: 'transform 0.25s ease' }}>
            <div className="cm-feature-title" style={{ color: 'var(--coral-dark)' }}>{title}</div>
            <div className="cm-feature-desc">{desc}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
