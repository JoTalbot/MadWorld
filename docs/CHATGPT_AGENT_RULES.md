# MadWorld ChatGPT / AI Agent Operating Rules

## Purpose

This document is the repository-level operating contract for AI agents working on MadWorld. It preserves the operational rules agreed for autonomous repository work so a new agent can recover the intended behavior by reading the repository.

## 1. Source of truth and startup

At the beginning of work, inspect the actual repository state. Do not rely on assumptions or stale conversation state.

Required startup checks:

1. Determine owner/repository, current branch and HEAD.
2. Read `README.md`, `AGENTS.md`, `docs/`, `.github/` and relevant project structure.
3. Identify stack, tests, CI/CD, deployment and operational tooling.
4. Identify the existing Remote Operator and its queue/result mechanisms.
5. Read this document together with `AGENTS.md` and `docs/REMOTE_OPERATOR.md`.
6. Read `docs/skills/MADWORLD_AGENT_SKILL.md` before making any repository modification.

GitHub is the source of truth for repository code, workflows and documentation. Server state is verified through Remote Operator evidence.

## 2. Mandatory evolving project skill

`docs/skills/MADWORLD_AGENT_SKILL.md` is a required, living skill for every AI agent, coding agent, reviewer, operator and automated worker working on MadWorld.

- A new worker MUST load and apply the skill before modifying the repository.
- The skill is part of the repository operating contract, not optional onboarding material.
- During each non-trivial task, the agent must identify reusable new knowledge.
- Verified new experience MUST be recorded in the skill during the same logically connected work batch whenever practical.
- Existing lessons must be corrected when verified evidence shows they are obsolete or incomplete.
- Do not record guesses as facts.
- Never store secrets or sensitive credentials in the skill.
- The repository must contain enough durable knowledge for the next agent to continue without private chat history.

The learning loop is:

`ANALYZE -> IMPLEMENT -> TEST -> VERIFY -> LEARN -> DOCUMENT -> RE-TEST -> REPORT`

If no reusable new knowledge appeared, `LEARN/DOCUMENT` may result in a documented "no new lesson" decision rather than a meaningless edit.

## 3. Autonomous continuous execution

The default mode for technical work is continuous execution through the current logically connected stage.

When the user requests `+`, `do everything`, `one batch`, `until the end`, or equivalent:

- execute the entire logically connected stage;
- do not stop after discovering the first defect;
- fix discovered defects automatically when technically possible;
- repeat relevant tests and verification after every fix;
- continue until the stage is complete, blocked by a genuine external/owner/legal decision, or technically impossible;
- report the final verified state and remaining blockers.

Do not ask for intermediate confirmation when the next action is technically necessary and authorized by the existing task.

## 4. Wait for results

Submitting an operation is never the same as completing it.

If a task is started and a terminal result is required:

1. Wait for the actual result.
2. Poll asynchronous operations until a terminal state or timeout.
3. Inspect workflow status and job status.
4. Inspect exit code, stdout and stderr.
5. Inspect `result.json` and artifacts when available.
6. Only then start dependent work or report success.

Terminal states include `DONE`, `FAILED`, `TIMEOUT`, `CANCELLED`, `INTERRUPTED` and `INVALID`.

If the result is missing after the defined timeout, use `TIMEOUT` or `UNKNOWN`. Never convert a missing result into success.

## 5. Fix-and-repeat loop

For audits, fixes, release preparation and requests containing `+`, use:

`ANALYZE -> IMPLEMENT -> TEST -> VERIFY -> FIX -> RE-TEST -> REPORT`

Continue the loop until all actionable defects in the current stage are resolved or an explicit external blocker remains.

A failed test is an input to the next repair cycle, not a reason to stop prematurely.

## 6. Remote Operator is the server channel

All server-side technical actions must use the repository's Remote Operator mechanism.

Preferred chain:

`ChatGPT/Agent -> GitHub -> GitHub Actions -> SSH -> server -> command -> result -> GitHub -> Agent`

For the installed queue executor, append new commands only to:

`.github/remote-operator/COMMANDS.txt`

Do not bypass Remote Operator with ad-hoc SSH when the operation is intended for it.

Short commands use `sync`. Long commands use `async` with polling and a bounded timeout.

## 7. Root execution

Remote Operator server commands are expected to execute as root according to the repository's configured operator implementation.

Execution must be verified from actual terminal evidence. SSH transport identity alone is not proof of root execution.

Never expose or persist SSH credentials. Secrets belong only in GitHub Secrets:

- `REMOTE_SSH_HOST`
- `REMOTE_SSH_PORT`
- `REMOTE_SSH_USER`
- `REMOTE_SSH_PRIVATE_KEY`
- `REMOTE_SSH_HOST_KEY`
- `REMOTE_WORKDIR`

Never put secrets, private keys, passwords, tokens or cookies into repository files, queue entries, logs, artifacts, issues or reports.

## 8. No allowlist requirement

Remote Operator may execute arbitrary shell commands as required by the task. Do not add a command allowlist merely to restrict the operator. Security is provided by the SSH account, GitHub Secrets, strict host-key verification and Linux permissions.

## 9. Evidence and status discipline

Never claim an action was performed merely because a workflow was queued or started.

Accepted operational evidence includes:

- terminal `result.json`;
- stdout/stderr;
- exit code;
- workflow/job status and conclusion;
- artifacts;
- executor/server identity;
- timestamps and duration;
- result records on `remote-operator-results`;
- relevant server logs and external verification.

Use these statuses accurately:

- `VERIFIED`
- `PARTIALLY VERIFIED`
- `NOT VERIFIED`
- `NOT EXECUTED`
- `FAILED`
- `UNKNOWN`

## 10. Safety and production

Do not perform production load/stress testing without the required maintenance window, rollback plan and evidence.

Before production operations:

- verify branch and HEAD;
- verify git state;
- verify service health;
- identify backup and rollback path;
- execute according to repository documentation.

After production operations:

- health check;
- smoke test;
- migration/status check;
- logs;
- CI/deployment result.

Do not touch unrelated infrastructure, databases, Docker networks/volumes or host services outside the task scope. Do not perform global Docker cleanup or alter UFW unless explicitly required and authorized.

Do not use force push unless explicitly required.

## 11. Release gates

Unknown external gates are not treated as passed.

Technical evidence may establish a technical gate, but owner/legal/product decisions remain human decisions. A verified command does not automatically mean a release gate is passed.

For release work, inspect and update the repository's release evidence documents using measured facts only. Never invent thresholds, capacity, device coverage, provider readiness or legal approval.

## 12. Queue and audit trail

The canonical queue is append-only. New entries receive a unique immutable `COMMAND_ID` and begin with `STATUS: PENDING`.

Do not rewrite, sort or delete historical queue entries. Completed execution records remain an audit trail.

Runtime results belong on the dedicated `remote-operator-results` branch and must not be copied into `main` as runtime-result commits unless repository documentation explicitly requires it.

## 13. Human action minimization

If a technical action would normally require a manual human step, automate it through Remote Operator whenever technically possible.

Manual action is acceptable only when:

- Remote Operator is technically incapable of performing the action; or
- explicit human/legal/owner approval is inherently required.

If a missing GitHub connector capability blocks an action, do not pretend it was executed. Route the action through Remote Operator or improve the operator path first when that is technically possible.

## 14. Documentation requirement

When operational behavior changes, update the relevant repository documentation in the same logically connected work cycle.

At minimum keep these aligned:

- `AGENTS.md`
- `docs/CHATGPT_AGENT_RULES.md`
- `docs/REMOTE_OPERATOR.md`
- `.github/remote-operator/QUEUE.md`
- `docs/skills/MADWORLD_AGENT_SKILL.md`
- relevant release/operations documents.

## 15. Final report

For serious operational tasks, report:

`STATUS`
`REPOSITORY`
`BRANCH`
`COMMIT`
`OPERATION`
`SERVER`
`VERIFIED`
`FAILED`
`EVIDENCE`
`REMAINING`

Keep large logs in GitHub artifacts and provide concise evidence references in the final report.

## 16. Core principle

**Do not stop merely because a step is waiting, failed, or inconvenient. Wait, inspect, fix, retry, verify, learn, document, and continue until the current logically connected stage is complete or a genuine external blocker remains.**
