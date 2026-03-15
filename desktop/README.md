# MeetingMind — Desktop App

Electron wrapper that bundles the Streamlit-based MeetingMind backend into a
native desktop application for macOS, Windows, and Linux.

## Quick Start

```bash
cd desktop
npm install
npm start          # Launch in development mode
```

## Building distributable packages

```bash
npm run build-mac    # macOS → dist/MeetingMind-2.0.0.dmg + .zip
npm run build-win    # Windows → dist/MeetingMind Setup 2.0.0.exe
npm run build-linux  # Linux → dist/MeetingMind-2.0.0.AppImage + .deb
```

Built artefacts land in `desktop/dist/`.

## Prerequisites

| Requirement | Notes |
|---|---|
| Node.js ≥ 18 | https://nodejs.org |
| Python 3.10+ | Or a `.venv` at the repo root |
| Streamlit + deps | `pip install -r ../requirements.txt` |

## How it works

1. Electron starts and immediately shows `splash.html`.
2. The main process spawns `python3 -m streamlit run app.py` in the repo root.
3. It polls `http://localhost:8501` every 500 ms until Streamlit responds.
4. The splash is replaced by a `BrowserWindow` pointing at `localhost:8501`.
5. On window close the Streamlit process is terminated cleanly.

## Python detection order

1. `.venv/bin/python3` (repo root virtual environment)
2. `.venv/bin/python`
3. `python3` (system PATH)
4. `python` (system PATH)

## Troubleshooting

**"Python Not Found" dialog** — Install Python 3 or run `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt` from the repo root.

**Startup timeout** — Make sure all dependencies are installed: `pip install -r ../requirements.txt`.

**Port conflict** — If port 8501 is already in use, quit any running Streamlit instances first.
