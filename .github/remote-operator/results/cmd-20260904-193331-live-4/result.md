# Remote Command Result

- **Command ID:** `cmd-20260904-193331-live-4`
- **Attempt ID:** `cmd-20260904-193331-live-4-attempt-20260904T193331Z-190994`
- **Status:** `DONE`
- **Exit code:** `0`
- **Executor:** `arm-server-01`
- **Started:** `2026-09-04T19:33:31Z`
- **Finished:** `2026-09-04T19:33:39Z`
- **Duration:** `8s`

## Command
```bash
printf 'LIVE4_START=%s\n' "$(date +%s)"
sleep 8
printf 'LIVE4_END=%s\n' "$(date +%s)"
```

## STDOUT
```text
LIVE4_START=1788550411
LIVE4_END=1788550419
```

## STDERR
```text
```
