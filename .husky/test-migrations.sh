#!/bin/bash
set -ex

# --- 1. Start Supabase container ---
docker compose -f docker-compose.yml -f .husky/docker-compose.ci.yml up -d supabase

# --- 2. Wait for Supabase to be healthy ---
echo "Waiting for Supabase to become healthy..."
for i in {1..60}; do
  if curl -sf http://localhost:54321/rest-admin/v1/ready > /dev/null; then
    echo "✅ Supabase is healthy"
    break
  fi
  echo "⏳ Supabase not ready yet... ($((i*2))s)"
  sleep 2
  if [[ $i -eq 60 ]]; then
    echo "❌ Supabase did not become healthy in time"
    exit 1
  fi
done

# --- 3. Set up DB connection vars ---
PGHOST=localhost
PGPORT=54322
PGUSER=postgres
PGDATABASE=postgres
PGPASSWORD=postgres
export PGHOST PGPORT PGUSER PGDATABASE PGPASSWORD

# Use dedicated test DB
export DATABASE_URL="postgresql://postgres:postgres@localhost:54322/test_migrations"

# Drop & recreate the DB
psql -c "DROP DATABASE IF EXISTS test_migrations;"
psql -c "CREATE DATABASE test_migrations;"

# --- 4. Run Alembic migration checks ---
cd backend

HEADS=$(uv run alembic heads | wc -l)
if [ "$HEADS" -gt 1 ]; then
  echo "❌ Multiple Alembic heads detected! Run 'uv run alembic heads'."
  exit 1
fi

uv run alembic upgrade head
uv run alembic check
uv run alembic downgrade base
uv run alembic upgrade head
uv run alembic downgrade base

# --- 5. Populate dummy data ---
if ! uv run -m app.data.populate_dummy_data; then
  echo "❌ Failed to populate dummy data."
  echo "Make sure app.data.populate_dummy_data is up to date."
  exit 1
fi

echo "✅ Supabase migration + Alembic logic tested successfully."
