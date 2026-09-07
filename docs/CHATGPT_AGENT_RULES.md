# MadWorld ChatGPT / AI Agent Operating Rules

## Purpose

This document is the repository-level operating contract for AI agents working on MadWorld. It preserves the operational rules agreed for autonomous repository work so a new agent can recover the intended behavior from the repository itself.

## 1. Source of truth and startup

At the beginning of work, inspect the actual repository state. Do not rely on assumptions or stale conversation state.

Required startup checks:
1. Determine owner/repository, current branch and HEAD.
2. Read `README.md`, `AGENTS.md`, `docs/`, `.github/` and relevant project structure.
3. Identify stack, tests, CI/CD, deployment and operational tooling.
4. Identify the existing Remote Operator and queue/result mechanisms.
5. Read this document, `AGENTS.md`, `docs/REMOTE_OPERATOR.md`, `.github/remote-operator/QUEUE.md` and `docs/skills/MADWORLD_AGENT_SKILL.md`.

GitHub is the source of truth for repository code, workflows and documentation. Server state is verified through Remote Operator evidence.

## 2. Mandatory evolving project skill

`docs/skills/MADWORLD_AGENT_SKILL.md` is required, living project memory for every AI agent, coding agent, reviewer, operator and automated worker.

- Load and apply it before modification.
- Record verified reusable knowledge during the same logical batch when practical.
- Correct obsolete lessons when evidence changes.
- Never record guesses as facts or secrets in the skill.

## 3. Autonomous continuation contract

The default mode for technical work is continuous execution through the current logically connected stage.

When the user requests `+`, "do everything", "one batch", "until the end", or an equivalent authorization:

- treat the request as authorization for the **whole logically connected stage**, not one next command;
- continue automatically through every technically necessary intermediate step;
- do not require another `+` after each internal stage;
- do not stop merely because a command, test, workflow dispatch, or partial verification completed;
- do not emit artificial prompts such as "send `+` to continue" while the authorized batch is still active;
- keep the operation inside the original goal and safety boundary.

**Silence between internal stages means continue, not wait for confirmation.**

A missing subsequent `+` is not a stop signal for an already authorized logical batch.

Stop only for completion, a genuine technical blocker, inherently required human/owner/legal approval, a safety boundary, or an unrecoverable defined timeout/failure.

## 4. State checkpoint invariant

Before every substantial dependent step or retry, verify:

- current branch and HEAD;
- current queue state;
- whether a newer commit/request supersedes the previous state;
- existing terminal results/evidence;
- whether the operation has already been completed;
- whether the next action is still inside the authorized goal.

Never rely on a stale workflow checkout when current queue state is required. If an old run cannot observe the current state, route execution through a mechanism that starts from the current HEAD.

## 5. Idempotency and duplicate protection

Before retrying or dispatching an operation, check for existing execution/result evidence using its immutable operation/command identity.

- Reuse verified terminal evidence when a duplicate execution is unnecessary.
- Do not execute the same command twice merely because an earlier result is inconvenient to retrieve.
- If re-execution is required, create a new immutable command identity unless the executor explicitly supports safe idempotent retry semantics.
- Never manually manufacture a terminal result.

## 6. Mandatory wait invariant

Submitting or dispatching an operation is never the same as completing it.

If a terminal result is required:
1. Wait for the actual result.
2. Poll asynchronous operations until terminal state or timeout.
3. Inspect workflow status and job status.
4. Inspect exit code, stdout and stderr.
5. Inspect `result.json`, artifacts and result records when available.
6. Only then start dependent work or report success.

Terminal states include `DONE`, `FAILED`, `TIMEOUT`, `CANCELLED`, `INTERRUPTED` and `INVALID`.

A queued/started/in-progress/dispatch-accepted state is never sufficient evidence of successful execution.

## 7. Fix-and-repeat / recovery budget

For audits, fixes, release preparation and `+` batches use:

`ANALYZE -> IMPLEMENT -> TEST -> VERIFY -> FIX -> RE-TEST -> REPORT`

When a failure appears:

`FAIL -> DIAGNOSE -> FIX -> TEST -> VERIFY`

Do not stop at the first defect. Use a reasonable bounded recovery effort. If the defect remains unresolved, classify it explicitly as `FAILED` or `BLOCKED`, provide evidence and explain the actual reason continuation is impossible.

A fix is not completion. All dependent checks must run again.

## 8. Goal completion gate

Do not declare the logical task complete solely because the last command returned `exit 0`.

Before finalizing, verify:

`TASK GOAL -> REQUIRED STEPS -> EVIDENCE -> ACCEPTANCE CRITERIA -> FINAL STATUS`

If acceptance criteria are not satisfied, continue the authorized work or classify the genuine blocker.

## 9. Automatic escalation

When blocked, do not ask the user to blindly repeat `+`.

Report:
- exact blocker;
- what was checked;
- evidence;
- why automated continuation is impossible or unsafe;
- the one concrete human/owner/legal action required, if any.

Human/owner/legal approval remains mandatory where inherently required.

## 10. Remote Operator is the server channel

All server-side technical actions must use the repository's Remote Operator mechanism.

Preferred chain:

`ChatGPT/Agent -> GitHub -> GitHub Actions -> Remote Operator -> SSH -> server -> command -> result -> GitHub -> Agent`

If GitHub API/connector cannot perform a required action, use Remote Operator whenever technically possible. Never claim dispatch or execution without terminal evidence.

Short commands use `sync`. Long commands use `async` with polling and bounded timeout. Server execution is expected to run as root according to the configured operator implementation, and root must be verified from terminal evidence.

## 11. Queue discipline

The canonical queue is append-oriented. Do not silently rewrite history or manually mark requests DONE.

Every new command has a unique immutable identity and starts `PENDING`. Historical malformed/stale/orphan requests must be classified rather than silently mutated away.

Before dispatching through a workflow broker, ensure the broker observes the current queue HEAD. Do not repeatedly rerun an old checkout that cannot see a newer request.

## 12. Evidence discipline

Accepted evidence includes terminal `result.json`, stdout/stderr, exit code, workflow/job status and conclusion, artifacts, executor/server identity, timestamps/duration, result-branch records and relevant server logs.

Use statuses accurately:
- `VERIFIED`
- `PARTIALLY VERIFIED`
- `NOT VERIFIED`
- `NOT EXECUTED`
- `FAILED`
- `UNKNOWN`

Unknown external conditions never PASS. Workflow launch success is not command success. Command success is not automatically a release PASS.

## 13. Human action minimization

If a technical action would normally require a manual human step, automate it through Remote Operator whenever technically possible.

If a missing GitHub connector capability blocks an action, route it through Remote Operator or improve the operator path first. Do not pretend it was executed.

## 14. Production safety

Before production: verify branch/HEAD, git state, health, backup/rollback and required approvals. After production: health, smoke test, migrations/status, logs and CI/deployment result.

Do not perform production load/stress without an approved maintenance window and rollback plan. Do not touch unrelated infrastructure, databases, Docker networks/volumes or host services. Never expose secrets. Do not force-push unless explicitly required.

## 15. Release gates

Technical evidence may establish technical gates, but owner/legal/product decisions remain human decisions. Do not invent thresholds, device coverage, provider readiness or legal approval.

## 16. Learning and documentation

For every non-trivial logical batch:

`ANALYZE -> IMPLEMENT -> TEST -> VERIFY -> LEARN -> DOCUMENT -> RE-TEST -> REPORT`

When verified reusable experience appears, update the appropriate skill/documentation before final completion when practical. Keep `AGENTS.md`, this document, `docs/REMOTE_OPERATOR.md`, `.github/remote-operator/QUEUE.md`, `docs/skills/MADWORLD_AGENT_SKILL.md` and related operational/release documents aligned.

## 17. Final report

For serious operational tasks report:

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

Keep large logs in artifacts.

## 18. Core principle

**Once a logically connected operation is authorized, the agent owns the continuation of that operation until completion or a genuine blocker. It must wait, inspect, fix, retry, verify, learn, document and continue without requiring repeated `+` confirmations.**
