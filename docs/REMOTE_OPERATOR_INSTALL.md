# Remote Operator installation

## Purpose

Install the server-side watcher/executor that reacts to changes in `.github/remote-operator/COMMANDS.txt`.

## One-time server installation

From the project checkout on the server:

```bash
cd /opt/madworld
git pull --ff-only origin main
sudo ./ops/remote-operator/install.sh /opt/madworld
```

Verify:

```bash
sudo systemctl is-enabled madworld-remote-operator.service
sudo systemctl is-active madworld-remote-operator.service
sudo journalctl -u madworld-remote-operator.service -n 100 --no-pager
```

## Important result-sync prerequisite

Execution state and results are durable locally. To publish them back to GitHub, the server checkout must already have an authenticated `git push` mechanism configured outside the repository, preferably a dedicated least-privilege deploy key/credential. Never place that credential in `COMMANDS.txt`, scripts, logs, or committed files.

## Operational model

1. GitHub push deploys repository changes to `/opt/madworld`.
2. Watcher notices the local queue change.
3. Executor parses only `PENDING` commands.
4. The command is atomically claimed and then marked `RUNNING`.
5. The command runs in its own process group.
6. Timeout/cancellation terminates the process group with `SIGTERM`, then `SIGKILL` after the grace period if needed.
7. The result and state are stored under `.github/remote-operator/results/` and `.github/remote-operator/state/`.
8. Result synchronization publishes those records to GitHub without rerunning the command.

## Do not use production commands as the first test

Use a harmless command such as:

```text
---
COMMAND_ID: cmd-smoke-<unique>
STATUS: PENDING
AGENT: operator
CREATED_AT: <UTC timestamp>
TIMEOUT_MINUTES: 1
MODE: sync

COMMAND:
printf 'REMOTE_OPERATOR_SMOKE_OK\\n'
---
```

Then verify the resulting state and result record before enabling real operational commands.
