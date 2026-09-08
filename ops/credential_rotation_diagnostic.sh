#!/usr/bin/env bash
set -euo pipefail

cd /opt/madworld

echo ROTATION_DIAG_START
echo "deployed_sha=$(cat .github-deployed-sha 2>/dev/null || echo missing)"

db_user="$(sed -n 's/^POSTGRES_USER=//p' .env | head -1)"
db_name="$(sed -n 's/^POSTGRES_DB=//p' .env | head -1)"
db_user="${db_user:-madworld}"
db_name="${db_name:-madworld_db}"

printf 'db_user_present=%s\n' "$(grep -q '^POSTGRES_USER=' .env && echo yes || echo no)"
printf 'db_name_present=%s\n' "$(grep -q '^POSTGRES_DB=' .env && echo yes || echo no)"
printf 'db_url_present=%s\n' "$(grep -q '^MADWORLD_DATABASE_URL=' .env && echo yes || echo no)"
printf 'postgres_container=%s\n' "$(docker inspect madworld-postgres-1 --format '{{.State.Status}}' 2>/dev/null || echo missing)"
printf 'disk_free_mb=%s\n' "$(df -Pm /opt/madworld | awk 'NR==2 {print $4}')"
printf 'backup_files=%s\n' "$(find backups -maxdepth 1 -type f -name 'madworld-*.dump' | wc -l)"

echo DB_PROBE
docker exec madworld-postgres-1 psql -U "$db_user" -d "$db_name" -Atqc "SELECT datname FROM pg_database WHERE datistemplate=false ORDER BY datname;"
echo ROTATION_DIAG_DONE
