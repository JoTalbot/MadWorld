#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT=${REMOTE_OPERATOR_PROJECT_ROOT:-$(cd "$(dirname "$0")/../.." && pwd)}
STATE_ROOT="$PROJECT_ROOT/.github/remote-operator/state"
COMMAND_ID=${1:?usage: cancel.sh COMMAND_ID}
STATE="$STATE_ROOT/$COMMAND_ID.json"

[[ -f "$STATE" ]] || { echo "command not found: $COMMAND_ID" >&2; exit 1; }

"$(cd "$(dirname "$0")" && pwd)/state-manager.sh" request-cancel "$STATE"
