"""
MeetingMind — AI Meeting Assistant
Record or upload meetings, get AI-powered transcription and structured notes.
"""

import os
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))

from core import transcriber, summarizer, storage, exporter

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MeetingMind",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

/* ── Global ── */
*, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}
[data-testid="stAppViewContainer"] { background: #09090F; }
[data-testid="stHeader"] { background: transparent; }
.block-container { padding: 1.5rem 2rem 4rem !important; max-width: 1200px; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0D0D18 0%, #111128 100%) !important;
    border-right: 1px solid rgba(124,58,237,0.15);
}
[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    border: 1px solid transparent !important;
    color: #8892A5 !important;
    text-align: left !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    border-radius: 10px !important;
    padding: 0.55rem 0.9rem !important;
    transition: all 0.2s ease !important;
    box-shadow: none !important;
    letter-spacing: 0 !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(124,58,237,0.12) !important;
    color: #C4B5FD !important;
    border-color: rgba(124,58,237,0.25) !important;
    transform: none !important;
}

/* ── Hero ── */
.hero-container {
    text-align: center;
    padding: 3rem 0 1rem;
    position: relative;
}
.hero-container::before {
    content: "";
    position: absolute;
    top: -60px; left: 50%; transform: translateX(-50%);
    width: 500px; height: 500px;
    background: radial-gradient(circle, rgba(124,58,237,0.08) 0%, transparent 70%);
    pointer-events: none;
}
.hero-title {
    font-size: 3.8rem;
    font-weight: 900;
    background: linear-gradient(135deg, #7C3AED 0%, #A78BFA 40%, #C084FC 70%, #E879F9 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.1;
    letter-spacing: -2px;
    margin-bottom: 0.5rem;
    animation: heroIn 0.8s ease both;
}
.hero-sub {
    font-size: 1.15rem;
    color: #64748B;
    font-weight: 500;
    animation: heroIn 1s ease both;
}
@keyframes heroIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

/* ── Page title ── */
.page-title {
    font-size: 1.8rem;
    font-weight: 800;
    color: #F1F5F9;
    letter-spacing: -0.5px;
    margin-bottom: 0.3rem;
}
.page-desc {
    font-size: 0.92rem;
    color: #64748B;
    margin-bottom: 1.5rem;
}

/* ── Stat cards ── */
.stats-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin: 1.5rem 0;
}
.stat-card {
    background: linear-gradient(135deg, #111128 0%, #13132E 100%);
    border: 1px solid rgba(124,58,237,0.15);
    border-radius: 16px;
    padding: 1.3rem 1.4rem;
    text-align: center;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}
.stat-card::after {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #7C3AED, #E879F9);
    opacity: 0;
    transition: opacity 0.3s;
}
.stat-card:hover { border-color: rgba(124,58,237,0.4); transform: translateY(-3px); }
.stat-card:hover::after { opacity: 1; }
.stat-value {
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #A78BFA, #C084FC);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.stat-label {
    font-size: 0.72rem;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-top: 0.3rem;
    font-weight: 600;
}

/* ── Feature cards (home) ── */
.features-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    margin: 2rem 0;
}
.feature-card {
    background: #111128;
    border: 1px solid rgba(124,58,237,0.12);
    border-radius: 16px;
    padding: 1.8rem 1.5rem;
    text-align: center;
    transition: all 0.3s ease;
    cursor: default;
}
.feature-card:hover {
    border-color: rgba(124,58,237,0.35);
    transform: translateY(-4px);
    box-shadow: 0 20px 40px rgba(124,58,237,0.12);
}
.feature-icon { font-size: 2.2rem; margin-bottom: 0.7rem; }
.feature-title {
    font-size: 1rem;
    font-weight: 700;
    color: #E2E8F0;
    margin-bottom: 0.4rem;
}
.feature-desc { font-size: 0.82rem; color: #64748B; line-height: 1.5; }

/* ── Meeting cards ── */
.m-card {
    background: #111128;
    border: 1px solid rgba(124,58,237,0.1);
    border-radius: 14px;
    padding: 1.1rem 1.3rem;
    margin-bottom: 0.7rem;
    transition: all 0.25s ease;
    border-left: 3px solid transparent;
}
.m-card:hover {
    border-left-color: #7C3AED;
    background: #14142F;
    transform: translateX(4px);
}
.m-card-title {
    font-size: 0.95rem;
    font-weight: 700;
    color: #E2E8F0;
    margin-bottom: 0.3rem;
}
.m-card-meta {
    display: flex;
    gap: 0.8rem;
    flex-wrap: wrap;
    font-size: 0.75rem;
    color: #475569;
}
.m-card-meta span { display: flex; align-items: center; gap: 0.25rem; }
.m-card-preview {
    font-size: 0.78rem;
    color: #475569;
    font-style: italic;
    margin-top: 0.4rem;
    line-height: 1.4;
}

/* ── Input mode tabs (Record / Upload) ── */
.input-mode-tabs {
    display: flex;
    gap: 0;
    margin-bottom: 1.5rem;
    background: #0D0D18;
    border-radius: 12px;
    padding: 4px;
    border: 1px solid rgba(124,58,237,0.12);
    width: fit-content;
}
.mode-tab {
    padding: 0.6rem 1.8rem;
    border-radius: 10px;
    font-size: 0.88rem;
    font-weight: 600;
    color: #64748B;
    cursor: pointer;
    transition: all 0.2s;
    text-align: center;
}
.mode-tab-active {
    background: linear-gradient(135deg, #7C3AED, #9333EA);
    color: white;
    box-shadow: 0 4px 15px rgba(124,58,237,0.3);
}

/* ── Recording indicator ── */
.recording-indicator {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    padding: 0.8rem 1.2rem;
    background: rgba(239,68,68,0.08);
    border: 1px solid rgba(239,68,68,0.25);
    border-radius: 12px;
    margin: 1rem 0;
}
.rec-dot {
    width: 12px; height: 12px;
    background: #EF4444;
    border-radius: 50%;
    animation: pulse 1.5s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.5; transform: scale(1.3); }
}

/* ── Section headers ── */
.section-label {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #7C3AED;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid rgba(124,58,237,0.15);
}

/* ── Glass card ── */
.glass-card {
    background: rgba(17,17,40,0.8);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(124,58,237,0.12);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}

/* ── Badges ── */
.badge {
    display: inline-block;
    padding: 0.15rem 0.55rem;
    border-radius: 20px;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}
.badge-high   { background: rgba(239,68,68,0.15); color: #F87171; border: 1px solid rgba(239,68,68,0.3); }
.badge-medium { background: rgba(234,179,8,0.15);  color: #FCD34D; border: 1px solid rgba(234,179,8,0.3); }
.badge-low    { background: rgba(34,197,94,0.15);  color: #4ADE80; border: 1px solid rgba(34,197,94,0.3); }
.badge-other  { background: rgba(100,116,139,0.15); color: #94A3B8; border: 1px solid rgba(100,116,139,0.3); }

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #7C3AED, #9333EA) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 15px rgba(124,58,237,0.25) !important;
}
.stButton > button:hover {
    box-shadow: 0 8px 25px rgba(124,58,237,0.4) !important;
    transform: translateY(-2px) !important;
}

/* ── Progress bar ── */
.stProgress > div > div > div {
    background: linear-gradient(90deg, #7C3AED, #A855F7, #E879F9) !important;
    border-radius: 8px;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    border: 2px dashed rgba(124,58,237,0.25) !important;
    border-radius: 16px !important;
    background: rgba(17,17,40,0.5) !important;
    transition: all 0.3s !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: rgba(124,58,237,0.5) !important;
    background: rgba(17,17,40,0.8) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] { gap: 0.3rem; border-bottom: 1px solid rgba(124,58,237,0.12); }
.stTabs [data-baseweb="tab"] {
    border-radius: 8px 8px 0 0;
    font-weight: 600;
    font-size: 0.85rem;
}

/* ── Transcript ── */
.transcript-box {
    max-height: 500px;
    overflow-y: auto;
    background: #0D0D18;
    border: 1px solid rgba(124,58,237,0.1);
    border-radius: 14px;
    padding: 1.2rem;
}
.ts-line {
    padding: 0.4rem 0;
    border-bottom: 1px solid rgba(124,58,237,0.05);
    font-size: 0.85rem;
    line-height: 1.6;
    color: #CBD5E1;
}
.ts-time {
    color: #7C3AED;
    font-size: 0.75rem;
    font-family: 'SF Mono', 'Fira Code', monospace;
    margin-right: 0.5rem;
    opacity: 0.8;
}

/* ── Dividers ── */
hr { border-color: rgba(124,58,237,0.1) !important; }

/* ── Hide Streamlit extras ── */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
[data-testid="stAlert"] { border-radius: 12px !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
_DEFAULTS = {
    "page": "home",
    "current_meeting_id": None,
    "whisper_model": "base",
    "ollama_model": "llama3.2",
    "auto_save": True,
    "input_mode": "upload",
    "search_query_lib": "",
}
for _k, _v in _DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def navigate(page, meeting_id=None):
    st.session_state.page = page
    if meeting_id is not None:
        st.session_state.current_meeting_id = meeting_id
    st.rerun()


def fmt_dur(seconds):
    if not seconds or seconds <= 0:
        return "—"
    h, m, s = int(seconds // 3600), int((seconds % 3600) // 60), int(seconds % 60)
    if h > 0:
        return f"{h}h {m}m"
    return f"{m}m {s}s" if m > 0 else f"{s}s"


def fmt_date(iso):
    try:
        return datetime.fromisoformat(iso).strftime("%b %d, %Y")
    except Exception:
        return iso or "—"


def fmt_datetime(iso):
    try:
        return datetime.fromisoformat(iso).strftime("%B %d, %Y at %I:%M %p")
    except Exception:
        return iso or "—"


def p_badge(priority):
    p = (priority or "").strip().capitalize()
    cls = {"High": "high", "Medium": "medium", "Low": "low"}.get(p, "other")
    return f'<span class="badge badge-{cls}">{p or "—"}</span>'


def type_icon(t):
    return {"Planning": "📋", "Status Update": "📊", "Brainstorm": "💡",
            "Review": "🔍", "Decision": "✅", "Interview": "🎤",
            "Training": "📚"}.get(t, "📝")


def sent_icon(s):
    return {"Productive": "🚀", "Positive": "😊", "Neutral": "😐",
            "Challenging": "😤", "Tense": "😬"}.get(s, "😐")


def check_ollama():
    return summarizer.check_ollama_available(st.session_state.ollama_model)


def total_hours(meetings):
    return round(sum(m.get("duration", 0) for m in meetings) / 3600, 1)


def action_count(meeting_id):
    full = storage.load_meeting(meeting_id)
    return len(full.get("notes", {}).get("action_items", [])) if full else 0


def total_actions(meetings):
    return sum(action_count(m["id"]) for m in meetings)


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────

def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center; padding:1.5rem 0 0.8rem;">
            <div style="font-size:2.5rem; margin-bottom:0.3rem;">🧠</div>
            <div style="font-size:1.3rem; font-weight:900;
                        background:linear-gradient(135deg,#7C3AED,#C084FC);
                        -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
                MeetingMind</div>
            <div style="font-size:0.7rem; color:#475569; letter-spacing:2px;
                        text-transform:uppercase; margin-top:0.2rem;">
                AI Meeting Assistant</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

        for pid, icon, label in [
            ("home", "🏠", "Dashboard"),
            ("new", "➕", "New Meeting"),
            ("library", "📚", "Library"),
            ("settings", "⚙️", "Settings"),
        ]:
            if st.button(f"{icon}  {label}", key=f"nav_{pid}", use_container_width=True):
                navigate(pid)

        st.markdown("<hr>", unsafe_allow_html=True)

        # Ollama status
        ok, _ = check_ollama()
        dot_color = "#4ADE80" if ok else "#EF4444"
        status_text = "Ollama connected" if ok else "Ollama offline"
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:0.5rem;
                    font-size:0.78rem; color:#64748B; padding:0 0.5rem;">
            <div style="width:8px; height:8px; border-radius:50%;
                        background:{dot_color};"></div>
            {status_text}
        </div>
        """, unsafe_allow_html=True)

        if not ok:
            with st.expander("Setup Ollama"):
                st.code("ollama serve\nollama pull llama3.2", language="bash")

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        meetings = storage.list_meetings()
        st.markdown(f"""
        <div style="background:rgba(124,58,237,0.06); border:1px solid rgba(124,58,237,0.12);
                    border-radius:12px; padding:0.8rem 1rem; font-size:0.78rem; color:#64748B;">
            <div><span style="color:#A78BFA; font-weight:700;">{len(meetings)}</span> meetings saved</div>
            <div style="margin-top:0.2rem;">
                <span style="color:#A78BFA; font-weight:700;">{total_hours(meetings)}</span> hours transcribed
            </div>
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: HOME
# ─────────────────────────────────────────────────────────────────────────────

def page_home():
    # Hero
    st.markdown("""
    <div class="hero-container">
        <div class="hero-title">MeetingMind</div>
        <div class="hero-sub">Record or upload any meeting. Get AI-powered notes in seconds.</div>
    </div>
    """, unsafe_allow_html=True)

    # CTA buttons
    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        if st.button("🎙  Record a Meeting", use_container_width=True):
            st.session_state.input_mode = "record"
            navigate("new")
    with c2:
        if st.button("📁  Upload Recording", use_container_width=True):
            st.session_state.input_mode = "upload"
            navigate("new")

    # Stats
    meetings = storage.list_meetings()
    st.markdown(f"""
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-value">{len(meetings)}</div>
            <div class="stat-label">Meetings</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{total_hours(meetings)}</div>
            <div class="stat-label">Hours Transcribed</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{total_actions(meetings)}</div>
            <div class="stat-label">Action Items</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{fmt_date(meetings[0]["created_at"]) if meetings else "—"}</div>
            <div class="stat-label">Latest Meeting</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Features
    st.markdown("""
    <div class="features-grid">
        <div class="feature-card">
            <div class="feature-icon">🎙️</div>
            <div class="feature-title">Record Live</div>
            <div class="feature-desc">Record audio directly in your browser — no external apps needed</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">🔊</div>
            <div class="feature-title">Whisper Transcription</div>
            <div class="feature-desc">OpenAI Whisper converts speech to text with timestamps, 100% locally</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">🤖</div>
            <div class="feature-title">AI Meeting Notes</div>
            <div class="feature-desc">Get summaries, action items, decisions, and follow-ups automatically</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Recent meetings
    if meetings:
        st.markdown("<div class='section-label'>Recent Meetings</div>", unsafe_allow_html=True)

        search = st.text_input("Search", placeholder="Search meetings...",
                               label_visibility="collapsed", key="home_search")
        results = storage.search_meetings(search) if search else meetings[:6]

        if search and not results:
            st.info(f'No meetings matching "{search}"')

        for m in results:
            ac = action_count(m["id"])
            card_col, btn_col = st.columns([8, 1])
            with card_col:
                st.markdown(f"""
                <div class="m-card">
                    <div class="m-card-title">{type_icon(m.get("meeting_type","Other"))} {m.get("title","Untitled")}</div>
                    <div class="m-card-meta">
                        <span>📅 {fmt_date(m.get("created_at",""))}</span>
                        <span>⏱ {fmt_dur(m.get("duration",0))}</span>
                        <span>✅ {ac} actions</span>
                        <span>{sent_icon(m.get("sentiment","Neutral"))} {m.get("sentiment","Neutral")}</span>
                    </div>
                    <div class="m-card-preview">{m.get("summary_preview","")[:140]}</div>
                </div>
                """, unsafe_allow_html=True)
            with btn_col:
                st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)
                if st.button("Open →", key=f"ho_{m['id']}"):
                    navigate("view", m["id"])
    else:
        st.markdown("""
        <div style="text-align:center; padding:3rem; background:#111128;
                    border:1px dashed rgba(124,58,237,0.2); border-radius:16px; margin-top:1rem;">
            <div style="font-size:3rem; margin-bottom:0.5rem;">🎙️</div>
            <div style="font-size:1.1rem; font-weight:700; color:#C4B5FD;">No meetings yet</div>
            <div style="color:#64748B; font-size:0.88rem; margin-top:0.3rem;">
                Record or upload your first meeting to get started
            </div>
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: NEW MEETING
# ─────────────────────────────────────────────────────────────────────────────

def page_new_meeting():
    st.markdown("<div class='page-title'>New Meeting</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-desc'>Record live audio or upload a file — AI handles the rest.</div>",
                unsafe_allow_html=True)

    # Ollama check
    ollama_ok, ollama_msg = check_ollama()
    if not ollama_ok:
        st.warning("Ollama is offline — transcription works but AI notes will be skipped. "
                    "Run `ollama serve` to enable AI analysis.")

    # ── Input mode toggle ──
    mode_col1, mode_col2, _ = st.columns([1, 1, 3])
    with mode_col1:
        if st.button("🎙  Record Audio", use_container_width=True,
                     key="mode_record"):
            st.session_state.input_mode = "record"
            st.rerun()
    with mode_col2:
        if st.button("📁  Upload File", use_container_width=True,
                     key="mode_upload"):
            st.session_state.input_mode = "upload"
            st.rerun()

    current_mode = st.session_state.input_mode
    st.markdown(f"""
    <div style="font-size:0.78rem; color:#475569; margin:0.5rem 0 1.5rem;">
        Mode: <span style="color:#A78BFA; font-weight:700;">
        {"🎙 Recording" if current_mode == "record" else "📁 File Upload"}</span>
    </div>
    """, unsafe_allow_html=True)

    # ── Options row ──
    opt1, opt2, opt3 = st.columns(3)
    with opt1:
        meeting_title = st.text_input("Meeting Title (optional)",
                                      placeholder="e.g. Sprint Planning")
    with opt2:
        num_speakers = st.selectbox("Speakers", [1, 2, 3, 4, 5], index=1)
    with opt3:
        lang_choice = st.selectbox("Language",
                                   ["Auto-detect", "English", "French", "Spanish",
                                    "German", "Japanese", "Chinese"])

    lang_map = {"Auto-detect": None, "English": "en", "French": "fr",
                "Spanish": "es", "German": "de", "Japanese": "ja", "Chinese": "zh"}
    lang_code = lang_map[lang_choice]

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── RECORD MODE ──
    if current_mode == "record":
        st.markdown("<div class='section-label'>Record Audio</div>", unsafe_allow_html=True)

        st.markdown("""
        <div style="background:rgba(124,58,237,0.06); border:1px solid rgba(124,58,237,0.15);
                    border-radius:12px; padding:1rem 1.3rem; margin-bottom:1rem;
                    font-size:0.85rem; color:#94A3B8;">
            Click the microphone button below to start recording. When done, click stop.
            Your audio stays on your device — nothing is uploaded to the cloud.
        </div>
        """, unsafe_allow_html=True)

        audio_data = st.audio_input("Record your meeting", key="audio_recorder",
                                    label_visibility="collapsed")

        if audio_data is not None:
            st.audio(audio_data, format="audio/wav")

            file_size_mb = len(audio_data.getvalue()) / (1024 * 1024)
            st.markdown(f"""
            <div style="display:flex; gap:1.5rem; align-items:center;
                        font-size:0.82rem; color:#94A3B8; margin:0.5rem 0 1rem;
                        padding:0.6rem 1rem; background:#111128;
                        border-radius:10px; border:1px solid rgba(124,58,237,0.1);">
                <span>🎙 Recorded audio</span>
                <span>💾 {file_size_mb:.1f} MB</span>
            </div>
            """, unsafe_allow_html=True)

            if st.button("🚀  Transcribe & Analyze", use_container_width=False, key="process_rec"):
                _process_audio(audio_data, "recorded_audio.wav", meeting_title,
                               num_speakers, lang_code, ollama_ok)

    # ── UPLOAD MODE ──
    else:
        st.markdown("<div class='section-label'>Upload Audio or Video</div>",
                    unsafe_allow_html=True)

        uploaded = st.file_uploader(
            "Drop your meeting recording here",
            type=["mp3", "wav", "mp4", "mov", "webm", "m4a", "ogg", "flac", "mpeg4"],
            label_visibility="collapsed",
        )

        if uploaded:
            file_size_mb = len(uploaded.getvalue()) / (1024 * 1024)
            st.markdown(f"""
            <div style="display:flex; gap:1.5rem; align-items:center;
                        font-size:0.82rem; color:#94A3B8; margin:0.5rem 0 1rem;
                        padding:0.6rem 1rem; background:#111128;
                        border-radius:10px; border:1px solid rgba(124,58,237,0.1);">
                <span>📁 <strong style="color:#E2E8F0;">{uploaded.name}</strong></span>
                <span>💾 {file_size_mb:.1f} MB</span>
                <span>🏷 {uploaded.type or "audio"}</span>
            </div>
            """, unsafe_allow_html=True)

            if st.button("🚀  Transcribe & Analyze", use_container_width=False, key="process_up"):
                _process_audio(uploaded, uploaded.name, meeting_title,
                               num_speakers, lang_code, ollama_ok)
        else:
            st.markdown("""
            <div style="text-align:center; padding:2rem; color:#475569; font-size:0.85rem;">
                Supports MP3, WAV, M4A, OGG, FLAC, MP4, MOV, WEBM — up to 500 MB
            </div>
            """, unsafe_allow_html=True)


def _process_audio(audio_data, filename, title, num_speakers, lang_code, ollama_ok):
    """Process audio data (from recording or upload) through the full pipeline."""
    auto_title = (title.strip() if title and title.strip()
                  else Path(filename).stem.replace("_", " ").replace("-", " ").title())

    sfx = Path(filename).suffix or ".wav"
    with tempfile.NamedTemporaryFile(suffix=sfx, delete=False) as tmp:
        tmp.write(audio_data.getvalue())
        tmp_path = tmp.name

    try:
        prog = st.progress(0, text="Preparing...")
        status = st.empty()

        def update(msg, pct):
            prog.progress(min(pct, 1.0), text=msg)
            status.markdown(
                f"<div style='color:#94A3B8; font-size:0.85rem;'>⏳ {msg}</div>",
                unsafe_allow_html=True)

        # Transcribe
        update("Loading Whisper engine...", 0.05)
        t_result = transcriber.transcribe_audio(
            file_path=tmp_path,
            model_name=st.session_state.whisper_model,
            progress_callback=update,
            language=lang_code,
        )

        # Speaker labels
        if num_speakers > 1 and t_result.get("segments"):
            spk_map = {i: f"Speaker {i+1}" for i in range(num_speakers)}
            t_result["formatted_transcript"] = transcriber.apply_speaker_labels(
                t_result["segments"], spk_map, num_speakers)

        # AI summarization
        update("AI is analyzing the meeting...", 0.55)
        if not ollama_ok:
            notes = {"summary": ["Transcription complete. Enable Ollama for AI notes."],
                     "key_decisions": [], "action_items": [], "discussion_topics": [],
                     "follow_up_items": [], "meeting_type": "Other",
                     "sentiment": "Neutral", "raw_response": ""}
        else:
            try:
                notes = summarizer.generate_meeting_notes(
                    transcript=t_result["text"],
                    meeting_title=auto_title,
                    model=st.session_state.ollama_model,
                    progress_callback=lambda msg, pct: update(msg, 0.55 + pct * 0.40),
                )
            except Exception as e:
                st.warning(f"AI analysis failed: {e}")
                notes = {"summary": ["AI analysis failed — review the transcript."],
                         "key_decisions": [], "action_items": [], "discussion_topics": [],
                         "follow_up_items": [], "meeting_type": "Other",
                         "sentiment": "Neutral", "raw_response": str(e)}

        update("Saving...", 0.98)
        mid = storage.save_meeting(
            title=auto_title,
            transcript=t_result["text"],
            notes=notes,
            file_name=filename,
            duration=t_result["duration"],
            language=t_result["language"],
            word_count=t_result["word_count"],
            formatted_transcript=t_result["formatted_transcript"],
            segments=t_result["segments"],
        )
        prog.progress(1.0, text="Done!")
        status.empty()
        st.success(f"**{auto_title}** — {fmt_dur(t_result['duration'])} · "
                   f"{t_result['word_count']:,} words")
        time.sleep(0.5)
        navigate("view", mid)

    except Exception as exc:
        st.error(f"Processing failed: {exc}")
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: VIEW MEETING
# ─────────────────────────────────────────────────────────────────────────────

def page_view_meeting():
    mid = st.session_state.current_meeting_id
    if not mid:
        st.warning("No meeting selected.")
        if st.button("← Dashboard"):
            navigate("home")
        return

    meeting = storage.load_meeting(mid)
    if not meeting:
        st.error("Meeting not found.")
        if st.button("← Library"):
            navigate("library")
        return

    notes = meeting.get("notes", {})

    # Header
    hdr, acts = st.columns([5, 1.5])
    with hdr:
        st.markdown(f"""
        <div class="page-title">{type_icon(notes.get("meeting_type","Other"))} {meeting.get("title","Untitled")}</div>
        <div style="display:flex; gap:1rem; flex-wrap:wrap; font-size:0.8rem; color:#64748B; margin-top:0.2rem;">
            <span>📅 {fmt_datetime(meeting.get("created_at",""))}</span>
            <span>⏱ {fmt_dur(meeting.get("duration",0))}</span>
            <span>💬 {meeting.get("word_count",0):,} words</span>
            <span>🌐 {meeting.get("language","en").upper()}</span>
            <span>{sent_icon(notes.get("sentiment","Neutral"))} {notes.get("sentiment","Neutral")}</span>
        </div>
        """, unsafe_allow_html=True)
    with acts:
        if st.button("← Back", use_container_width=True, key="v_back"):
            navigate("library")
        if st.button("🗑 Delete", use_container_width=True, key="v_del"):
            st.session_state[f"cdel_{mid}"] = True

    if st.session_state.get(f"cdel_{mid}"):
        st.warning("Permanently delete this meeting?")
        y, n, _ = st.columns([1, 1, 5])
        with y:
            if st.button("Yes, delete", key="dy"):
                storage.delete_meeting(mid)
                st.session_state.current_meeting_id = None
                navigate("library")
        with n:
            if st.button("Cancel", key="dn"):
                del st.session_state[f"cdel_{mid}"]
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Tabs
    tab_sum, tab_trans, tab_act, tab_exp = st.tabs(
        ["📋 Summary", "📜 Transcript", "✅ Actions", "📤 Export"])

    # ── Summary ──
    with tab_sum:
        l, r = st.columns([1.1, 1])
        with l:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.markdown("<div class='section-label'>Summary</div>", unsafe_allow_html=True)
            for b in notes.get("summary", []):
                st.markdown(f"<div style='margin-bottom:0.5rem; color:#CBD5E1;'>• {b}</div>",
                            unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            decisions = notes.get("key_decisions", [])
            if decisions:
                st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
                st.markdown("<div class='section-label'>Key Decisions</div>", unsafe_allow_html=True)
                for d in decisions:
                    st.markdown(f"<div style='margin-bottom:0.4rem; color:#CBD5E1;'>🔷 {d}</div>",
                                unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

        with r:
            topics = notes.get("discussion_topics", [])
            if topics:
                st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
                st.markdown("<div class='section-label'>Discussion Topics</div>", unsafe_allow_html=True)
                for t in topics:
                    st.markdown(f"<div style='margin-bottom:0.4rem; color:#CBD5E1;'>💬 {t}</div>",
                                unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            followups = notes.get("follow_up_items", [])
            if followups:
                st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
                st.markdown("<div class='section-label'>Follow-up Items</div>", unsafe_allow_html=True)
                for item in followups:
                    st.markdown(f"<div style='margin-bottom:0.4rem; color:#CBD5E1;'>☐ {item}</div>",
                                unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            # Details
            st.markdown(f"""
            <div class="glass-card">
                <div class="section-label">Meeting Details</div>
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:0.8rem; font-size:0.85rem;">
                    <div><span style="color:#475569;">Type</span><br>
                        <strong>{type_icon(notes.get("meeting_type","Other"))} {notes.get("meeting_type","Other")}</strong></div>
                    <div><span style="color:#475569;">Sentiment</span><br>
                        <strong>{sent_icon(notes.get("sentiment","Neutral"))} {notes.get("sentiment","Neutral")}</strong></div>
                    <div><span style="color:#475569;">Duration</span><br>
                        <strong>{fmt_dur(meeting.get("duration",0))}</strong></div>
                    <div><span style="color:#475569;">Words</span><br>
                        <strong>{meeting.get("word_count",0):,}</strong></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ── Transcript ──
    with tab_trans:
        segments = meeting.get("segments", [])
        formatted = meeting.get("formatted_transcript", meeting.get("transcript", ""))

        st.markdown(f"""
        <div style="color:#475569; font-size:0.8rem; margin-bottom:0.8rem;">
            {len(segments)} segments · {meeting.get("word_count",0):,} words ·
            Language: {meeting.get("language","en").upper()}
        </div>
        """, unsafe_allow_html=True)

        if segments:
            lines = []
            for seg in segments:
                s_ts = transcriber.format_timestamp(seg.get("start", 0))
                e_ts = transcriber.format_timestamp(seg.get("end", 0))
                text = seg.get("text", "").strip()
                if text:
                    lines.append(f'<div class="ts-line"><span class="ts-time">[{s_ts} → {e_ts}]</span>{text}</div>')
            st.markdown('<div class="transcript-box">' + "\n".join(lines) + "</div>",
                        unsafe_allow_html=True)
        else:
            st.text_area("Transcript", value=formatted, height=500, disabled=True)

    # ── Action Items ──
    with tab_act:
        items = notes.get("action_items", [])
        if not items:
            st.markdown("""
            <div style="text-align:center; padding:2.5rem; color:#475569;
                        background:#111128; border-radius:14px; border:1px dashed rgba(124,58,237,0.2);">
                <div style="font-size:2rem; margin-bottom:0.4rem;">✅</div>
                No action items identified in this meeting.
            </div>
            """, unsafe_allow_html=True)
        else:
            f1, f2 = st.columns([2, 3])
            with f1:
                filter_p = st.multiselect("Priority", ["High", "Medium", "Low"],
                                          default=["High", "Medium", "Low"],
                                          key=f"fp_{mid}")
            with f2:
                filter_a = st.text_input("Assignee", placeholder="e.g. Alice",
                                         key=f"fa_{mid}")

            filtered = [it for it in items if isinstance(it, dict)
                        and it.get("priority", "Medium") in filter_p
                        and (not filter_a or filter_a.lower() in it.get("assignee", "").lower())]

            st.markdown(f"<div style='color:#475569; font-size:0.78rem; margin:0.5rem 0 1rem;'>"
                        f"Showing {len(filtered)} of {len(items)}</div>",
                        unsafe_allow_html=True)

            for i, item in enumerate(filtered, 1):
                if not isinstance(item, dict):
                    st.markdown(f"- {item}")
                    continue
                st.markdown(f"""
                <div class="m-card" style="padding:1rem 1.2rem;">
                    <div style="display:flex; align-items:flex-start; gap:0.8rem;">
                        <div style="font-size:1.1rem; color:#7C3AED; font-weight:800; min-width:1.5rem;">{i}.</div>
                        <div style="flex:1;">
                            <div style="font-size:0.92rem; font-weight:600; color:#E2E8F0;
                                        margin-bottom:0.35rem;">{item.get("task","")}</div>
                            <div style="display:flex; gap:1rem; flex-wrap:wrap;
                                        font-size:0.78rem; color:#64748B;">
                                <span>👤 {item.get("assignee","TBD")}</span>
                                <span>📅 {item.get("deadline","?")}</span>
                                <span>{p_badge(item.get("priority","Medium"))}</span>
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # ── Export ──
    with tab_exp:
        st.markdown("""
        <div style="color:#94A3B8; margin-bottom:1.5rem; font-size:0.88rem;">
            Download your meeting notes in any format.
        </div>
        """, unsafe_allow_html=True)

        safe = meeting.get("title", "meeting").replace(" ", "_").replace("/", "-")[:50]
        e1, e2, e3 = st.columns(3)

        with e1:
            st.markdown("""
            <div class="glass-card" style="text-align:center;">
                <div style="font-size:2rem;">📝</div>
                <div style="font-weight:700; margin:0.4rem 0;">Markdown</div>
                <div style="font-size:0.78rem; color:#64748B;">Notion, Obsidian, GitHub</div>
            </div>
            """, unsafe_allow_html=True)
            md = exporter.to_markdown(meeting)
            st.download_button("⬇ Download .md", data=md.encode("utf-8"),
                               file_name=f"{safe}.md", mime="text/markdown",
                               use_container_width=True, key="dl_md")

        with e2:
            st.markdown("""
            <div class="glass-card" style="text-align:center;">
                <div style="font-size:2rem;">📄</div>
                <div style="font-weight:700; margin:0.4rem 0;">PDF</div>
                <div style="font-size:0.78rem; color:#64748B;">Professional report</div>
            </div>
            """, unsafe_allow_html=True)
            try:
                pdf_bytes = exporter.to_pdf(meeting)
                st.download_button("⬇ Download .pdf", data=pdf_bytes,
                                   file_name=f"{safe}.pdf", mime="application/pdf",
                                   use_container_width=True, key="dl_pdf")
            except Exception as exc:
                st.error(f"PDF error: {exc}")

        with e3:
            st.markdown("""
            <div class="glass-card" style="text-align:center;">
                <div style="font-size:2rem;">📃</div>
                <div style="font-weight:700; margin:0.4rem 0;">Plain Text</div>
                <div style="font-size:0.78rem; color:#64748B;">Universal, copy-paste</div>
            </div>
            """, unsafe_allow_html=True)
            txt = exporter.to_plain_text(meeting)
            st.download_button("⬇ Download .txt", data=txt.encode("utf-8"),
                               file_name=f"{safe}.txt", mime="text/plain",
                               use_container_width=True, key="dl_txt")


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: LIBRARY
# ─────────────────────────────────────────────────────────────────────────────

def page_library():
    st.markdown("<div class='page-title'>Meeting Library</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-desc'>All your meetings — search, review, and export.</div>",
                unsafe_allow_html=True)

    s_col, sort_col, new_col = st.columns([4, 2, 1.5])
    with s_col:
        query = st.text_input("Search", placeholder="Search meetings...",
                              label_visibility="collapsed", key="lib_search")
    with sort_col:
        sort_by = st.selectbox("Sort", ["Newest", "Oldest", "Longest", "Most words"],
                               label_visibility="collapsed")
    with new_col:
        if st.button("➕ New", use_container_width=True):
            navigate("new")

    meetings = storage.search_meetings(query) if query else storage.list_meetings()
    if sort_by == "Oldest":
        meetings = sorted(meetings, key=lambda m: m.get("created_at", ""))
    elif sort_by == "Longest":
        meetings = sorted(meetings, key=lambda m: m.get("duration", 0), reverse=True)
    elif sort_by == "Most words":
        meetings = sorted(meetings, key=lambda m: m.get("word_count", 0), reverse=True)

    if not meetings:
        st.info("No meetings found." if query else "Library is empty — record or upload a meeting!")
        return

    st.markdown(f"<div style='color:#475569; font-size:0.78rem; margin:0.5rem 0 1rem;'>"
                f"{len(meetings)} meeting{'s' if len(meetings) != 1 else ''}</div>",
                unsafe_allow_html=True)

    grid = st.columns(2)
    for idx, m in enumerate(meetings):
        with grid[idx % 2]:
            ac = action_count(m["id"])
            st.markdown(f"""
            <div class="m-card">
                <div class="m-card-title">{type_icon(m.get("meeting_type","Other"))} {m.get("title","Untitled")}</div>
                <div class="m-card-meta">
                    <span>📅 {fmt_date(m.get("created_at",""))}</span>
                    <span>⏱ {fmt_dur(m.get("duration",0))}</span>
                    <span>✅ {ac} items</span>
                </div>
                <div class="m-card-preview">{m.get("summary_preview","")[:120]}</div>
            </div>
            """, unsafe_allow_html=True)

            b1, b2 = st.columns([3, 1])
            with b1:
                if st.button("Open", key=f"lo_{m['id']}", use_container_width=True):
                    navigate("view", m["id"])
            with b2:
                if st.button("🗑", key=f"ld_{m['id']}", use_container_width=True):
                    st.session_state[f"lc_{m['id']}"] = True

            if st.session_state.get(f"lc_{m['id']}"):
                st.warning(f"Delete **{m.get('title','?')}**?")
                y, n = st.columns(2)
                with y:
                    if st.button("Yes", key=f"ly_{m['id']}"):
                        storage.delete_meeting(m["id"])
                        if f"lc_{m['id']}" in st.session_state:
                            del st.session_state[f"lc_{m['id']}"]
                        st.rerun()
                with n:
                    if st.button("No", key=f"ln_{m['id']}"):
                        del st.session_state[f"lc_{m['id']}"]
                        st.rerun()

    # Bulk export
    st.markdown("<hr>", unsafe_allow_html=True)
    ex_col, info_col = st.columns([2, 5])
    with ex_col:
        all_json = storage.export_all_meetings_json()
        st.download_button("⬇ Export All (JSON)", data=all_json.encode("utf-8"),
                           file_name="meetingmind_export.json", mime="application/json",
                           use_container_width=True)
    with info_col:
        stats = storage.get_storage_stats()
        st.markdown(f"<div style='color:#475569; font-size:0.75rem; padding-top:0.6rem;'>"
                    f"📁 {stats['total_meetings']} meetings · 💾 {stats['total_size_mb']} MB"
                    f"</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: SETTINGS
# ─────────────────────────────────────────────────────────────────────────────

def page_settings():
    st.markdown("<div class='page-title'>Settings</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    l, r = st.columns(2)

    with l:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-label'>Whisper Model</div>", unsafe_allow_html=True)
        desc = {"tiny": "Fastest · lower accuracy", "base": "Good balance (recommended)",
                "small": "Better accuracy · moderate", "medium": "High accuracy · slower",
                "large": "Best accuracy · slowest"}
        opts = list(desc.keys())
        cur = opts.index(st.session_state.whisper_model) if st.session_state.whisper_model in opts else 1
        new_wm = st.selectbox("Model", opts, index=cur,
                              format_func=lambda m: f"{m} — {desc[m]}",
                              label_visibility="collapsed")
        if new_wm != st.session_state.whisper_model:
            st.session_state.whisper_model = new_wm
            st.success(f"Model set to **{new_wm}**")
        st.markdown("<div style='font-size:0.75rem; color:#475569; margin-top:0.5rem;'>"
                    "tiny/base: CPU. small/medium: 8GB RAM. large: GPU or 16GB+ RAM.</div>",
                    unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-label'>Behavior</div>", unsafe_allow_html=True)
        auto = st.toggle("Auto-save after processing", value=st.session_state.auto_save)
        st.session_state.auto_save = auto
        st.markdown(f"<div style='font-size:0.78rem; color:#64748B; margin-top:0.3rem;'>"
                    f"Auto-save is <strong>{'on' if auto else 'off'}</strong>.</div>",
                    unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with r:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-label'>Ollama (AI Summarization)</div>", unsafe_allow_html=True)
        new_model = st.text_input("Model", value=st.session_state.ollama_model,
                                  help="e.g. llama3.2, mistral, phi3, gemma2")
        if st.button("Apply", key="apply_ollama"):
            st.session_state.ollama_model = new_model.strip()
            st.success(f"Model set to **{new_model.strip()}**")

        ok, msg = check_ollama()
        color = "#4ADE80" if ok else "#EF4444"
        st.markdown(f"<div style='font-size:0.82rem; color:{color}; margin-top:0.5rem;'>"
                    f"{'🟢' if ok else '🔴'} {msg}</div>", unsafe_allow_html=True)
        if not ok:
            st.code("ollama serve\nollama pull llama3.2", language="bash")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-label'>Storage</div>", unsafe_allow_html=True)
        stats = storage.get_storage_stats()
        st.markdown(f"""
        <div style="font-size:0.85rem; line-height:2.2;">
            <div>📁 <code style="color:#A78BFA;">{stats['storage_path']}</code></div>
            <div>📊 <strong>{stats['total_meetings']}</strong> meetings</div>
            <div>💾 <strong>{stats['total_size_mb']} MB</strong> on disk</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # About
    st.markdown("""
    <div style="background:rgba(124,58,237,0.04); border:1px solid rgba(124,58,237,0.1);
                border-radius:16px; padding:1.5rem; text-align:center; margin-top:2rem;">
        <div style="font-size:1.3rem; font-weight:800; margin-bottom:0.3rem;
                    background:linear-gradient(135deg,#7C3AED,#C084FC);
                    -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
            🧠 MeetingMind</div>
        <div style="color:#475569; font-size:0.82rem; line-height:1.8;">
            Transcription: <strong style="color:#A78BFA;">OpenAI Whisper</strong> ·
            AI Analysis: <strong style="color:#A78BFA;">Ollama</strong> ·
            UI: <strong style="color:#A78BFA;">Streamlit</strong>
            <br>100% local. No cloud. No subscriptions.
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# ROUTER
# ─────────────────────────────────────────────────────────────────────────────

def main():
    render_sidebar()
    page = st.session_state.page
    {"home": page_home, "new": page_new_meeting, "view": page_view_meeting,
     "library": page_library, "settings": page_settings}.get(page, page_home)()


if __name__ == "__main__":
    main()
