# Remote Command Result

- **Command ID:** `cmd-20260904-193331-live-3`
- **Attempt ID:** `cmd-20260904-193331-live-3-attempt-20260904T193331Z-190987`
- **Status:** `DONE`
- **Exit code:** `0`
- **Executor:** `arm-server-01`
- **Started:** `2026-09-04T19:33:31Z`
- **Finished:** `2026-09-04T19:33:39Z`
- **Duration:** `8s`

## Command
```bash
printf 'LIVE3_START=%s\n' "$(date +%s)"
sleep 8
printf 'LIVE3_END=%s\n' "$(date +%s)"
```

## STDOUT
```text
LIVE3_START=1788550411
LIVE3_END=1788550419
```

## STDERR
```text
```
