#!/usr/bin/env bash
set -euo pipefail

# Atomic state helper. Usage:
#   state-manager.sh claim <state-file> <command-id> <attempt-id> <executor>
#   state-manager.sh transition <state-file> <expected> <new-state> <metadata-json>
#   state-manager.sh request-cancel <state-file>

ACTION=${1:-}
STATE_FILE=${2:-}

[[ -n "$STATE_FILE" ]] || { echo 'state file is required' >&2; exit 2; }

mkdir -p "$(dirname "$STATE_FILE")"
lock_file="${STATE_FILE}.lock"

with_lock() {
  exec 9>"$lock_file"
  flock -x 9
  "$@"
}

claim() {
  local command_id=$3 attempt_id=$4 executor=$5 now
  [[ -n "$command_id" && -n "$attempt_id" && -n "$executor" ]] || {
    echo 'claim requires state-file command-id attempt-id executor' >&2
    return 2
  }
  now=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  if [[ -f "$STATE_FILE" ]]; then
    local state
    state=$(python3 - "$STATE_FILE" <<'PY'
import json,sys
try:
    print(json.load(open(sys.argv[1], encoding='utf-8')).get('status','UNKNOWN'))
except Exception:
    print('UNKNOWN')
PY
)
    [[ "$state" == PENDING ]] || { echo "NOT_CLAIMABLE:$state"; return 1; }
  fi
  local tmp="${STATE_FILE}.tmp.$$"
  python3 - "$tmp" "$command_id" "$attempt_id" "$executor" "$now" <<'PY'
import json,sys
p,c,a,e,n=sys.argv[1:]
json.dump({'command_id':c,'attempt_id':a,'status':'CLAIMED','executor':e,'claimed_at':n},open(p,'w',encoding='utf-8'),indent=2)
PY
  mv -f -- "$tmp" "$STATE_FILE"
}

request_cancel() {
  local now
  [[ -f "$STATE_FILE" ]] || { echo 'STATE_NOT_FOUND' >&2; return 1; }
  now=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  python3 - "$STATE_FILE" "$now" <<'PY'
import json,sys,os,tempfile
p,now=sys.argv[1:]
with open(p,encoding='utf-8') as f: data=json.load(f)
state=data.get('status')
if state != 'RUNNING': raise SystemExit(f"cannot cancel state={state}")
data['cancel_requested_at']=now
fd,tmp=tempfile.mkstemp(prefix='.state.',dir=os.path.dirname(p),text=True)
os.close(fd)
with open(tmp,'w',encoding='utf-8') as f: json.dump(data,f,indent=2); f.write('\n')
os.replace(tmp,p)
PY
  echo 'CANCEL_REQUESTED'
}

transition() {
  local expected=$3 new_state=$4 metadata=$5
  [[ -n "$expected" && -n "$new_state" ]] || {
    echo 'transition requires state-file expected new-state metadata-json' >&2
    return 2
  }
  python3 - "$STATE_FILE" "$expected" "$new_state" "$metadata" <<'PY'
import json,sys,os,tempfile
p,expected,new_state,metadata=sys.argv[1:]
if not os.path.exists(p): raise SystemExit('STATE_NOT_FOUND')
with open(p,encoding='utf-8') as f: data=json.load(f)
if data.get('status') != expected: raise SystemExit(f"INVALID_TRANSITION:{data.get('status')}->{new_state}")
extra=json.loads(metadata) if metadata else {}
data.update(extra,status=new_state)
fd,tmp=tempfile.mkstemp(prefix='.state.',dir=os.path.dirname(p),text=True)
os.close(fd)
with open(tmp,'w',encoding='utf-8') as f: json.dump(data,f,indent=2); f.write('\n')
os.replace(tmp,p)
PY
}

case "$ACTION" in
  claim) with_lock claim "$@" ;;
  request-cancel) with_lock request_cancel "$@" ;;
  transition) with_lock transition "$@" ;;
  *) echo 'usage: state-manager.sh {claim|request-cancel|transition} STATE_FILE ...' >&2; exit 2 ;;
esac
