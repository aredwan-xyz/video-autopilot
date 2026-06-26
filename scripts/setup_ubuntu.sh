#!/usr/bin/env bash
# One-shot installer for a fresh Ubuntu/Debian cloud server (VPS).
# Installs ffmpeg + python venv + deps. Run once after cloning the repo.
#
#   bash scripts/setup_ubuntu.sh
#
set -euo pipefail
cd "$(dirname "$0")/.."

echo "▶ Installing system packages (ffmpeg, python venv)..."
sudo apt-get update -y
sudo apt-get install -y ffmpeg python3 python3-venv python3-pip fonts-dejavu-core unzip curl

echo "▶ Creating python venv (.venv)..."
python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
pip install --upgrade pip >/dev/null
pip install -r requirements.txt

echo "▶ Fetching a default caption font (Montserrat ExtraBold)..."
FONT="assets/fonts/Montserrat-ExtraBold.ttf"
mkdir -p assets/fonts assets/music
if [ ! -f "$FONT" ]; then
  curl -fsSL -o "$FONT" \
    "https://github.com/google/fonts/raw/main/ofl/montserrat/Montserrat%5Bwght%5D.ttf" \
    || echo "  (font download failed — drop any .ttf at $FONT)"
fi

cat <<'EOF'

✓ Server install complete.

Next:
  1. cp .env.example .env && nano .env       # add your API keys
  2. nano config/settings.yaml               # set llm.provider + publish.provider
  3. Test:  source .venv/bin/activate && python -m src.orchestrator --channel motivation --count 1 --dry-run
  4. Schedule the daily run with cron:        crontab -e
     0 9 * * * BASH_ENV=/dev/null /full/path/to/scripts/run_daily.sh >> output/cron.log 2>&1
  5. (optional) Run the dashboard:            bash scripts/serve.sh   (see docs/DEPLOY.md to expose it safely)
EOF
