#!/bin/bash
# Script to reset the database and run migrations
# Usage: ./backend/scripts/reset_database.sh

set -e  # Exit on error

echo "================================"
echo "RESETTING DATABASE"
echo "================================"

# Database configuration (adjust these if needed)
DB_NAME="bets_db"
DB_USER="bets_user"
DB_HOST="localhost"

echo ""
echo "Step 1: Dropping existing database..."
psql -U "$DB_USER" -h "$DB_HOST" -d postgres -c "DROP DATABASE IF EXISTS $DB_NAME;" 2>/dev/null || true

echo "Step 2: Creating fresh database..."
psql -U "$DB_USER" -h "$DB_HOST" -d postgres -c "CREATE DATABASE $DB_NAME;"

echo "Step 3: Enabling PostGIS extension..."
psql -U "$DB_USER" -h "$DB_HOST" -d "$DB_NAME" -c "CREATE EXTENSION IF NOT EXISTS postgis;"

echo "Step 4: Running Alembic migrations..."
cd "$(dirname "$0")/.."  # Go to backend directory
alembic upgrade head

echo ""
echo "================================"
echo "✓ DATABASE RESET COMPLETE!"
echo "================================"
echo ""
echo "Next steps:"
echo "  1. Run the data ingestion pipeline:"
echo "     python backend/scripts/run_ingestion.py --all"
echo ""
