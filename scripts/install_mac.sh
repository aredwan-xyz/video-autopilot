#!/usr/bin/env bash
# One-shot installer for macOS. Installs ffmpeg + a python venv + deps.
# Works WITH or WITHOUT Homebrew (falls back to a static ffmpeg download).
set -euo pipefail
cd "$(dirname "$0")/.."

echo "▶ Creating python venv (.venv)..."
python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
pip install --upgrade pip >/dev/null
pip install -r requirements.txt

echo "▶ Ensuring ffmpeg + ffprobe..."
if command -v ffmpeg >/dev/null 2>&1 && command -v ffprobe >/dev/null 2>&1; then
  echo "  ffmpeg already on PATH — skipping."
elif command -v brew >/dev/null 2>&1; then
  brew list ffmpeg >/dev/null 2>&1 || brew install ffmpeg
else
  # No Homebrew: drop static binaries into the venv (no admin needed).
  echo "  Homebrew not found — downloading static ffmpeg into .venv/bin..."
  ARCH="$(uname -m)"   # arm64 (Apple Silicon) or x86_64 (Intel)
  [ "$ARCH" = "x86_64" ] && ARCH="amd64"
  BASE="https://ffmpeg.martin-riedl.de/redirect/latest/macos/${ARCH}/release"
  for tool in ffmpeg ffprobe; do
    curl -fsSL -o "/tmp/${tool}.zip" "${BASE}/${tool}.zip" \
      && unzip -o -q "/tmp/${tool}.zip" -d .venv/bin \
      && chmod +x ".venv/bin/${tool}" \
      && xattr -d com.apple.quarantine ".venv/bin/${tool}" 2>/dev/null || true
  done
  if .venv/bin/ffmpeg -version >/dev/null 2>&1; then
    echo "  ✓ static ffmpeg installed in .venv/bin"
  else
    echo "  ✗ ffmpeg install failed — install Homebrew (https://brew.sh) then 'brew install ffmpeg'" >&2
  fi
fi

echo "▶ Fetching a default caption font (Montserrat ExtraBold)..."
FONT="assets/fonts/Montserrat-ExtraBold.ttf"
if [ ! -f "$FONT" ]; then
  curl -fsSL -o "$FONT" \
    "https://github.com/google/fonts/raw/main/ofl/montserrat/Montserrat%5Bwght%5D.ttf" \
    || echo "  (font download failed — drop any .ttf at $FONT)"
fi

cat <<'EOF'

✓ Install complete.

Next:
  1. cp .env.example .env   # add your API keys
  2. Add 1–2 royalty-free tracks to assets/music/ (optional but recommended)
  3. source .venv/bin/activate
  4. bash scripts/serve.sh   # open the dashboard at http://127.0.0.1:8000
     (or CLI: python -m src.orchestrator --channel motivation --count 1 --dry-run)
EOF
