# MeetingMind — Edge-Native AI Meeting Intelligence Platform

**13 Industries. 45+ Templates. 50+ Jurisdictions. 37+ Languages.**
**100% on-device processing. Zero cloud. Zero data leakage.**

MeetingMind is a privacy-first AI meeting assistant that transcribes, analyzes, and generates structured notes — all on your local machine. Built for regulated industries where data cannot leave the device.

---

## Why MeetingMind?

Every competitor (Otter.ai, Gong, Fireflies) sends your voice data to the cloud. MeetingMind doesn't.

- **HIPAA-ready** — Patient data never leaves the clinic's device
- **Privilege-preserving** — Attorney-client communications stay on the lawyer's machine
- **SEC-compliant** — Financial meeting records with local audit trail
- **FERPA-safe** — Student data processed entirely on-device
- **BIPA-immune** — No biometric data (voiceprints) ever transmitted
- **GDPR by design** — Data minimization is the architecture, not a feature

---

## Industry Verticals

| Tier | Industry | Templates |
|------|----------|-----------|
| **Tier 1** | Healthcare | SOAP Notes, H&P, Progress Notes, Discharge Summary |
| **Tier 1** | Legal | Client Intake, Deposition Summary, Case Brief, Contract Review |
| **Tier 1** | Financial | Client Meeting, Trade Rationale, Compliance Log, KYC Record |
| **Tier 2** | Veterinary | SOAP Notes, Treatment Plan, Client Communication |
| **Tier 2** | HR & Recruiting | Interview Scorecard, Performance Review, Exit Interview |
| **Tier 2** | Education | IEP Meeting Notes, Parent-Teacher Conference, Faculty Minutes |
| **Tier 2** | Sales & Consulting | Call Summary, Discovery Notes, QBR Notes |
| **Tier 2** | Construction | Site Minutes, Safety Briefing, Change Order, Daily Log |
| **Tier 3** | Government | Council Minutes, Police Interview, Social Worker Notes |
| **Tier 3** | Religious & Nonprofit | Board Minutes, Pastoral Notes, Donor Meeting |
| **Tier 3** | Insurance | Claims Meeting, Underwriting Review, Policy Review |
| **Tier 3** | Real Estate | Property Showing, Closing Meeting, Inspection Review |
| **Universal** | General | Standard meeting notes for any context |

---

## Quick Start

### 1. Setup

```bash
cd ~/ai-meeting-notes
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. AI Engine

```bash
# Install Ollama (macOS)
brew install ollama

# Start server and pull model
ollama serve &
ollama pull llama3.2
```

### 3. Run

```bash
python3 -m streamlit run app.py
```

Opens at `http://localhost:8501`

---

## Features

### Core
- **Live audio recording** via browser microphone
- **File upload** — MP3, WAV, M4A, MP4, MOV, WebM, MKV, AVI, OGG, FLAC
- **Whisper transcription** — 5 model sizes (tiny → large)
- **AI-powered notes** — summaries, action items, decisions, follow-ups
- **37+ languages** with auto-detection
- **Multi-speaker detection** — pause-based speaker labeling

### Verticals
- **13 industry verticals** with **45+ specialized templates**
- **Industry-specific AI prompts** — SOAP notes, case briefs, IEP templates, etc.
- **Compliance badges** — HIPAA, FERPA, SEC, attorney-client privilege, etc.
- **Vertical-aware exports** — formatted for each industry

### Compliance Center
- **50+ jurisdictions** — US (all 50 states), Canada, EU/GDPR, UK, Brazil, Japan, Korea, India, China, Singapore, Australia, UAE, Saudi Arabia
- **Recording consent engine** — auto-detects jurisdiction, generates consent scripts
- **10 compliance frameworks** — HIPAA, attorney-client privilege, FERPA, SEC 17a-4, FINRA 3110, BIPA, GDPR, COPPA, CJIS, FedRAMP
- **Audit logging** — every action logged to `~/.meetingmind/audit/`

### Analytics Dashboard
- Meeting trends, sentiment tracking, productivity scoring
- Action item stats by priority and assignee
- Language distribution, peak hours, word cloud
- Duration histograms and vertical distribution

### Export
- **PDF** — branded, professional with purple theme
- **Markdown** — formatted notes with metadata
- **Plain Text** — universal format
- **JSON** — structured data for integrations

---

## Architecture

```
ai-meeting-notes/
├── app.py                      Multi-page SaaS platform UI
├── core/
│   ├── transcriber.py          Whisper transcription + audio extraction
│   ├── summarizer.py           AI notes (generic + vertical-specific)
│   ├── templates.py            13 verticals × 45+ industry templates
│   ├── compliance.py           50+ jurisdictions, 10 frameworks, audit log
│   ├── analytics.py            Meeting analytics + insights engine
│   ├── languages.py            37+ language support
│   ├── storage.py              Local JSON storage (~/.meetingmind/)
│   └── exporter.py             PDF, Markdown, text, JSON export
├── .streamlit/
│   └── config.toml             Dark theme
├── MARKET_INTELLIGENCE_REPORT.md
├── requirements.txt
└── README.md
```

---

## Privacy Architecture

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│  Microphone  │────▶│   Whisper    │────▶│   Ollama     │
│  or File     │     │  (on-device) │     │  (on-device) │
└─────────────┘     └──────────────┘     └──────────────┘
                           │                      │
                           ▼                      ▼
                    ┌──────────────┐     ┌──────────────┐
                    │  Transcript  │     │  AI Notes    │
                    │  (local)     │     │  (local)     │
                    └──────────────┘     └──────────────┘
                                  │
                                  ▼
                           ┌──────────────┐
                           │ ~/.meetingmind│
                           │  (your disk)  │
                           └──────────────┘

              ☁️ ZERO CLOUD CONTACT ☁️
```

All data stays in `~/.meetingmind/` on your local disk. No audio, transcript, or notes data ever leaves your machine.

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| UI Framework | Streamlit |
| Speech-to-Text | OpenAI Whisper (on-device) |
| LLM | Ollama / llama3.2 (on-device) |
| PDF Export | fpdf2 |
| Storage | Python stdlib (JSON, pathlib) |
| Audio Processing | ffmpeg, imageio-ffmpeg |

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Whisper not found | `pip install openai-whisper` |
| Ollama connection error | `ollama serve` then `ollama pull llama3.2` |
| ffmpeg not found | `brew install ffmpeg` |
| PDF export fails | `pip install fpdf2` |
| Slow transcription | Use smaller Whisper model (tiny/base) |
| Port in use | `lsof -ti:8501 \| xargs kill -9` |

---

*Built with Streamlit, OpenAI Whisper, and Ollama.*
