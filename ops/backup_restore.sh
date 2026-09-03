#!/usr/bin/env bash
set -euo pipefail

: "${MADWORLD_DATABASE_URL:?MADWORLD_DATABASE_URL is required}"
: "${BACKUP_FILE:?BACKUP_FILE is required}"
: "${RESTORE_DATABASE_URL:?RESTORE_DATABASE_URL is required}"

pg_dump --format=custom --file="$BACKUP_FILE" "$MADWORLD_DATABASE_URL"
pg_restore --clean --if-exists --no-owner --dbname="$RESTORE_DATABASE_URL" "$BACKUP_FILE"

psql "$RESTORE_DATABASE_URL" -v ON_ERROR_STOP=1 -c 'SELECT 1 AS restore_verified;'
psql "$RESTORE_DATABASE_URL" -v ON_ERROR_STOP=1 -c 'SELECT COUNT(*) AS migration_count FROM schema_migrations;'
echo 'backup_restore_verified=true'
