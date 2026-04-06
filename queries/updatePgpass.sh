#!/usr/bin/env fish

# --- Configuration ---
set PGPASS_FILE "$HOME/.pgpass"
set TARGET_HOST "spr.ocket.cloud"  # The host you want to update
set TARGET_PORT "30000"            # The port you want to update
set TARGET_DB "sprocket_main"      # The database you want to update (or '*' for wildcard)

set GOPASS_USER_PATH "sprocket/db_main_username" # Your gopass path for username
set GOPASS_PW_PATH "sprocket/db_main_pw"         # Your gopass path for password

# --- Get new credentials from gopass ---
# It's crucial to escape any special characters that might appear in the gopass output
# before inserting them into the .pgpass file.
# The .pgpass file specifies that ':' and '\' must be escaped.
set NEW_USERNAME (gopass show "$GOPASS_USER_PATH" | string replace -a ':' '\\:' | string replace -a '\\' '\\\\')
set NEW_PASSWORD (gopass show "$GOPASS_PW_PATH" | string replace -a ':' '\\:' | string replace -a '\\' '\\\\')

# Check if gopass commands succeeded and returned values
if test -z "$NEW_USERNAME" -o -z "$NEW_PASSWORD"
  echo "Error: Could not retrieve username or password from gopass."
  exit 1
end

# --- Construct the new line ---
set NEW_LINE "$TARGET_HOST:$TARGET_PORT:$TARGET_DB:$NEW_USERNAME:$NEW_PASSWORD"

# --- Create a temporary file for the new .pgpass content ---
set TEMP_PGPASS (mktemp)

# --- Process the .pgpass file using awk ---
# awk is much better for field-based processing and escaping.
# This script will:
# 1. Look for lines that match the host, port, database, and old username.
# 2. If a match is found, replace the entire line with the NEW_LINE.
# 3. Print all other lines unchanged.
awk -v target_host="$TARGET_HOST" \
  -v target_port="$TARGET_PORT" \
  -v target_db="$TARGET_DB" \
  -v new_line_content="$NEW_LINE" \
  'BEGIN { FS=":"; OFS=":" }
    {
        if ( ($1 == target_host || $1 == "*") && \
             ($2 == target_port || $2 == "*") && \
             ($3 == target_db || $3 == "*")) {
            print new_line_content  # Replace the line
            found_and_replaced = 1
        } else {
            print $0  # Print the original line
        }
    }' "$PGPASS_FILE" > "$TEMP_PGPASS"

# --- Atomically replace the original file ---
mv "$TEMP_PGPASS" "$PGPASS_FILE"

# --- Set correct permissions (crucial for .pgpass) ---
chmod 600 "$PGPASS_FILE"
echo "Updated $PGPASS_FILE for host $TARGET_HOST."
