#!/usr/bin/env bash

# Stop execution if any command fails
set -e

echo "Starting local deployment setup..."

# Virtual Environment Check & Activation
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
else
    echo "Virtual environment directory found."
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Verifying/installing dependencies..."
pip install -r deploy/requirements.txt -q

# PostgreSQL Service Check & Port Detection
echo "Checking PostgreSQL status..."
if ! pg_isready -q 2>/dev/null; then
    echo "Starting PostgreSQL server via Homebrew..."
    brew services start postgresql 2>/dev/null || brew services start postgresql@16 2>/dev/null
    sleep 2
fi

# Detect running port (defaults to 5432 if query fails)
PGPORT=$(psql postgres -t -A -c "SHOW port;" 2>/dev/null || echo "5432")
echo "PostgreSQL is running on port: ${PGPORT}"

# Database Reset (Drop existing & recreate fresh)
echo "Resetting local databases..."
psql postgres -c "DROP DATABASE IF EXISTS agile_board WITH (FORCE);" >/dev/null 2>&1 || psql postgres -c "DROP DATABASE IF EXISTS agile_board;"
psql postgres -c "DROP DATABASE IF EXISTS agile_board_test WITH (FORCE);" >/dev/null 2>&1 || psql postgres -c "DROP DATABASE IF EXISTS agile_board_test;"

psql postgres -c "CREATE DATABASE agile_board;"
psql postgres -c "CREATE DATABASE agile_board_test;"
echo "Databases 'agile_board' and 'agile_board_test' recreated."

# Generate/Update .env File
echo "Writing .env configuration..."
cat <<EOF > .env
DB_URL=postgresql://localhost:${PGPORT}/agile_board
TEST_DB_URL=postgresql://localhost:${PGPORT}/agile_board_test
EOF

# Export variables to script environment
export $(grep -v '^#' .env | xargs)

# Load demo data (engineers + tasks)
echo "Seeding demo data..."
psql "$DB_URL" -q -f scripts/seed.sql

# 5. Run the Web Application
echo "Starting Gunicorn server on http://127.0.0.1:8000 ..."
PYTHONPATH=src gunicorn 'agile_board.app:create_app()' --bind 127.0.0.1:8000