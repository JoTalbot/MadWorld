# Remote Command Result

- **Command ID:** `cmd-20260904-192532-stress-4`
- **Attempt ID:** `cmd-20260904-192532-stress-4-attempt-20260904T192534Z-178913`
- **Status:** `DONE`
- **Exit code:** `0`
- **Executor:** `arm-server-01`
- **Started:** `2026-09-04T19:25:34Z`
- **Finished:** `2026-09-04T19:25:42Z`
- **Duration:** `8s`

## Command
```bash
printf 'STRESS_4_START=%s\n' "$(date +%s)"
sleep 8
printf 'STRESS_4_END=%s\n' "$(date +%s)"
```

## STDOUT
```text
STRESS_4_START=1788549934
STRESS_4_END=1788549942
```

## STDERR
```text
```
