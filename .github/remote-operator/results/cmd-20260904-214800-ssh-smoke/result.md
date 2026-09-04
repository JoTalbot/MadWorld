# Remote Command Result

- **Command ID:** `cmd-20260904-214800-ssh-smoke`
- **Attempt ID:** `cmd-20260904-214800-ssh-smoke-attempt-20260904T214951Z-756027`
- **Status:** `DONE`
- **Exit code:** `0`
- **Executor:** `arm-server-01`
- **Started:** `2026-09-04T21:49:51Z`
- **Finished:** `2026-09-04T21:49:51Z`
- **Duration:** `0s`

## Command
```bash
set -e; echo SSH_REMOTE_OPERATOR_START; echo HOST=$(hostname); echo USER=$(id -un); echo UID=$(id -u); echo PWD=$(pwd); echo SSH_REMOTE_OPERATOR_OK
```

## STDOUT
```text
SSH_REMOTE_OPERATOR_START
HOST=arm-server-01
USER=ubuntu
UID=1001
PWD=/opt/madworld
SSH_REMOTE_OPERATOR_OK
```

## STDERR
```text
```
