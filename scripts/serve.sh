#!/usr/bin/env bash
# Launch the web dashboard at http://127.0.0.1:8000
set -euo pipefail
cd "$(dirname "$0")/.."
# shellcheck disable=SC1091
[ -d .venv ] && source .venv/bin/activate
exec uvicorn webapp.server:app --host 127.0.0.1 --port "${PORT:-8000}" --reload
