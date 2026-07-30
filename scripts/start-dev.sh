#!/usr/bin/env bash
set -uo pipefail

# Source the Python venv so uvicorn and other tools are in PATH
source /app/.venv/bin/activate

cleanup() {
  kill "${FASTAPI_PID:-}" "${VITE_PID:-}" 2>/dev/null || true
  wait 2>/dev/null || true
}
trap cleanup EXIT INT TERM

echo "Starting FastAPI (reload enabled)..."
cd /app/server
python -m uvicorn src.main:app --host 0.0.0.0 --port 3000 --reload &
FASTAPI_PID=$!

echo "Starting Vite dev server..."
cd /app/ui

if [[ ! -d node_modules ]] || [[ ! -x node_modules/.bin/vite ]]; then
  echo "Installing frontend dependencies..."
  npm ci
fi

npm run dev -- --host 0.0.0.0 --port 5173 &
VITE_PID=$!

echo ""
echo "Dev environment ready — http://localhost:5173"
echo "  Vite serves UI with HMR on :5173"
echo "  FastAPI serves API on :3000 (internal, proxied by Vite)"
echo "  FastAPI auto-reloads on Python file changes"
echo ""

wait -n "$FASTAPI_PID" "$VITE_PID"
