#!/usr/bin/env fish

# 1. Generate Random Passwords
# using openssl to generate 24 bytes of base64 randomness (approx 32 chars)
set SPROCKET_RO_PW (openssl rand -base64 24)
set FANTASY_RO_PW  (openssl rand -base64 24)
set FANTASY_RW_PW  (openssl rand -base64 24)

# 2. Define the Output Filename
set OUT_FILE "setup_permissions.sql"

# 3. Generate the SQL File
# We use a variable for the content to keep the echo command clean
echo "/*
 * DATABASE PERMISSION SETUP SCRIPT (Generated)
 *
 * INSTRUCTIONS:
 * 1. This file was auto-generated with secure passwords.
 * 2. If using a GUI (DBeaver, pgAdmin), run SECTION 1 first.
 * Then connect to 'sprocket_main' and run SECTION 2.
 * Then connect to 'fantasy' and run SECTION 3.
 * 3. If using psql terminal, the \c commands will handle connection switching.
 */

-- ==========================================
-- SECTION 1: GLOBAL OBJECTS (Run as Admin)
-- ==========================================

-- 1. Create the new database
-- Note: This will fail if the DB already exists.
CREATE DATABASE fantasy;

-- 2. Create the Users
CREATE USER \"sprocket-readonly\" WITH PASSWORD '$SPROCKET_RO_PW';
CREATE USER \"fantasy-readonly\"  WITH PASSWORD '$FANTASY_RO_PW';
CREATE USER \"fantasy-rw\"        WITH PASSWORD '$FANTASY_RW_PW';

-- ==========================================
-- SECTION 2: SPROCKET_MAIN SETUP
-- ==========================================

-- Connect to the specific database (If using psql)
\c sprocket_main

-- 1. Isolate the database (Optional but Recommended)
-- This prevents other random users from connecting by default
REVOKE CONNECT ON DATABASE sprocket_main FROM PUBLIC;

-- 2. Grant Connection
GRANT CONNECT ON DATABASE sprocket_main TO \"sprocket-readonly\";

-- 3. Grant Schema Usage (Access to the 'public' folder)
GRANT USAGE ON SCHEMA public TO \"sprocket-readonly\";

-- 4. Grant Permissions on EXISTING tables/sequences
GRANT SELECT ON ALL TABLES IN SCHEMA public TO \"sprocket-readonly\";
GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO \"sprocket-readonly\";

-- 5. Grant Permissions on FUTURE tables (Default Privileges)
-- This ensures tables created later are also readable by this user
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO \"sprocket-readonly\";
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON SEQUENCES TO \"sprocket-readonly\";

-- ==========================================
-- SECTION 3: FANTASY SETUP
-- ==========================================

-- Connect to the specific database (If using psql)
\c fantasy

-- 1. Isolate the database
REVOKE CONNECT ON DATABASE fantasy FROM PUBLIC;

-- --- SETUP READ-ONLY USER ---

GRANT CONNECT ON DATABASE fantasy TO \"fantasy-readonly\";
GRANT USAGE ON SCHEMA public TO \"fantasy-readonly\";

-- Permissions for existing objects
GRANT SELECT ON ALL TABLES IN SCHEMA public TO \"fantasy-readonly\";
GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO \"fantasy-readonly\";

-- Permissions for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO \"fantasy-readonly\";
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON SEQUENCES TO \"fantasy-readonly\";

-- --- SETUP READ-WRITE USER ---

GRANT CONNECT ON DATABASE fantasy TO \"fantasy-rw\";
GRANT USAGE ON SCHEMA public TO \"fantasy-rw\";

-- Permissions for existing objects
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO \"fantasy-rw\";
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO \"fantasy-rw\";

-- Permissions for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO \"fantasy-rw\";
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO \"fantasy-rw\";
" > $OUT_FILE

# 4. Print Passwords to Terminal
echo "=================================================="
echo " SUCCESS: $OUT_FILE created"
echo "=================================================="
echo "Use these credentials for your team:"
echo ""
echo "User: sprocket-readonly"
echo "Pass: $SPROCKET_RO_PW"
echo ""
echo "User: fantasy-readonly"
echo "Pass: $FANTASY_RO_PW"
echo ""
echo "User: fantasy-rw"
echo "Pass: $FANTASY_RW_PW"
echo "=================================================="