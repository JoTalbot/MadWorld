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

## 4. Goal Lock and dependency ownership

At batch start, define one logical goal and explicit acceptance criteria. Every action must be justified as required to reach, verify, recover, or safely support that goal.

Treat the batch as a dependency graph, not a list of isolated commands. When a step completes, automatically execute newly unblocked steps required by the goal. Parallelize independent safe read-only checks where useful, but serialize conflicting mutations.

**AGENT OWNS THE WORKFLOW, NOT JUST THE COMMAND.** Delegating execution to a workflow, server, or another agent does not transfer responsibility for collecting terminal evidence and proving the final acceptance criteria.

Do not allow a successful intermediate step to become a dead-end success. Continue until the logical goal is complete or a valid stop condition applies.

## 5. State checkpoint and fresh-state invariant

Before every substantial dependent step, retry, dispatch, or recovery action, verify:

- current branch and HEAD;
- current queue state;
- whether a newer commit/request supersedes the previous state;
- existing terminal results/evidence;
- whether the operation has already completed;
- relevant deployment/server state;
- whether the next action is still inside the authorized goal.

Never rely on stale workflow checkout, stale queue snapshot, stale deployment version, or stale result as evidence for newer state.

## 6. Idempotency and duplicate protection

Before retrying or dispatching an operation, check for existing execution/result evidence using its immutable operation identity.

- Reuse verified terminal evidence when safe.
- Do not repeat side effects merely because earlier evidence is inconvenient to retrieve.
- If re-execution is required, use a new immutable command identity unless the executor explicitly provides safe idempotent retry semantics.
- Detect already-completed work after interruption before starting a replacement operation.
- Never manufacture a terminal result manually.

## 7. Mandatory wait invariant

Submitting or dispatching an operation is never the same as completing it.

If a terminal result matters:
1. Wait for the actual result.
2. Poll asynchronous operations until terminal state or bounded timeout.
3. Inspect workflow status and job status.
4. Inspect exit code, stdout and stderr.
5. Inspect `result.json`, artifacts and result records when available.
6. Only then start dependent work or report success.

Terminal states include `DONE`, `FAILED`, `TIMEOUT`, `CANCELLED`, `INTERRUPTED` and `INVALID`.

A queued/started/in-progress/dispatch-accepted state is never sufficient evidence of successful execution.

## 8. Retry intelligence and bounded recovery

When a failure appears, classify it before retrying:
- transient;
- deterministic/code defect;
- stale state;
- configuration;
- dependency/tooling;
- permission/authentication;
- concurrency/idempotency;
- safety or infrastructure risk.

Then use:

`FAIL -> DIAGNOSE -> FIX -> TEST -> VERIFY`

Use a bounded autonomy budget with defined timeout, polling and retry limits. Never blindly loop.

If repeated failure indicates risk of duplicate side effects, data corruption, infrastructure damage, or secret exposure, activate a circuit breaker for the affected path and preserve evidence.

## 9. No premature success / goal completion gate

Do not declare success because a workflow was accepted, a job started, one command returned `exit 0`, one test passed, a service is reachable, or an artifact exists.

Before finalizing, verify:

`TASK GOAL -> REQUIRED STEPS -> EVIDENCE -> ACCEPTANCE CRITERIA -> FINAL STATUS`

If acceptance criteria are not satisfied, continue the authorized work or classify the genuine blocker.

## 10. Crash recovery and result ownership

After interruption, reconstruct state from durable evidence before continuing. Identify completed operations, current HEAD, queue state and outstanding dependencies. Resume from the latest verified checkpoint without duplicating side effects.

The initiating agent owns the result chain until the final report. Every delegated operation must have a terminal outcome reconciled into the batch result.

## 11. Human approval boundary and escalation

Technical inconvenience, missing convenience tooling, or a preference for manual clicking is not by itself a stop reason.

Autonomy stops only for:
- completed logical goal;
- genuine technical blocker;
- inherently required human/owner/legal approval;
- safety boundary;
- unrecoverable defined timeout/failure.

Before escalating, complete all independent safe work. Then report the exact blocker, checks performed, evidence, why automation is impossible or unsafe, and the one concrete human/owner/legal action required.

## 12. Remote Operator is the server channel

All server-side technical actions must use the repository's Remote Operator mechanism.

Preferred chain:

`ChatGPT/Agent -> GitHub -> GitHub Actions -> Remote Operator -> SSH -> server -> command -> result -> GitHub -> Agent`

If GitHub API/connector cannot perform a required action, use Remote Operator whenever technically possible. Never claim dispatch or execution without terminal evidence.

Short commands use `sync`. Long commands use `async` with polling and bounded timeout. Server execution is expected to run as root according to the configured operator implementation, and root must be verified from terminal evidence.

## 13. Queue discipline

The canonical queue is append-oriented. Do not silently rewrite history or manually mark requests DONE.

Every new command has a unique immutable identity and starts `PENDING`. Historical malformed/stale/orphan requests must be classified rather than silently mutated away.

Before dispatching through a workflow broker, ensure the broker observes the current queue HEAD. Do not repeatedly rerun an old checkout that cannot see a newer request.

## 14. Parallel work control

Independent read-only checks may run in parallel. Mutating operations that can conflict must be serialized or protected by explicit idempotency/concurrency controls.

Parallel work must preserve evidence ordering, clear result ownership, and safe resource limits. When a dependency becomes invalid, stop only the affected branches and continue independent safe branches.

## 15. Invariant checkpoints

At major milestones verify the invariants required by the goal:
- repository/branch/commit identity;
- queue integrity;
- command identity/idempotency;
- server identity and root execution where applicable;
- isolation boundaries;
- service health;
- expected artifacts and result records;
- required CI/deployment state.

A broken invariant blocks dependent work until repaired or explicitly classified.

## 16. Human action minimization

If a technical action would normally require a manual human step, automate it through Remote Operator whenever technically possible.

If a missing GitHub connector capability blocks an action, route it through Remote Operator or improve the operator path first. Do not pretend it was executed.

## 17. Production safety

Before production: verify branch/HEAD, git state, health, backup/rollback and required approvals. After production: health, smoke test, migrations/status, logs and CI/deployment result.

Do not perform production load/stress without an approved maintenance window and rollback plan. Do not touch unrelated infrastructure, databases, Docker networks/volumes or host services. Never expose secrets. Do not force-push unless explicitly required.

## 18. Release gates

Technical evidence may establish technical gates, but owner/legal/product decisions remain human decisions. Do not invent thresholds, device coverage, provider readiness or legal approval.

Unknown external conditions never PASS.

## 19. Final autonomous sweep

Before reporting completion, perform one final sweep of the locked goal:
- all required steps reached terminal state;
- all acceptance criteria checked;
- regressions/relevant tests re-run after fixes;
- evidence reconciled;
- documentation/learning updated when reusable knowledge appeared;
- remaining blockers classified.

If the sweep finds unfinished work inside scope, continue it automatically. Do not stop simply because a previous milestone was successful.

## 20. Learning and documentation

For every non-trivial logical batch:

`ANALYZE -> IMPLEMENT -> TEST -> VERIFY -> LEARN -> DOCUMENT -> RE-TEST -> REPORT`

When verified reusable experience appears, update the appropriate skill/documentation before final completion when practical. Keep `AGENTS.md`, this document, `docs/REMOTE_OPERATOR.md`, `.github/remote-operator/QUEUE.md`, `docs/skills/MADWORLD_AGENT_SKILL.md` and related operational/release documents aligned.

## 21. Final report

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

## 22. Core principle

**Once a logically connected operation is authorized, the agent owns the continuation of that operation until completion or a genuine blocker. It must wait, inspect, fix, retry, verify, learn, document and continue without requiring repeated `+` confirmations.**
