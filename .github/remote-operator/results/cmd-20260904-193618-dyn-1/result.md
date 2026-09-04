# Remote Command Result

- **Command ID:** `cmd-20260904-193618-dyn-1`
- **Attempt ID:** `cmd-20260904-193618-dyn-1-attempt-20260904T193619Z-205206`
- **Status:** `DONE`
- **Exit code:** `0`
- **Executor:** `arm-server-01`
- **Started:** `2026-09-04T19:36:19Z`
- **Finished:** `2026-09-04T19:36:31Z`
- **Duration:** `12s`

## Command
```bash
printf 'DYN1_START=%s\n' "$(date +%s)"
sleep 12
printf 'DYN1_END=%s\n' "$(date +%s)"
```

## STDOUT
```text
DYN1_START=1788550579
DYN1_END=1788550591
```

## STDERR
```text
```
