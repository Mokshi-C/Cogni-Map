import { useEffect, useLayoutEffect, useRef } from 'react'
import { NavLink, useLocation } from 'react-router-dom'
import gsap from 'gsap'
import mascot from '../assets/mascot.png'
import usePrefersReducedMotion from '../hooks/usePrefersReducedMotion'

const LINKS = [
  { to: '/', end: true, label: 'Home' },
  { to: '/existing-student', end: false, label: 'Existing Student' },
  { to: '/new-student', end: false, label: 'New Student' },
  { to: '/understand-your-score', end: false, label: 'Understand Your Score' },
]

function matchPath(pathname) {
  return LINKS.find((l) => (l.end ? pathname === l.to : pathname.startsWith(l.to)))?.to || '/'
}

export default function NavBar() {
  const location = useLocation()
  const navRef = useRef(null)
  const linkRefs = useRef({})
  const indicatorRef = useRef(null)
  const prefersReducedMotion = usePrefersReducedMotion()

  const moveIndicatorTo = (path, instant = false) => {
    const el = linkRefs.current[path]
    const indicator = indicatorRef.current
    const nav = navRef.current
    if (!el || !indicator || !nav) return
    const navBox = nav.getBoundingClientRect()
    const linkBox = el.getBoundingClientRect()
    const left = linkBox.left - navBox.left
    const width = linkBox.width
    if (prefersReducedMotion || instant) {
      gsap.set(indicator, { x: left, width })
    } else {
      gsap.to(indicator, { x: left, width, duration: 0.35, ease: 'power3.out' })
    }
  }

  useLayoutEffect(() => {
    moveIndicatorTo(matchPath(location.pathname))
  }, [location.pathname, prefersReducedMotion])

  useEffect(() => {
    const onResize = () => moveIndicatorTo(matchPath(location.pathname), true)
    window.addEventListener('resize', onResize)
    return () => window.removeEventListener('resize', onResize)
  }, [location.pathname])

  const handleLeave = () => moveIndicatorTo(matchPath(location.pathname))

  return (
    <div className="cm-navbar">
      <div className="cm-navbar-brand">
        <img src={mascot} alt="CogniMap mascot" />
        <span>CogniMap AI</span>
      </div>
      <nav className="cm-navlinks" ref={navRef} onMouseLeave={handleLeave}>
        <span className="cm-nav-indicator" ref={indicatorRef} aria-hidden="true" />
        {LINKS.map((l) => (
          <NavLink
            key={l.to}
            to={l.to}
            end={l.end}
            ref={(el) => { linkRefs.current[l.to] = el }}
            onMouseEnter={() => moveIndicatorTo(l.to)}
            className={({ isActive }) => (isActive ? 'active' : '')}
          >
            {l.label}
          </NavLink>
        ))}
      </nav>
    </div>
  )
}
