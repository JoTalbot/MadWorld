# Remote Command Result

- **Command ID:** `cmd-20260904-194301-production-late`
- **Attempt ID:** `cmd-20260904-194301-production-late-attempt-20260904T194332Z-233072`
- **Status:** `DONE`
- **Exit code:** `0`
- **Executor:** `arm-server-01`
- **Started:** `2026-09-04T19:43:32Z`
- **Finished:** `2026-09-04T19:43:34Z`
- **Duration:** `2s`

## Command
```bash
printf 'PROD_LATE_START=%s\n' "$(date +%s)"
sleep 2
printf 'PROD_LATE_END=%s\n' "$(date +%s)"
```

## STDOUT
```text
PROD_LATE_START=1788551012
PROD_LATE_END=1788551014
```

## STDERR
```text
```
