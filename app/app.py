"""CogniMap AI — Streamlit frontend. Visual layer only.
Backend pipeline (src/recommend.py) is untouched and unchanged."""
import base64
import sys
import time
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from recommend import recommend, students  # noqa: E402 — unchanged pipeline

APP_DIR = Path(__file__).resolve().parent

st.set_page_config(page_title="CogniMap AI", page_icon="🚀", layout="centered")

# ---------- load assets ----------
css = (APP_DIR / "style.css").read_text()
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

mascot_b64 = base64.b64encode((APP_DIR / "assets" / "mascot.png").read_bytes()).decode()
mascot_src = f"data:image/png;base64,{mascot_b64}"


# ---------- loading / intro screen ----------
def show_loading():
    st.markdown(
        f"""
        <div class="cm-loading-wrap">
            <img src="{mascot_src}" />
            <div class="cm-loading-title">CogniMap AI</div>
            <div class="cm-loading-subtitle">Personalized academic pathways, mapped for you.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    progress = st.progress(0)
    for pct in range(0, 101, 10):
        progress.progress(pct)
        time.sleep(0.035)
    st.session_state.loaded = True
    st.rerun()


if not st.session_state.get("loaded"):
    show_loading()
    st.stop()

# ---------- header ----------
st.markdown(
    f"""
    <div class="cm-header">
        <img src="{mascot_src}" />
        <div>
            <p class="cm-title">CogniMap AI</p>
            <p class="cm-subtitle">Personalized academic pathways, mapped for you.</p>
        </div>
    </div>
    <hr class="cm-rule">
    """,
    unsafe_allow_html=True,
)

# ---------- student selection (same data/pipeline as before) ----------
student_options = students.apply(
    lambda r: f"{r.student_id} — {r['name']} ({r.current_branch}, Sem {r.semester})", axis=1
)
choice = st.selectbox("Select a student", student_options)
student_id = choice.split(" — ")[0]
student_row = students.set_index("student_id").loc[student_id]

st.markdown(
    f"""
    <div class="cm-milestones">
        <div class="cm-milestone"><div class="label">Current Branch</div><div class="value">{student_row['current_branch']}</div></div>
        <div class="cm-milestone"><div class="label">Semester</div><div class="value">{int(student_row['semester'])}</div></div>
        <div class="cm-milestone"><div class="label">CGPA</div><div class="value">{student_row['cgpa']}</div></div>
    </div>
    """,
    unsafe_allow_html=True,
)

top_n = st.slider("Number of recommendations", 1, 7, 3)
go = st.button("Chart My Pathways →", type="primary")

# ---------- recommendations (same pipeline call, same fields) ----------
if go:
    results = recommend(student_id, top_n=top_n)

    st.markdown("### Recommended Pathways")
    st.markdown('<div class="cm-path-line"></div>', unsafe_allow_html=True)

    COMPONENTS = [
        ("Academic Fit", "academic_fit", ""),
        ("Skill Match", "skill_match_pct", "%"),
        ("Credit Completion", "credit_completion_pct", "%"),
        ("Prerequisite Satisfaction", "prerequisite_satisfaction_pct", "%"),
    ]

    for i, r in enumerate(results, start=1):
        rank_class = f"rank-{i}" if i <= 3 else "rank-3"

        # derived purely from the 4 existing component scores — no new backend logic
        scored = {label: r[key] for label, key, _ in COMPONENTS}
        strongest = max(scored, key=scored.get)
        weakest = min(scored, key=scored.get)

        comp_html = ""
        for label, key, suffix in COMPONENTS:
            val = r[key]
            pct_width = min(val, 100) if suffix == "%" else min(val, 100)
            comp_html += f"""
            <div class="cm-comp">
                <div class="label">{label}</div>
                <div class="value">{val}{suffix}</div>
                <div class="cm-bar-track"><div class="cm-bar-fill" style="width:{pct_width}%;"></div></div>
            </div>"""

        st.markdown(
            f"""
            <div class="cm-card {rank_class}">
                <div class="cm-card-top">
                    <div><span class="cm-rank-badge">#{i}</span><span class="cm-branch-name">{r['branch_name']}</span></div>
                    <div class="cm-score">{r['predicted_score']}</div>
                </div>
                <div class="cm-why">🧭 Why this pathway? Strongest factor: <b>{strongest}</b></div>
                <div class="cm-components">{comp_html}</div>
                <div class="cm-improve">💡 How to improve: focus on <b>{weakest}</b> — it's the lowest-scoring factor here.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.caption(
        "Scores predicted by a Linear Regression model (R² = 0.9999 on held-out test data) "
        "trained on academic_fit, skill_match_pct, credit_completion_pct, and "
        "prerequisite_satisfaction_pct for each (student, branch) pair."
    )
