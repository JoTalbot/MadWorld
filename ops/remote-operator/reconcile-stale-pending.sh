#!/usr/bin/env bash
set -euo pipefail

ROOT=${REMOTE_OPERATOR_ROOT:-$(cd "$(dirname "$0")" && pwd)}
PROJECT_ROOT=${REMOTE_OPERATOR_PROJECT_ROOT:-$(cd "$ROOT/../.." && pwd)}
QUEUE="$PROJECT_ROOT/.github/remote-operator/COMMANDS.txt"
STATE_ROOT="$PROJECT_ROOT/.github/remote-operator/state"
MAX_AGE_SECONDS=${REMOTE_OPERATOR_PENDING_MAX_AGE_SECONDS:-86400}

[[ -f "$QUEUE" ]] || { echo 'QUEUE_NOT_FOUND'; exit 1; }
mkdir -p "$STATE_ROOT"

python3 - "$QUEUE" "$STATE_ROOT" "$MAX_AGE_SECONDS" <<'PY'
import json, os, re, sys, time
from datetime import datetime
queue, state_root, max_age = sys.argv[1], sys.argv[2], int(sys.argv[3])
text = open(queue, encoding='utf-8').read()
now = time.time()
scanned = orphaned = stale = 0
for block in re.split(r'(?m)^---\s*$', text):
    m = re.search(r'(?m)^COMMAND_ID:\s*(\S+)', block)
    s = re.search(r'(?m)^STATUS:\s*(\S+)', block)
    if not m or not s or s.group(1) != 'PENDING':
        continue
    scanned += 1
    cid = m.group(1)
    state_path = os.path.join(state_root, cid + '.json')
    if os.path.exists(state_path):
        try:
            state = json.load(open(state_path, encoding='utf-8'))
            if state.get('status') in {'CLAIMED','RUNNING','DONE','FAILED','TIMEOUT','CANCELLED','INTERRUPTED','INVALID'}:
                continue
        except Exception:
            continue
    orphaned += 1
    cm = re.search(r'(?m)^CREATED_AT:\s*(\S+)', block)
    if not cm:
        print(f'ORPHAN_PENDING_WITHOUT_CREATED_AT={cid}')
        continue
    try:
        created = datetime.fromisoformat(cm.group(1).replace('Z','+00:00')).timestamp()
    except Exception:
        print(f'INVALID_CREATED_AT={cid}')
        continue
    age = now - created
    if age >= max_age:
        stale += 1
        print(f'STALE_PENDING={cid} AGE_SECONDS={int(age)}')

print(f'PENDING_SCANNED={scanned}')
print(f'ORPHAN_PENDING={orphaned}')
print(f'STALE_PENDING_CANDIDATES={stale}')
print('RECONCILIATION_ONLY=true')
print('QUEUE_NOT_MODIFIED=true')
PY
