-- File: grant_sprocket_access.sql
-- Run this script using psql or a tool that supports meta-commands.
-- Example: psql -U postgres -f grant_sprocket_access.sql

-- 1. Connect to the specific database
-- Note: \c is a psql meta-command. If running in a GUI (like DBeaver/PgAdmin), 
-- simply ensure you have selected the 'sprocket_main' database active connection.
\c sprocket_main

-- 2. Grant Connection and Schema Usage
-- Allows the user to log in and "see" the public schema
GRANT CONNECT ON DATABASE sprocket_main TO sprocket_main;
GRANT USAGE ON SCHEMA public TO sprocket_main;

-- 3. Grant Access to EXISTING Objects
-- Read/Write access for tables currently in the database
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO sprocket_main;
-- Permission to use sequences (required for auto-incrementing IDs)
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO sprocket_main;

-- 4. Grant Access to FUTURE Objects (Default Privileges)
-- Ensures tables created *after* this script runs are automatically accessible
ALTER DEFAULT PRIVILEGES IN SCHEMA public 
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO sprocket_main;

ALTER DEFAULT PRIVILEGES IN SCHEMA public 
GRANT USAGE, SELECT ON SEQUENCES TO sprocket_main;
