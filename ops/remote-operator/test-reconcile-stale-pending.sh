#!/usr/bin/env bash
set -euo pipefail

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
mkdir -p "$TMP/.github/remote-operator/state" "$TMP/.github/remote-operator/REQUESTS"
cat > "$TMP/.github/remote-operator/COMMANDS.txt" <<'EOF'
---
COMMAND_ID: cmd-20200101-000000-legacy
STATUS: PENDING
AGENT: test
TIMEOUT_MINUTES: 1
MODE: sync
COMMAND:
printf legacy
---
---
COMMAND_ID: cmd-20990101-000000-fresh
STATUS: PENDING
AGENT: test
CREATED_AT: 2099-01-01T00:00:00Z
TIMEOUT_MINUTES: 1
MODE: sync
COMMAND:
printf fresh
---
EOF
cp ops/remote-operator/reconcile-stale-pending.sh "$TMP/reconcile.sh"
chmod +x "$TMP/reconcile.sh"
out=$(REMOTE_OPERATOR_PROJECT_ROOT="$TMP" REMOTE_OPERATOR_ROOT="$TMP" "$TMP/reconcile.sh")
grep -q 'ORPHAN_PENDING_WITHOUT_CREATED_AT=cmd-20200101-000000-legacy' <<<"$out"
grep -q 'PENDING_SCANNED=2' <<<"$out"
grep -q 'STALE_PENDING_CANDIDATES=0' <<<"$out"
