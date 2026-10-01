import { useEffect, useState } from 'react'
import { Routes, Route, useLocation } from 'react-router-dom'
import mascot from './assets/mascot.png'
import NavBar from './components/NavBar'
import RouteTransition from './components/RouteTransition'
import Home from './pages/Home'
import ExistingStudent from './pages/ExistingStudent'
import NewStudent from './pages/NewStudent'
import UnderstandScore from './pages/UnderstandScore'
import usePrefersReducedMotion from './hooks/usePrefersReducedMotion'

function Loading() {
  return (
    <div className="cm-loading-wrap">
      <img src={mascot} alt="CogniMap mascot" className="cm-float" />
      <div className="cm-loading-title">CogniMap AI</div>
      <div className="cm-loading-subtitle">Personalized academic pathways, mapped for you.</div>
    </div>
  )
}

function BackgroundNodes() {
  const [nodes, setNodes] = useState([])
  useEffect(() => {
    const initialNodes = Array.from({ length: 15 }, () => ({
      x: Math.random() * 100,
      y: Math.random() * 100,
      vx: (Math.random() - 0.5) * 0.04,
      vy: (Math.random() - 0.5) * 0.04,
      r: Math.random() * 4 + 2,
    }))
    setNodes(initialNodes)

    let animationFrameId
    const update = () => {
      setNodes((prev) =>
        prev.map((n) => {
          let nx = n.x + n.vx
          let ny = n.y + n.vy
          let nvx = n.vx
          let nvy = n.vy
          if (nx < 0 || nx > 100) nvx = -nvx
          if (ny < 0 || ny > 100) nvy = -nvy
          return { ...n, x: nx, y: ny, vx: nvx, vy: nvy }
        })
      )
      animationFrameId = requestAnimationFrame(update)
    }
    animationFrameId = requestAnimationFrame(update)
    return () => cancelAnimationFrame(animationFrameId)
  }, [])

  return (
    <svg className="cm-bg-nodes">
      {nodes.map((n, i) => (
        <circle key={i} cx={`${n.x}%`} cy={`${n.y}%`} r={n.r} fill="#6E8F7B" opacity="0.3" />
      ))}
      {nodes.map((n1, i) => {
        return nodes.slice(i + 1).map((n2, j) => {
          const dx = n1.x - n2.x
          const dy = n1.y - n2.y
          const dist = Math.sqrt(dx * dx + dy * dy)
          if (dist < 25) {
            return (
              <line
                key={`${i}-${j}`}
                x1={`${n1.x}%`}
                y1={`${n1.y}%`}
                x2={`${n2.x}%`}
                y2={`${n2.y}%`}
                stroke="#6E8F7B"
                strokeWidth="0.5"
                opacity={0.2 * (1 - dist / 25)}
              />
            )
          }
          return null
        })
      })}
    </svg>
  )
}

export default function App() {
  const [loaded, setLoaded] = useState(false)
  const location = useLocation()
  const prefersReducedMotion = usePrefersReducedMotion()

  useEffect(() => {
    const timer = setTimeout(() => setLoaded(true), 1400)
    return () => clearTimeout(timer)
  }, [])

  if (!loaded) return <Loading />

  return (
    <>
      <BackgroundNodes />
      <NavBar />
      <RouteTransition routeKey={location.pathname} prefersReducedMotion={prefersReducedMotion}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/existing-student" element={<ExistingStudent />} />
          <Route path="/new-student" element={<NewStudent />} />
          <Route path="/understand-your-score" element={<UnderstandScore />} />
        </Routes>
      </RouteTransition>
    </>
  )
}
