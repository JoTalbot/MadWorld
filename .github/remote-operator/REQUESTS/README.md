# Remote Operator Requests

This directory is an additional append-only request intake for the installed Remote Operator.

Each request file contains the same immutable `COMMAND_ID` / `STATUS: PENDING` format as `COMMANDS.txt`.
The executor consumes both inputs, preserves idempotency through state files, and stores stdout/stderr/results in the normal result tree.

Requests must contain no secrets. Do not mark requests DONE manually.
