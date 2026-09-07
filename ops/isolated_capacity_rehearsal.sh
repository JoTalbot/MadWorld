#!/usr/bin/env bash
set -euo pipefail
cd /opt/madworld
N="madworld-capacity-$$"
NET="$N-net"
DB="$N-db"
API="$N-api"
cleanup(){ docker rm -f "$API" "$DB" >/dev/null 2>&1 || true; docker network rm "$NET" >/dev/null 2>&1 || true; rm -rf "/tmp/$N"; }
trap cleanup EXIT
mkdir -p "/tmp/$N"
docker network create "$NET" >/dev/null
docker run -d --name "$DB" --network "$NET" -e POSTGRES_USER=madworld -e POSTGRES_PASSWORD=madworld -e POSTGRES_DB=madworld postgres:16 >/dev/null
for i in $(seq 1 45); do docker exec "$DB" pg_isready -U madworld -d madworld >/dev/null 2>&1 && break; sleep 1; done
docker build -q -f ops/Dockerfile.backend -t "$N-backend" . >/tmp/$N/build.log
docker run --rm --network "$NET" -e PYTHONPATH=/app/backend -e MADWORLD_DATABASE_URL="postgresql://madworld:madworld@$DB:5432/madworld" "$N-backend" python scripts/migrate.py >/tmp/$N/migrate.log
docker run -d --name "$API" --network "$NET" -e PYTHONPATH=/app/backend -e MADWORLD_DATABASE_URL="postgresql://madworld:madworld@$DB:5432/madworld" "$N-backend" uvicorn app.main:app --host 0.0.0.0 --port 8000 >/tmp/$N/api.log
for i in $(seq 1 45); do docker exec "$API" python -c 'import urllib.request; urllib.request.urlopen("http://127.0.0.1:8000/health/ready", timeout=2).read()' >/tmp/$N/ready 2>/dev/null && break; sleep 1; done
printf 'CAPACITY_WORKLOAD=GET /health/ready, 20 concurrent clients, 30s bounded read-only\n'
docker run --rm --network "$NET" -v /opt/madworld/ops/isolated_capacity_client.py:/client.py:ro python:3.12-slim python /client.py "$API" 30 20
printf 'DB_CONNECTIONS='
docker exec "$DB" psql -U madworld -d madworld -tAc 'select count(*) from pg_stat_activity;'
docker stats --no-stream --format 'API_CPU={{.CPUPerc}} API_MEM={{.MemUsage}}' "$API"
cat /tmp/$N/ready
echo 'CAPACITY_ENVIRONMENT=isolated_postgres16_api_container'
echo 'PRODUCTION_DATABASE_TOUCHED=false'
