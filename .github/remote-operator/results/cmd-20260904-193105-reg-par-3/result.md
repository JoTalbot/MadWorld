# Remote Command Result

- **Command ID:** `cmd-20260904-193105-reg-par-3`
- **Attempt ID:** `cmd-20260904-193105-reg-par-3-attempt-20260904T193105Z-187809`
- **Status:** `DONE`
- **Exit code:** `0`
- **Executor:** `arm-server-01`
- **Started:** `2026-09-04T19:31:06Z`
- **Finished:** `2026-09-04T19:31:09Z`
- **Duration:** `3s`

## Command
```bash
printf 'PAR_3_START=%s\n' "$(date +%s)"
sleep 3
printf 'PAR_3_END=%s\n' "$(date +%s)"
```

## STDOUT
```text
PAR_3_START=1788550266
PAR_3_END=1788550269
```

## STDERR
```text
```
