#!/usr/bin/env bash
set -euo pipefail

SUPABASE_HOST="${SUPABASE_HOST:-host.docker.internal}"
SUPABASE_PORT="${SUPABASE_PORT:-54321}"

echo "🔄  Waiting for Supabase to be healthy at ${SUPABASE_HOST}:${SUPABASE_PORT} …"
for i in {1..60}; do
  if curl -sf "http://${SUPABASE_HOST}:${SUPABASE_PORT}/rest-admin/v1/ready" >/dev/null; then
    echo "✅ Supabase is healthy"
    break
  fi
  echo "⏳ Supabase not ready yet... ($((i*2)) s)"
  sleep 2
  [[ $i -eq 60 ]] && { echo "❌ Supabase did not become healthy in time";
   exit 1; }
done

export PGHOST="${PGHOST:-host.docker.internal}"
export PGPORT="${PGPORT:-54322}"
export PGUSER="${PGUSER:-postgres}"
export PGPASSWORD="${PGPASSWORD:-postgres}"
export PGDATABASE="postgres"
export DATABASE_URL="postgresql://${PGUSER}:${PGPASSWORD}@${PGHOST}:${PGPORT}/test_migrations"

psql -v ON_ERROR_STOP=1 -c "DROP DATABASE IF EXISTS test_migrations;"
psql -v ON_ERROR_STOP=1 -c "CREATE DATABASE test_migrations;"

cd /app

HEADS=$(uv run alembic heads | wc -l)
if [[ "$HEADS" -gt 1 ]]; then
  echo "❌ Multiple Alembic heads detected!"
  exit 1
fi

uv run alembic upgrade head
uv run alembic check
uv run alembic downgrade base
uv run alembic upgrade head
uv run alembic downgrade base

if ! uv run -m app.data.populate_dummy_data; then
  echo "❌ Failed to populate dummy data."
  exit 1
fi

echo "🎉 Supabase migration + Alembic logic tested successfully."
