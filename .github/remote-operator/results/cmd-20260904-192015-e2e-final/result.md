# Remote Command Result

- **Command ID:** `cmd-20260904-192015-e2e-final`
- **Attempt ID:** `cmd-20260904-192015-e2e-final-attempt-20260904T192016Z-171582`
- **Status:** `DONE`
- **Exit code:** `0`
- **Executor:** `arm-server-01`
- **Started:** `2026-09-04T19:20:16Z`
- **Finished:** `2026-09-04T19:20:17Z`
- **Duration:** `1s`

## Command
```bash
printf 'MADWORLD_REMOTE_OPERATOR_OK\n'
printf 'USER=%s\n' "$(id -un)"
printf 'HOST=%s\n' "$(hostname -s)"
```

## STDOUT
```text
MADWORLD_REMOTE_OPERATOR_OK
USER=ubuntu
HOST=arm-server-01
```

## STDERR
```text
```
