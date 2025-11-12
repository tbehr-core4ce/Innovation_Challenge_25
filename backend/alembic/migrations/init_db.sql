-- Database initialization script for BETS
-- This runs automatically when the PostgreSQL container starts for the first time

-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- Verify PostGIS installation
SELECT PostGIS_version();

-- Create additional schemas if needed
-- CREATE SCHEMA IF NOT EXISTS staging;
-- CREATE SCHEMA IF NOT EXISTS archive;

-- Set search path
-- ALTER DATABASE bets_db SET search_path TO public, postgis;

-- Grant necessary permissions
GRANT ALL PRIVILEGES ON DATABASE bets_db TO bets_user;

-- Create a read-only user for reporting (optional)
-- CREATE USER bets_readonly WITH PASSWORD 'readonly_password';
-- GRANT CONNECT ON DATABASE bets_db TO bets_readonly;
-- GRANT USAGE ON SCHEMA public TO bets_readonly;
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO bets_readonly;
-- ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO bets_readonly;

-- Log successful initialization
SELECT 'Database initialized successfully' AS status;