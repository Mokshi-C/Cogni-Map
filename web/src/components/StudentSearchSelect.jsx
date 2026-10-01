import { useMemo, useState, useRef, useEffect } from 'react'

/** Filters the students array (already fetched from the API — no separate data
 * source) by student_id, name, or current_branch as the user types. */
export default function StudentSearchSelect({ students, value, onChange }) {
  const [query, setQuery] = useState('')
  const [open, setOpen] = useState(false)
  const boxRef = useRef(null)

  const selected = students.find((s) => s.student_id === value)

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase()
    if (!q) return students.slice(0, 25)
    return students
      .filter(
        (s) =>
          s.student_id.toLowerCase().includes(q) ||
          s.name.toLowerCase().includes(q) ||
          s.current_branch.toLowerCase().includes(q)
      )
      .slice(0, 25)
  }, [query, students])

  useEffect(() => {
    function handleClickOutside(e) {
      if (boxRef.current && !boxRef.current.contains(e.target)) setOpen(false)
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  return (
    <div className="cm-search-box" ref={boxRef}>
      <div className="cm-search-input-wrap">
        <span className="cm-search-icon">🔍</span>
        <input
          type="text"
          className="cm-search-input"
          placeholder="Search student by ID, name or branch..."
          value={open ? query : selected ? `${selected.student_id} — ${selected.name} (${selected.current_branch}, Sem ${selected.semester})` : query}
          onFocus={() => { setOpen(true); setQuery('') }}
          onChange={(e) => setQuery(e.target.value)}
        />
      </div>
      {open && (
        <div className="cm-search-dropdown">
          {filtered.length === 0 && <div className="cm-search-empty">No matching students</div>}
          {filtered.map((s) => (
            <div
              key={s.student_id}
              className="cm-search-option"
              onClick={() => { onChange(s.student_id); setOpen(false); setQuery('') }}
            >
              {s.student_id} — {s.name} ({s.current_branch}, Sem {s.semester})
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
