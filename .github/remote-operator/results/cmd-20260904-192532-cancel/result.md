# Remote Command Result

- **Command ID:** `cmd-20260904-192532-cancel`
- **Attempt ID:** `cmd-20260904-192532-cancel-attempt-20260904T192547Z-179288`
- **Status:** `CANCELLED`
- **Exit code:** `130`
- **Executor:** `arm-server-01`
- **Started:** `2026-09-04T19:25:47Z`
- **Finished:** `2026-09-04T19:26:03Z`
- **Duration:** `16s`

## Command
```bash
printf 'CANCEL_TEST_STARTED\n'
sleep 60
printf 'CANCEL_TEST_FINISHED\n'
```

## STDOUT
```text
CANCEL_TEST_STARTED
```

## STDERR
```text
CANCELLED by operator request
```
