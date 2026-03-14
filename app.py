"""
MeetingMind — AI Meeting Assistant
A professional Streamlit app for transcribing, summarizing, and managing meeting notes.
"""

import os
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path

import streamlit as st

# ── Path setup so core imports work regardless of cwd ──────────────────────────
sys.path.insert(0, str(Path(__file__).parent))

from core import transcriber, summarizer, storage, exporter

# ──────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG  (must be the very first Streamlit call)
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MeetingMind",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS
# ──────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* ── Base resets ── */
    [data-testid="stAppViewContainer"] {
        background: #0F0F1A;
    }
    [data-testid="stSidebar"] {
        background: #13132B !important;
        border-right: 1px solid #2D2D5E;
    }

    /* ── Gradient hero text ── */
    .hero-title {
        font-size: 3.6rem;
        font-weight: 900;
        background: linear-gradient(135deg, #7C3AED 0%, #A855F7 45%, #EC4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1.1;
        letter-spacing: -1px;
        animation: fadeSlideDown 0.7s ease both;
    }
    .hero-tagline {
        font-size: 1.2rem;
        color: #94A3B8;
        margin-top: 0.4rem;
        animation: fadeSlideDown 0.9s ease both;
    }

    @keyframes fadeSlideDown {
        from { opacity: 0; transform: translateY(-18px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    /* ── Stat card ── */
    .stat-card {
        background: linear-gradient(135deg, #1A1A2E 0%, #1E1E3F 100%);
        border: 1px solid #2D2D5E;
        border-radius: 16px;
        padding: 1.4rem 1.6rem;
        text-align: center;
        transition: transform 0.2s, box-shadow 0.2s;
        cursor: default;
    }
    .stat-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(124, 58, 237, 0.25);
        border-color: #7C3AED;
    }
    .stat-value {
        font-size: 2.4rem;
        font-weight: 800;
        background: linear-gradient(135deg, #7C3AED, #A855F7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .stat-label {
        font-size: 0.82rem;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 0.2rem;
    }

    /* ── Meeting card ── */
    .meeting-card {
        background: #1A1A2E;
        border: 1px solid #2D2D5E;
        border-radius: 14px;
        padding: 1.2rem 1.4rem;
        margin-bottom: 0.85rem;
        transition: transform 0.18s, box-shadow 0.18s, border-color 0.18s;
        position: relative;
        overflow: hidden;
    }
    .meeting-card::before {
        content: "";
        position: absolute;
        left: 0; top: 0; bottom: 0;
        width: 4px;
        background: linear-gradient(180deg, #7C3AED, #EC4899);
        border-radius: 4px 0 0 4px;
    }
    .meeting-card:hover {
        transform: translateX(4px);
        box-shadow: 0 8px 30px rgba(124, 58, 237, 0.18);
        border-color: #7C3AED;
    }
    .meeting-card-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #E2E8F0;
        margin-bottom: 0.35rem;
    }
    .meeting-card-meta {
        font-size: 0.8rem;
        color: #64748B;
        display: flex;
        gap: 1rem;
        flex-wrap: wrap;
    }
    .meeting-card-meta span { display: flex; align-items: center; gap: 0.3rem; }

    /* ── Priority badges ── */
    .badge {
        display: inline-block;
        padding: 0.2rem 0.65rem;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    .badge-high   { background: rgba(239,68,68,0.18); color: #F87171; border: 1px solid rgba(239,68,68,0.35); }
    .badge-medium { background: rgba(234,179,8,0.18);  color: #FCD34D; border: 1px solid rgba(234,179,8,0.35); }
    .badge-low    { background: rgba(34,197,94,0.18);  color: #4ADE80; border: 1px solid rgba(34,197,94,0.35); }
    .badge-other  { background: rgba(100,116,139,0.18); color: #94A3B8; border: 1px solid rgba(100,116,139,0.35); }

    /* ── Section card ── */
    .section-card {
        background: #1A1A2E;
        border: 1px solid #2D2D5E;
        border-radius: 14px;
        padding: 1.4rem 1.6rem;
        margin-bottom: 1rem;
    }
    .section-header {
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: #7C3AED;
        margin-bottom: 0.8rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #2D2D5E;
    }

    /* ── Gradient upload zone ── */
    [data-testid="stFileUploader"] {
        border: 2px dashed #2D2D5E !important;
        border-radius: 14px !important;
        background: #13132B !important;
        transition: border-color 0.2s !important;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: #7C3AED !important;
    }

    /* ── Gradient primary button ── */
    .stButton > button[kind="primary"],
    .stButton > button {
        background: linear-gradient(135deg, #7C3AED, #A855F7) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        letter-spacing: 0.3px !important;
        transition: opacity 0.2s, transform 0.15s, box-shadow 0.2s !important;
        box-shadow: 0 4px 15px rgba(124,58,237,0.35) !important;
    }
    .stButton > button:hover {
        opacity: 0.92 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(124,58,237,0.5) !important;
    }

    /* ── Ollama status ── */
    .ollama-ok   { color: #4ADE80; font-size: 0.82rem; }
    .ollama-err  { color: #F87171; font-size: 0.82rem; }

    /* ── Dividers ── */
    hr { border-color: #2D2D5E !important; }

    /* ── Misc ── */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #7C3AED, #A855F7, #EC4899) !important;
    }
    [data-testid="stAlert"] { border-radius: 10px !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 0.5rem; }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        font-weight: 600;
    }
    .block-container { padding-top: 1.5rem !important; }

    /* ── Transcript segment ── */
    .transcript-segment {
        border-bottom: 1px solid #1E1E3F;
        padding: 0.55rem 0;
        font-size: 0.88rem;
        line-height: 1.6;
    }
    .ts-time {
        color: #7C3AED;
        font-size: 0.78rem;
        font-family: monospace;
        margin-right: 0.6rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────────────────────────────────────
# SESSION STATE DEFAULTS
# ──────────────────────────────────────────────────────────────────────────────
_DEFAULTS: dict = {
    "page": "home",
    "current_meeting_id": None,
    "whisper_model": "base",
    "ollama_model": "llama3.2",
    "auto_save": True,
    "search_query_lib": "",
}
for _k, _v in _DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v


# ──────────────────────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────────────────────

def navigate(page: str, meeting_id: str | None = None) -> None:
    st.session_state.page = page
    if meeting_id is not None:
        st.session_state.current_meeting_id = meeting_id
    st.rerun()


def fmt_duration(seconds: float) -> str:
    if not seconds or seconds <= 0:
        return "—"
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    if h > 0:
        return f"{h}h {m}m"
    if m > 0:
        return f"{m}m {s}s"
    return f"{s}s"


def fmt_date(iso: str) -> str:
    try:
        return datetime.fromisoformat(iso).strftime("%b %d, %Y")
    except Exception:
        return iso or "—"


def fmt_datetime_long(iso: str) -> str:
    try:
        return datetime.fromisoformat(iso).strftime("%B %d, %Y at %I:%M %p")
    except Exception:
        return iso or "—"


def priority_badge(priority: str) -> str:
    p = (priority or "").strip().capitalize()
    cls = {"High": "high", "Medium": "medium", "Low": "low"}.get(p, "other")
    return f'<span class="badge badge-{cls}">{p or "—"}</span>'


def meeting_type_icon(mtype: str) -> str:
    return {
        "Planning": "📋", "Status Update": "📊", "Brainstorm": "💡",
        "Review": "🔍", "Decision": "✅", "Interview": "🎤",
        "Training": "📚", "Other": "📝",
    }.get(mtype, "📝")


def sentiment_icon(sentiment: str) -> str:
    return {
        "Productive": "🚀", "Positive": "😊", "Neutral": "😐",
        "Challenging": "😤", "Tense": "😬",
    }.get(sentiment, "😐")


def check_ollama_status() -> tuple[bool, str]:
    return summarizer.check_ollama_available(st.session_state.ollama_model)


def _total_hours(meetings: list) -> float:
    return round(sum(m.get("duration", 0) for m in meetings) / 3600, 1)


def _total_actions(meetings: list) -> int:
    total = 0
    for m in meetings:
        full = storage.load_meeting(m["id"])
        if full:
            total += len(full.get("notes", {}).get("action_items", []))
    return total


def _action_count_for(meeting_id: str) -> int:
    full = storage.load_meeting(meeting_id)
    if full:
        return len(full.get("notes", {}).get("action_items", []))
    return 0


def _copy_to_clipboard(text: str, toast_msg: str = "Copied!") -> None:
    try:
        import pyperclip
        pyperclip.copy(text)
        st.toast(toast_msg)
    except Exception:
        st.code(text, language="text")


# ──────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────────────────────────

def render_sidebar() -> None:
    with st.sidebar:
        st.markdown(
            """
            <div style="padding:1rem 0 0.5rem 0; text-align:center;">
                <div style="font-size:2rem; margin-bottom:0.1rem;">🧠</div>
                <div style="font-size:1.25rem; font-weight:900;
                            background:linear-gradient(135deg,#7C3AED,#EC4899);
                            -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                            background-clip:text;">
                    MeetingMind
                </div>
                <div style="font-size:0.72rem; color:#475569; margin-top:0.15rem;">
                    AI Meeting Assistant
                </div>
            </div>
            <hr style="margin:0.8rem 0;">
            """,
            unsafe_allow_html=True,
        )

        nav_items = [
            ("home",     "🏠", "Dashboard"),
            ("new",      "➕", "New Meeting"),
            ("library",  "📚", "Meeting Library"),
            ("settings", "⚙️", "Settings"),
        ]

        for page_id, icon, label in nav_items:
            if st.button(
                f"{icon}  {label}",
                key=f"nav_{page_id}",
                use_container_width=True,
            ):
                navigate(page_id)

        st.markdown("<hr style='margin:0.8rem 0;'>", unsafe_allow_html=True)

        # Ollama status dot
        ok, _ = check_ollama_status()
        dot = "🟢" if ok else "🔴"
        status_label = "connected" if ok else "offline"
        st.markdown(
            f"<div style='font-size:0.78rem; color:#64748B;'>"
            f"{dot} Ollama {status_label}"
            f"</div>",
            unsafe_allow_html=True,
        )
        if not ok:
            with st.expander("Fix Ollama", expanded=False):
                st.code("ollama serve", language="bash")
                st.code(f"ollama pull {st.session_state.ollama_model}", language="bash")

        st.markdown("<br>", unsafe_allow_html=True)

        # Quick counters
        meetings = storage.list_meetings()
        st.markdown(
            f"""
            <div style="font-size:0.75rem; color:#475569; padding:0.6rem 0.8rem;
                        background:#13132B; border-radius:10px; border:1px solid #2D2D5E;">
                <div style="margin-bottom:0.3rem;">
                    <span style="color:#7C3AED; font-weight:700;">{len(meetings)}</span>
                    &nbsp;meetings saved
                </div>
                <div>
                    <span style="color:#7C3AED; font-weight:700;">{_total_hours(meetings)}</span>
                    &nbsp;hours transcribed
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ──────────────────────────────────────────────────────────────────────────────
# PAGE: HOME / DASHBOARD
# ──────────────────────────────────────────────────────────────────────────────

def page_home() -> None:
    # Hero
    st.markdown(
        """
        <div style="margin-bottom:1.2rem;">
            <div class="hero-title">MeetingMind</div>
            <div class="hero-tagline">Your AI-powered meeting intelligence platform</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_a, col_b, _ = st.columns([1.6, 1.4, 6])
    with col_a:
        if st.button("➕  New Meeting", use_container_width=True):
            navigate("new")
    with col_b:
        if st.button("📚  Library", use_container_width=True):
            navigate("library")

    st.markdown("<br>", unsafe_allow_html=True)

    # Stats
    meetings = storage.list_meetings()
    stats = [
        (str(len(meetings)),                                "Total Meetings"),
        (str(_total_hours(meetings)),                       "Hours Transcribed"),
        (str(_total_actions(meetings)),                     "Action Items Tracked"),
        (fmt_date(meetings[0]["created_at"]) if meetings else "—", "Latest Meeting"),
    ]

    cols = st.columns(4)
    for col, (val, label) in zip(cols, stats):
        with col:
            st.markdown(
                f"""
                <div class="stat-card">
                    <div class="stat-value">{val}</div>
                    <div class="stat-label">{label}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>Recent Meetings</div>", unsafe_allow_html=True)

    if not meetings:
        st.markdown(
            """
            <div style="text-align:center; padding:3rem; color:#475569;
                        background:#1A1A2E; border:1px dashed #2D2D5E; border-radius:14px;">
                <div style="font-size:2.5rem; margin-bottom:0.6rem;">🎙️</div>
                <div style="font-size:1.05rem; font-weight:600; color:#64748B;">No meetings yet</div>
                <div style="font-size:0.85rem; margin-top:0.3rem;">
                    Upload your first recording to get started
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕  Transcribe Your First Meeting"):
            navigate("new")
        return

    # Search
    search = st.text_input(
        "Search",
        placeholder="🔍  Search by keyword, topic, or action item...",
        key="home_search",
        label_visibility="collapsed",
    )
    results = storage.search_meetings(search) if search else meetings[:8]

    if search and not results:
        st.info(f'No meetings found matching "{search}"')

    for m in results:
        mtype = m.get("meeting_type", "Other")
        sentiment = m.get("sentiment", "Neutral")
        ac = _action_count_for(m["id"])

        card_col, btn_col = st.columns([8, 1.2])
        with card_col:
            st.markdown(
                f"""
                <div class="meeting-card">
                    <div class="meeting-card-title">
                        {meeting_type_icon(mtype)} {m.get("title", "Untitled")}
                    </div>
                    <div class="meeting-card-meta">
                        <span>📅 {fmt_date(m.get("created_at",""))}</span>
                        <span>⏱ {fmt_duration(m.get("duration",0))}</span>
                        <span>📄 {m.get("file_name","—")}</span>
                        <span>✅ {ac} action items</span>
                        <span>{sentiment_icon(sentiment)} {sentiment}</span>
                    </div>
                    <div style="margin-top:0.55rem; font-size:0.82rem; color:#64748B; font-style:italic;">
                        {m.get("summary_preview","")[:160]}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with btn_col:
            st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
            if st.button("Open →", key=f"home_open_{m['id']}"):
                navigate("view", m["id"])


# ──────────────────────────────────────────────────────────────────────────────
# PAGE: NEW MEETING
# ──────────────────────────────────────────────────────────────────────────────

def page_new_meeting() -> None:
    st.markdown(
        "<div class='hero-title' style='font-size:2.2rem'>➕ New Meeting</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div class='hero-tagline'>Upload an audio or video file — AI does the rest.</div>",
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)

    # Ollama pre-check banner
    ollama_ok, ollama_msg = check_ollama_status()
    if not ollama_ok:
        st.warning(
            f"**Ollama is not available** — {ollama_msg}\n\n"
            "Transcription will still work, but AI note generation will be skipped."
        )

    # ── Step 1: Upload ──────────────────────────────────────────────────────
    st.markdown("<div class='section-header'>Step 1 — Upload File</div>", unsafe_allow_html=True)

    col_up, col_opts = st.columns([3, 1.5])
    with col_up:
        uploaded = st.file_uploader(
            "Drop your meeting recording here",
            type=["mp3", "wav", "mp4", "mov", "webm", "m4a", "ogg", "flac"],
            help="Supported: MP3, WAV, MP4, MOV, WEBM, M4A, OGG, FLAC (max 500 MB)",
            label_visibility="collapsed",
        )

    with col_opts:
        meeting_title = st.text_input(
            "Meeting Title (optional)",
            placeholder="e.g. Q1 Planning Sprint",
        )
        num_speakers = st.selectbox(
            "Number of Speakers",
            options=[1, 2, 3, 4, 5],
            index=1,
        )
        lang_choice = st.selectbox(
            "Language",
            ["Auto-detect", "English", "French", "Spanish", "German", "Japanese", "Chinese"],
        )

    lang_map = {
        "Auto-detect": None, "English": "en", "French": "fr",
        "Spanish": "es", "German": "de", "Japanese": "ja", "Chinese": "zh",
    }
    lang_code = lang_map[lang_choice]

    if not uploaded:
        st.markdown(
            "<div style='text-align:center; padding:1.5rem; color:#475569; font-size:0.85rem;'>"
            "Supports MP3, WAV, M4A, OGG, FLAC, MP4, MOV, WEBM · Max 500 MB"
            "</div>",
            unsafe_allow_html=True,
        )
        return

    # File info strip
    file_size_mb = len(uploaded.getvalue()) / (1024 * 1024)
    auto_title = (
        meeting_title.strip()
        or Path(uploaded.name).stem.replace("_", " ").replace("-", " ").title()
    )

    st.markdown(
        f"""
        <div style="background:#13132B; border:1px solid #2D2D5E; border-radius:10px;
                    padding:0.7rem 1.1rem; font-size:0.85rem; color:#94A3B8;
                    display:flex; gap:1.5rem; align-items:center; margin-top:0.5rem;">
            <span>📁 <strong>{uploaded.name}</strong></span>
            <span>💾 {file_size_mb:.1f} MB</span>
            <span>🏷 {uploaded.type or "audio/unknown"}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Step 2: Model info & start ──────────────────────────────────────────
    st.markdown("<div class='section-header'>Step 2 — Transcribe & Analyse</div>", unsafe_allow_html=True)

    wm = st.session_state.whisper_model
    model_notes = {
        "tiny":   "Fastest · least accurate",
        "base":   "Good balance (recommended)",
        "small":  "Better accuracy · moderate speed",
        "medium": "High accuracy · slower",
        "large":  "Best accuracy · slowest",
    }
    st.info(
        f"Using Whisper **{wm}** — {model_notes.get(wm, '')}. "
        "Change model in **Settings**."
    )

    if st.button("🚀  Start Transcription & AI Analysis", use_container_width=False):
        # Save upload to a temp file
        sfx = Path(uploaded.name).suffix or ".audio"
        with tempfile.NamedTemporaryFile(suffix=sfx, delete=False) as tmp:
            tmp.write(uploaded.getvalue())
            tmp_path = tmp.name

        try:
            prog = st.progress(0, text="Preparing...")
            status = st.empty()

            def update(msg: str, pct: float) -> None:
                prog.progress(min(pct, 1.0), text=msg)
                status.markdown(
                    f"<div style='color:#94A3B8; font-size:0.88rem;'>⏳ {msg}</div>",
                    unsafe_allow_html=True,
                )

            # ── Transcription ───────────────────────────────────────────────
            update("Initialising Whisper engine...", 0.02)
            t_result = transcriber.transcribe_audio(
                file_path=tmp_path,
                model_name=wm,
                progress_callback=update,
                language=lang_code,
            )

            # Optional speaker labels
            if num_speakers > 1 and t_result.get("segments"):
                spk_map = {i: f"Speaker {i+1}" for i in range(num_speakers)}
                t_result["formatted_transcript"] = transcriber.apply_speaker_labels(
                    t_result["segments"], spk_map, num_speakers
                )

            # ── Summarisation ───────────────────────────────────────────────
            update("AI is analysing the meeting...", 0.55)

            if not ollama_ok:
                notes = {
                    "summary": ["Transcription complete. Start Ollama to generate AI notes."],
                    "key_decisions": [], "action_items": [], "discussion_topics": [],
                    "follow_up_items": [], "meeting_type": "Other",
                    "sentiment": "Neutral", "raw_response": "",
                }
            else:
                try:
                    notes = summarizer.generate_meeting_notes(
                        transcript=t_result["text"],
                        meeting_title=auto_title,
                        model=st.session_state.ollama_model,
                        progress_callback=lambda msg, pct: update(msg, 0.55 + pct * 0.40),
                    )
                except Exception as e:
                    st.warning(f"AI summarisation failed: {e}")
                    notes = {
                        "summary": ["AI summarisation failed — review the transcript."],
                        "key_decisions": [], "action_items": [], "discussion_topics": [],
                        "follow_up_items": [], "meeting_type": "Other",
                        "sentiment": "Neutral", "raw_response": str(e),
                    }

            update("Finalising...", 0.98)

            # ── Save or preview ─────────────────────────────────────────────
            if st.session_state.auto_save:
                mid = storage.save_meeting(
                    title=auto_title,
                    transcript=t_result["text"],
                    notes=notes,
                    file_name=uploaded.name,
                    duration=t_result["duration"],
                    language=t_result["language"],
                    word_count=t_result["word_count"],
                    formatted_transcript=t_result["formatted_transcript"],
                    segments=t_result["segments"],
                )
                prog.progress(1.0, text="Done!")
                status.empty()
                st.success(
                    f"Meeting saved — **{auto_title}** · "
                    f"{fmt_duration(t_result['duration'])} · "
                    f"{t_result['word_count']:,} words"
                )
                time.sleep(0.6)
                navigate("view", mid)
            else:
                prog.progress(1.0, text="Done!")
                status.empty()
                st.success("Transcription complete! Review below, then save.")
                _render_pending_preview(auto_title, t_result, notes, uploaded.name)

        except Exception as exc:
            st.error(f"Transcription failed: {exc}")
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass


def _render_pending_preview(
    title: str, t_result: dict, notes: dict, file_name: str
) -> None:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        "<div class='section-header'>Preview — Review before saving</div>",
        unsafe_allow_html=True,
    )

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Duration",   fmt_duration(t_result["duration"]))
    m2.metric("Words",      f"{t_result['word_count']:,}")
    m3.metric("Language",   t_result["language"].upper())
    m4.metric("Type",       notes.get("meeting_type", "—"))
    m5.metric("Sentiment",  notes.get("sentiment", "—"))

    with st.expander("Summary", expanded=True):
        for b in notes.get("summary", []):
            st.markdown(f"- {b}")

    with st.expander("Action Items"):
        items = notes.get("action_items", [])
        if not items:
            st.write("None identified.")
        for item in items:
            if isinstance(item, dict):
                st.markdown(
                    f"- **{item.get('task','')}** — "
                    f"{item.get('assignee','TBD')} | {item.get('deadline','?')} | "
                    + priority_badge(item.get("priority", "Medium")),
                    unsafe_allow_html=True,
                )

    custom_title = st.text_input("Meeting Title", value=title, key="pending_title")
    if st.button("💾  Save Meeting", key="save_pending"):
        mid = storage.save_meeting(
            title=custom_title.strip() or title,
            transcript=t_result["text"],
            notes=notes,
            file_name=file_name,
            duration=t_result["duration"],
            language=t_result["language"],
            word_count=t_result["word_count"],
            formatted_transcript=t_result["formatted_transcript"],
            segments=t_result["segments"],
        )
        navigate("view", mid)


# ──────────────────────────────────────────────────────────────────────────────
# PAGE: MEETING VIEW
# ──────────────────────────────────────────────────────────────────────────────

def page_view_meeting() -> None:
    mid = st.session_state.current_meeting_id
    if not mid:
        st.warning("No meeting selected.")
        if st.button("← Back to Library"):
            navigate("library")
        return

    meeting = storage.load_meeting(mid)
    if not meeting:
        st.error("Meeting not found — it may have been deleted.")
        if st.button("← Back to Library"):
            navigate("library")
        return

    notes = meeting.get("notes", {})

    # ── Header ──────────────────────────────────────────────────────────────
    hdr_col, act_col = st.columns([6, 2])
    with hdr_col:
        st.markdown(
            f"<div class='hero-title' style='font-size:2rem;'>"
            f"{meeting_type_icon(notes.get('meeting_type','Other'))} "
            f"{meeting.get('title','Untitled')}"
            f"</div>",
            unsafe_allow_html=True,
        )
        meta = [
            f"📅 {fmt_datetime_long(meeting.get('created_at',''))}",
            f"⏱ {fmt_duration(meeting.get('duration',0))}",
            f"💬 {meeting.get('word_count',0):,} words",
            f"🌐 {meeting.get('language','en').upper()}",
            f"{sentiment_icon(notes.get('sentiment','Neutral'))} {notes.get('sentiment','Neutral')}",
        ]
        st.markdown(
            "<div style='color:#64748B; font-size:0.82rem; display:flex; gap:1rem;"
            "flex-wrap:wrap; margin-top:0.4rem;'>"
            + "".join(f"<span>{p}</span>" for p in meta)
            + "</div>",
            unsafe_allow_html=True,
        )

    with act_col:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("← Library", use_container_width=True, key="view_back"):
            navigate("library")
        if st.button("🗑  Delete", use_container_width=True, key="view_delete"):
            st.session_state[f"confirm_delete_{mid}"] = True

    # Delete confirmation
    if st.session_state.get(f"confirm_delete_{mid}"):
        st.warning("This will permanently delete the meeting. Are you sure?")
        yes_col, no_col, _ = st.columns([1, 1, 5])
        with yes_col:
            if st.button("Yes, delete", key="del_yes"):
                storage.delete_meeting(mid)
                st.session_state.current_meeting_id = None
                navigate("library")
        with no_col:
            if st.button("Cancel", key="del_no"):
                del st.session_state[f"confirm_delete_{mid}"]
                st.rerun()

    # Inline rename
    with st.expander("✏️  Rename this meeting", expanded=False):
        new_title = st.text_input(
            "New title",
            value=meeting.get("title", ""),
            key=f"rename_input_{mid}",
        )
        if st.button("Save", key=f"rename_save_{mid}"):
            if new_title.strip():
                storage.update_meeting_title(mid, new_title.strip())
                st.success("Title updated!")
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Tabs ────────────────────────────────────────────────────────────────
    tab_summary, tab_transcript, tab_actions, tab_export = st.tabs(
        ["📋  Summary", "📜  Full Transcript", "✅  Action Items", "📤  Export"]
    )

    # ── TAB 1: SUMMARY ──────────────────────────────────────────────────────
    with tab_summary:
        left, right = st.columns([1.1, 1])

        with left:
            st.markdown(
                "<div class='section-card'>"
                "<div class='section-header'>Meeting Summary</div>",
                unsafe_allow_html=True,
            )
            for b in notes.get("summary", []):
                st.markdown(
                    f"<div style='margin-bottom:0.5rem; color:#CBD5E1;'>• {b}</div>",
                    unsafe_allow_html=True,
                )
            st.markdown("</div>", unsafe_allow_html=True)

            decisions = notes.get("key_decisions", [])
            if decisions:
                st.markdown(
                    "<div class='section-card'>"
                    "<div class='section-header'>Key Decisions</div>",
                    unsafe_allow_html=True,
                )
                for d in decisions:
                    st.markdown(
                        f"<div style='margin-bottom:0.4rem; color:#CBD5E1;'>🔷 {d}</div>",
                        unsafe_allow_html=True,
                    )
                st.markdown("</div>", unsafe_allow_html=True)

        with right:
            topics = notes.get("discussion_topics", [])
            if topics:
                st.markdown(
                    "<div class='section-card'>"
                    "<div class='section-header'>Discussion Topics</div>",
                    unsafe_allow_html=True,
                )
                for t in topics:
                    st.markdown(
                        f"<div style='margin-bottom:0.4rem; color:#CBD5E1;'>💬 {t}</div>",
                        unsafe_allow_html=True,
                    )
                st.markdown("</div>", unsafe_allow_html=True)

            followups = notes.get("follow_up_items", [])
            if followups:
                st.markdown(
                    "<div class='section-card'>"
                    "<div class='section-header'>Follow-up Items</div>",
                    unsafe_allow_html=True,
                )
                for item in followups:
                    st.markdown(
                        f"<div style='margin-bottom:0.4rem; color:#CBD5E1;'>☐ {item}</div>",
                        unsafe_allow_html=True,
                    )
                st.markdown("</div>", unsafe_allow_html=True)

            # Details chip card
            st.markdown(
                f"""
                <div class="section-card">
                    <div class="section-header">Meeting Details</div>
                    <div style="display:grid; grid-template-columns:1fr 1fr; gap:0.8rem; font-size:0.85rem;">
                        <div><span style="color:#475569;">Type</span><br>
                            <strong>{meeting_type_icon(notes.get('meeting_type','Other'))} {notes.get('meeting_type','Other')}</strong>
                        </div>
                        <div><span style="color:#475569;">Sentiment</span><br>
                            <strong>{sentiment_icon(notes.get('sentiment','Neutral'))} {notes.get('sentiment','Neutral')}</strong>
                        </div>
                        <div><span style="color:#475569;">Duration</span><br>
                            <strong>{fmt_duration(meeting.get('duration',0))}</strong>
                        </div>
                        <div><span style="color:#475569;">Words</span><br>
                            <strong>{meeting.get('word_count',0):,}</strong>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Copy summary button
        summary_text = "\n".join(f"• {b}" for b in notes.get("summary", []))
        if st.button("📋  Copy Summary to Clipboard", key="copy_summary"):
            _copy_to_clipboard(summary_text, "Summary copied!")

    # ── TAB 2: TRANSCRIPT ────────────────────────────────────────────────────
    with tab_transcript:
        segments = meeting.get("segments", [])
        formatted = meeting.get("formatted_transcript", meeting.get("transcript", ""))

        meta_col, copy_col = st.columns([5, 1])
        with meta_col:
            st.markdown(
                f"<div style='color:#475569; font-size:0.82rem; margin-bottom:0.8rem;'>"
                f"{len(segments)} segments · {meeting.get('word_count',0):,} words · "
                f"Language: {meeting.get('language','en').upper()}"
                f"</div>",
                unsafe_allow_html=True,
            )
        with copy_col:
            if st.button("📋 Copy", key="copy_transcript"):
                _copy_to_clipboard(formatted, "Transcript copied!")

        if segments:
            lines_html = []
            for seg in segments:
                start_ts = transcriber.format_timestamp(seg.get("start", 0))
                end_ts = transcriber.format_timestamp(seg.get("end", 0))
                text = seg.get("text", "").strip()
                if text:
                    lines_html.append(
                        f"<div class='transcript-segment'>"
                        f"<span class='ts-time'>[{start_ts} → {end_ts}]</span>"
                        f"{text}"
                        f"</div>"
                    )
            st.markdown(
                "<div style='max-height:540px; overflow-y:auto; background:#13132B;"
                "border:1px solid #2D2D5E; border-radius:12px; padding:1rem 1.2rem;'>"
                + "\n".join(lines_html)
                + "</div>",
                unsafe_allow_html=True,
            )
        else:
            st.text_area("Transcript", value=formatted, height=500, disabled=True)

    # ── TAB 3: ACTION ITEMS ──────────────────────────────────────────────────
    with tab_actions:
        action_items = notes.get("action_items", [])

        if not action_items:
            st.markdown(
                """
                <div style="text-align:center; padding:2.5rem; color:#475569;
                            background:#1A1A2E; border-radius:12px; border:1px dashed #2D2D5E;">
                    <div style="font-size:2rem; margin-bottom:0.4rem;">✅</div>
                    <div>No action items were identified in this meeting.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            f_col1, f_col2 = st.columns([2, 3])
            with f_col1:
                filter_priority = st.multiselect(
                    "Filter by Priority",
                    ["High", "Medium", "Low"],
                    default=["High", "Medium", "Low"],
                    key=f"priority_filter_{mid}",
                )
            with f_col2:
                filter_assignee = st.text_input(
                    "Filter by Assignee",
                    placeholder="e.g. Alice",
                    key=f"assignee_filter_{mid}",
                )

            filtered = [
                item for item in action_items
                if isinstance(item, dict)
                and item.get("priority", "Medium") in filter_priority
                and (
                    not filter_assignee
                    or filter_assignee.lower() in item.get("assignee", "").lower()
                )
            ]

            st.markdown(
                f"<div style='color:#475569; font-size:0.82rem; margin:0.5rem 0 1rem;'>"
                f"Showing {len(filtered)} of {len(action_items)} action items"
                f"</div>",
                unsafe_allow_html=True,
            )

            for i, item in enumerate(filtered, 1):
                if not isinstance(item, dict):
                    st.markdown(f"- {item}")
                    continue
                task = item.get("task", "")
                assignee = item.get("assignee", "TBD")
                deadline = item.get("deadline", "Not specified")
                priority = item.get("priority", "Medium")

                st.markdown(
                    f"""
                    <div class="meeting-card" style="padding:1rem 1.2rem;">
                        <div style="display:flex; align-items:flex-start; gap:0.8rem;">
                            <div style="font-size:1.1rem; color:#7C3AED; font-weight:800;
                                        min-width:1.5rem;">{i}.</div>
                            <div style="flex:1;">
                                <div style="font-size:0.95rem; font-weight:600;
                                            color:#E2E8F0; margin-bottom:0.4rem;">{task}</div>
                                <div style="display:flex; gap:1rem; flex-wrap:wrap;
                                            font-size:0.8rem; color:#64748B;">
                                    <span>👤 {assignee}</span>
                                    <span>📅 {deadline}</span>
                                    <span>{priority_badge(priority)}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # ── TAB 4: EXPORT ────────────────────────────────────────────────────────
    with tab_export:
        st.markdown(
            "<div style='color:#94A3B8; margin-bottom:1.5rem;'>"
            "Download your meeting notes in any format. All exports include the full transcript."
            "</div>",
            unsafe_allow_html=True,
        )

        safe_title = meeting.get("title", "meeting").replace(" ", "_").replace("/", "-")[:50]

        e1, e2, e3 = st.columns(3)

        # Markdown
        with e1:
            st.markdown(
                "<div class='section-card' style='text-align:center;'>"
                "<div style='font-size:2rem;'>📝</div>"
                "<div style='font-weight:700; margin:0.4rem 0;'>Markdown</div>"
                "<div style='font-size:0.8rem; color:#64748B; margin-bottom:1rem;'>"
                "Notion, Obsidian, GitHub</div>",
                unsafe_allow_html=True,
            )
            md = exporter.to_markdown(meeting)
            st.download_button(
                "⬇️  Download .md",
                data=md.encode("utf-8"),
                file_name=f"{safe_title}.md",
                mime="text/markdown",
                use_container_width=True,
                key="dl_md",
            )
            if st.button("📋 Copy Markdown", use_container_width=True, key="copy_md"):
                _copy_to_clipboard(md, "Markdown copied!")
            st.markdown("</div>", unsafe_allow_html=True)

        # PDF
        with e2:
            st.markdown(
                "<div class='section-card' style='text-align:center;'>"
                "<div style='font-size:2rem;'>📄</div>"
                "<div style='font-weight:700; margin:0.4rem 0;'>PDF</div>"
                "<div style='font-size:0.8rem; color:#64748B; margin-bottom:1rem;'>"
                "Professional branded report</div>",
                unsafe_allow_html=True,
            )
            try:
                pdf_bytes = exporter.to_pdf(meeting)
                st.download_button(
                    "⬇️  Download .pdf",
                    data=pdf_bytes,
                    file_name=f"{safe_title}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    key="dl_pdf",
                )
            except ImportError:
                st.warning("Install fpdf2: `pip install fpdf2`")
            except Exception as exc:
                st.error(f"PDF error: {exc}")
            st.markdown("</div>", unsafe_allow_html=True)

        # Plain text
        with e3:
            st.markdown(
                "<div class='section-card' style='text-align:center;'>"
                "<div style='font-size:2rem;'>📃</div>"
                "<div style='font-weight:700; margin:0.4rem 0;'>Plain Text</div>"
                "<div style='font-size:0.8rem; color:#64748B; margin-bottom:1rem;'>"
                "Universal, copy-paste friendly</div>",
                unsafe_allow_html=True,
            )
            txt = exporter.to_plain_text(meeting)
            st.download_button(
                "⬇️  Download .txt",
                data=txt.encode("utf-8"),
                file_name=f"{safe_title}.txt",
                mime="text/plain",
                use_container_width=True,
                key="dl_txt",
            )
            if st.button("📋 Copy Text", use_container_width=True, key="copy_txt"):
                _copy_to_clipboard(txt, "Text copied!")
            st.markdown("</div>", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# PAGE: MEETING LIBRARY
# ──────────────────────────────────────────────────────────────────────────────

def page_library() -> None:
    st.markdown(
        "<div class='hero-title' style='font-size:2.2rem'>📚 Meeting Library</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div class='hero-tagline'>All your meetings — search, open, or export.</div>",
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)

    search_col, sort_col, new_col = st.columns([4, 2, 1.5])
    with search_col:
        query = st.text_input(
            "Search",
            value=st.session_state.search_query_lib,
            placeholder="🔍  keyword, topic, action item...",
            key="lib_search",
            label_visibility="collapsed",
        )
        st.session_state.search_query_lib = query

    with sort_col:
        sort_by = st.selectbox(
            "Sort",
            ["Newest first", "Oldest first", "Longest", "Most words"],
            label_visibility="collapsed",
        )

    with new_col:
        if st.button("➕  New Meeting", use_container_width=True):
            navigate("new")

    meetings = storage.search_meetings(query) if query else storage.list_meetings()

    # Sort
    if sort_by == "Oldest first":
        meetings = sorted(meetings, key=lambda m: m.get("created_at", ""))
    elif sort_by == "Longest":
        meetings = sorted(meetings, key=lambda m: m.get("duration", 0), reverse=True)
    elif sort_by == "Most words":
        meetings = sorted(meetings, key=lambda m: m.get("word_count", 0), reverse=True)

    if not meetings:
        msg = f'No meetings found for "{query}"' if query else "Library is empty"
        st.info(msg)
        return

    st.markdown(
        f"<div style='color:#475569; font-size:0.82rem; margin:0.5rem 0 1rem;'>"
        f"{len(meetings)} meeting{'s' if len(meetings)!=1 else ''}"
        f"</div>",
        unsafe_allow_html=True,
    )

    # 2-column grid
    grid = st.columns(2)
    for idx, m in enumerate(meetings):
        col = grid[idx % 2]
        with col:
            mtype = m.get("meeting_type", "Other")
            ac = _action_count_for(m["id"])

            st.markdown(
                f"""
                <div class="meeting-card">
                    <div class="meeting-card-title">
                        {meeting_type_icon(mtype)} {m.get("title", "Untitled")}
                    </div>
                    <div class="meeting-card-meta">
                        <span>📅 {fmt_date(m.get("created_at",""))}</span>
                        <span>⏱ {fmt_duration(m.get("duration",0))}</span>
                        <span>✅ {ac} items</span>
                    </div>
                    <div style="margin-top:0.4rem; font-size:0.8rem; color:#64748B;">
                        {m.get("file_name","—")}
                    </div>
                    <div style="margin-top:0.4rem; font-size:0.8rem; color:#64748B; font-style:italic;">
                        {m.get("summary_preview","")[:120]}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            btn_open, btn_del = st.columns([3, 1])
            with btn_open:
                if st.button("Open", key=f"lib_open_{m['id']}", use_container_width=True):
                    navigate("view", m["id"])
            with btn_del:
                if st.button("🗑", key=f"lib_del_{m['id']}", use_container_width=True):
                    st.session_state[f"lib_confirm_{m['id']}"] = True

            if st.session_state.get(f"lib_confirm_{m['id']}"):
                st.warning(f"Delete **{m.get('title','this meeting')}**?")
                y_col, n_col = st.columns(2)
                with y_col:
                    if st.button("Yes", key=f"lib_yes_{m['id']}"):
                        storage.delete_meeting(m["id"])
                        if f"lib_confirm_{m['id']}" in st.session_state:
                            del st.session_state[f"lib_confirm_{m['id']}"]
                        st.rerun()
                with n_col:
                    if st.button("No", key=f"lib_no_{m['id']}"):
                        del st.session_state[f"lib_confirm_{m['id']}"]
                        st.rerun()

    # Bulk export
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>Bulk Export</div>", unsafe_allow_html=True)

    bulk_col, stats_col = st.columns([2, 5])
    with bulk_col:
        all_json = storage.export_all_meetings_json()
        st.download_button(
            "⬇️  Export All as JSON",
            data=all_json.encode("utf-8"),
            file_name="meetingmind_export.json",
            mime="application/json",
            use_container_width=True,
        )

    stats = storage.get_storage_stats()
    with stats_col:
        st.markdown(
            f"<div style='color:#475569; font-size:0.78rem; padding-top:0.55rem;'>"
            f"📁 {stats['total_meetings']} meetings · 💾 {stats['total_size_mb']} MB · "
            f"<code style='color:#7C3AED;'>{stats['storage_path']}</code>"
            f"</div>",
            unsafe_allow_html=True,
        )


# ──────────────────────────────────────────────────────────────────────────────
# PAGE: SETTINGS
# ──────────────────────────────────────────────────────────────────────────────

def page_settings() -> None:
    st.markdown(
        "<div class='hero-title' style='font-size:2.2rem'>⚙️ Settings</div>",
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)

    left, right = st.columns(2)

    with left:
        # Whisper model
        st.markdown(
            "<div class='section-card'>"
            "<div class='section-header'>Transcription — Whisper Model</div>",
            unsafe_allow_html=True,
        )
        model_options = ["tiny", "base", "small", "medium", "large"]
        model_desc = {
            "tiny":   "~39M params · Fastest · Lower accuracy",
            "base":   "~74M params · Good balance (default)",
            "small":  "~244M params · Better accuracy",
            "medium": "~769M params · High accuracy",
            "large":  "~1.5B params · Best accuracy · Slowest",
        }
        cur_idx = model_options.index(st.session_state.whisper_model) \
            if st.session_state.whisper_model in model_options else 1

        new_wm = st.selectbox(
            "Whisper Model",
            options=model_options,
            index=cur_idx,
            format_func=lambda m: f"{m}  —  {model_desc[m]}",
            label_visibility="collapsed",
        )
        if new_wm != st.session_state.whisper_model:
            st.session_state.whisper_model = new_wm
            st.success(f"Whisper model updated to **{new_wm}**")

        st.markdown(
            "<div style='font-size:0.78rem; color:#475569; margin-top:0.5rem;'>"
            "tiny/base run on CPU. small/medium need 8 GB RAM. large requires GPU or 16+ GB RAM."
            "</div>",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

        # Behaviour
        st.markdown(
            "<div class='section-card'>"
            "<div class='section-header'>Behaviour</div>",
            unsafe_allow_html=True,
        )
        auto_save = st.toggle(
            "Auto-save meetings after processing",
            value=st.session_state.auto_save,
        )
        st.session_state.auto_save = auto_save
        st.markdown(
            f"<div style='font-size:0.8rem; color:#64748B; margin-top:0.3rem;'>"
            f"Auto-save is <strong>{'on' if auto_save else 'off'}</strong>. "
            "When off you can edit the title before saving."
            "</div>",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        # Ollama
        st.markdown(
            "<div class='section-card'>"
            "<div class='section-header'>AI Summarisation — Ollama</div>",
            unsafe_allow_html=True,
        )
        new_ollama = st.text_input(
            "Model name",
            value=st.session_state.ollama_model,
            help="Must be pulled via `ollama pull <model>`. e.g. llama3.2, mistral, phi3, gemma2",
        )
        if st.button("Apply", key="apply_ollama"):
            st.session_state.ollama_model = new_ollama.strip()
            st.success(f"Ollama model set to **{new_ollama.strip()}**")

        st.markdown("<br>", unsafe_allow_html=True)
        ok, msg = check_ollama_status()
        if ok:
            st.markdown(f"<div class='ollama-ok'>🟢 {msg}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='ollama-err'>🔴 {msg}</div>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("**Quick start:**")
            st.code(
                "# 1. Start Ollama\nollama serve\n\n"
                "# 2. Pull the model\nollama pull llama3.2",
                language="bash",
            )
        st.markdown("</div>", unsafe_allow_html=True)

        # Storage info
        st.markdown(
            "<div class='section-card'>"
            "<div class='section-header'>Storage</div>",
            unsafe_allow_html=True,
        )
        stats = storage.get_storage_stats()
        st.markdown(
            f"""
            <div style="font-size:0.88rem; line-height:2.2;">
                <div>📁 <code style="color:#A78BFA;">{stats['storage_path']}</code></div>
                <div>📊 <strong>{stats['total_meetings']}</strong> meetings stored</div>
                <div>💾 <strong>{stats['total_size_mb']} MB</strong> used on disk</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    # About footer
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="background:#13132B; border:1px solid #2D2D5E; border-radius:14px;
                    padding:1.6rem 2rem; text-align:center;">
            <div style="font-size:1.5rem; font-weight:900; margin-bottom:0.35rem;
                        background:linear-gradient(135deg,#7C3AED,#EC4899);
                        -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                        background-clip:text;">
                🧠 MeetingMind
            </div>
            <div style="color:#475569; font-size:0.85rem; line-height:1.9;">
                Transcription by <strong style="color:#A78BFA;">OpenAI Whisper</strong>
                &nbsp;·&nbsp;
                AI analysis by <strong style="color:#A78BFA;">Ollama</strong> (100% local)
                &nbsp;·&nbsp;
                UI by <strong style="color:#A78BFA;">Streamlit</strong>
                <br>All data stays on your machine. No cloud. No subscriptions.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ──────────────────────────────────────────────────────────────────────────────
# MAIN ROUTER
# ──────────────────────────────────────────────────────────────────────────────

def main() -> None:
    render_sidebar()

    page = st.session_state.page

    if page == "home":
        page_home()
    elif page == "new":
        page_new_meeting()
    elif page == "view":
        page_view_meeting()
    elif page == "library":
        page_library()
    elif page == "settings":
        page_settings()
    else:
        st.error(f"Unknown page: '{page}'")
        navigate("home")


if __name__ == "__main__":
    main()
