#!/usr/bin/env bash
set -euo pipefail

RESULT_ROOT=${1:?result root required}
COMMAND_ID=${2:?command id required}
ATTEMPT_ID=${3:?attempt id required}
STATUS=${4:?status required}
EXIT_CODE=${5:?exit code required}
STARTED_AT=${6:?started at required}
FINISHED_AT=${7:?finished at required}
DURATION_SECONDS=${8:?duration required}
COMMAND_FILE=${9:?command file required}
STDOUT_FILE=${10:?stdout file required}
STDERR_FILE=${11:?stderr file required}
EXECUTOR=${12:?executor required}

out="$RESULT_ROOT/$COMMAND_ID"
mkdir -p "$out"
cp -- "$STDOUT_FILE" "$out/stdout.log"
cp -- "$STDERR_FILE" "$out/stderr.log"

python3 - "$out/result.json" "$COMMAND_ID" "$ATTEMPT_ID" "$STATUS" "$EXIT_CODE" "$STARTED_AT" "$FINISHED_AT" "$DURATION_SECONDS" "$EXECUTOR" "$COMMAND_FILE" <<'PY'
import json,sys
out,c,a,s,rc,started,finished,duration,executor,command_file=sys.argv[1:]
with open(command_file,encoding='utf-8') as f: command=f.read()
json.dump({'command_id':c,'attempt_id':a,'status':s,'exit_code':int(rc),'started_at':started,'finished_at':finished,'duration_seconds':int(duration),'executor':executor,'command':command},open(out,'w',encoding='utf-8'),indent=2)
with open(out,'a',encoding='utf-8') as f: f.write('\n')
PY

{
  echo '# Remote Command Result'
  echo
  echo "- **Command ID:** \`$COMMAND_ID\`"
  echo "- **Attempt ID:** \`$ATTEMPT_ID\`"
  echo "- **Status:** \`$STATUS\`"
  echo "- **Exit code:** \`$EXIT_CODE\`"
  echo "- **Executor:** \`$EXECUTOR\`"
  echo "- **Started:** \`$STARTED_AT\`"
  echo "- **Finished:** \`$FINISHED_AT\`"
  echo "- **Duration:** \`${DURATION_SECONDS}s\`"
  echo
  echo '## Command'
  echo '```bash'
  cat -- "$COMMAND_FILE"
  echo '```'
  echo
  echo '## STDOUT'
  echo '```text'
  cat -- "$STDOUT_FILE"
  echo '```'
  echo
  echo '## STDERR'
  echo '```text'
  cat -- "$STDERR_FILE"
  echo '```'
} > "$out/result.md"
