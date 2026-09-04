#!/usr/bin/env bash
set -euo pipefail

# Atomic state helper. Usage:
#   state-manager.sh claim <state-file> <command-id> <attempt-id> <executor>
#   state-manager.sh transition <state-file> <expected> <new-state> <metadata-json>

STATE_FILE=${2:-}
ACTION=${1:-}

[[ -n "$STATE_FILE" ]] || { echo 'state file is required' >&2; exit 2; }

mkdir -p "$(dirname "$STATE_FILE")"
lock_file="${STATE_FILE}.lock"

with_lock() {
  exec 9>"$lock_file"
  flock -x 9
  "$@"
}

claim() {
  local command_id=$2 attempt_id=$3 executor=$4 now
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

transition() {
  local expected=$2 new_state=$3 metadata=$4
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
  transition) with_lock transition "$@" ;;
  *) echo 'usage: state-manager.sh {claim|transition} STATE_FILE ...' >&2; exit 2 ;;
esac
