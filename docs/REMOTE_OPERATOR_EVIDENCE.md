# Remote Operator External Evidence Policy

## Purpose

Remote Operator execution results are accepted as valid external evidence for MadWorld release gates and operational verification when the evidence has a verifiable execution chain.

## Accepted evidence

Evidence produced or collected by Remote Operator may include:

- `result.json`;
- `result.md`;
- `stdout.log`;
- `stderr.log`;
- terminal execution state;
- exit code;
- executor/server identity;
- start/finish timestamps and duration;
- GitHub Actions artifacts containing the execution result;
- records published to `remote-operator-results`;
- server logs or external verification output captured and recorded by Remote Operator.

## Acceptance criteria

Remote Operator evidence is acceptable when all applicable conditions are satisfied:

1. The command has a unique `COMMAND_ID`.
2. The execution reached a terminal state: `DONE`, `FAILED`, `TIMEOUT`, `CANCELLED`, `INTERRUPTED` or `INVALID`.
3. The recorded executor/result can be associated with the requested operation.
4. The exit code and available stdout/stderr have been inspected.
5. The evidence directly addresses the specific release or operational gate.
6. No secret or credential is required to interpret or validate the evidence.
7. Where integrity or freshness matters, timestamps and the recorded result source are checked.

## Gate decision rules

- `DONE` with exit code `0` is successful execution evidence, but is **not by itself** an automatic gate PASS. The command output must satisfy the gate requirement.
- Evidence that only partially satisfies a gate is `PARTIALLY VERIFIED`.
- Missing or unavailable evidence is `NOT VERIFIED`.
- A command that was never executed is `NOT EXECUTED`.
- A failed execution is `FAILED`.
- A timeout or contradictory/untrustworthy result is `UNKNOWN` unless the gate procedure explicitly defines a stronger conclusion.

## External checks

A manual check does not have to be repeated solely because it occurred outside the repository if Remote Operator actually performed or collected that check and preserved the resulting evidence through the Remote Operator result chain.

Examples include public HTTP/TLS checks, provider/API checks, server health checks, backup verification and other release-gate probes that can be executed safely by the configured Remote Operator.

For checks requiring human/legal/product-owner judgment, Remote Operator evidence may establish the technical facts but cannot substitute for the required human approval.

## Mandatory provenance

Never accept a pasted assertion such as "the check passed" without a corresponding Remote Operator result or other verifiable evidence. The queue entry alone is submission evidence, not execution evidence.

The canonical flow remains:

`queue -> executor -> terminal result -> result/state evidence -> gate evaluation`

This policy does not weaken the mandatory wait-for-terminal-result rule. Agents must wait for and inspect the actual result before using it for a dependent operation or reporting a gate as verified.
