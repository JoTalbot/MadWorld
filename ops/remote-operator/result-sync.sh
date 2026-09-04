#!/usr/bin/env bash
set -euo pipefail

# Result synchronization is intentionally a separate concern from command execution.
# Configure the repository push mechanism on the server without placing credentials in Git.
# This helper stages only remote-operator state/results and creates a local commit.
# The caller must provide an authenticated Git transport (credential helper/SSH agent).

PROJECT_ROOT=${REMOTE_OPERATOR_PROJECT_ROOT:-/opt/madworld}
cd "$PROJECT_ROOT"

git add .github/remote-operator/state .github/remote-operator/results
if git diff --cached --quiet; then
  exit 0
fi

git -c user.name='MadWorld Remote Operator' \
    -c user.email='remote-operator@localhost' \
    commit -m 'chore(remote-operator): record command execution result'

git push origin HEAD:main
