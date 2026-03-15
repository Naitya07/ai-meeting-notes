"""
MeetingMind — Edge-Native AI Meeting Intelligence Platform
13 verticals | 45+ templates | 50+ jurisdictions | 37+ languages
100% on-device processing. Zero cloud. Zero data leakage.
"""

import os
import sys
import tempfile
import time
import json
from datetime import datetime
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))

from core import transcriber, summarizer, storage, exporter

# Lazy imports for new modules (graceful degradation if not yet built)
def _load_module(name):
    try:
        return __import__(f"core.{name}", fromlist=[name])
    except ImportError:
        return None

templates_mod = _load_module("templates")
compliance_mod = _load_module("compliance")
analytics_mod = _load_module("analytics")
languages_mod = _load_module("languages")

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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* ── Global ── */
*, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}
[data-testid="stAppViewContainer"] { background: #09090F; }
[data-testid="stHeader"] { background: transparent; }
.block-container { padding: 1rem 2rem 4rem !important; max-width: 1400px; }

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
    width: 100% !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(124,58,237,0.12) !important;
    color: #C4B5FD !important;
    border-color: rgba(124,58,237,0.25) !important;
}

/* ── Hero ── */
.hero-container {
    text-align: center;
    padding: 2rem 0 1rem;
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
    font-size: 3.2rem;
    font-weight: 900;
    background: linear-gradient(135deg, #7C3AED 0%, #A78BFA 40%, #C084FC 70%, #E879F9 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.1;
    letter-spacing: -2px;
    margin-bottom: 0.5rem;
}
.hero-sub {
    font-size: 1.1rem;
    color: #64748B;
    font-weight: 500;
}

/* ── Glass Cards ── */
.glass-card {
    background: rgba(15, 15, 30, 0.6);
    border: 1px solid rgba(124, 58, 237, 0.15);
    border-radius: 16px;
    padding: 1.5rem;
    backdrop-filter: blur(20px);
    margin-bottom: 1rem;
}
.glass-card:hover {
    border-color: rgba(124, 58, 237, 0.35);
    box-shadow: 0 0 30px rgba(124, 58, 237, 0.08);
}

/* ── Vertical Cards ── */
.vertical-card {
    background: rgba(15, 15, 30, 0.5);
    border: 1px solid rgba(124, 58, 237, 0.12);
    border-radius: 14px;
    padding: 1.2rem;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s ease;
    min-height: 160px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}
.vertical-card:hover {
    border-color: rgba(124, 58, 237, 0.5);
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(124, 58, 237, 0.15);
}
.vertical-icon { font-size: 2.2rem; margin-bottom: 0.5rem; }
.vertical-name { font-size: 0.95rem; font-weight: 700; color: #E2E8F0; }
.vertical-desc { font-size: 0.72rem; color: #64748B; margin-top: 0.3rem; }

/* ── Stat Cards ── */
.stat-card {
    background: rgba(15, 15, 30, 0.6);
    border: 1px solid rgba(124, 58, 237, 0.12);
    border-radius: 14px;
    padding: 1.2rem 1.5rem;
    text-align: center;
}
.stat-value {
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #7C3AED, #A78BFA);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.stat-label { font-size: 0.78rem; color: #64748B; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }

/* ── Compliance Badge ── */
.compliance-badge {
    display: inline-block;
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 700;
    margin: 0.2rem;
    letter-spacing: 0.5px;
}

/* ── Section Headers ── */
.section-header {
    font-size: 1.5rem;
    font-weight: 800;
    color: #E2E8F0;
    margin: 1.5rem 0 1rem;
    letter-spacing: -0.5px;
}
.section-sub {
    font-size: 0.85rem;
    color: #64748B;
    margin-bottom: 1.5rem;
}

/* ── Processing Animation ── */
@keyframes pulse {
    0%, 100% { opacity: 0.6; }
    50% { opacity: 1; }
}
.processing { animation: pulse 2s ease-in-out infinite; }

/* ── Active nav ── */
.nav-active > button {
    background: rgba(124,58,237,0.2) !important;
    color: #C4B5FD !important;
    border-color: rgba(124,58,237,0.4) !important;
}

/* ── Notes sections ── */
.notes-section {
    background: rgba(15, 15, 30, 0.4);
    border: 1px solid rgba(124, 58, 237, 0.1);
    border-radius: 12px;
    padding: 1.2rem;
    margin-bottom: 0.8rem;
}
.notes-section h4 {
    color: #A78BFA;
    font-size: 0.9rem;
    font-weight: 700;
    margin-bottom: 0.6rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* ── Meeting history cards ── */
.meeting-card {
    background: rgba(15, 15, 30, 0.5);
    border: 1px solid rgba(124, 58, 237, 0.1);
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.6rem;
    transition: all 0.2s ease;
}
.meeting-card:hover {
    border-color: rgba(124, 58, 237, 0.3);
}

/* hide streamlit branding */
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE INITIALIZATION
# ─────────────────────────────────────────────────────────────────────────────
DEFAULTS = {
    "page": "home",
    "vertical": "general",
    "template": None,
    "transcript_result": None,
    "notes_result": None,
    "current_meeting_id": None,
    "processing": False,
    "whisper_model": "base",
    "language": None,
    "consent_given": False,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ─────────────────────────────────────────────────────────────────────────────
# VERTICAL DEFINITIONS (fallback if templates module not loaded)
# ─────────────────────────────────────────────────────────────────────────────
VERTICALS_FALLBACK = [
    {"id": "general", "name": "General", "icon": "📋", "description": "Universal meeting notes", "color": "#7C3AED"},
    {"id": "healthcare", "name": "Healthcare", "icon": "🏥", "description": "SOAP, H&P, progress notes", "color": "#EF4444"},
    {"id": "legal", "name": "Legal", "icon": "⚖️", "description": "Client intake, depositions, briefs", "color": "#3B82F6"},
    {"id": "financial", "name": "Financial", "icon": "🏦", "description": "Compliance logs, KYC, trade docs", "color": "#10B981"},
    {"id": "veterinary", "name": "Veterinary", "icon": "🐾", "description": "Vet SOAP notes, treatment plans", "color": "#F59E0B"},
    {"id": "hr", "name": "HR & Recruiting", "icon": "👥", "description": "Interview scorecards, reviews", "color": "#8B5CF6"},
    {"id": "education", "name": "Education", "icon": "🎓", "description": "IEP notes, faculty meetings", "color": "#06B6D4"},
    {"id": "sales", "name": "Sales & Consulting", "icon": "📈", "description": "Call summaries, QBRs", "color": "#F97316"},
    {"id": "construction", "name": "Construction", "icon": "🏗️", "description": "Site minutes, safety briefings", "color": "#EAB308"},
    {"id": "government", "name": "Government", "icon": "🏛️", "description": "Council minutes, case notes", "color": "#6366F1"},
    {"id": "religious", "name": "Religious & Nonprofit", "icon": "🕊️", "description": "Board minutes, pastoral notes", "color": "#EC4899"},
    {"id": "insurance", "name": "Insurance", "icon": "🛡️", "description": "Claims, underwriting reviews", "color": "#14B8A6"},
    {"id": "realestate", "name": "Real Estate", "icon": "🏠", "description": "Showings, closings, inspections", "color": "#84CC16"},
]


def get_verticals():
    """Get list of verticals from templates module or fallback."""
    if templates_mod:
        try:
            return templates_mod.get_all_verticals()
        except Exception:
            pass
    return VERTICALS_FALLBACK


def get_vertical_info(vid):
    """Get a single vertical's info."""
    for v in get_verticals():
        if v["id"] == vid:
            return v
    return VERTICALS_FALLBACK[0]


def get_templates_for_vertical(vid):
    """Get available templates for a vertical."""
    if templates_mod:
        try:
            v = templates_mod.get_vertical(vid)
            if v and "templates" in v:
                return [
                    {"id": tid, "name": t.get("name", tid), "description": t.get("description", "")}
                    for tid, t in v["templates"].items()
                ]
        except Exception:
            pass
    return [{"id": "general", "name": "General Notes", "description": "Standard meeting analysis"}]


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR NAVIGATION
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 1rem 0 0.5rem;">
        <span style="font-size: 2rem;">🧠</span>
        <div style="font-size: 1.3rem; font-weight: 900;
             background: linear-gradient(135deg, #7C3AED, #A78BFA);
             -webkit-background-clip: text; -webkit-text-fill-color: transparent;
             background-clip: text; letter-spacing: -1px;">MeetingMind</div>
        <div style="font-size: 0.65rem; color: #64748B; font-weight: 600;
             letter-spacing: 2px; text-transform: uppercase;">EDGE-NATIVE AI</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    # Navigation buttons
    nav_items = [
        ("home", "🏠  Dashboard"),
        ("record", "🎙️  Record / Upload"),
        ("verticals", "🏢  Industry Verticals"),
        ("history", "📚  Meeting History"),
        ("analytics", "📊  Analytics"),
        ("compliance", "🔒  Compliance"),
        ("settings", "⚙️  Settings"),
    ]

    for page_id, label in nav_items:
        is_active = st.session_state.page == page_id
        wrapper = "nav-active" if is_active else ""
        st.markdown(f'<div class="{wrapper}">', unsafe_allow_html=True)
        if st.button(label, key=f"nav_{page_id}", use_container_width=True):
            st.session_state.page = page_id
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Current vertical indicator
    st.markdown("<hr style='border-color: rgba(124,58,237,0.15); margin: 1rem 0;'>", unsafe_allow_html=True)
    v_info = get_vertical_info(st.session_state.vertical)
    st.markdown(f"""
    <div style="text-align:center; padding: 0.5rem;">
        <div style="font-size: 0.65rem; color: #64748B; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;">Active Vertical</div>
        <div style="font-size: 1.5rem; margin: 0.3rem 0;">{v_info['icon']}</div>
        <div style="font-size: 0.85rem; color: #E2E8F0; font-weight: 700;">{v_info['name']}</div>
    </div>
    """, unsafe_allow_html=True)

    # Ollama status
    st.markdown("<hr style='border-color: rgba(124,58,237,0.15); margin: 1rem 0;'>", unsafe_allow_html=True)
    available, msg = summarizer.check_ollama_available()
    status_color = "#10B981" if available else "#EF4444"
    status_icon = "●" if available else "○"
    st.markdown(f"""
    <div style="text-align:center; padding: 0.3rem;">
        <span style="color: {status_color}; font-size: 0.7rem;">{status_icon}</span>
        <span style="color: #64748B; font-size: 0.7rem; font-weight: 600;"> AI Engine {'Online' if available else 'Offline'}</span>
    </div>
    """, unsafe_allow_html=True)

    # Privacy badge
    st.markdown("""
    <div style="text-align:center; padding: 0.8rem 0 0.3rem;">
        <div class="compliance-badge" style="background: rgba(16,185,129,0.15); color: #10B981; border: 1px solid rgba(16,185,129,0.3);">
            🔒 100% ON-DEVICE
        </div>
        <div style="font-size: 0.6rem; color: #475569; margin-top: 0.4rem;">Zero cloud. Zero data leakage.</div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# HELPER: Format duration
# ─────────────────────────────────────────────────────────────────────────────
def fmt_duration(seconds):
    if not seconds or seconds <= 0:
        return "0m"
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    if h > 0:
        return f"{h}h {m}m"
    return f"{m}m"


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: HOME / DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
def page_home():
    st.markdown("""
    <div class="hero-container">
        <div class="hero-title">MeetingMind</div>
        <div class="hero-sub">Edge-Native AI Meeting Intelligence Platform</div>
        <div style="font-size: 0.75rem; color: #475569; margin-top: 0.5rem;">
            13 Industries &nbsp;·&nbsp; 45+ Templates &nbsp;·&nbsp; 50+ Jurisdictions &nbsp;·&nbsp; 37+ Languages
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Quick stats
    meetings = storage.list_meetings()
    stats = storage.get_storage_stats()
    total = stats["total_meetings"]
    total_dur = sum(m.get("duration", 0) for m in meetings if isinstance(m.get("duration"), (int, float)))
    total_words = sum(m.get("word_count", 0) for m in meetings if isinstance(m.get("word_count"), (int, float)))

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="stat-card"><div class="stat-value">{total}</div><div class="stat-label">Meetings</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-card"><div class="stat-value">{fmt_duration(total_dur)}</div><div class="stat-label">Total Duration</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="stat-card"><div class="stat-value">{total_words:,}</div><div class="stat-label">Words Transcribed</div></div>', unsafe_allow_html=True)
    with c4:
        time_saved = total_words / 40 if total_words > 0 else 0  # 40 WPM manual typing
        st.markdown(f'<div class="stat-card"><div class="stat-value">{fmt_duration(time_saved * 60)}</div><div class="stat-label">Time Saved</div></div>', unsafe_allow_html=True)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # Quick actions
    st.markdown('<div class="section-header">Quick Actions</div>', unsafe_allow_html=True)
    qa1, qa2, qa3 = st.columns(3)
    with qa1:
        if st.button("🎙️  Record New Meeting", use_container_width=True, type="primary"):
            st.session_state.page = "record"
            st.rerun()
    with qa2:
        if st.button("🏢  Choose Industry", use_container_width=True):
            st.session_state.page = "verticals"
            st.rerun()
    with qa3:
        if st.button("📊  View Analytics", use_container_width=True):
            st.session_state.page = "analytics"
            st.rerun()

    # Recent meetings
    if meetings:
        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        st.markdown('<div class="section-header">Recent Meetings</div>', unsafe_allow_html=True)
        for m in meetings[:5]:
            created = ""
            try:
                dt = datetime.fromisoformat(m["created_at"])
                created = dt.strftime("%b %d, %Y  %I:%M %p")
            except (ValueError, KeyError):
                created = m.get("created_at", "")
            dur = fmt_duration(m.get("duration", 0))
            words = m.get("word_count", 0)
            mtype = m.get("meeting_type", "")
            sentiment = m.get("sentiment", "")
            preview = m.get("summary_preview", "")

            st.markdown(f"""
            <div class="meeting-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <span style="color:#E2E8F0; font-weight:700; font-size:0.95rem;">{m.get('title', 'Untitled')}</span>
                        <span style="color:#475569; font-size:0.75rem; margin-left:0.5rem;">{created}</span>
                    </div>
                    <div style="display:flex; gap:0.5rem;">
                        <span class="compliance-badge" style="background:rgba(124,58,237,0.15); color:#A78BFA;">{dur}</span>
                        <span class="compliance-badge" style="background:rgba(124,58,237,0.1); color:#64748B;">{words:,} words</span>
                    </div>
                </div>
                <div style="color:#64748B; font-size:0.78rem; margin-top:0.4rem;">{preview}</div>
            </div>
            """, unsafe_allow_html=True)

    # Verticals preview
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">Industry Verticals</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Purpose-built AI templates for every industry. Select your vertical to unlock specialized note-taking.</div>', unsafe_allow_html=True)

    verticals = get_verticals()
    # Show in rows of 4
    for i in range(0, len(verticals), 4):
        cols = st.columns(4)
        for j, col in enumerate(cols):
            idx = i + j
            if idx < len(verticals):
                v = verticals[idx]
                with col:
                    is_active = st.session_state.vertical == v["id"]
                    border = f"border-color: {v.get('color', '#7C3AED')} !important; box-shadow: 0 0 15px {v.get('color', '#7C3AED')}22;" if is_active else ""
                    st.markdown(f"""
                    <div class="vertical-card" style="{border}">
                        <div class="vertical-icon">{v['icon']}</div>
                        <div class="vertical-name">{v['name']}</div>
                        <div class="vertical-desc">{v.get('description', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"Select", key=f"home_v_{v['id']}", use_container_width=True):
                        st.session_state.vertical = v["id"]
                        st.session_state.page = "record"
                        st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: VERTICALS SELECTOR
# ═══════════════════════════════════════════════════════════════════════════════
def page_verticals():
    st.markdown('<div class="section-header">Industry Verticals</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Select your industry to unlock AI templates designed for your specific workflow. Each vertical includes compliance frameworks, specialized prompts, and export formats.</div>', unsafe_allow_html=True)

    verticals = get_verticals()

    # Tier labels
    tiers = {
        "Tier 1 — Launch Verticals": ["healthcare", "legal", "financial"],
        "Tier 2 — Growth Verticals": ["veterinary", "hr", "education", "sales", "construction"],
        "Tier 3 — Expansion Verticals": ["government", "religious", "insurance", "realestate"],
        "Universal": ["general"],
    }

    for tier_name, tier_ids in tiers.items():
        tier_verticals = [v for v in verticals if v["id"] in tier_ids]
        if not tier_verticals:
            continue

        st.markdown(f"""
        <div style="margin: 1.5rem 0 0.8rem;">
            <span style="font-size: 1rem; font-weight: 700; color: #A78BFA;">{tier_name}</span>
        </div>
        """, unsafe_allow_html=True)

        cols = st.columns(min(len(tier_verticals), 4))
        for i, v in enumerate(tier_verticals):
            with cols[i % 4]:
                is_active = st.session_state.vertical == v["id"]
                border = f"border-color: {v.get('color', '#7C3AED')}; box-shadow: 0 0 20px {v.get('color', '#7C3AED')}33;" if is_active else ""
                check = "✓ " if is_active else ""

                st.markdown(f"""
                <div class="vertical-card" style="{border}">
                    <div class="vertical-icon">{v['icon']}</div>
                    <div class="vertical-name">{check}{v['name']}</div>
                    <div class="vertical-desc">{v.get('description', '')}</div>
                </div>
                """, unsafe_allow_html=True)

                if st.button(
                    "✓ Active" if is_active else "Select",
                    key=f"vert_{v['id']}",
                    use_container_width=True,
                    disabled=is_active,
                ):
                    st.session_state.vertical = v["id"]
                    st.session_state.template = None
                    st.rerun()

    # Show templates for selected vertical
    st.markdown("<hr style='border-color: rgba(124,58,237,0.15); margin: 2rem 0;'>", unsafe_allow_html=True)
    v_info = get_vertical_info(st.session_state.vertical)
    st.markdown(f"""
    <div class="section-header">{v_info['icon']} {v_info['name']} Templates</div>
    """, unsafe_allow_html=True)

    templates = get_templates_for_vertical(st.session_state.vertical)
    for t in templates:
        st.markdown(f"""
        <div class="glass-card">
            <div style="font-weight:700; color:#E2E8F0; font-size:0.95rem;">{t['name']}</div>
            <div style="color:#64748B; font-size:0.8rem; margin-top:0.3rem;">{t.get('description', '')}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"Use {t['name']}", key=f"tmpl_{t['id']}", use_container_width=True):
            st.session_state.template = t["id"]
            st.session_state.page = "record"
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: RECORD / UPLOAD
# ═══════════════════════════════════════════════════════════════════════════════
def page_record():
    v_info = get_vertical_info(st.session_state.vertical)

    st.markdown(f"""
    <div class="section-header">🎙️ Record or Upload</div>
    <div class="section-sub">
        Active: {v_info['icon']} {v_info['name']}
        {(' · Template: ' + st.session_state.template) if st.session_state.template else ''}
    </div>
    """, unsafe_allow_html=True)

    # Compliance consent (if compliance module available)
    if compliance_mod and not st.session_state.consent_given:
        st.markdown("""
        <div class="glass-card" style="border-color: rgba(234,179,8,0.3);">
            <div style="font-weight:700; color:#EAB308; font-size:0.9rem;">⚠️ Recording Consent Required</div>
            <div style="color:#94A3B8; font-size:0.8rem; margin-top:0.5rem;">
                Before recording, ensure all participants have consented. MeetingMind processes everything on-device —
                no audio or transcript data leaves this machine. However, recording consent laws vary by jurisdiction.
            </div>
        </div>
        """, unsafe_allow_html=True)

        consent = st.checkbox("I confirm all participants have consented to this recording", key="consent_check")
        if consent:
            st.session_state.consent_given = True
            st.rerun()
        st.stop()

    # Meeting title
    meeting_title = st.text_input(
        "Meeting Title",
        value=f"{v_info['name']} Meeting — {datetime.now().strftime('%b %d, %Y')}",
        key="meeting_title_input",
    )

    # Template selector
    templates = get_templates_for_vertical(st.session_state.vertical)
    if len(templates) > 1:
        template_names = {t["id"]: t["name"] for t in templates}
        selected_template = st.selectbox(
            "Note Template",
            options=list(template_names.keys()),
            format_func=lambda x: template_names[x],
            index=0,
            key="template_select",
        )
        st.session_state.template = selected_template

    # Language selector
    if languages_mod:
        try:
            langs = languages_mod.get_all_languages()
            lang_options = {l["code"]: languages_mod.get_language_display(l["code"]) for l in langs}
            lang_options = {"auto": "Auto-detect"} | lang_options
        except Exception:
            lang_options = {"auto": "Auto-detect", "en": "English", "es": "Spanish", "fr": "French"}
    else:
        lang_options = {"auto": "Auto-detect", "en": "English", "es": "Spanish", "fr": "French",
                        "de": "German", "pt": "Portuguese", "ja": "Japanese", "zh": "Chinese",
                        "ko": "Korean", "ar": "Arabic", "hi": "Hindi"}

    col_model, col_lang = st.columns(2)
    with col_model:
        model_size = st.selectbox(
            "Whisper Model",
            ["tiny", "base", "small", "medium", "large"],
            index=1,
            help="Larger = more accurate but slower. 'base' is recommended for most use cases.",
            key="model_select",
        )
        st.session_state.whisper_model = model_size
    with col_lang:
        selected_lang = st.selectbox(
            "Language",
            options=list(lang_options.keys()),
            format_func=lambda x: lang_options[x],
            index=0,
            key="lang_select",
        )
        st.session_state.language = None if selected_lang == "auto" else selected_lang

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    # Input mode tabs
    input_tab1, input_tab2 = st.tabs(["🎙️ Record Audio", "📁 Upload File"])

    audio_data = None
    uploaded_file = None

    with input_tab1:
        st.markdown("""
        <div class="glass-card">
            <div style="font-weight:600; color:#E2E8F0; font-size:0.9rem; margin-bottom:0.5rem;">Live Recording</div>
            <div style="color:#64748B; font-size:0.78rem;">Click the microphone to record. All processing happens on this device.</div>
        </div>
        """, unsafe_allow_html=True)
        audio_data = st.audio_input("Record your meeting", key="audio_recorder")

    with input_tab2:
        st.markdown("""
        <div class="glass-card">
            <div style="font-weight:600; color:#E2E8F0; font-size:0.9rem; margin-bottom:0.5rem;">Upload Audio/Video</div>
            <div style="color:#64748B; font-size:0.78rem;">Supports MP3, WAV, M4A, MP4, MOV, WebM, and more.</div>
        </div>
        """, unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Drop your file here",
            type=["mp3", "wav", "m4a", "ogg", "flac", "mp4", "mov", "webm", "mkv", "avi"],
            key="file_uploader",
        )

    # Process button
    has_input = audio_data is not None or uploaded_file is not None
    if has_input and not st.session_state.processing:
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

        if st.button("🚀  Process with AI", use_container_width=True, type="primary"):
            st.session_state.processing = True
            _process_meeting(audio_data, uploaded_file, meeting_title)

    # Show results if available
    if st.session_state.transcript_result and st.session_state.notes_result:
        _render_results()


def _process_meeting(audio_data, uploaded_file, meeting_title):
    """Process audio/video through Whisper + AI summarization."""
    progress = st.progress(0, text="Preparing...")

    def update(msg, pct):
        progress.progress(pct, text=msg)

    # Save input to temp file
    tmp = None
    file_name = "recording.wav"
    try:
        if audio_data is not None:
            tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            tmp.write(audio_data.getvalue())
            tmp.close()
            file_name = "live_recording.wav"
        elif uploaded_file is not None:
            suffix = Path(uploaded_file.name).suffix
            tmp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
            tmp.write(uploaded_file.getvalue())
            tmp.close()
            file_name = uploaded_file.name

        if tmp is None:
            st.error("No audio input provided.")
            st.session_state.processing = False
            return

        # Step 1: Transcribe
        update("Transcribing audio...", 0.1)
        result = transcriber.transcribe_audio(
            file_path=tmp.name,
            model_name=st.session_state.whisper_model,
            progress_callback=update,
            language=st.session_state.language,
        )
        st.session_state.transcript_result = result

        # Step 2: Generate notes (vertical-specific or generic)
        update("Generating AI notes...", 0.6)
        vid = st.session_state.vertical
        tid = st.session_state.template

        if vid != "general" and tid and templates_mod:
            notes = summarizer.generate_vertical_notes(
                transcript=result["text"],
                vertical_id=vid,
                template_id=tid,
                meeting_title=meeting_title,
                progress_callback=update,
            )
        else:
            notes = summarizer.generate_meeting_notes(
                transcript=result["text"],
                meeting_title=meeting_title,
                progress_callback=update,
            )
        st.session_state.notes_result = notes

        # Step 3: Save
        update("Saving meeting...", 0.95)
        meeting_id = storage.save_meeting(
            title=meeting_title,
            transcript=result["text"],
            notes=notes,
            file_name=file_name,
            duration=result["duration"],
            language=result["language"],
            word_count=result["word_count"],
            formatted_transcript=result["formatted_transcript"],
            segments=result["segments"],
        )
        st.session_state.current_meeting_id = meeting_id
        update("Complete!", 1.0)
        time.sleep(0.5)

    except ConnectionError as e:
        st.error(f"AI Engine Error: {e}")
    except Exception as e:
        st.error(f"Processing Error: {e}")
    finally:
        if tmp and os.path.exists(tmp.name):
            os.unlink(tmp.name)
        st.session_state.processing = False
        st.rerun()


def _render_results():
    """Render transcription and AI notes results."""
    result = st.session_state.transcript_result
    notes = st.session_state.notes_result
    v_info = get_vertical_info(st.session_state.vertical)

    st.markdown(f"""
    <div class="section-header">📝 Results — {v_info['icon']} {v_info['name']}</div>
    """, unsafe_allow_html=True)

    # Stats bar
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="stat-card"><div class="stat-value">{fmt_duration(result["duration"])}</div><div class="stat-label">Duration</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-card"><div class="stat-value">{result["word_count"]:,}</div><div class="stat-label">Words</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="stat-card"><div class="stat-value">{result["language"].upper()}</div><div class="stat-label">Language</div></div>', unsafe_allow_html=True)
    with c4:
        sentiment = notes.get("sentiment", "Neutral")
        st.markdown(f'<div class="stat-card"><div class="stat-value">{sentiment}</div><div class="stat-label">Sentiment</div></div>', unsafe_allow_html=True)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # Notes sections
    notes_tab, transcript_tab, export_tab = st.tabs(["📋 AI Notes", "📜 Transcript", "📤 Export"])

    with notes_tab:
        # Check if it's a vertical-specific output
        if notes.get("vertical_id") and notes["vertical_id"] != "general":
            _render_vertical_notes(notes)
        else:
            _render_generic_notes(notes)

    with transcript_tab:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.text_area(
            "Full Transcript (with timestamps)",
            value=result.get("formatted_transcript", result.get("text", "")),
            height=500,
            key="transcript_display",
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with export_tab:
        _render_export(result, notes)


def _render_generic_notes(notes):
    """Render standard meeting notes."""
    # Summary
    if notes.get("summary"):
        st.markdown("""<div class="notes-section"><h4>Meeting Summary</h4>""", unsafe_allow_html=True)
        for bullet in notes["summary"]:
            st.markdown(f"- {bullet}")
        st.markdown("</div>", unsafe_allow_html=True)

    # Key Decisions
    if notes.get("key_decisions"):
        st.markdown("""<div class="notes-section"><h4>Key Decisions</h4>""", unsafe_allow_html=True)
        for d in notes["key_decisions"]:
            st.markdown(f"- {d}")
        st.markdown("</div>", unsafe_allow_html=True)

    # Action Items
    if notes.get("action_items"):
        st.markdown("""<div class="notes-section"><h4>Action Items</h4>""", unsafe_allow_html=True)
        for item in notes["action_items"]:
            if isinstance(item, dict):
                priority = item.get("priority", "Medium")
                colors = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}
                icon = colors.get(priority, "⚪")
                st.markdown(
                    f"- {icon} **{item.get('task', '')}** — "
                    f"*{item.get('assignee', 'TBD')}* · "
                    f"{item.get('deadline', 'No deadline')}"
                )
            else:
                st.markdown(f"- {item}")
        st.markdown("</div>", unsafe_allow_html=True)

    # Discussion Topics
    if notes.get("discussion_topics"):
        st.markdown("""<div class="notes-section"><h4>Discussion Topics</h4>""", unsafe_allow_html=True)
        for t in notes["discussion_topics"]:
            st.markdown(f"- {t}")
        st.markdown("</div>", unsafe_allow_html=True)

    # Follow-up Items
    if notes.get("follow_up_items"):
        st.markdown("""<div class="notes-section"><h4>Follow-up Items</h4>""", unsafe_allow_html=True)
        for f in notes["follow_up_items"]:
            st.markdown(f"- [ ] {f}")
        st.markdown("</div>", unsafe_allow_html=True)


def _render_vertical_notes(notes):
    """Render vertical-specific notes with all available fields."""
    # Show all keys from the notes (except meta keys) as sections
    skip_keys = {"raw_response", "vertical_id", "template_id", "meeting_type", "sentiment"}

    for key, value in notes.items():
        if key in skip_keys:
            continue

        # Format key as section title
        title = key.replace("_", " ").title()

        if isinstance(value, list):
            st.markdown(f'<div class="notes-section"><h4>{title}</h4>', unsafe_allow_html=True)
            for item in value:
                if isinstance(item, dict):
                    for k, v in item.items():
                        st.markdown(f"**{k.replace('_', ' ').title()}:** {v}")
                    st.markdown("---")
                else:
                    st.markdown(f"- {item}")
            st.markdown("</div>", unsafe_allow_html=True)

        elif isinstance(value, dict):
            st.markdown(f'<div class="notes-section"><h4>{title}</h4>', unsafe_allow_html=True)
            for k, v in value.items():
                if isinstance(v, list):
                    st.markdown(f"**{k.replace('_', ' ').title()}:**")
                    for sub in v:
                        st.markdown(f"  - {sub}")
                elif isinstance(v, dict):
                    st.markdown(f"**{k.replace('_', ' ').title()}:**")
                    for sk, sv in v.items():
                        st.markdown(f"  - *{sk}:* {sv}")
                else:
                    st.markdown(f"**{k.replace('_', ' ').title()}:** {v}")
            st.markdown("</div>", unsafe_allow_html=True)

        elif isinstance(value, str) and value:
            st.markdown(f'<div class="notes-section"><h4>{title}</h4>', unsafe_allow_html=True)
            st.markdown(value)
            st.markdown("</div>", unsafe_allow_html=True)


def _render_export(result, notes):
    """Render export options."""
    st.markdown('<div class="section-header">Export Options</div>', unsafe_allow_html=True)

    meeting_data = {
        "title": st.session_state.get("meeting_title_input", "Meeting"),
        "created_at": datetime.now().isoformat(),
        "file_name": "recording",
        "duration": result.get("duration", 0),
        "word_count": result.get("word_count", 0),
        "language": result.get("language", "en"),
        "transcript": result.get("text", ""),
        "formatted_transcript": result.get("formatted_transcript", ""),
        "notes": notes,
    }

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        md_content = exporter.to_markdown(meeting_data)
        st.download_button(
            "📄 Markdown",
            data=md_content,
            file_name="meeting_notes.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with c2:
        txt_content = exporter.to_plain_text(meeting_data)
        st.download_button(
            "📝 Plain Text",
            data=txt_content,
            file_name="meeting_notes.txt",
            mime="text/plain",
            use_container_width=True,
        )
    with c3:
        try:
            pdf_bytes = exporter.to_pdf(meeting_data)
            st.download_button(
                "📕 PDF",
                data=pdf_bytes,
                file_name="meeting_notes.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        except Exception as e:
            st.button("📕 PDF (unavailable)", disabled=True, use_container_width=True)
    with c4:
        json_content = json.dumps(meeting_data, indent=2, ensure_ascii=False, default=str)
        st.download_button(
            "🔧 JSON",
            data=json_content,
            file_name="meeting_data.json",
            mime="application/json",
            use_container_width=True,
        )


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: MEETING HISTORY
# ═══════════════════════════════════════════════════════════════════════════════
def page_history():
    st.markdown('<div class="section-header">📚 Meeting History</div>', unsafe_allow_html=True)

    meetings = storage.list_meetings()

    if not meetings:
        st.markdown("""
        <div class="glass-card" style="text-align:center; padding:3rem;">
            <div style="font-size:3rem; margin-bottom:1rem;">📭</div>
            <div style="color:#64748B; font-size:1rem;">No meetings yet. Record or upload your first meeting!</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🎙️ Record First Meeting", type="primary"):
            st.session_state.page = "record"
            st.rerun()
        return

    # Search
    search_query = st.text_input("🔍 Search meetings...", key="search_meetings", placeholder="Search by title, content, or topic...")

    if search_query:
        meetings = storage.search_meetings(search_query)

    st.markdown(f"<div style='color:#64748B; font-size:0.78rem; margin-bottom:1rem;'>{len(meetings)} meetings found</div>", unsafe_allow_html=True)

    for m in meetings:
        created = ""
        try:
            dt = datetime.fromisoformat(m["created_at"])
            created = dt.strftime("%b %d, %Y  %I:%M %p")
        except (ValueError, KeyError):
            created = m.get("created_at", "")

        dur = fmt_duration(m.get("duration", 0))
        words = m.get("word_count", 0)
        mtype = m.get("meeting_type", "General")
        preview = m.get("summary_preview", "")

        with st.expander(f"{m.get('title', 'Untitled')}  —  {created}  ·  {dur}  ·  {words:,} words"):
            # Load full meeting
            full = storage.load_meeting(m["id"])
            if full:
                notes = full.get("notes", {})

                # Summary
                if notes.get("summary"):
                    st.markdown("**Summary:**")
                    for bullet in notes["summary"]:
                        st.markdown(f"- {bullet}")

                # Action Items
                if notes.get("action_items"):
                    st.markdown("**Action Items:**")
                    for item in notes["action_items"]:
                        if isinstance(item, dict):
                            st.markdown(f"- **{item.get('task', '')}** → {item.get('assignee', 'TBD')}")
                        else:
                            st.markdown(f"- {item}")

                # Transcript preview
                transcript = full.get("formatted_transcript", full.get("transcript", ""))
                if transcript:
                    st.text_area("Transcript", value=transcript[:3000], height=200, key=f"hist_trans_{m['id']}")

                # Export + Delete
                ec1, ec2, ec3 = st.columns([1, 1, 1])
                with ec1:
                    md = exporter.to_markdown(full)
                    st.download_button("📄 Export MD", data=md, file_name=f"{m['id']}_notes.md", mime="text/markdown", key=f"exp_md_{m['id']}", use_container_width=True)
                with ec2:
                    txt = exporter.to_plain_text(full)
                    st.download_button("📝 Export TXT", data=txt, file_name=f"{m['id']}_notes.txt", mime="text/plain", key=f"exp_txt_{m['id']}", use_container_width=True)
                with ec3:
                    if st.button("🗑️ Delete", key=f"del_{m['id']}", use_container_width=True):
                        storage.delete_meeting(m["id"])
                        st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: ANALYTICS
# ═══════════════════════════════════════════════════════════════════════════════
def page_analytics():
    st.markdown('<div class="section-header">📊 Analytics Dashboard</div>', unsafe_allow_html=True)

    meetings = storage.list_meetings()

    if not meetings:
        st.markdown("""
        <div class="glass-card" style="text-align:center; padding:3rem;">
            <div style="font-size:3rem; margin-bottom:1rem;">📊</div>
            <div style="color:#64748B;">Record some meetings to see analytics.</div>
        </div>
        """, unsafe_allow_html=True)
        return

    # Try analytics module first
    if analytics_mod:
        try:
            analyzer = analytics_mod.MeetingAnalytics()
            stats = analyzer.get_dashboard_stats()

            # Top stats
            c1, c2, c3, c4, c5 = st.columns(5)
            with c1:
                st.markdown(f'<div class="stat-card"><div class="stat-value">{stats.get("total_meetings", 0)}</div><div class="stat-label">Total Meetings</div></div>', unsafe_allow_html=True)
            with c2:
                st.markdown(f'<div class="stat-card"><div class="stat-value">{stats.get("total_duration_hours", 0):.1f}h</div><div class="stat-label">Total Hours</div></div>', unsafe_allow_html=True)
            with c3:
                st.markdown(f'<div class="stat-card"><div class="stat-value">{stats.get("total_words", 0):,}</div><div class="stat-label">Total Words</div></div>', unsafe_allow_html=True)
            with c4:
                st.markdown(f'<div class="stat-card"><div class="stat-value">{stats.get("avg_duration_minutes", 0):.0f}m</div><div class="stat-label">Avg Duration</div></div>', unsafe_allow_html=True)
            with c5:
                score = stats.get("productivity_score", analyzer.get_productivity_score())
                st.markdown(f'<div class="stat-card"><div class="stat-value">{score}/100</div><div class="stat-label">Productivity</div></div>', unsafe_allow_html=True)

            st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

            # Charts row
            ch1, ch2 = st.columns(2)
            with ch1:
                st.markdown('<div class="glass-card"><h4 style="color:#A78BFA;">Meeting Types</h4>', unsafe_allow_html=True)
                type_dist = analyzer.get_meeting_type_distribution()
                if type_dist:
                    for mtype, count in sorted(type_dist.items(), key=lambda x: -x[1]):
                        pct = (count / sum(type_dist.values())) * 100
                        st.markdown(f"""
                        <div style="display:flex; justify-content:space-between; align-items:center; margin:0.3rem 0;">
                            <span style="color:#E2E8F0; font-size:0.85rem;">{mtype}</span>
                            <div style="display:flex; align-items:center; gap:0.5rem;">
                                <div style="width:100px; height:6px; background:rgba(124,58,237,0.15); border-radius:3px; overflow:hidden;">
                                    <div style="width:{pct}%; height:100%; background:linear-gradient(90deg,#7C3AED,#A78BFA); border-radius:3px;"></div>
                                </div>
                                <span style="color:#64748B; font-size:0.75rem;">{count}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with ch2:
                st.markdown('<div class="glass-card"><h4 style="color:#A78BFA;">Sentiment</h4>', unsafe_allow_html=True)
                sent_dist = analyzer.get_sentiment_distribution()
                if sent_dist:
                    sent_colors = {"Productive": "#10B981", "Positive": "#3B82F6", "Neutral": "#64748B", "Challenging": "#F59E0B", "Tense": "#EF4444"}
                    for sent, count in sorted(sent_dist.items(), key=lambda x: -x[1]):
                        color = sent_colors.get(sent, "#64748B")
                        st.markdown(f"""
                        <div style="display:flex; justify-content:space-between; margin:0.4rem 0;">
                            <span style="color:{color}; font-size:0.85rem; font-weight:600;">{sent}</span>
                            <span style="color:#64748B; font-size:0.85rem;">{count}</span>
                        </div>
                        """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            # Action item stats
            ai_stats = analyzer.get_action_item_stats()
            if ai_stats and ai_stats.get("total", 0) > 0:
                st.markdown('<div class="glass-card"><h4 style="color:#A78BFA;">Action Items Overview</h4>', unsafe_allow_html=True)
                ac1, ac2, ac3 = st.columns(3)
                with ac1:
                    st.metric("Total", ai_stats["total"])
                with ac2:
                    high = ai_stats.get("by_priority", {}).get("High", 0)
                    st.metric("High Priority", high)
                with ac3:
                    assignees = len(ai_stats.get("by_assignee", {}))
                    st.metric("Assignees", assignees)
                st.markdown('</div>', unsafe_allow_html=True)

            return
        except Exception:
            pass

    # Fallback analytics (without analytics module)
    total = len(meetings)
    total_dur = sum(m.get("duration", 0) for m in meetings if isinstance(m.get("duration"), (int, float)))
    total_words = sum(m.get("word_count", 0) for m in meetings if isinstance(m.get("word_count"), (int, float)))

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="stat-card"><div class="stat-value">{total}</div><div class="stat-label">Meetings</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-card"><div class="stat-value">{total_dur / 3600:.1f}h</div><div class="stat-label">Total Hours</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="stat-card"><div class="stat-value">{total_words:,}</div><div class="stat-label">Total Words</div></div>', unsafe_allow_html=True)
    with c4:
        avg = total_dur / total / 60 if total > 0 else 0
        st.markdown(f'<div class="stat-card"><div class="stat-value">{avg:.0f}m</div><div class="stat-label">Avg Duration</div></div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: COMPLIANCE
# ═══════════════════════════════════════════════════════════════════════════════
def page_compliance():
    st.markdown('<div class="section-header">🔒 Compliance Center</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">MeetingMind processes everything on-device. No audio, transcript, or notes data ever leaves your machine.</div>', unsafe_allow_html=True)

    # Architecture overview
    st.markdown("""
    <div class="glass-card">
        <div style="font-weight:700; color:#10B981; font-size:1rem; margin-bottom:0.8rem;">🛡️ Edge-Native Architecture</div>
        <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:1rem;">
            <div style="text-align:center;">
                <div style="font-size:1.8rem;">🎤</div>
                <div style="color:#E2E8F0; font-weight:600; font-size:0.85rem;">Audio Capture</div>
                <div style="color:#64748B; font-size:0.72rem;">Recorded on-device<br>Never uploaded</div>
            </div>
            <div style="text-align:center;">
                <div style="font-size:1.8rem;">🧠</div>
                <div style="color:#E2E8F0; font-weight:600; font-size:0.85rem;">AI Processing</div>
                <div style="color:#64748B; font-size:0.72rem;">Whisper + LLM<br>100% local inference</div>
            </div>
            <div style="text-align:center;">
                <div style="font-size:1.8rem;">💾</div>
                <div style="color:#E2E8F0; font-weight:600; font-size:0.85rem;">Data Storage</div>
                <div style="color:#64748B; font-size:0.72rem;">~/.meetingmind/<br>Your disk only</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if compliance_mod:
        try:
            # Show frameworks for current vertical
            v_info = get_vertical_info(st.session_state.vertical)
            frameworks = compliance_mod.get_frameworks_for_vertical(st.session_state.vertical)

            st.markdown(f"""
            <div class="section-header">{v_info['icon']} {v_info['name']} Compliance</div>
            """, unsafe_allow_html=True)

            if frameworks:
                for fw in frameworks:
                    if isinstance(fw, dict):
                        st.markdown(f"""
                        <div class="glass-card">
                            <div style="font-weight:700; color:#A78BFA; font-size:0.95rem;">{fw.get('name', '')}</div>
                            <div style="color:#94A3B8; font-size:0.8rem; margin:0.4rem 0;">{fw.get('description', '')}</div>
                            <div style="color:#10B981; font-size:0.78rem; font-weight:600;">✓ {fw.get('meetingmind_compliance', 'Compliant via on-device processing')}</div>
                        </div>
                        """, unsafe_allow_html=True)

            # Jurisdiction info
            st.markdown('<div class="section-header">🌍 Recording Consent Laws</div>', unsafe_allow_html=True)

            cm = compliance_mod.ConsentManager()
            reqs = cm.get_consent_requirements()
            if isinstance(reqs, dict):
                st.markdown(f"""
                <div class="glass-card">
                    <div style="font-weight:700; color:#E2E8F0;">Your Jurisdiction: {reqs.get('name', 'Unknown')}</div>
                    <div style="color:#94A3B8; font-size:0.85rem; margin-top:0.4rem;">Consent Type: <b>{reqs.get('consent_type', 'Unknown')}</b></div>
                    <div style="color:#64748B; font-size:0.8rem; margin-top:0.3rem;">{reqs.get('description', '')}</div>
                </div>
                """, unsafe_allow_html=True)

            # Audit log
            st.markdown('<div class="section-header">📋 Audit Log</div>', unsafe_allow_html=True)
            logger = compliance_mod.AuditLogger()
            events = logger.get_events()
            if events:
                for event in events[:20]:
                    if isinstance(event, dict):
                        st.markdown(f"""
                        <div style="padding:0.4rem 0; border-bottom:1px solid rgba(124,58,237,0.08);">
                            <span style="color:#64748B; font-size:0.72rem;">{event.get('timestamp', '')[:19]}</span>
                            <span style="color:#A78BFA; font-size:0.78rem; font-weight:600; margin-left:0.5rem;">{event.get('event_type', '')}</span>
                            <span style="color:#94A3B8; font-size:0.75rem; margin-left:0.5rem;">{event.get('details', '')}</span>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.markdown('<div style="color:#64748B; font-size:0.85rem;">No audit events yet.</div>', unsafe_allow_html=True)

            return
        except Exception:
            pass

    # Fallback compliance info
    st.markdown("""
    <div class="glass-card">
        <div style="font-weight:700; color:#A78BFA; font-size:1rem; margin-bottom:0.8rem;">Compliance Frameworks Supported</div>
    </div>
    """, unsafe_allow_html=True)

    frameworks = [
        ("🏥 HIPAA", "Healthcare data stays on-device. No BAA needed — PHI never transmitted.", "#EF4444"),
        ("⚖️ Attorney-Client Privilege", "Privileged communications never leave the attorney's device. Heppner-safe.", "#3B82F6"),
        ("🎓 FERPA", "Student education records processed locally. No third-party data sharing.", "#06B6D4"),
        ("🏦 SEC Rule 17a-4", "Financial meeting records stored on-device with full audit trail.", "#10B981"),
        ("👁️ BIPA", "No biometric data (voiceprints) transmitted. Zero BIPA exposure.", "#F59E0B"),
        ("🇪🇺 GDPR", "Data minimization by design. No cross-border transfers. On-device = privacy by default.", "#6366F1"),
        ("🔒 FINRA 3110", "Supervisory compliance for financial advisor meetings.", "#EC4899"),
        ("👶 COPPA", "No children's data collected or transmitted to third parties.", "#14B8A6"),
    ]

    for name, desc, color in frameworks:
        st.markdown(f"""
        <div class="glass-card" style="border-left: 3px solid {color};">
            <div style="font-weight:700; color:#E2E8F0; font-size:0.9rem;">{name}</div>
            <div style="color:#94A3B8; font-size:0.8rem; margin-top:0.3rem;">{desc}</div>
            <div style="color:#10B981; font-size:0.75rem; font-weight:600; margin-top:0.4rem;">✓ Automatically compliant via on-device architecture</div>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: SETTINGS
# ═══════════════════════════════════════════════════════════════════════════════
def page_settings():
    st.markdown('<div class="section-header">⚙️ Settings</div>', unsafe_allow_html=True)

    # AI Engine
    st.markdown("""
    <div class="glass-card">
        <div style="font-weight:700; color:#A78BFA; font-size:0.95rem; margin-bottom:0.8rem;">🧠 AI Engine</div>
    </div>
    """, unsafe_allow_html=True)

    available, msg = summarizer.check_ollama_available()
    if available:
        st.success(f"Ollama: {msg}")
    else:
        st.warning(f"Ollama: {msg}")

    st.selectbox(
        "Default Whisper Model",
        ["tiny", "base", "small", "medium", "large"],
        index=1,
        help="tiny=fastest, large=most accurate. 'base' recommended.",
        key="settings_whisper_model",
    )

    st.selectbox(
        "LLM Model",
        ["llama3.2", "llama3.1", "mistral", "phi3", "gemma2"],
        index=0,
        help="Requires Ollama. Run 'ollama pull <model>' first.",
        key="settings_llm_model",
    )

    # Storage
    st.markdown("""
    <div class="glass-card">
        <div style="font-weight:700; color:#A78BFA; font-size:0.95rem; margin-bottom:0.8rem;">💾 Storage</div>
    </div>
    """, unsafe_allow_html=True)

    stats = storage.get_storage_stats()
    st.markdown(f"""
    - **Location:** `{stats['storage_path']}`
    - **Meetings stored:** {stats['total_meetings']}
    - **Disk usage:** {stats['total_size_mb']} MB
    """)

    # Data export
    st.markdown("""
    <div class="glass-card">
        <div style="font-weight:700; color:#A78BFA; font-size:0.95rem; margin-bottom:0.8rem;">📤 Data Export</div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("📦 Export All Meetings (JSON)", use_container_width=True):
            all_data = storage.export_all_meetings_json()
            st.download_button(
                "Download JSON",
                data=all_data,
                file_name="meetingmind_export.json",
                mime="application/json",
                key="export_all_json",
            )
    with c2:
        if compliance_mod:
            if st.button("📋 Export Audit Log", use_container_width=True):
                try:
                    logger = compliance_mod.AuditLogger()
                    audit_data = logger.export()
                    st.download_button(
                        "Download Audit Log",
                        data=json.dumps(audit_data, indent=2, default=str) if isinstance(audit_data, (dict, list)) else str(audit_data),
                        file_name="meetingmind_audit.json",
                        mime="application/json",
                        key="export_audit",
                    )
                except Exception:
                    st.info("Audit log not available.")

    # About
    st.markdown("""
    <div class="glass-card" style="margin-top:1rem;">
        <div style="font-weight:700; color:#A78BFA; font-size:0.95rem; margin-bottom:0.5rem;">About MeetingMind</div>
        <div style="color:#94A3B8; font-size:0.82rem;">
            Edge-Native AI Meeting Intelligence Platform<br>
            Version 2.0.0<br><br>
            13 Industry Verticals · 45+ Templates · 50+ Jurisdictions · 37+ Languages<br>
            100% on-device processing. Zero cloud. Zero data leakage.<br><br>
            <span style="color:#64748B;">Powered by Whisper (OpenAI) + Ollama (Local LLM)</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# ROUTER
# ═══════════════════════════════════════════════════════════════════════════════
PAGES = {
    "home": page_home,
    "record": page_record,
    "verticals": page_verticals,
    "history": page_history,
    "analytics": page_analytics,
    "compliance": page_compliance,
    "settings": page_settings,
}

current_page = st.session_state.get("page", "home")
page_fn = PAGES.get(current_page, page_home)
page_fn()
