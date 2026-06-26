#!/usr/bin/env bash
# Daily autopilot entrypoint — wire this into cron (see docs/SETUP.md §6).
# Runs every channel in config/channels.yaml, posts_per_day videos each.
set -euo pipefail
cd "$(dirname "$0")/.."

# shellcheck disable=SC1091
[ -d .venv ] && source .venv/bin/activate

echo "=== Video Autopilot daily run: $(date) ==="
python -m src.orchestrator --all
echo "=== done: $(date) ==="
