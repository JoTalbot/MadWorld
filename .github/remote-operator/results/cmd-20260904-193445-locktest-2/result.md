# Remote Command Result

- **Command ID:** `cmd-20260904-193445-locktest-2`
- **Attempt ID:** `cmd-20260904-193445-locktest-2-attempt-20260904T193445Z-197074`
- **Status:** `DONE`
- **Exit code:** `0`
- **Executor:** `arm-server-01`
- **Started:** `2026-09-04T19:34:45Z`
- **Finished:** `2026-09-04T19:34:54Z`
- **Duration:** `9s`

## Command
```bash
printf 'LOCKTEST2_START=%s\n' "$(date +%s)"
sleep 8
printf 'LOCKTEST2_END=%s\n' "$(date +%s)"
```

## STDOUT
```text
LOCKTEST2_START=1788550485
LOCKTEST2_END=1788550493
```

## STDERR
```text
```
