import streamlit as st
import time
import random
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from Rubik import Cube, astar, ALL_MOVES

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="2×2×2 Rubik's Cube Solver",
    page_icon="🧊",
    layout="wide",
)

# ─── Styling ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Rajdhani', sans-serif;
}

/* Dark background */
.stApp {
    background: #0d0d0f;
    color: #e8e8e8;
}

h1, h2, h3 {
    font-family: 'Share Tech Mono', monospace !important;
}

/* Cube grid cell */
.tile {
    display: inline-block;
    width: 48px;
    height: 48px;
    border-radius: 6px;
    margin: 3px;
    border: 2px solid rgba(255,255,255,0.15);
    box-shadow: inset 0 2px 4px rgba(0,0,0,0.4), 0 0 8px rgba(255,255,255,0.05);
    transition: transform 0.2s ease;
}
.tile:hover { transform: scale(1.08); }

.face-label {
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
    color: #666;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 4px;
}

.cube-row {
    display: flex;
    align-items: center;
    justify-content: center;
    line-height: 0;
}

.cube-wrap {
    background: #16161a;
    border: 1px solid #2a2a2e;
    border-radius: 16px;
    padding: 24px;
    display: inline-block;
    box-shadow: 0 8px 32px rgba(0,0,0,0.6);
}

/* Move badge */
.move-badge {
    display: inline-block;
    background: #1e1e24;
    border: 1px solid #3a3a44;
    border-radius: 8px;
    padding: 4px 12px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 14px;
    color: #7DF9AA;
    margin: 3px;
}

.move-badge.current {
    background: #7DF9AA22;
    border-color: #7DF9AA;
    color: #7DF9AA;
    box-shadow: 0 0 12px #7DF9AA44;
}

.move-badge.done {
    color: #555;
    border-color: #2a2a2e;
}

/* Stat card */
.stat-card {
    background: #16161a;
    border: 1px solid #2a2a2e;
    border-radius: 12px;
    padding: 16px 20px;
    text-align: center;
}
.stat-value {
    font-family: 'Share Tech Mono', monospace;
    font-size: 28px;
    color: #7DF9AA;
    font-weight: bold;
}
.stat-label {
    font-size: 12px;
    color: #666;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-top: 4px;
}

/* Section header */
.section-header {
    font-family: 'Share Tech Mono', monospace;
    font-size: 13px;
    color: #444;
    letter-spacing: 3px;
    text-transform: uppercase;
    border-bottom: 1px solid #1e1e24;
    padding-bottom: 8px;
    margin-bottom: 16px;
}

/* Buttons */
.stButton > button {
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: 1px !important;
    border-radius: 8px !important;
    transition: all 0.2s !important;
}

/* Input */
.stTextInput > div > div > input {
    font-family: 'Share Tech Mono', monospace !important;
    background: #16161a !important;
    color: #e8e8e8 !important;
    border: 1px solid #2a2a2e !important;
    border-radius: 8px !important;
}

/* Solution step area */
.step-box {
    background: #16161a;
    border: 1px solid #2a2a2e;
    border-radius: 12px;
    padding: 20px;
    margin-top: 12px;
}

.goal-banner {
    background: linear-gradient(135deg, #7DF9AA22, #00d4ff22);
    border: 1px solid #7DF9AA;
    border-radius: 12px;
    padding: 16px 24px;
    text-align: center;
    font-family: 'Share Tech Mono', monospace;
    font-size: 18px;
    color: #7DF9AA;
    margin: 12px 0;
    box-shadow: 0 0 24px #7DF9AA22;
}

.already-solved {
    background: linear-gradient(135deg, #7DF9AA22, #00d4ff22);
    border: 1px solid #7DF9AA55;
    border-radius: 10px;
    padding: 12px 20px;
    font-family: 'Share Tech Mono', monospace;
    color: #7DF9AA;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ─── Colour map ──────────────────────────────────────────────────────────────
COLOUR_HEX = {
    'W': '#f0f0f0',
    'R': '#e8273a',
    'G': '#22c55e',
    'Y': '#facc15',
    'O': '#f97316',
    'B': '#3b82f6',
}
COLOUR_NAME = {'W': 'White', 'R': 'Red', 'G': 'Green',
               'Y': 'Yellow', 'O': 'Orange', 'B': 'Blue'}

# ─── Helpers ─────────────────────────────────────────────────────────────────
def tile(colour):
    hex_col = COLOUR_HEX.get(colour, '#333')
    return f'<span class="tile" style="background:{hex_col};"></span>'

def render_cube(state):
    """Return HTML cross-layout for a 24-char state tuple/string."""
    s = list(state)
    empty = '<span style="display:inline-block;width:48px;height:48px;margin:3px;"></span>'

    rows = [
        # top face
        f'<div class="cube-row">{empty}{empty}{tile(s[0])}{tile(s[1])}{empty}{empty}{empty}{empty}</div>',
        f'<div class="cube-row">{empty}{empty}{tile(s[2])}{tile(s[3])}{empty}{empty}{empty}{empty}</div>',
        # middle band
        f'<div class="cube-row">{tile(s[16])}{tile(s[17])}{tile(s[8])}{tile(s[9])}{tile(s[4])}{tile(s[5])}{tile(s[20])}{tile(s[21])}</div>',
        f'<div class="cube-row">{tile(s[18])}{tile(s[19])}{tile(s[10])}{tile(s[11])}{tile(s[6])}{tile(s[7])}{tile(s[22])}{tile(s[23])}</div>',
        # bottom face
        f'<div class="cube-row">{empty}{empty}{tile(s[12])}{tile(s[13])}{empty}{empty}{empty}{empty}</div>',
        f'<div class="cube-row">{empty}{empty}{tile(s[14])}{tile(s[15])}{empty}{empty}{empty}{empty}</div>',
    ]
    legend = "".join(
        f'<span style="font-family:Share Tech Mono,monospace;font-size:11px;'
        f'color:{COLOUR_HEX[c]};margin-right:10px;">■ {COLOUR_NAME[c]}</span>'
        for c in ['W','R','G','Y','O','B']
    )
    return (
        f'<div class="cube-wrap">{"".join(rows)}</div>'
        f'<div style="margin-top:12px;text-align:center;">{legend}</div>'
    )

DEFAULT_STATE = "WWWWRRRRGGGGYYYYOOOOBBBB"

# ─── Session state init ───────────────────────────────────────────────────────
for key, val in {
    "cube_state": DEFAULT_STATE,
    "solution": None,
    "step": 0,
    "stats": None,
    "history": [DEFAULT_STATE],
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ─── Title ───────────────────────────────────────────────────────────────────
st.markdown("# 🧊 2×2×2 Rubik's Cube Solver")
st.markdown('<p style="color:#555;font-family:Share Tech Mono,monospace;font-size:13px;letter-spacing:2px;">A* SEARCH · ADMISSIBLE HEURISTIC · OPTIMAL SOLUTION</p>', unsafe_allow_html=True)
st.divider()

# ─── Layout: left panel | right panel ───────────────────────────────────────
left, right = st.columns([1, 1], gap="large")

# ════════════════════════════════════════════════
# LEFT — Cube display + controls
# ════════════════════════════════════════════════
with left:
    st.markdown('<div class="section-header">Current State</div>', unsafe_allow_html=True)

    current_cube = Cube(st.session_state.cube_state)
    st.markdown(render_cube(st.session_state.cube_state), unsafe_allow_html=True)

    # goal check badge
    if current_cube.is_goal():
        st.markdown('<div class="already-solved">✔ SOLVED</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Manual state input ──────────────────────────────────────────────
    st.markdown('<div class="section-header">Load State</div>', unsafe_allow_html=True)
    raw_input = st.text_input(
        "24-char state (e.g. WWWWRRRRGGGGYYYYOOOOBBBB)",
        value=st.session_state.cube_state,
        label_visibility="collapsed",
        placeholder="WWWWRRRRGGGGYYYYOOOOBBBB",
    )
    col_load, col_reset = st.columns(2)
    with col_load:
        if st.button("📥 Load State", use_container_width=True):
            clean = raw_input.replace(" ", "").upper()
            if len(clean) == 24:
                st.session_state.cube_state = clean
                st.session_state.solution = None
                st.session_state.step = 0
                st.session_state.stats = None
                st.session_state.history = [clean]
                st.rerun()
            else:
                st.error("State must be exactly 24 characters.")
    with col_reset:
        if st.button("🔄 Reset to Solved", use_container_width=True):
            st.session_state.cube_state = DEFAULT_STATE
            st.session_state.solution = None
            st.session_state.step = 0
            st.session_state.stats = None
            st.session_state.history = [DEFAULT_STATE]
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Scramble controls ───────────────────────────────────────────────
    st.markdown('<div class="section-header">Scramble</div>', unsafe_allow_html=True)

    sc1, sc2 = st.columns([2, 1])
    with sc1:
        n_moves = st.slider("Number of random moves", 1, 10, 5, label_visibility="collapsed")
    with sc2:
        st.markdown(f'<div style="padding-top:8px;color:#888;font-size:13px;">{n_moves} moves</div>', unsafe_allow_html=True)

    if st.button("🎲 Scramble!", use_container_width=True):
        cube = Cube(st.session_state.cube_state)
        applied = []
        for _ in range(n_moves):
            m = random.choice(ALL_MOVES)
            cube = cube.apply_move(m)
            applied.append(m)
        st.session_state.cube_state = "".join(cube.state)
        st.session_state.solution = None
        st.session_state.step = 0
        st.session_state.stats = None
        st.session_state.history = [st.session_state.cube_state]
        st.toast(f"Scrambled with: {' '.join(applied)}", icon="🎲")
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Apply single move ───────────────────────────────────────────────
    st.markdown('<div class="section-header">Apply Move</div>', unsafe_allow_html=True)
    move_cols = st.columns(6)
    base_moves = ['U', 'F', 'R', 'B', 'L', 'D']
    for i, bm in enumerate(base_moves):
        with move_cols[i]:
            if st.button(bm, use_container_width=True, key=f"mv_{bm}"):
                cube = Cube(st.session_state.cube_state)
                cube = cube.apply_move(bm)
                st.session_state.cube_state = "".join(cube.state)
                st.session_state.solution = None
                st.session_state.step = 0
                st.session_state.stats = None
                st.rerun()

    ccw_cols = st.columns(6)
    for i, bm in enumerate(base_moves):
        with ccw_cols[i]:
            if st.button(f"{bm}'", use_container_width=True, key=f"mv_{bm}p"):
                cube = Cube(st.session_state.cube_state)
                cube = cube.apply_move(f"{bm}'")
                st.session_state.cube_state = "".join(cube.state)
                st.session_state.solution = None
                st.session_state.step = 0
                st.session_state.stats = None
                st.rerun()

# ════════════════════════════════════════════════
# RIGHT — Solver
# ════════════════════════════════════════════════
with right:
    st.markdown('<div class="section-header">A* Solver</div>', unsafe_allow_html=True)

    current_cube = Cube(st.session_state.cube_state)

    if current_cube.is_goal():
        st.markdown('<div class="goal-banner">✨ Cube is already solved!</div>', unsafe_allow_html=True)
    else:
        if st.button("🚀 Solve with A*", use_container_width=True, type="primary"):
            with st.spinner("Running A* Search... this may take a few seconds for deep scrambles."):
                t0 = time.time()
                sol, gen, exp, elapsed = astar(current_cube)
            if sol:
                st.session_state.solution = sol
                st.session_state.step = 0
                st.session_state.stats = {"gen": gen, "exp": exp, "time": elapsed, "moves": len(sol)}
                st.session_state.history = [st.session_state.cube_state]
                # Pre-compute all intermediate states
                cube = Cube(st.session_state.cube_state)
                for m in sol:
                    cube = cube.apply_move(m)
                    st.session_state.history.append("".join(cube.state))
                st.rerun()
            else:
                st.error("No solution found.")

    # ── Stats ────────────────────────────────────────────────────────────
    if st.session_state.stats:
        st.markdown("<br>", unsafe_allow_html=True)
        stats = st.session_state.stats
        c1, c2, c3, c4 = st.columns(4)
        for col, val, label in [
            (c1, stats["moves"], "Moves"),
            (c2, f'{stats["gen"]:,}', "Generated"),
            (c3, f'{stats["exp"]:,}', "Expanded"),
            (c4, f'{stats["time"]:.2f}s', "Time"),
        ]:
            with col:
                st.markdown(
                    f'<div class="stat-card"><div class="stat-value">{val}</div>'
                    f'<div class="stat-label">{label}</div></div>',
                    unsafe_allow_html=True
                )

    # ── Solution playback ─────────────────────────────────────────────────
    if st.session_state.solution:
        sol = st.session_state.solution
        step = st.session_state.step

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-header">Solution Playback</div>', unsafe_allow_html=True)

        # Move sequence with highlights
        badges = ""
        for i, m in enumerate(sol):
            if i < step:
                cls = "done"
            elif i == step:
                cls = "current"
            else:
                cls = ""
            badges += f'<span class="move-badge {cls}">{m}</span>'
        st.markdown(f'<div style="margin-bottom:12px;">{badges}</div>', unsafe_allow_html=True)

        # Progress bar
        st.progress(step / len(sol))
        st.markdown(f'<p style="text-align:center;color:#555;font-size:13px;font-family:Share Tech Mono,monospace;">Step {step} / {len(sol)}</p>', unsafe_allow_html=True)

        # Navigation buttons
        nav1, nav2, nav3, nav4 = st.columns(4)
        with nav1:
            if st.button("⏮ Start", use_container_width=True):
                st.session_state.step = 0
                st.rerun()
        with nav2:
            if st.button("◀ Prev", use_container_width=True) and step > 0:
                st.session_state.step -= 1
                st.rerun()
        with nav3:
            if st.button("Next ▶", use_container_width=True) and step < len(sol):
                st.session_state.step += 1
                st.rerun()
        with nav4:
            if st.button("End ⏭", use_container_width=True):
                st.session_state.step = len(sol)
                st.rerun()

        # Show cube at current step
        st.markdown("<br>", unsafe_allow_html=True)
        display_state = st.session_state.history[step]

        if step == 0:
            step_label = "Initial (Scrambled) State"
        elif step == len(sol):
            step_label = f"✅ Solved! — after move: <b>{sol[step-1]}</b>"
        else:
            step_label = f"After move <b>{sol[step-1]}</b> — {step}/{len(sol)}"

        st.markdown(
            f'<p style="font-family:Share Tech Mono,monospace;font-size:13px;color:#888;">{step_label}</p>',
            unsafe_allow_html=True
        )
        st.markdown(render_cube(display_state), unsafe_allow_html=True)

        if step == len(sol):
            st.markdown('<div class="goal-banner">🎉 SOLVED! Optimal solution found by A*</div>', unsafe_allow_html=True)

        # Auto-play button
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("▶️ Auto-Play All Steps", use_container_width=True):
            for s in range(st.session_state.step, len(sol) + 1):
                st.session_state.step = s
                time.sleep(0.6)
                st.rerun()
