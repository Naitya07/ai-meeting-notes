#!/usr/bin/env bash
# =============================================================================
#  MeetingMind — One-Click Installer for macOS
#  Installs all prerequisites, sets up the environment, and creates launchers.
# =============================================================================

set -euo pipefail

# ─── Colour palette ──────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

ok()   { echo -e "${GREEN}  ✓  ${1}${RESET}"; }
info() { echo -e "${CYAN}  →  ${1}${RESET}"; }
warn() { echo -e "${YELLOW}  ⚠  ${1}${RESET}"; }
die()  { echo -e "${RED}  ✗  ${1}${RESET}" >&2; exit 1; }
step() { echo -e "\n${BOLD}${CYAN}╌╌╌  ${1}  ╌╌╌${RESET}"; }

# ─── Banner ──────────────────────────────────────────────────────────────────
print_banner() {
  echo -e "${CYAN}"
  cat << 'EOF'
  ╔══════════════════════════════════════════════════════════════╗
  ║                                                              ║
  ║    ███╗   ███╗███████╗███████╗████████╗██╗███╗   ██╗ ██████╗ ║
  ║    ████╗ ████║██╔════╝██╔════╝╚══██╔══╝██║████╗  ██║██╔════╝ ║
  ║    ██╔████╔██║█████╗  █████╗     ██║   ██║██╔██╗ ██║██║  ███╗║
  ║    ██║╚██╔╝██║██╔══╝  ██╔══╝     ██║   ██║██║╚██╗██║██║   ██║║
  ║    ██║ ╚═╝ ██║███████╗███████╗   ██║   ██║██║ ╚████║╚██████╔╝║
  ║    ╚═╝     ╚═╝╚══════╝╚══════╝   ╚═╝   ╚═╝╚═╝  ╚═══╝ ╚═════╝ ║
  ║                                                              ║
  ║           ███╗   ███╗██╗███╗   ██╗██████╗                   ║
  ║           ████╗ ████║██║████╗  ██║██╔══██╗                  ║
  ║           ██╔████╔██║██║██╔██╗ ██║██║  ██║                  ║
  ║           ██║╚██╔╝██║██║██║╚██╗██║██║  ██║                  ║
  ║           ██║ ╚═╝ ██║██║██║ ╚████║██████╔╝                  ║
  ║           ╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═════╝                   ║
  ║                                                              ║
  ║         AI-Powered Meeting Notes  •  Local & Private         ║
  ╚══════════════════════════════════════════════════════════════╝
EOF
  echo -e "${RESET}"
  echo -e "  ${BOLD}MeetingMind Installer${RESET}  —  macOS One-Click Setup"
  echo -e "  $(date '+%Y-%m-%d %H:%M:%S')\n"
}

# ─── Sanity check: must run on macOS ─────────────────────────────────────────
check_macos() {
  step "Platform check"
  if [[ "$(uname -s)" != "Darwin" ]]; then
    die "This installer is for macOS only. Detected: $(uname -s)"
  fi
  ok "Running on macOS $(sw_vers -productVersion)"
}

# ─── Resolve the project directory ───────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"

# ─── 1. Homebrew ─────────────────────────────────────────────────────────────
check_brew() {
  step "Homebrew"
  if command -v brew &>/dev/null; then
    ok "Homebrew already installed ($(brew --version | head -1))"
  else
    warn "Homebrew not found — installing now…"
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" \
      || die "Homebrew installation failed. Visit https://brew.sh and install manually."

    # Add brew to PATH for Apple Silicon or Intel
    if [[ -f /opt/homebrew/bin/brew ]]; then
      eval "$(/opt/homebrew/bin/brew shellenv)"
    elif [[ -f /usr/local/bin/brew ]]; then
      eval "$(/usr/local/bin/brew shellenv)"
    fi
    ok "Homebrew installed successfully"
  fi
}

# ─── 2. Python 3.9+ ──────────────────────────────────────────────────────────
check_python() {
  step "Python 3.9+"

  PYTHON_BIN=""
  for candidate in python3 python3.13 python3.12 python3.11 python3.10 python3.9; do
    if command -v "$candidate" &>/dev/null; then
      ver="$("$candidate" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
      major="${ver%%.*}"
      minor="${ver##*.}"
      if [[ "$major" -ge 3 && "$minor" -ge 9 ]]; then
        PYTHON_BIN="$candidate"
        ok "Found $candidate (v$ver)"
        break
      fi
    fi
  done

  if [[ -z "$PYTHON_BIN" ]]; then
    warn "Python 3.9+ not found — installing via Homebrew…"
    brew install python3 || die "Failed to install Python 3. Run: brew install python3"
    PYTHON_BIN="python3"
    ok "Python 3 installed via Homebrew"
  fi

  export PYTHON_BIN
}

# ─── 3. ffmpeg ───────────────────────────────────────────────────────────────
check_ffmpeg() {
  step "ffmpeg"

  if [[ -x "$HOME/bin/ffmpeg" ]]; then
    ok "ffmpeg found at ~/bin/ffmpeg"
    return
  fi

  if command -v ffmpeg &>/dev/null; then
    ok "ffmpeg found at $(command -v ffmpeg)"
    return
  fi

  warn "ffmpeg not found — installing via Homebrew…"
  brew install ffmpeg || die "Failed to install ffmpeg. Run: brew install ffmpeg"
  ok "ffmpeg installed"
}

# ─── 4. Ollama ───────────────────────────────────────────────────────────────
check_ollama() {
  step "Ollama"

  if command -v ollama &>/dev/null; then
    ok "Ollama already installed ($(ollama --version 2>/dev/null || echo 'version unknown'))"
    return
  fi

  warn "Ollama not found — installing via Homebrew…"
  brew install ollama || die "Failed to install Ollama. Visit https://ollama.com/download and install manually."
  ok "Ollama installed"
}

# ─── 5. Python virtual environment ───────────────────────────────────────────
setup_venv() {
  step "Python virtual environment"

  VENV_DIR="$PROJECT_DIR/.venv"

  if [[ -d "$VENV_DIR" && -f "$VENV_DIR/bin/activate" ]]; then
    ok "Virtual environment already exists at .venv"
  else
    info "Creating virtual environment in .venv …"
    "$PYTHON_BIN" -m venv "$VENV_DIR" \
      || die "Failed to create virtual environment."
    ok "Virtual environment created"
  fi

  # Activate for the remainder of this script
  # shellcheck source=/dev/null
  source "$VENV_DIR/bin/activate"
  ok "Virtual environment activated"

  export VENV_DIR
}

# ─── 6. Install Python dependencies ──────────────────────────────────────────
install_requirements() {
  step "Python dependencies"

  REQ_FILE="$PROJECT_DIR/requirements.txt"

  if [[ ! -f "$REQ_FILE" ]]; then
    die "requirements.txt not found at $REQ_FILE"
  fi

  info "Upgrading pip …"
  pip install --upgrade pip --quiet

  info "Installing packages from requirements.txt …"
  pip install -r "$REQ_FILE" \
    || die "pip install failed. Check requirements.txt for errors."

  ok "All Python dependencies installed"
}

# ─── 7. Pull llama3.2 model ──────────────────────────────────────────────────
pull_model() {
  step "Ollama — llama3.2 model"

  MODEL="llama3.2"

  # Start Ollama server temporarily if needed so we can pull
  start_ollama_if_needed

  if ollama list 2>/dev/null | grep -q "^${MODEL}"; then
    ok "Model '${MODEL}' is already present"
    return
  fi

  info "Pulling '${MODEL}' from Ollama registry — this may take a few minutes…"
  ollama pull "$MODEL" \
    || die "Failed to pull model '${MODEL}'. Ensure you have a working internet connection."
  ok "Model '${MODEL}' downloaded"
}

# ─── Helper: start Ollama server if not already running ──────────────────────
start_ollama_if_needed() {
  if pgrep -x "ollama" &>/dev/null; then
    return
  fi

  info "Starting Ollama server in background…"
  nohup ollama serve &>/tmp/ollama_serve.log &
  OLLAMA_PID=$!
  disown "$OLLAMA_PID" 2>/dev/null || true

  # Give it a moment to bind
  local retries=10
  while [[ $retries -gt 0 ]]; do
    if curl -s http://localhost:11434/api/tags &>/dev/null; then
      ok "Ollama server is running (PID $OLLAMA_PID)"
      return
    fi
    sleep 1
    (( retries-- ))
  done
  warn "Ollama server may still be starting. If issues arise, run: ollama serve"
}

# ─── 8. Create MeetingMind.command launcher ───────────────────────────────────
create_command_launcher() {
  step "MeetingMind.command launcher"

  LAUNCHER="$PROJECT_DIR/MeetingMind.command"

  cat > "$LAUNCHER" << LAUNCHER_EOF
#!/usr/bin/env bash
# MeetingMind — Double-click launcher
# Auto-generated by install.sh

SCRIPT_DIR="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")" && pwd)"

# Activate virtual environment
if [[ -f "\$SCRIPT_DIR/.venv/bin/activate" ]]; then
  source "\$SCRIPT_DIR/.venv/bin/activate"
else
  echo "ERROR: Virtual environment not found. Please run install.sh first."
  exit 1
fi

# Add ~/bin to PATH (for local ffmpeg, etc.)
export PATH="\$HOME/bin:\$PATH"

# Start Ollama if not running
if ! pgrep -x "ollama" &>/dev/null; then
  echo "Starting Ollama server…"
  nohup ollama serve &>/tmp/ollama_serve.log &
  sleep 2
fi

echo ""
echo "  Starting MeetingMind…"
echo "  Opening http://localhost:8501 in your browser"
echo ""

# Open browser after a short delay
(sleep 3 && open "http://localhost:8501") &

# Run Streamlit
cd "\$SCRIPT_DIR"
exec python3 -m streamlit run app.py --server.headless true
LAUNCHER_EOF

  chmod +x "$LAUNCHER"
  ok "Created MeetingMind.command (double-click to launch)"
}

# ─── 9. Create macOS .app bundle ─────────────────────────────────────────────
create_app_bundle() {
  step "macOS app bundle"

  APP_PATH="$HOME/Desktop/MeetingMind.app"
  MACOS_DIR="$APP_PATH/Contents/MacOS"
  RESOURCES_DIR="$APP_PATH/Contents/Resources"

  info "Creating app bundle at ~/Desktop/MeetingMind.app …"

  mkdir -p "$MACOS_DIR"
  mkdir -p "$RESOURCES_DIR"

  # ── Info.plist ────────────────────────────────────────────────────────────
  cat > "$APP_PATH/Contents/Info.plist" << PLIST_EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleName</key>
  <string>MeetingMind</string>
  <key>CFBundleDisplayName</key>
  <string>MeetingMind</string>
  <key>CFBundleIdentifier</key>
  <string>com.meetingmind.app</string>
  <key>CFBundleVersion</key>
  <string>1.0.0</string>
  <key>CFBundleShortVersionString</key>
  <string>1.0.0</string>
  <key>CFBundlePackageType</key>
  <string>APPL</string>
  <key>CFBundleSignature</key>
  <string>????</string>
  <key>CFBundleExecutable</key>
  <string>MeetingMind</string>
  <key>LSMinimumSystemVersion</key>
  <string>11.0</string>
  <key>NSHighResolutionCapable</key>
  <true/>
  <key>LSUIElement</key>
  <false/>
  <key>NSHumanReadableCopyright</key>
  <string>MeetingMind — AI Meeting Notes</string>
</dict>
</plist>
PLIST_EOF

  # ── Shell launcher inside Contents/MacOS/ ────────────────────────────────
  cat > "$MACOS_DIR/MeetingMind" << EXEC_EOF
#!/usr/bin/env bash
# MeetingMind.app — macOS app bundle launcher
# Auto-generated by install.sh

PROJECT_DIR="${PROJECT_DIR}"

# Activate virtual environment
if [[ -f "\$PROJECT_DIR/.venv/bin/activate" ]]; then
  source "\$PROJECT_DIR/.venv/bin/activate"
else
  osascript -e 'display alert "MeetingMind" message "Virtual environment not found.\nPlease run install.sh first." as critical'
  exit 1
fi

export PATH="\$HOME/bin:\$PATH"

# Start Ollama if not running
if ! pgrep -x "ollama" &>/dev/null; then
  nohup ollama serve &>/tmp/ollama_serve.log &
  sleep 2
fi

# Open browser after delay
(sleep 3 && open "http://localhost:8501") &

cd "\$PROJECT_DIR"
exec python3 -m streamlit run app.py --server.headless true
EXEC_EOF

  chmod +x "$MACOS_DIR/MeetingMind"

  ok "App bundle created at ~/Desktop/MeetingMind.app"

  # Attempt to remove quarantine attribute so it opens without Gatekeeper warning
  if command -v xattr &>/dev/null; then
    xattr -cr "$APP_PATH" 2>/dev/null || true
  fi
}

# ─── 10. Success summary ──────────────────────────────────────────────────────
print_success() {
  echo ""
  echo -e "${GREEN}${BOLD}"
  cat << 'EOF'
  ╔══════════════════════════════════════════════════════════════╗
  ║            Installation Complete — You're all set!          ║
  ╚══════════════════════════════════════════════════════════════╝
EOF
  echo -e "${RESET}"

  echo -e "  ${BOLD}How to launch MeetingMind:${RESET}\n"
  echo -e "  ${GREEN}Option 1${RESET} — Double-click ${BOLD}MeetingMind.app${RESET} on your Desktop"
  echo -e "  ${GREEN}Option 2${RESET} — Double-click ${BOLD}MeetingMind.command${RESET} in this folder"
  echo -e "  ${GREEN}Option 3${RESET} — Terminal:"
  echo -e "           ${CYAN}cd ${PROJECT_DIR}${RESET}"
  echo -e "           ${CYAN}source .venv/bin/activate${RESET}"
  echo -e "           ${CYAN}streamlit run app.py${RESET}\n"

  echo -e "  ${BOLD}Ollama model:${RESET}  llama3.2 (local, private — no data leaves your Mac)"
  echo -e "  ${BOLD}Web UI:${RESET}        http://localhost:8501\n"

  echo -e "  ${YELLOW}Tip:${RESET} To re-run setup safely at any time, just run ./install.sh again.\n"
}

# ─── Main ────────────────────────────────────────────────────────────────────
main() {
  print_banner
  check_macos
  check_brew
  check_python
  check_ffmpeg
  check_ollama
  setup_venv
  install_requirements
  pull_model
  start_ollama_if_needed
  create_command_launcher
  create_app_bundle
  print_success
}

main "$@"
