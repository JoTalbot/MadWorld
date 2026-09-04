#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT=${REMOTE_OPERATOR_PROJECT_ROOT:-$(cd "$(dirname "$0")/../.." && pwd)}
STATE_ROOT="$PROJECT_ROOT/.github/remote-operator/state"
COMMAND_ID=${1:?usage: cancel.sh COMMAND_ID}
STATE="$STATE_ROOT/$COMMAND_ID.json"

[[ -f "$STATE" ]] || { echo "command not found: $COMMAND_ID" >&2; exit 1; }

python3 - "$STATE" <<'PY'
import json,sys,tempfile,os
p=sys.argv[1]
with open(p,encoding='utf-8') as f: d=json.load(f)
if d.get('status') != 'RUNNING':
    raise SystemExit(f"cannot cancel state={d.get('status')}")
d['cancel_requested_at']=__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat().replace('+00:00','Z')
fd,tmp=tempfile.mkstemp(dir=os.path.dirname(p),prefix='.cancel.',text=True); os.close(fd)
with open(tmp,'w',encoding='utf-8') as f: json.dump(d,f,indent=2); f.write('\n')
os.replace(tmp,p)
print('CANCEL_REQUESTED')
PY
