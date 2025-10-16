#!/usr/bin/env bash
set -euo pipefail
export PYTHONUNBUFFERED=1
export PORT=${PORT:-8000}
PY=${PYTHON_BIN:-python3}
# Install deps if missing (idempotent)
if ! $PY -c "import fastapi" >/dev/null 2>&1; then
  $PY -m pip install -r requirements.txt
fi
exec $PY -m uvicorn app.main:app --host 0.0.0.0 --port "$PORT" --reload
