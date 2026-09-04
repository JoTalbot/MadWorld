#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT=${1:-/opt/madworld}
ROOT="$PROJECT_ROOT/ops/remote-operator"

[[ -d "$PROJECT_ROOT/.git" ]] || { echo "Not a git checkout: $PROJECT_ROOT" >&2; exit 2; }
[[ -f "$PROJECT_ROOT/.github/remote-operator/COMMANDS.txt" ]] || { echo "COMMANDS.txt missing" >&2; exit 2; }
command -v python3 >/dev/null || { echo 'python3 required' >&2; exit 2; }
command -v flock >/dev/null || { echo 'flock required' >&2; exit 2; }

install -d -m 0750 "$PROJECT_ROOT/.github/remote-operator/state" "$PROJECT_ROOT/.github/remote-operator/results"
chmod 0750 "$ROOT"/*.sh

if command -v apt-get >/dev/null 2>&1; then
  if ! command -v inotifywait >/dev/null 2>&1; then
    apt-get update
    DEBIAN_FRONTEND=noninteractive apt-get install -y inotify-tools
  fi
fi

install -m 0644 "$ROOT/madworld-remote-operator.service" /etc/systemd/system/madworld-remote-operator.service
systemctl daemon-reload
systemctl enable --now madworld-remote-operator.service
systemctl --no-pager --full status madworld-remote-operator.service || true

echo 'REMOTE_OPERATOR_INSTALLED'
