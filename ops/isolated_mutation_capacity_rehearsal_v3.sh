#!/usr/bin/env bash
set -euo pipefail
cd /opt/madworld
N="madworld-mutation-v3-$$"
NET="$N-net"; DB="$N-db"; API="$N-api"
cleanup(){ docker rm -f "$API" "$DB" >/dev/null 2>&1 || true; docker network rm "$NET" >/dev/null 2>&1 || true; rm -rf "/tmp/$N"; }
trap cleanup EXIT
mkdir -p "/tmp/$N"
docker network create "$NET" >/dev/null
docker run -d --name "$DB" --network "$NET" -e POSTGRES_USER=madworld -e POSTGRES_PASSWORD=madworld -e POSTGRES_DB=madworld postgres:16 >/dev/null
for i in $(seq 1 60); do docker exec "$DB" pg_isready -U madworld -d madworld >/dev/null 2>&1 && break; sleep 1; done
docker build -q -f ops/Dockerfile.backend -t "$N-backend" . >/tmp/$N/build.log
docker run --rm --network "$NET" -e PYTHONPATH=/app/backend -e MADWORLD_DATABASE_URL="postgresql://madworld:madworld@$DB:5432/madworld" "$N-backend" python scripts/migrate.py >/tmp/$N/migrate.log
docker run -d --name "$API" --network "$NET" -e PYTHONPATH=/app/backend -e MADWORLD_DATABASE_URL="postgresql://madworld:madworld@$DB:5432/madworld" -e MADWORLD_RATE_LIMIT=10000 "$N-backend" uvicorn app.main:app --host 0.0.0.0 --port 8000 >/tmp/$N/api.log
printf 'MUTATION_WORKLOAD=POST /api/v1/sessions, 20 concurrent clients, 15s bounded synthetic-account writes\n'
docker run --rm --network "$NET" python:3.12-slim python - "$API" <<'PY'
import concurrent.futures, json, sys, time, urllib.error, urllib.request, uuid
host=sys.argv[1]
base=f'http://{host}:8000'
ready=False
for _ in range(60):
    try:
        with urllib.request.urlopen(base+'/health/ready', timeout=2) as r:
            if r.status==200: ready=True; break
    except Exception: time.sleep(1)
print(f'API_READY={str(ready).lower()}')
if not ready: sys.exit(2)
end=time.monotonic()+15
def one(_):
    ok=err=0
    while time.monotonic()<end:
        handle='load_'+uuid.uuid4().hex[:24]
        req=urllib.request.Request(base+'/api/v1/sessions',data=json.dumps({'handle':handle}).encode(),headers={'Content-Type':'application/json'},method='POST')
        try:
            with urllib.request.urlopen(req,timeout=3) as r:
                payload=json.loads(r.read())
                ok += int(r.status==201 and payload.get('player_id') and payload.get('token') and payload.get('handle')==handle)
                err += int(r.status!=201)
        except Exception: err+=1
    return ok,err
s=e=0
with concurrent.futures.ThreadPoolExecutor(max_workers=20) as ex:
    for ok,err in ex.map(one,range(20)): s+=ok; e+=err
t=s+e
print(f'MUTATION_SUCCESS={s}'); print(f'MUTATION_ERRORS={e}'); print(f'MUTATION_TOTAL={t}'); print(f'MUTATION_RPS={t/15:.3f}'); print(f'MUTATION_ERROR_RATE={(e/t if t else 1):.6f}')
def code(path, method='GET', body=None, headers=None):
    req=urllib.request.Request(base+path,data=body,headers=headers or {},method=method)
    try:
        with urllib.request.urlopen(req,timeout=3) as r: return r.status
    except urllib.error.HTTPError as x: return x.code
    except Exception: return 0
auth=code('/api/v1/capabilities')
print(f'AUTH_NO_TOKEN_HTTP={auth}')
rid='mutation-replay-'+uuid.uuid4().hex
h={'Content-Type':'application/json','X-Request-ID':rid}
r1=code('/api/v1/sessions','POST',json.dumps({'handle':'replay_probe_a'}).encode(),h)
r2=code('/api/v1/sessions','POST',json.dumps({'handle':'replay_probe_b'}).encode(),h)
print(f'REPLAY_FIRST_HTTP={r1}'); print(f'REPLAY_SECOND_HTTP={r2}'); print(f'REPLAY_CONTAINMENT_PASS={str(r1==201 and r2==409).lower()}')
PY
printf 'MUTATION_DB_SESSIONS='
docker exec "$DB" psql -U madworld -d madworld -tAc 'select count(*) from player_sessions;'
docker logs "$API" 2>/dev/null | tail -20 >/tmp/$N/api-tail.log || true
docker stats --no-stream --format 'API_CPU={{.CPUPerc}} API_MEM={{.MemUsage}}' "$API"
echo 'MUTATION_ENVIRONMENT=isolated_postgres16_api_container'
echo 'PRODUCTION_DATABASE_TOUCHED=false'
