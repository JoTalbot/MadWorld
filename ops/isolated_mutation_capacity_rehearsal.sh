#!/usr/bin/env bash
set -euo pipefail
cd /opt/madworld
N="madworld-mutation-$$"
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
docker run -d --name "$API" --network "$NET" -e PYTHONPATH=/app/backend -e MADWORLD_DATABASE_URL="postgresql://madworld:madworld@$DB:5432/madworld" -e MADWORLD_RATE_LIMIT=10000 "$N-backend" uvicorn app.main:app --host 0.0.0.0 --port 8000 >/tmp/$N/api.log
for i in $(seq 1 45); do docker exec "$API" python -c 'import urllib.request; urllib.request.urlopen("http://127.0.0.1:8000/health/ready", timeout=2).read()' >/tmp/$N/ready 2>/dev/null && break; sleep 1; done
printf 'MUTATION_WORKLOAD=POST /api/v1/sessions, 20 concurrent clients, 15s bounded synthetic-account writes\n'
docker run --rm --network "$NET" python:3.12-slim python - "$API" <<'PY'
import concurrent.futures, json, sys, time, urllib.request, uuid
host=sys.argv[1]
end=time.monotonic()+15
counts={'success':0,'errors':0}
def one(i):
    ok=err=0
    while time.monotonic()<end:
        handle='load_'+uuid.uuid4().hex[:24]
        body=json.dumps({'handle':handle}).encode()
        req=urllib.request.Request(f'http://{host}:8000/api/v1/sessions',data=body,headers={'Content-Type':'application/json'},method='POST')
        try:
            with urllib.request.urlopen(req,timeout=3) as r:
                payload=json.loads(r.read())
                if r.status==201 and payload.get('player_id') and payload.get('token') and payload.get('handle')==handle: ok+=1
                else: err+=1
        except Exception: err+=1
    return ok,err
with concurrent.futures.ThreadPoolExecutor(max_workers=20) as ex:
    for ok,err in ex.map(one,range(20)):
        counts['success']+=ok; counts['errors']+=err
print(f"MUTATION_SUCCESS={counts['success']}")
print(f"MUTATION_ERRORS={counts['errors']}")
print(f"MUTATION_TOTAL={counts['success']+counts['errors']}")
print(f"MUTATION_RPS={(counts['success']+counts['errors'])/15:.3f}")
print(f"MUTATION_ERROR_RATE={(counts['errors']/(counts['success']+counts['errors'])) if counts['success']+counts['errors'] else 1:.6f}")
PY
printf 'MUTATION_DB_SESSIONS='
docker exec "$DB" psql -U madworld -d madworld -tAc 'select count(*) from player_sessions;'
AUTH_CODE=$(curl -sS -o /tmp/$N/auth-body -w '%{http_code}' --max-time 3 "http://$API:8000/api/v1/capabilities" || true)
printf 'AUTH_NO_TOKEN_HTTP=%s\n' "$AUTH_CODE"
RID="mutation-replay-$(cat /proc/sys/kernel/random/uuid)"
R1=$(curl -sS -o /tmp/$N/r1 -w '%{http_code}' --max-time 3 -X POST -H 'Content-Type: application/json' -H "X-Request-ID: $RID" --data '{"handle":"replay_probe_a"}' "http://$API:8000/api/v1/sessions" || true)
R2=$(curl -sS -o /tmp/$N/r2 -w '%{http_code}' --max-time 3 -X POST -H 'Content-Type: application/json' -H "X-Request-ID: $RID" --data '{"handle":"replay_probe_b"}' "http://$API:8000/api/v1/sessions" || true)
printf 'REPLAY_FIRST_HTTP=%s\n' "$R1"
printf 'REPLAY_SECOND_HTTP=%s\n' "$R2"
python3 - "$R1" "$R2" <<'PY'
import sys
print('REPLAY_CONTAINMENT_PASS=' + str(sys.argv[1]=='201' and sys.argv[2]=='409').lower())
PY
cat /tmp/$N/ready
docker stats --no-stream --format 'API_CPU={{.CPUPerc}} API_MEM={{.MemUsage}}' "$API"
echo 'MUTATION_ENVIRONMENT=isolated_postgres16_api_container'
echo 'PRODUCTION_DATABASE_TOUCHED=false'
