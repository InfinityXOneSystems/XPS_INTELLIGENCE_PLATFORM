#!/usr/bin/env bash
# XPS Intelligence Platform — Database Migration Runner
# Usage: ./scripts/db-migrate.sh [up|down|status]

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

DIRECTION="${1:-up}"

# Load .env if available
if [[ -f ".env" ]]; then
  set -a
  source .env
  set +a
fi

if [[ -z "${DATABASE_URL:-}" ]]; then
  echo "❌ DATABASE_URL environment variable is not set"
  echo "   Set it in your .env file or environment"
  exit 1
fi

echo "🗄️  XPS Intelligence Platform — Database Migrations"
echo "====================================================="
echo "Direction: $DIRECTION"
echo "Database: $(echo "$DATABASE_URL" | sed 's|:.*@|:***@|')"
echo ""

if [[ -d "apps/backend" ]]; then
  cd apps/backend
  if command -v alembic &>/dev/null; then
    case "$DIRECTION" in
      up)
        alembic upgrade head
        echo "✅ Migrations applied"
        ;;
      down)
        alembic downgrade -1
        echo "✅ Last migration reverted"
        ;;
      status)
        alembic current
        alembic history
        ;;
      *)
        echo "❌ Unknown direction: $DIRECTION"
        echo "Usage: ./scripts/db-migrate.sh [up|down|status]"
        exit 1
        ;;
    esac
  else
    echo "⚠️  alembic not installed — run ./scripts/bootstrap.sh first"
  fi
else
  echo "⚠️  No backend yet — skipping migrations (foundation phase)"
fi
