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
for i in $(seq 1 45); do curl -fsS --max-time 2 "http://$API:8000/health/ready" >/tmp/$N/ready 2>/dev/null && break; sleep 1; done
: >/tmp/$N/t
: >/tmp/$N/e
END=$(( $(date +%s)+30 ))
while [ $(date +%s) -lt "$END" ]; do
  for c in $(seq 1 20); do
    (a=$(date +%s%N); if curl -fsS --max-time 3 -o /dev/null "http://$API:8000/health/ready"; then b=$(date +%s%N); echo $((b-a)) >>/tmp/$N/t; else echo 1 >>/tmp/$N/e; fi) &
  done
  wait
done
python3 - "$N" <<'PY'
import pathlib,sys
n=sys.argv[1]
t=[int(x)/1e6 for x in pathlib.Path('/tmp/'+n+'/t').read_text().splitlines() if x]
e=len(pathlib.Path('/tmp/'+n+'/e').read_text().splitlines())
z=len(t)+e
s=sorted(t)
def pct(p):
    return round(s[int((len(s)-1)*p/100)],3) if s else None
print('CAPACITY_WORKLOAD=GET /health/ready, 20 concurrent clients, 30s bounded read-only')
print(f'CAPACITY_REQUESTS={z}')
print(f'CAPACITY_SUCCESS={len(t)}')
print(f'CAPACITY_ERRORS={e}')
print(f'CAPACITY_RPS={z/30:.3f}')
print(f'LATENCY_P50_MS={pct(50)}')
print(f'LATENCY_P95_MS={pct(95)}')
print(f'LATENCY_P99_MS={pct(99)}')
print(f'ERROR_RATE={e/z if z else 1:.6f}')
PY
printf 'DB_CONNECTIONS='
docker exec "$DB" psql -U madworld -d madworld -tAc 'select count(*) from pg_stat_activity;'
docker stats --no-stream --format 'API_CPU={{.CPUPerc}} API_MEM={{.MemUsage}}' "$API"
cat /tmp/$N/ready
echo 'CAPACITY_ENVIRONMENT=isolated_postgres16_api_container'
echo 'PRODUCTION_DATABASE_TOUCHED=false'
