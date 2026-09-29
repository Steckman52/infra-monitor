#!/usr/bin/env bash
# Start the whole tool with one command: builds the frontend if needed,
# then serves it and the API from a single backend process on port 8000.
set -euo pipefail
cd "$(dirname "$0")"
PORT="${INFRA_MONITOR_PORT:-8000}"

if [ ! -d backend/.venv ]; then
    echo "Creating the Python environment..."
    python3 -m venv backend/.venv
    backend/.venv/bin/python -m pip install --quiet -r backend/requirements.txt
fi

if [ ! -d frontend/dist ]; then
    echo "Building the frontend..."
    (cd frontend && { [ -d node_modules ] || npm install; } && npm run build)
fi

echo
echo "Infrastructure Monitor is starting on http://localhost:$PORT"
echo "Press Ctrl+C to stop."
echo
cd backend
exec .venv/bin/python -m uvicorn src.main:app --port "$PORT"
