# MadWorld Remote Operator Engine

This directory contains the server-side execution engine for `.github/remote-operator/COMMANDS.txt`.

## Architecture

- `watcher.sh` watches the canonical queue and wakes the executor immediately after changes.
- `executor.sh` claims and executes pending commands, records lifecycle state, timeout/cancellation metadata, and results.
- `state-manager.sh` owns atomic state transitions and lock handling.
- `result-manager.sh` writes bounded structured results and stdout/stderr files.
- `cancel.sh` requests cancellation of an active command.
- `madworld-remote-operator.service` runs the watcher as a persistent systemd service.

## State model

`PENDING -> CLAIMED -> RUNNING -> DONE | FAILED | TIMEOUT | CANCELLED | INTERRUPTED`

A command ID is immutable and is never executed twice automatically. Attempts have independent `ATTEMPT_ID` values.

## Repository synchronization

The normal GitHub-to-server deployment copies repository files to the configured project directory. The operator watches the resulting local `COMMANDS.txt` and does not require a GitHub Actions workflow dispatch.

Results are written under `.github/remote-operator/results/<COMMAND_ID>/` and state under `.github/remote-operator/state/`. The engine must never commit secrets or credentials.

## Safety defaults

- Maximum concurrent commands: 4.
- Default timeout: 30 minutes.
- Grace period after cancellation/timeout: 15 seconds.
- Automatic retry: disabled unless explicitly requested by the command metadata.
- Commands are launched in their own process group so cancellation can terminate descendants.
- Server-only files are not deleted by deployment.

## Installation

See `docs/REMOTE_OPERATOR_ENGINE.md`. Installation must be performed on the project server with the repository already deployed. The installer validates the target directory and installs the systemd unit without embedding secrets.
