#!/usr/bin/env bash
set -euo pipefail

: "${MADWORLD_DATABASE_URL:?MADWORLD_DATABASE_URL is required}"
BACKUP_DIR="${BACKUP_DIR:-/opt/madworld/backups}"
RETENTION_DAYS="${RETENTION_DAYS:-14}"
MIN_FREE_MB="${MIN_FREE_MB:-1024}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="${BACKUP_DIR}/madworld-${STAMP}.dump"
LOG="${BACKUP_DIR}/backup.log"
mkdir -p "$BACKUP_DIR"
exec >>"$LOG" 2>&1

echo "[$(date -u +%FT%TZ)] backup start"
FREE_MB="$(df -Pm "$BACKUP_DIR" | awk 'NR==2 {print $4}')"
if [ "${FREE_MB:-0}" -lt "$MIN_FREE_MB" ]; then
  echo "backup aborted: free space ${FREE_MB}MB < ${MIN_FREE_MB}MB" >&2
  exit 20
fi

umask 077
pg_dump --format=custom --no-owner --file="$OUT" "$MADWORLD_DATABASE_URL"
pg_restore --list "$OUT" >/dev/null
SIZE="$(stat -c '%s' "$OUT")"
if [ "${SIZE:-0}" -le 0 ]; then
  echo "backup invalid: zero-byte dump" >&2
  exit 21
fi
sha256sum "$OUT" >"${OUT}.sha256"
find "$BACKUP_DIR" -type f -name 'madworld-*.dump' -mtime "+${RETENTION_DAYS}" -delete
find "$BACKUP_DIR" -type f -name 'madworld-*.dump.sha256' -mtime "+${RETENTION_DAYS}" -delete

echo "[$(date -u +%FT%TZ)] backup success file=$OUT bytes=$SIZE"
