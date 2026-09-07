#!/usr/bin/env bash
set -euo pipefail
cd /opt/madworld
N="madworld-mutation-v4-$$"; NET="$N-net"; DB="$N-db"; API="$N-api"
cleanup(){ docker rm -f "$API" "$DB" >/dev/null 2>&1 || true; docker network rm "$NET" >/dev/null 2>&1 || true; rm -rf "/tmp/$N"; }
trap cleanup EXIT
mkdir -p "/tmp/$N"
docker network create "$NET" >/dev/null
docker run -d --name "$DB" --network "$NET" -e POSTGRES_USER=madworld -e POSTGRES_PASSWORD=madworld -e POSTGRES_DB=madworld postgres:16 >/dev/null
for i in $(seq 1 60); do docker exec "$DB" pg_isready -U madworld -d madworld >/dev/null 2>&1 && break; sleep 1; done
docker build -q -f ops/Dockerfile.backend -t "$N-backend" . >/tmp/$N/build.log
docker run --rm --network "$NET" -e PYTHONPATH=/app/backend -e MADWORLD_DATABASE_URL="postgresql://madworld:madworld@$DB:5432/madworld" "$N-backend" python scripts/migrate.py >/tmp/$N/migrate.log
docker run -d --name "$API" --network "$NET" -e PYTHONPATH=/app/backend -e MADWORLD_DATABASE_URL="postgresql://madworld:madworld@$DB:5432/madworld" -e MADWORLD_RATE_LIMIT=10000 "$N-backend" uvicorn app.main:app --host 0.0.0.0 --port 8000 >/tmp/$N/api.log
cat > /tmp/$N/client.py <<'PY'
import concurrent.futures,json,sys,time,urllib.error,urllib.request,uuid
base='http://127.0.0.1:8000'
def call(path,method='GET',body=None,headers=None):
    req=urllib.request.Request(base+path,data=body,headers=headers or {},method=method)
    try:
        with urllib.request.urlopen(req,timeout=4) as r:return r.status,r.read()
    except urllib.error.HTTPError as e:return e.code,e.read()
    except Exception:return 0,b''
ready=False
for _ in range(60):
    code,_=call('/health/ready')
    if code==200:ready=True;break
    time.sleep(1)
print(f'API_READY={str(ready).lower()}',flush=True)
if not ready: sys.exit(2)
end=time.monotonic()+15
def one(_):
    ok=err=0; lat=[]
    while time.monotonic()<end:
        h='load_'+uuid.uuid4().hex[:24]; body=json.dumps({'handle':h}).encode(); t=time.perf_counter()
        code,data=call('/api/v1/sessions','POST',body,{'Content-Type':'application/json'}); lat.append(time.perf_counter()-t)
        if code==201:
            try:
                p=json.loads(data); ok+=int(bool(p.get('player_id') and p.get('token') and p.get('handle')==h))
                err+=int(not bool(p.get('player_id') and p.get('token') and p.get('handle')==h))
            except Exception:err+=1
        else:err+=1
    return ok,err,lat
s=e=0; ls=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=20) as ex:
    for ok,err,lat in ex.map(one,range(20)):s+=ok;e+=err;ls.extend(lat)
t=s+e; ls.sort()
def pct(p): return ls[min(len(ls)-1,max(0,int(len(ls)*p)-1))]*1000 if ls else 0
print(f'MUTATION_SUCCESS={s}',flush=True);print(f'MUTATION_ERRORS={e}',flush=True);print(f'MUTATION_TOTAL={t}',flush=True);print(f'MUTATION_RPS={t/15:.3f}',flush=True);print(f'MUTATION_ERROR_RATE={(e/t if t else 1):.6f}',flush=True);print(f'MUTATION_P50_MS={pct(.50):.3f}',flush=True);print(f'MUTATION_P95_MS={pct(.95):.3f}',flush=True);print(f'MUTATION_P99_MS={pct(.99):.3f}',flush=True)
code,_=call('/api/v1/capabilities');print(f'AUTH_NO_TOKEN_HTTP={code}',flush=True)
rid='mutation-replay-'+uuid.uuid4().hex; h={'Content-Type':'application/json','X-Request-ID':rid}
r1,_=call('/api/v1/sessions','POST',json.dumps({'handle':'replay_probe_a'}).encode(),h);r2,_=call('/api/v1/sessions','POST',json.dumps({'handle':'replay_probe_b'}).encode(),h)
print(f'REPLAY_FIRST_HTTP={r1}',flush=True);print(f'REPLAY_SECOND_HTTP={r2}',flush=True);print(f'REPLAY_CONTAINMENT_PASS={str(r1==201 and r2==409).lower()}',flush=True)
PY
printf 'MUTATION_WORKLOAD=POST /api/v1/sessions, 20 concurrent clients, 15s bounded synthetic-account writes\n'
docker cp /tmp/$N/client.py "$API":/tmp/client.py
docker exec "$API" python /tmp/client.py
printf 'MUTATION_DB_SESSIONS='
docker exec "$DB" psql -U madworld -d madworld -tAc 'select count(*) from player_sessions;'
echo 'MUTATION_ENVIRONMENT=isolated_postgres16_api_container'
echo 'PRODUCTION_DATABASE_TOUCHED=false'
