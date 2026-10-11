#!/usr/bin/env bash
# Open-Trend-Tracker Quickstart Runner
# Starts the FastAPI backend (port 8000) and Vite React frontend (port 5173).
# Press Ctrl+C to stop both cleanly.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="${ROOT_DIR}/backend"
FRONTEND_DIR="${ROOT_DIR}/frontend"

echo "=========================================================="
echo "          Starting Open-Trend-Tracker                     "
echo "=========================================================="

cleanup() {
  echo ""
  echo "Shutting down Open-Trend-Tracker services..."
  trap - SIGINT SIGTERM EXIT
  kill 0 2>/dev/null || true
  wait 2>/dev/null || true
  echo "All services stopped."
}
trap cleanup SIGINT SIGTERM EXIT

# 1. Start Backend
echo "-> Starting Backend API (http://localhost:8000)..."
if command -v uv >/dev/null 2>&1; then
  (cd "${BACKEND_DIR}" && uv run uvicorn app.api:app --reload --port 8000) &
elif [ -f "${BACKEND_DIR}/.venv/bin/uvicorn" ]; then
  (cd "${BACKEND_DIR}" && "${BACKEND_DIR}/.venv/bin/uvicorn" app.api:app --reload --port 8000) &
else
  (cd "${BACKEND_DIR}" && python3 -m uvicorn app.api:app --reload --port 8000) &
fi

# 2. Start Frontend
echo "-> Starting Frontend UI (http://localhost:5173)..."
(cd "${FRONTEND_DIR}" && npm run dev:backend) &

echo ""
echo "-> Both services launched!"
echo "   - Frontend UI:  http://localhost:5173"
echo "   - Backend API:  http://localhost:8000/docs"
echo "   - Press Ctrl+C to stop both."
echo ""

wait
