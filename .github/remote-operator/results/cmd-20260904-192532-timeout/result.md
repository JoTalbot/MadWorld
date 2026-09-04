# Remote Command Result

- **Command ID:** `cmd-20260904-192532-timeout`
- **Attempt ID:** `cmd-20260904-192532-timeout-attempt-20260904T192615Z-180850`
- **Status:** `TIMEOUT`
- **Exit code:** `124`
- **Executor:** `arm-server-01`
- **Started:** `2026-09-04T19:26:15Z`
- **Finished:** `2026-09-04T19:27:30Z`
- **Duration:** `75s`

## Command
```bash
printf 'TIMEOUT_TEST_STARTED\n'
sleep 90
```

## STDOUT
```text
TIMEOUT_TEST_STARTED
```

## STDERR
```text
TIMEOUT after 1 minutes
```
