#!/usr/bin/env bash
set -euo pipefail

ROOT=${REMOTE_OPERATOR_ROOT:-$(cd "$(dirname "$0")" && pwd)}
PROJECT_ROOT=${REMOTE_OPERATOR_PROJECT_ROOT:-$(cd "$ROOT/../.." && pwd)}
QUEUE="$PROJECT_ROOT/.github/remote-operator/COMMANDS.txt"
STATE_ROOT="$PROJECT_ROOT/.github/remote-operator/state"
RESULT_ROOT="$PROJECT_ROOT/.github/remote-operator/results"
MAX_CONCURRENCY=${REMOTE_OPERATOR_MAX_CONCURRENCY:-4}
DEFAULT_TIMEOUT=${REMOTE_OPERATOR_DEFAULT_TIMEOUT:-30}
GRACE_SECONDS=${REMOTE_OPERATOR_GRACE_SECONDS:-15}
EXECUTOR_ID=${REMOTE_OPERATOR_EXECUTOR_ID:-$(hostname -s)}

mkdir -p "$STATE_ROOT" "$RESULT_ROOT"
[[ -f "$QUEUE" ]] || exit 0

# Queue parser emits one base64-encoded command per record, so multiline Bash
# commands cannot corrupt the record stream. Documentation/template IDs are
# ignored. Claiming is delegated to state-manager.sh, which owns the lock.
python3 - "$QUEUE" <<'PY' | while IFS=$'\t' read -r id timeout mode encoded; do
import base64,re,sys
p=sys.argv[1]
s=open(p,encoding='utf-8').read()
for block in re.split(r'(?m)^---\s*$',s):
    m=re.search(r'(?m)^COMMAND_ID:\s*(\S+)',block)
    st=re.search(r'(?m)^STATUS:\s*(\S+)',block)
    if not m or not st or st.group(1)!='PENDING':
        continue
    cid=m.group(1)
    if not re.fullmatch(r'cmd-[0-9]{8}-[0-9]{6}-[A-Za-z0-9._-]+',cid):
        continue
    tm=re.search(r'(?m)^TIMEOUT_MINUTES:\s*(\d+)',block)
    md=re.search(r'(?m)^MODE:\s*(\S+)',block)
    cm=re.search(r'(?ms)^COMMAND:\s*\n(.*?)(?:\n---\s*$|\Z)',block)
    if not cm:
        continue
    command=cm.group(1).strip('\n')
    encoded=base64.b64encode(command.encode()).decode()
    print(cid,tm.group(1) if tm else '30',md.group(1) if md else 'sync',encoded,sep='\t')
PY
  command=$(printf '%s' "$encoded" | base64 -d)
  state="$STATE_ROOT/$id.json"
  attempt="${id}-attempt-$(date -u +%Y%m%dT%H%M%SZ)-$$"

  if ! "$ROOT/state-manager.sh" claim "$state" "$id" "$attempt" "$EXECUTOR_ID" >/dev/null 2>&1; then
    continue
  fi

  work="$RESULT_ROOT/$id/$attempt"
  mkdir -p "$work"
  printf '%s\n' "$command" > "$work/command.sh"
  chmod 700 "$work/command.sh"
  started=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  start_epoch=$(date +%s)
  "$ROOT/state-manager.sh" transition "$state" CLAIMED RUNNING "{\"started_at\":\"$started\",\"pid\":$$,\"timeout_minutes\":$timeout,\"executor\":\"$EXECUTOR_ID\"}" >/dev/null

  set +e
  setsid bash "$work/command.sh" >"$work/stdout.log" 2>"$work/stderr.log" &
  pid=$!
  deadline=$((start_epoch + timeout*60))
  rc=0
  status=RUNNING
  timed_out=0
  while kill -0 "$pid" 2>/dev/null; do
    if (( $(date +%s) >= deadline )); then
      timed_out=1
      rc=124
      status=TIMEOUT
      printf '%s\n' "TIMEOUT after ${timeout} minutes" >> "$work/stderr.log"
      kill -TERM -- "-$pid" 2>/dev/null || kill -TERM "$pid" 2>/dev/null || true
      sleep "$GRACE_SECONDS"
      kill -0 "$pid" 2>/dev/null && { kill -KILL -- "-$pid" 2>/dev/null || kill -KILL "$pid" 2>/dev/null || true; }
      break
    fi
    sleep 1
  done
  wait "$pid" 2>/dev/null
  observed=$?
  set -e

  finished=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  duration=$(( $(date +%s)-start_epoch ))
  if (( timed_out == 0 )); then
    rc=$observed
    if [[ "$rc" -eq 0 ]]; then
      status=DONE
    else
      status=FAILED
    fi
  fi

  "$ROOT/result-manager.sh" "$RESULT_ROOT" "$id" "$attempt" "$status" "$rc" "$started" "$finished" "$duration" "$work/command.sh" "$work/stdout.log" "$work/stderr.log" "$EXECUTOR_ID"
  "$ROOT/state-manager.sh" transition "$state" RUNNING "$status" "{\"finished_at\":\"$finished\",\"duration_seconds\":$duration,\"exit_code\":$rc,\"result_path\":\".github/remote-operator/results/$id/result.md\"}" >/dev/null
  rm -rf "$work"
done
