#!/usr/bin/env bash
set -euo pipefail
cd /opt/madworld
N="madworld-full-capacity-v5-$$"; NET="$N-net"; DB="$N-db"; API="$N-api"; WORKER="$N-worker"
cleanup(){ docker rm -f "$API" "$WORKER" "$DB" >/dev/null 2>&1 || true; docker network rm "$NET" >/dev/null 2>&1 || true; rm -rf "/tmp/$N"; }
trap cleanup EXIT
mkdir -p "/tmp/$N"
docker network create "$NET" >/dev/null
docker run -d --name "$DB" --network "$NET" -e POSTGRES_USER=madworld -e POSTGRES_PASSWORD=madworld -e POSTGRES_DB=madworld postgres:16 >/dev/null
for i in $(seq 1 60); do docker exec "$DB" pg_isready -U madworld -d madworld >/dev/null 2>&1 && break; sleep 1; done
docker build -q -f ops/Dockerfile.backend -t "$N-backend" . >/tmp/$N/build.log
docker run --rm --network "$NET" -e PYTHONPATH=/app/backend -e MADWORLD_DATABASE_URL="postgresql://madworld:madworld@$DB:5432/madworld" "$N-backend" python scripts/migrate.py >/tmp/$N/migrate.log
docker run -d --name "$API" --network "$NET" -e PYTHONPATH=/app/backend -e MADWORLD_DATABASE_URL="postgresql://madworld:madworld@$DB:5432/madworld" -e MADWORLD_RATE_LIMIT=10000 "$N-backend" uvicorn app.main:app --host 0.0.0.0 --port 8000 >/tmp/$N/api.log
docker run -d --name "$WORKER" --network "$NET" -e PYTHONPATH=/app/backend -e MADWORLD_DATABASE_URL="postgresql://madworld:madworld@$DB:5432/madworld" -e MADWORLD_WORLD_TICK_SECONDS=5 "$N-backend" python -m scripts.world_tick_worker >/tmp/$N/worker.log
cat >/tmp/$N/client.py <<'PY'
import concurrent.futures,json,time,urllib.error,urllib.request,uuid
base='http://127.0.0.1:8000'
def call(path,method='GET',body=None,headers=None):
 req=urllib.request.Request(base+path,data=body,headers=headers or {},method=method)
 try:
  with urllib.request.urlopen(req,timeout=5) as r:return r.status,r.read()
 except urllib.error.HTTPError as e:return e.code,e.read()
 except Exception:return 0,b''
ready=False
for _ in range(60):
 c,_=call('/health/ready')
 if c==200:ready=True;break
 time.sleep(1)
print(f'API_READY={str(ready).lower()}',flush=True)
if not ready:raise SystemExit(2)
# Authenticated bootstrap idempotency probe in the isolated database.
handle='idempotency_probe_'+uuid.uuid4().hex[:12]
c,data=call('/api/v1/sessions','POST',json.dumps({'handle':handle}).encode(),{'Content-Type':'application/json'})
if c!=201: print(f'IDEMPOTENCY_SESSION_HTTP={c}',flush=True);raise SystemExit(3)
s=json.loads(data); pid=s['player_id']; token=s['token']; auth={'Content-Type':'application/json','Authorization':'Bearer '+token,'Idempotency-Key':'bootstrap-'+uuid.uuid4().hex}
b=json.dumps({'player_id':pid,'character_name':'IdempotencyProbe'}).encode()
i1,d1=call('/api/v1/players/bootstrap','POST',b,auth);i2,d2=call('/api/v1/players/bootstrap','POST',b,auth)
print(f'IDEMPOTENCY_FIRST_HTTP={i1}',flush=True);print(f'IDEMPOTENCY_SECOND_HTTP={i2}',flush=True);print(f'IDEMPOTENCY_REPLAY_PASS={str(i1==201 and i2==201 and d1==d2).lower()}',flush=True)
# Concurrent synthetic-account mutation workload.
end=time.monotonic()+15
def one(_):
 ok=err=0;lat=[]
 while time.monotonic()<end:
  h='load_'+uuid.uuid4().hex[:24];body=json.dumps({'handle':h}).encode();t=time.perf_counter();c,d=call('/api/v1/sessions','POST',body,{'Content-Type':'application/json'});lat.append(time.perf_counter()-t)
  if c==201:
   try:
    p=json.loads(d);valid=bool(p.get('player_id') and p.get('token') and p.get('handle')==h);ok+=valid;err+=not valid
   except Exception:err+=1
  else:err+=1
 return ok,err,lat
suc=err=0;lat=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=20) as ex:
 for a,b,c in ex.map(one,range(20)):suc+=a;err+=b;lat+=c
lat.sort();n=suc+err
def pct(p):return lat[min(len(lat)-1,max(0,int(len(lat)*p)-1))]*1000 if lat else 0
print(f'MUTATION_SUCCESS={suc}',flush=True);print(f'MUTATION_ERRORS={err}',flush=True);print(f'MUTATION_TOTAL={n}',flush=True);print(f'MUTATION_RPS={n/15:.3f}',flush=True);print(f'MUTATION_ERROR_RATE={(err/n if n else 1):.6f}',flush=True);print(f'MUTATION_P50_MS={pct(.5):.3f}',flush=True);print(f'MUTATION_P95_MS={pct(.95):.3f}',flush=True);print(f'MUTATION_P99_MS={pct(.99):.3f}',flush=True)
# Protected boundary and middleware replay containment.
c,_=call('/api/v1/characters','POST',json.dumps({'player_id':str(uuid.uuid4()),'name':'auth_probe'}).encode(),{'Content-Type':'application/json','Idempotency-Key':'auth-'+uuid.uuid4().hex});print(f'AUTH_NO_TOKEN_HTTP={c}',flush=True)
rid='request-replay-'+uuid.uuid4().hex;h={'Content-Type':'application/json','X-Request-ID':rid};r1,_=call('/api/v1/sessions','POST',json.dumps({'handle':'replay_probe_a'}).encode(),h);r2,_=call('/api/v1/sessions','POST',json.dumps({'handle':'replay_probe_b'}).encode(),h);print(f'REPLAY_FIRST_HTTP={r1}',flush=True);print(f'REPLAY_SECOND_HTTP={r2}',flush=True);print(f'REPLAY_CONTAINMENT_PASS={str(r1==201 and r2==409).lower()}',flush=True)
PY
docker cp /tmp/$N/client.py "$API":/tmp/client.py
docker exec "$API" python /tmp/client.py
printf 'MUTATION_DB_SESSIONS=';docker exec "$DB" psql -U madworld -d madworld -tAc 'select count(*) from player_sessions;'
printf 'DB_CONNECTIONS=';docker exec "$DB" psql -U madworld -d madworld -tAc 'select count(*) from pg_stat_activity;'
printf 'WORLD_TICK=';docker exec "$DB" psql -U madworld -d madworld -tAc 'select tick from world_simulation_state where id=1;'
printf 'WORLD_TICK_LOG_TAIL=\n';docker logs --tail 30 "$WORKER" 2>&1 || true
docker stats --no-stream --format 'API_CPU={{.CPUPerc}} API_MEM={{.MemUsage}}' "$API"
docker stats --no-stream --format 'WORKER_CPU={{.CPUPerc}} WORKER_MEM={{.MemUsage}}' "$WORKER"
echo 'CAPACITY_ENVIRONMENT=isolated_postgres16_api_worker_containers'
echo 'PRODUCTION_DATABASE_TOUCHED=false'
