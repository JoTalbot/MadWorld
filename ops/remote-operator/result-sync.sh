#!/usr/bin/env bash
set -euo pipefail

# Publish state/results without mutating the deployment worktree.
# The main checkout may contain local application changes or be used by deploy.
PROJECT_ROOT=${REMOTE_OPERATOR_PROJECT_ROOT:-/opt/madworld}
STATE_ROOT="$PROJECT_ROOT/.github/remote-operator/state"
RESULT_ROOT="$PROJECT_ROOT/.github/remote-operator/results"
LOCK_FILE="$STATE_ROOT/result-sync.lock"
MAX_ATTEMPTS=${REMOTE_OPERATOR_SYNC_MAX_ATTEMPTS:-3}

mkdir -p "$STATE_ROOT" "$RESULT_ROOT"
exec 9>"$LOCK_FILE"
flock -n 9 || exit 0

TMP_ROOT=$(mktemp -d /tmp/madworld-result-sync.XXXXXX)
WORKTREE="$TMP_ROOT/worktree"
cleanup() {
  git -C "$PROJECT_ROOT" worktree remove --force "$WORKTREE" >/dev/null 2>&1 || true
  rm -rf -- "$TMP_ROOT"
}
trap cleanup EXIT

cd "$PROJECT_ROOT"
git fetch origin main

for attempt in $(seq 1 "$MAX_ATTEMPTS"); do
  rm -rf -- "$WORKTREE"
  git worktree add --detach "$WORKTREE" origin/main >/dev/null

  python3 - "$PROJECT_ROOT" "$WORKTREE" <<'PY'
import os, shutil, sys
from pathlib import Path
src_root = Path(sys.argv[1]) / '.github' / 'remote-operator'
dst_root = Path(sys.argv[2]) / '.github' / 'remote-operator'
for name in ('state', 'results'):
    src = src_root / name
    dst = dst_root / name
    dst.mkdir(parents=True, exist_ok=True)
    for path in src.rglob('*'):
        if not path.is_file() or path.name.endswith('.lock'):
            continue
        rel = path.relative_to(src)
        target = dst / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
PY

  cd "$WORKTREE"
  git add .github/remote-operator/state .github/remote-operator/results
  if git diff --cached --quiet; then
    exit 0
  fi

  git -c user.name='MadWorld Remote Operator' \
      -c user.email='remote-operator@localhost' \
      commit -m 'chore(remote-operator): record command execution result' >/dev/null

  if git push origin HEAD:main; then
    exit 0
  fi

  cd "$PROJECT_ROOT"
  git fetch origin main
  sleep "$attempt"
done

echo 'result sync failed after retries' >&2
exit 1
