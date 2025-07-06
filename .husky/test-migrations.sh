#!/bin/bash
set -ex

HEADS=$(uv run alembic heads | wc -l)
if [ "$HEADS" -gt 1 ]; then
    echo "❌- Multiple Alembic heads detected! Run 'uv run alembic heads'."
    exit 1
fi

psql -h db -U postgres -c "DROP DATABASE IF EXISTS test_migrations;"
psql -h db -U postgres -c "CREATE DATABASE test_migrations;"

uv run alembic upgrade head
uv run alembic check
uv run alembic downgrade base
uv run alembic upgrade head
uv run alembic downgrade base
if ! uv run -m app.data.populate_dummy_data; then
    echo "❌- Failed to populate dummy data."
    echo "Make sure you updated the dummy data script (app.data.populate_dummy_data) to match your latest model changes."
    exit 1
fi
