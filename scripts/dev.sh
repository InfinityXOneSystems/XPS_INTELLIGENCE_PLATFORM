#!/usr/bin/env bash
# XPS Intelligence Platform — Local Development Launcher
# Starts all services for local development
# Usage: ./scripts/dev.sh [backend|frontend|all]

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

SERVICE="${1:-all}"

echo "🚀 XPS Intelligence Platform — Dev Mode"
echo "======================================="
echo "Service: $SERVICE"
echo ""

# ── Validate .env ──────────────────────────────────────────────────────────
if [[ ! -f ".env" ]]; then
  echo "⚠️  No .env file found. Creating from .env.example..."
  if [[ -f ".env.example" ]]; then
    cp .env.example .env
    echo "✅ .env created from .env.example — please fill in your values"
  else
    echo "⚠️  No .env.example either — you may need to set env vars manually"
  fi
fi

# ── Start backend ──────────────────────────────────────────────────────────
start_backend() {
  if [[ -f "apps/backend/main.py" ]]; then
    echo "🔧 Starting backend (FastAPI)..."
    # Run uvicorn from the repo root with PYTHONPATH set so that
    # `from apps.backend.*` imports resolve correctly.
    PYTHONPATH="$REPO_ROOT" uvicorn apps.backend.main:app \
      --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    echo "✅ Backend started on http://localhost:8000 (PID: $BACKEND_PID)"
  else
    echo "⚠️  No backend entry point yet (apps/backend/main.py) — skipping"
  fi
}

# ── Start frontend ─────────────────────────────────────────────────────────
start_frontend() {
  if [[ -f "apps/frontend/package.json" ]]; then
    echo "🖥️  Starting frontend (Next.js)..."
    cd apps/frontend
    npm run dev &
    FRONTEND_PID=$!
    echo "✅ Frontend started on http://localhost:3000 (PID: $FRONTEND_PID)"
    cd "$REPO_ROOT"
  else
    echo "⚠️  No frontend package.json yet — skipping"
  fi
}

# ── Main ───────────────────────────────────────────────────────────────────
case "$SERVICE" in
  backend)
    start_backend
    ;;
  frontend)
    start_frontend
    ;;
  all)
    start_backend
    start_frontend
    ;;
  *)
    echo "❌ Unknown service: $SERVICE"
    echo "Usage: ./scripts/dev.sh [backend|frontend|all]"
    exit 1
    ;;
esac

echo ""
echo "Development environment started!"
echo "  Backend API:  http://localhost:8000"
echo "  Frontend:     http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all services"
wait
