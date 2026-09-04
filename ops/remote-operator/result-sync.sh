#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT=${REMOTE_OPERATOR_PROJECT_ROOT:-/opt/madworld}
STATE_ROOT="$PROJECT_ROOT/.github/remote-operator/state"
RESULT_ROOT="$PROJECT_ROOT/.github/remote-operator/results"
LOCK_FILE="$STATE_ROOT/result-sync.lock"
RESULT_BRANCH=${REMOTE_OPERATOR_RESULT_BRANCH:-remote-operator-results}
MAX_ATTEMPTS=${REMOTE_OPERATOR_SYNC_MAX_ATTEMPTS:-3}

mkdir -p "$STATE_ROOT" "$RESULT_ROOT"

exec 9>"$LOCK_FILE"
flock -n 9 || exit 0

TMP_ROOT=$(mktemp -d /tmp/madworld-result-sync.XXXXXX)
WORKTREE="$TMP_ROOT/worktree"

cleanup() {
    cd "$PROJECT_ROOT" 2>/dev/null || true
    git worktree remove --force "$WORKTREE" >/dev/null 2>&1 || true
    git worktree prune >/dev/null 2>&1 || true
    rm -rf -- "$TMP_ROOT"
}
trap cleanup EXIT

cd "$PROJECT_ROOT"
git fetch origin main
git fetch origin "$RESULT_BRANCH" >/dev/null 2>&1 || true

for attempt in $(seq 1 "$MAX_ATTEMPTS"); do
    cd "$PROJECT_ROOT"
    git worktree prune >/dev/null 2>&1 || true
    rm -rf -- "$WORKTREE"

    if ! git show-ref --verify --quiet "refs/remotes/origin/$RESULT_BRANCH"; then
        git fetch origin "$RESULT_BRANCH" >/dev/null 2>&1 || true
    fi

    if git show-ref --verify --quiet "refs/remotes/origin/$RESULT_BRANCH"; then
        git worktree add --detach "$WORKTREE" "origin/$RESULT_BRANCH" >/dev/null
    else
        git worktree add --detach "$WORKTREE" origin/main >/dev/null
    fi

    python3 - "$PROJECT_ROOT" "$WORKTREE" <<'PY'
import shutil
import sys
from pathlib import Path

src_root = Path(sys.argv[1]) / ".github" / "remote-operator"
dst_root = Path(sys.argv[2]) / ".github" / "remote-operator"

for name in ("state", "results"):
    src = src_root / name
    dst = dst_root / name
    dst.mkdir(parents=True, exist_ok=True)

    if not src.exists():
        continue

    for path in src.rglob("*"):
        if not path.is_file() or path.name.endswith(".lock"):
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

    git -c user.name="MadWorld Remote Operator" \
        -c user.email="remote-operator@localhost" \
        commit -m "chore(remote-operator): record command execution result" >/dev/null

    if git push origin HEAD:"$RESULT_BRANCH"; then
        exit 0
    fi

    cd "$PROJECT_ROOT"
    git worktree prune >/dev/null 2>&1 || true
    git fetch origin "$RESULT_BRANCH" >/dev/null 2>&1 || true
    sleep "$attempt"
done

echo "result sync failed after retries" >&2
exit 1
