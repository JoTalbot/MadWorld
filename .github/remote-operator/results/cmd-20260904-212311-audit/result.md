# Remote Command Result

- **Command ID:** `cmd-20260904-212311-audit`
- **Attempt ID:** `cmd-20260904-212311-audit-attempt-20260904T212312Z-675382`
- **Status:** `FAILED`
- **Exit code:** `1`
- **Executor:** `arm-server-01`
- **Started:** `2026-09-04T21:23:12Z`
- **Finished:** `2026-09-04T21:23:13Z`
- **Duration:** `1s`

## Command
```bash
  cd /opt/madworld
  set -e
  echo "=== MADWORLD PRODUCTION AUDIT ==="
  date -u
  echo "=== GIT ==="
  git fetch origin main
  echo "HEAD=$(git rev-parse HEAD)"
  echo "ORIGIN=$(git rev-parse origin/main)"
  test "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)"
  echo "GIT_SYNC=PASS"
  echo "=== SERVICE ==="
  systemctl is-active madworld-remote-operator.service
  echo "=== TIMER ==="
  systemctl is-active madworld-remote-operator-sync.timer
  echo "=== EXECUTOR ==="
  pgrep -af '/opt/madworld/ops/remote-operator/executor.sh' || echo "EXECUTOR_IDLE"
  echo "=== LOCK ==="
  flock -n .github/remote-operator/state/executor.lock -c 'echo LOCK=FREE'
  echo "=== QUEUE ==="
  echo "COMMANDS=$(grep -c "^COMMAND_ID:" .github/remote-operator/COMMANDS.txt || true)"
  echo "PENDING=$(grep -c "^STATUS: PENDING$" .github/remote-operator/COMMANDS.txt || true)"
  echo "=== SYNTAX ==="
  for f in ops/remote-operator/*.sh; do bash -n "$f"; done
  echo "SHELL_SYNTAX=PASS"
  echo "=== DISK ==="
  df -h /opt/madworld
  echo "=== MEMORY ==="
  free -h
  echo "=== FAILED ==="
  systemctl --failed --no-legend || true
  echo "=== AUDIT COMPLETE ==="
```

## STDOUT
```text
=== MADWORLD PRODUCTION AUDIT ===
Fri Sep  4 21:23:12 UTC 2026
=== GIT ===
HEAD=8398df430db68cfd11b8fd3be2f6fe1aea81f36a
ORIGIN=85605a5e527bf48834eb0cf588d8e29ba2a29d9b
```

## STDERR
```text
From github.com-madworld:JoTalbot/MadWorld
 * branch            main       -> FETCH_HEAD
```
