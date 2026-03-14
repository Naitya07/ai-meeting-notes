# MeetingMind

**AI-powered meeting notes from audio/video recordings.**

Upload a meeting recording → Whisper transcribes it → AI generates structured notes with summaries, action items, decisions, and follow-ups.

---

## Features

- Upload MP4, MP3, WAV, M4A, MOV, or WEBM recordings
- Local Whisper transcription (no API keys, runs on your machine)
- Speaker labeling (manual hints after transcription)
- AI-generated structured notes via Ollama (llama3.2)
  - Meeting Summary (3–5 bullets)
  - Key Decisions Made
  - Action Items with assignee, deadline, priority
  - Discussion Topics
  - Follow-up Items
- Export: PDF, Markdown, plain text
- Persistent meeting history at `~/.meetingmind/`
- Full-text search across all past transcripts

---

## Setup

### 1. Create and activate a virtual environment

```bash
cd ~/ai-meeting-notes
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

> **Note:** `torch` may take a few minutes to download. If you're on Apple Silicon:
> ```bash
> pip install torch torchvision torchaudio
> ```

### 3. Install Ollama and pull the model

```bash
# Install Ollama (macOS)
brew install ollama
# or download from https://ollama.com

# Start the server
ollama serve &

# Pull the llama3.2 model (~2GB)
ollama pull llama3.2
```

### 4. Ensure ffmpeg is available

```bash
# Check if ~/bin/ffmpeg exists (already set up on this machine)
ls ~/bin/ffmpeg

# If not, install via Homebrew:
brew install ffmpeg
```

### 5. Run MeetingMind

```bash
cd ~/ai-meeting-notes
source .venv/bin/activate
streamlit run app.py
```

The app will open at `http://localhost:8501`

---

## File Structure

```
ai-meeting-notes/
├── app.py                 # Main Streamlit application
├── core/
│   ├── __init__.py
│   ├── transcriber.py     # Whisper transcription + speaker labeling
│   ├── summarizer.py      # AI notes generation via Ollama
│   ├── exporter.py        # PDF, Markdown, plain text export
│   └── storage.py         # Meeting history (save/load/search)
├── .streamlit/
│   └── config.toml        # Dark theme configuration
├── requirements.txt
├── .gitignore
└── README.md
```

Meeting data is stored at: `~/.meetingmind/`

---

## Usage

1. Click **New Meeting** in the sidebar
2. Upload your recording (MP4/MP3/WAV/etc.)
3. Set the meeting title and approximate speaker count
4. Click **Start Transcription** — Whisper processes the audio locally
5. Optionally name the speakers (Speaker 1 → "Alice", etc.)
6. Click **Continue** — AI generates structured notes
7. Browse the tabs: Summary, Action Items, Decisions, Discussion, Transcript
8. Export as PDF, Markdown, or plain text
9. All meetings are saved automatically and searchable from the sidebar

---

## Customization

| Setting | Location |
|---------|----------|
| Ollama model | `core/summarizer.py` → `DEFAULT_MODEL` |
| Whisper model size | `app.py` → `render_transcribing_step()` |
| Max transcript length sent to AI | `core/summarizer.py` → `MAX_TRANSCRIPT_CHARS` |
| Storage location | `core/storage.py` → `STORAGE_DIR` |
| Theme colors | `.streamlit/config.toml` + CSS in `app.py` |

### Whisper model sizes

| Model | Size | Speed | Quality |
|-------|------|-------|---------|
| tiny  | 75 MB | Fastest | Basic |
| base  | 145 MB | Fast | Good |
| small | 465 MB | Medium | Better |
| medium | 1.5 GB | Slow | Great |
| large | 2.9 GB | Slowest | Best |

---

## Troubleshooting

**Whisper not found:**
```bash
pip install openai-whisper
```

**Ollama connection error:**
```bash
ollama serve
# In another terminal:
ollama pull llama3.2
```

**ffmpeg not found:**
```bash
# Copy system ffmpeg to ~/bin or install:
brew install ffmpeg
cp $(which ffmpeg) ~/bin/ffmpeg
```

**PDF export fails:**
```bash
pip install fpdf2
```

**Transcription is slow:**
- Use a smaller Whisper model: change `"base"` to `"tiny"` in `app.py`
- For GPU acceleration, ensure PyTorch with CUDA/MPS is installed

---

## Privacy

All processing is 100% local:
- Whisper runs on your machine (no audio sent to any server)
- Ollama runs on your machine (no text sent to any server)
- Meetings are stored in `~/.meetingmind/` on your local disk

---

*Built with Streamlit, OpenAI Whisper, and Ollama.*
