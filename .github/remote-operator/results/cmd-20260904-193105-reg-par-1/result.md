# Remote Command Result

- **Command ID:** `cmd-20260904-193105-reg-par-1`
- **Attempt ID:** `cmd-20260904-193105-reg-par-1-attempt-20260904T193105Z-187806`
- **Status:** `DONE`
- **Exit code:** `0`
- **Executor:** `arm-server-01`
- **Started:** `2026-09-04T19:31:06Z`
- **Finished:** `2026-09-04T19:31:09Z`
- **Duration:** `3s`

## Command
```bash
printf 'PAR_1_START=%s\n' "$(date +%s)"
sleep 3
printf 'PAR_1_END=%s\n' "$(date +%s)"
```

## STDOUT
```text
PAR_1_START=1788550266
PAR_1_END=1788550269
```

## STDERR
```text
```
