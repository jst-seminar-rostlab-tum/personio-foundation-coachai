set -e

psql -h db -U postgres -tAc "SELECT 1 FROM pg_database WHERE datname='test_migrations'" | grep -q 1 || \
psql -h db -U postgres -c "CREATE DATABASE test_migrations;"

HEADS=$(uv run alembic heads | wc -l)
if [ "$HEADS" -gt 1 ]; then 
    echo "❌- Multiple Alembic heads detected! Run 'uv run alembic heads'."; 
    exit 1; 
fi

uv run -m app.data.populate_dummy_data
uv run alembic check
uv run -m app.data.populate_dummy_data
