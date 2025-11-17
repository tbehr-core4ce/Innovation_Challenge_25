#!/usr/bin/env python3
"""
Script to reset the database and run migrations.
Python alternative to reset_database.sh

Usage:
    python backend/scripts/reset_database.py
"""

import subprocess
import sys
import os


def run_command(cmd, description):
    """Run a shell command and handle errors."""
    print(f"\n{description}")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: {e.stderr}")
        return False


def main():
    """Reset database and run migrations."""
    print("=" * 60)
    print("RESETTING DATABASE")
    print("=" * 60)

    # Database configuration (adjust if needed)
    DB_NAME = os.environ.get('DB_NAME', 'bets_db')
    DB_USER = os.environ.get('DB_USER', 'bets_user')
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DOCKER_COMMAND = 'docker exec -it bets-postgres-1'

    # Step 1: Drop existing database
    print("\nStep 1: Dropping existing database...")
    run_command(
        f'{DOCKER_COMMAND} psql -U {DB_USER} -h {DB_HOST} -d postgres -c "DROP DATABASE IF EXISTS {DB_NAME};" 2>/dev/null || true',
        "Dropping old database if exists..."
    )

    # Step 2: Create fresh database
    print("\nStep 2: Creating fresh database...")
    if not run_command(
        f'{DOCKER_COMMAND} psql -U {DB_USER} -h {DB_HOST} -d postgres -c "CREATE DATABASE {DB_NAME};"',
        "Creating new database..."
    ):
        print("Failed to create database")
        sys.exit(1)

    # Step 3: Enable PostGIS
    print("\nStep 3: Enabling PostGIS extension...")
    if not run_command(
        f'{DOCKER_COMMAND} psql -U {DB_USER} -h {DB_HOST} -d {DB_NAME} -c "CREATE EXTENSION IF NOT EXISTS postgis;"',
        "Enabling PostGIS..."
    ):
        print("Failed to enable PostGIS")
        sys.exit(1)

    # Step 4: Run Alembic migrations
    print("\nStep 4: Running Alembic migrations...")

    # Change to backend directory
    backend_dir = os.path.join(os.path.dirname(__file__), '..')
    os.chdir(backend_dir)

    if not run_command('alembic upgrade head', "Running migrations..."):
        print("Failed to run migrations")
        sys.exit(1)

    # Success
    print("\n" + "=" * 60)
    print("✓ DATABASE RESET COMPLETE!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Run the data ingestion pipeline:")
    print("     python backend/scripts/run_ingestion.py --all")
    print()


if __name__ == '__main__':
    main()
