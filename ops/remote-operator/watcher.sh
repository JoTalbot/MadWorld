#!/usr/bin/env bash
set -euo pipefail

ROOT=${REMOTE_OPERATOR_ROOT:-$(cd "$(dirname "$0")" && pwd)}
PROJECT_ROOT=${REMOTE_OPERATOR_PROJECT_ROOT:-$(cd "$ROOT/../.." && pwd)}
QUEUE="$PROJECT_ROOT/.github/remote-operator/COMMANDS.txt"
REQUEST_DIR="$PROJECT_ROOT/.github/remote-operator/REQUESTS"
EXECUTOR="$ROOT/executor.sh"
DEBOUNCE_SECONDS=${REMOTE_OPERATOR_DEBOUNCE_SECONDS:-1}
RESCAN_SECONDS=${REMOTE_OPERATOR_RESCAN_SECONDS:-30}

run_once() {
  "$EXECUTOR" || logger -t madworld-remote-operator 'executor returned non-zero'
}

run_once

if command -v inotifywait >/dev/null 2>&1; then
  while true; do
    inotifywait -q -e close_write,move,create,delete "$QUEUE" "$REQUEST_DIR" >/dev/null 2>&1 || true
    sleep "$DEBOUNCE_SECONDS"
    run_once
  done
else
  while true; do
    sleep "$RESCAN_SECONDS"
    run_once
  done
fi
