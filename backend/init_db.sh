#!/bin/bash
set -e

echo "Waiting for PostgreSQL to be ready..."
export PGPASSWORD=postgres

# Wait for PostgreSQL to accept connections
until psql -h db -U postgres -d postgres -c '\q' 2>/dev/null; do
  >&2 echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

echo "PostgreSQL is ready. Creating database if needed..."
# Create database if it doesn't exist
psql -h db -U postgres -d postgres -tc "SELECT 1 FROM pg_database WHERE datname = 'sqlinjection_db'" | grep -q 1 || \
psql -h db -U postgres -d postgres -c "CREATE DATABASE sqlinjection_db"

echo "Initializing database..."
python /app/init_db.py
