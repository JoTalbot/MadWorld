# Remote Command Result

- **Command ID:** `cmd-20260904-212234-production-audit`
- **Attempt ID:** `cmd-20260904-212234-production-audit-attempt-20260904T212235Z-673405`
- **Status:** `FAILED`
- **Exit code:** `1`
- **Executor:** `arm-server-01`
- **Started:** `2026-09-04T21:22:35Z`
- **Finished:** `2026-09-04T21:22:36Z`
- **Duration:** `1s`

## Command
```bash
  cd /opt/madworld
  set -euo pipefail

  echo "=== MADWORLD FULL PRODUCTION AUDIT ==="
  date -u

  echo
  echo "=== 1. GIT ==="
  git fetch origin main
  HEAD="$(git rev-parse HEAD)"
  ORIGIN="$(git rev-parse origin/main)"
  echo "HEAD=$HEAD"
  echo "ORIGIN=$ORIGIN"
  test "$HEAD" = "$ORIGIN"
  echo "GIT_SYNC=PASS"

  echo
  echo "=== 2. WORKTREE ==="
  git status --short

  echo
  echo "=== 3. REMOTE OPERATOR ==="
  systemctl is-enabled madworld-remote-operator.service
  systemctl is-active madworld-remote-operator.service
  echo "REMOTE_OPERATOR=ACTIVE"

  echo
  echo "=== 4. RESULT SYNC ==="
  systemctl is-enabled madworld-remote-operator-sync.timer
  systemctl is-active madworld-remote-operator-sync.timer
  echo "RESULT_SYNC_TIMER=ACTIVE"

  echo
  echo "=== 5. EXECUTOR ==="
  if pgrep -af '/opt/madworld/ops/remote-operator/executor.sh' >/dev/null; then
    echo "EXECUTOR_RUNNING"
  else
    echo "EXECUTOR_IDLE"
  fi

  echo
  echo "=== 6. LOCK ==="
  flock -n .github/remote-operator/state/executor.lock -c 'echo LOCK=FREE'

  echo
  echo "=== 7. QUEUE ==="
  COMMANDS="$(grep -c '^COMMAND_ID:' .github/remote-operator/COMMANDS.txt || true)"
  PENDING="$(grep -c '^STATUS: PENDING$' .github/remote-operator/COMMANDS.txt || true)"
  echo "COMMANDS=$COMMANDS"
  echo "PENDING=$PENDING"

  echo
  echo "=== 8. SHELL SYNTAX ==="
  for f in ops/remote-operator/*.sh; do
    bash -n "$f"
  done
  echo "SHELL_SYNTAX=PASS"

  echo
  echo "=== 9. SERVICES ==="
  systemctl --no-pager --full status madworld-remote-operator.service | sed -n '1,18p'
  systemctl --no-pager --full status madworld-remote-operator-sync.timer | sed -n '1,18p'

  echo
  echo "=== 10. LISTENING PORTS ==="
  ss -lntup

  echo
  echo "=== 11. DISK ==="
  df -h /opt/madworld

  echo
  echo "=== 12. MEMORY ==="
  free -h

  echo
  echo "=== 13. LOAD ==="
  uptime

  echo
  echo "=== 14. FAILED SYSTEMD ==="
  systemctl --failed --no-legend || true

  echo
  echo "=== 15. RECENT OPERATOR LOG ==="
  journalctl -u madworld-remote-operator.service -n 40 --no-pager

  echo
  echo "=== 16. RECENT SYNC LOG ==="
  journalctl -u madworld-remote-operator-sync.service -n 30 --no-pager

  echo
  echo "=== 17. SECURITY / PERMISSIONS ==="
  stat -c '%U:%G %a %n'     ops/remote-operator/*.sh     .github/remote-operator/state     .github/remote-operator/results

  echo
  echo "=== 18. PRODUCTION AUDIT RESULT ==="
  echo "AUDIT_COMMAND=cmd-20260904-212234-production-audit"
  echo "GIT_SYNC=PASS"
  echo "REMOTE_OPERATOR=ACTIVE"
  echo "RESULT_SYNC_TIMER=ACTIVE"
  echo "QUEUE_COMMANDS=$COMMANDS"
  echo "QUEUE_PENDING=$PENDING"
  echo "SHELL_SYNTAX=PASS"
  echo "=== AUDIT COMPLETE ==="
```

## STDOUT
```text
=== MADWORLD FULL PRODUCTION AUDIT ===
Fri Sep  4 21:22:35 UTC 2026

=== 1. GIT ===
HEAD=8398df430db68cfd11b8fd3be2f6fe1aea81f36a
ORIGIN=8398df430db68cfd11b8fd3be2f6fe1aea81f36a
GIT_SYNC=PASS

=== 2. WORKTREE ===
 M .github/remote-operator/COMMANDS.txt
?? .github/remote-operator/results/cmd-20260904-212234-production-audit/
?? .github/remote-operator/state/cmd-20260904-212234-production-audit.json

=== 3. REMOTE OPERATOR ===
enabled
active
REMOTE_OPERATOR=ACTIVE

=== 4. RESULT SYNC ===
enabled
active
RESULT_SYNC_TIMER=ACTIVE

=== 5. EXECUTOR ===
EXECUTOR_RUNNING

=== 6. LOCK ===
```

## STDERR
```text
From github.com-madworld:JoTalbot/MadWorld
 * branch            main       -> FETCH_HEAD
```
