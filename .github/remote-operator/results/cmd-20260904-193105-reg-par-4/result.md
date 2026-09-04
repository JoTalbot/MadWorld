# Remote Command Result

- **Command ID:** `cmd-20260904-193105-reg-par-4`
- **Attempt ID:** `cmd-20260904-193105-reg-par-4-attempt-20260904T193105Z-187813`
- **Status:** `DONE`
- **Exit code:** `0`
- **Executor:** `arm-server-01`
- **Started:** `2026-09-04T19:31:06Z`
- **Finished:** `2026-09-04T19:31:09Z`
- **Duration:** `3s`

## Command
```bash
printf 'PAR_4_START=%s\n' "$(date +%s)"
sleep 3
printf 'PAR_4_END=%s\n' "$(date +%s)"
```

## STDOUT
```text
PAR_4_START=1788550266
PAR_4_END=1788550269
```

## STDERR
```text
```
