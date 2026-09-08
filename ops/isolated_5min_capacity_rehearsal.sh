#!/usr/bin/env bash
set -euo pipefail
cd /opt/madworld
N="madworld-5min-capacity-$$"; NET="$N-net"; DB="$N-db"; API="$N-api"; WORKER="$N-worker"
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
DURATION=300
end=time.monotonic()+DURATION
start=time.monotonic(); total=errors=0; lats=[]; statuses={}
from threading import Lock
lock=Lock(); inflight=0; max_inflight=0

def one(_):
 global inflight,max_inflight
 local_ok=local_err=0; local_lat=[]; local_status={}
 while time.monotonic()<end:
  h='load5_'+uuid.uuid4().hex[:24]; body=json.dumps({'handle':h}).encode(); t=time.perf_counter()
  with lock:
   inflight+=1; max_inflight=max(max_inflight,inflight)
  c,d=call('/api/v1/sessions','POST',body,{'Content-Type':'application/json'})
  with lock: inflight-=1
  dt=time.perf_counter()-t; local_lat.append(dt); local_status[c]=local_status.get(c,0)+1
  if c==201:
   try:
    p=json.loads(d); valid=bool(p.get('player_id') and p.get('token') and p.get('handle')==h)
    if valid: local_ok+=1
    else: local_err+=1
   except Exception: local_err+=1
  else: local_err+=1
 return local_ok,local_err,local_lat,local_status
# Acceptance requires >=120 RPS. The previous 20-worker client capped throughput at ~94 RPS
# simply because measured latency was ~0.29-0.31s. Use 40 workers so the harness can
# exercise the server above the acceptance threshold without changing production limits.
CLIENT_WORKERS=40
with concurrent.futures.ThreadPoolExecutor(max_workers=CLIENT_WORKERS) as ex:
 for ok,err,lat,st in ex.map(one,range(CLIENT_WORKERS)):
  total+=ok+err; errors+=err; lats+=lat
  for k,v in st.items(): statuses[k]=statuses.get(k,0)+v
elapsed=time.monotonic()-start
lats.sort()
def pct(p): return (lats[min(len(lats)-1,max(0,int(len(lats)*p)-1))]*1000) if lats else 0
print(f'CAPACITY_DURATION_SECONDS={elapsed:.3f}',flush=True)
print(f'CAPACITY_REQUESTS={total}',flush=True);print(f'CAPACITY_SUCCESS={total-errors}',flush=True);print(f'CAPACITY_ERRORS={errors}',flush=True)
print(f'CAPACITY_RPS={total/elapsed:.3f}',flush=True);print(f'CAPACITY_ERROR_RATE={(errors/total if total else 1):.6f}',flush=True)
print(f'CAPACITY_P50_MS={pct(.50):.3f}',flush=True);print(f'CAPACITY_P95_MS={pct(.95):.3f}',flush=True);print(f'CAPACITY_P99_MS={pct(.99):.3f}',flush=True)
print('HTTP_STATUS_DISTRIBUTION='+json.dumps(statuses,sort_keys=True),flush=True);print(f'CLIENT_MAX_INFLIGHT={max_inflight}',flush=True)
PY
# Monitor durable outbox queue and DB connections during load, then continue for a
# dedicated recovery window. World-tick health is measured from worker lag_ms logs,
# not from a 5-second sampling interval that cannot prove a <=1s lag requirement.
(
  load_end=$(( $(date +%s) + 300 )); recovery_end=$(( load_end + 60 )); i=0; max_queue=0; min_queue=999999999
  while [ "$(date +%s)" -lt "$recovery_end" ]; do
    ts=$(date +%s); q=$(docker exec "$DB" psql -U madworld -d madworld -tAc "select count(*) from outbox_events where published_at is null;" 2>/dev/null || echo 0); c=$(docker exec "$DB" psql -U madworld -d madworld -tAc "select count(*) from pg_stat_activity;" 2>/dev/null || echo 0); tick=$(docker exec "$DB" psql -U madworld -d madworld -tAc "select tick from world_simulation_state where id=1;" 2>/dev/null || echo -1)
    q=${q//[[:space:]]/}; c=${c//[[:space:]]/}; tick=${tick//[[:space:]]/}; [ -z "$q" ] && q=0; [ -z "$c" ] && c=0; [ -z "$tick" ] && tick=-1
    [ "$q" -gt "$max_queue" ] 2>/dev/null && max_queue=$q; [ "$q" -lt "$min_queue" ] 2>/dev/null && min_queue=$q
    printf 'METRIC t=%s queue_depth=%s db_connections=%s world_tick=%s phase=%s\n' "$i" "$q" "$c" "$tick" "$( [ "$(date +%s)" -lt "$load_end" ] && echo load || echo recovery )" | tee -a "/tmp/$N/metrics.log" >/dev/null
    i=$((i+1)); sleep 5
  done
  echo "MAX_QUEUE_DEPTH=$max_queue" >> "/tmp/$N/metrics.log"; echo "MIN_QUEUE_DEPTH=$min_queue" >> "/tmp/$N/metrics.log"
  grep '^METRIC ' /tmp/$N/metrics.log | awk -F'queue_depth=' 'NR==1{split($2,a," "); start=a[1]} END{split($2,a," "); end=a[1]; printf "QUEUE_DEPTH_START=%s\nQUEUE_DEPTH_RECOVERY_END=%s\nQUEUE_RECOVERY_PASS=%s\n", start,end,(end<=start ? "true":"false")}' >> /tmp/$N/metrics.log
) &
MON=$!
docker cp /tmp/$N/client.py "$API":/tmp/client.py
docker exec "$API" python /tmp/client.py
wait "$MON" || true
printf 'QUEUE_DEPTH_START='; grep 'QUEUE_DEPTH_START=' /tmp/$N/metrics.log | tail -1 | cut -d= -f2
printf 'QUEUE_DEPTH_MAX='; grep 'MAX_QUEUE_DEPTH=' /tmp/$N/metrics.log | tail -1 | cut -d= -f2
printf 'QUEUE_DEPTH_MIN='; grep 'MIN_QUEUE_DEPTH=' /tmp/$N/metrics.log | tail -1 | cut -d= -f2
printf 'QUEUE_DEPTH_END='; grep 'QUEUE_DEPTH_RECOVERY_END=' /tmp/$N/metrics.log | tail -1 | cut -d= -f2
printf 'QUEUE_RECOVERY_PASS='; grep 'QUEUE_RECOVERY_PASS=' /tmp/$N/metrics.log | tail -1 | cut -d= -f2
printf 'DB_CONNECTIONS_FINAL='; docker exec "$DB" psql -U madworld -d madworld -tAc 'select count(*) from pg_stat_activity;'
printf 'WORLD_TICK_FINAL='; docker exec "$DB" psql -U madworld -d madworld -tAc 'select tick from world_simulation_state where id=1;'
printf 'WORLD_TICK_MAX_LAG_MS='; docker logs "$WORKER" 2>&1 | sed -n 's/.*lag_ms=\([0-9][0-9]*\).*/\1/p' | sort -n | tail -1
printf 'WORLD_TICK_LOG_TAIL=\n'; docker logs --tail 30 "$WORKER" 2>&1 || true
docker stats --no-stream --format 'API_CPU={{.CPUPerc}} API_MEM={{.MemUsage}}' "$API"
docker stats --no-stream --format 'WORKER_CPU={{.CPUPerc}} WORKER_MEM={{.MemUsage}}' "$WORKER"
echo 'CAPACITY_ENVIRONMENT=isolated_postgres16_api_worker_containers'
echo 'PRODUCTION_DATABASE_TOUCHED=false'
