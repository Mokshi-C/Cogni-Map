import { useLayoutEffect, useRef } from 'react'
import gsap from 'gsap'

export default function RouteTransition({ routeKey, prefersReducedMotion, children }) {
  const ref = useRef(null)

  useLayoutEffect(() => {
    const el = ref.current
    if (!el) return
    if (prefersReducedMotion) {
      gsap.set(el, { opacity: 1, y: 0 })
      return
    }
    gsap.fromTo(el, { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: 0.45, ease: 'power2.out' })
  }, [routeKey, prefersReducedMotion])

  return <div ref={ref} className="cm-route-transition">{children}</div>
}
