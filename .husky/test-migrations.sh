#!/bin/bash
set -ex

# --- 1. Reset Supabase DB ---
cd supabase
npx supabase db reset --debug --yes
cd ..

# --- 2. Set up connection details (match supabase/config.toml) ---
PGHOST=localhost
PGPORT=54322
PGUSER=postgres
PGDATABASE=postgres
PGPASSWORD=postgres
export PGHOST PGPORT PGUSER PGDATABASE PGPASSWORD

# Test-specific DB
export DATABASE_URL="postgresql://postgres:postgres@localhost:54322/test_migrations"

# Drop and recreate the test DB
psql -c "DROP DATABASE IF EXISTS test_migrations;"
psql -c "CREATE DATABASE test_migrations;"

# --- 3. Run Alembic checks using `uv` ---
cd backend

# Check for multiple Alembic heads
HEADS=$(uv run alembic heads | wc -l)
if [ "$HEADS" -gt 1 ]; then
  echo "❌- Multiple Alembic heads detected! Run 'uv run alembic heads'."
  exit 1
fi

# Migration up/down test cycle
uv run alembic upgrade head
uv run alembic check
uv run alembic downgrade base
uv run alembic upgrade head
uv run alembic downgrade base

# --- 4. Populate with dummy data ---
if ! uv run -m app.data.populate_dummy_data; then
  echo "❌- Failed to populate dummy data."
  echo "Make sure you updated app.data.populate_dummy_data to match your latest model changes."
  exit 1
fi

echo "✅ Supabase migration + Alembic logic tested successfully."
