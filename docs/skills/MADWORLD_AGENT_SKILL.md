# MadWorld Agent Skill

## Status
REQUIRED / EVOLVING.

This skill is a mandatory operating contract for every worker, agent, and autonomous operator modifying or validating MadWorld. It is durable project memory and must evolve from verified experience.

## Mandatory onboarding
Before modifying the repository, every new worker MUST read and apply:
1. `AGENTS.md`
2. `docs/CHATGPT_AGENT_RULES.md`
3. `docs/REMOTE_OPERATOR.md`
4. `.github/remote-operator/QUEUE.md`
5. `docs/skills/MADWORLD_AGENT_SKILL.md`

A worker that has not loaded the skill is NOT READY TO MODIFY THE REPOSITORY.

## Autonomous one-batch operation
Treat `+` as the user's established signal that the current logically connected operation must continue automatically. This interaction pattern must be generalized by agents: once a logically connected batch has been authorized, agents MUST continue through all required intermediate stages without forcing the user to send another `+` after each stage.

Do not stop merely because an internal stage completed, a command returned, a workflow started, or a partial result appeared. Continue automatically through:

`ANALYZE -> IMPLEMENT -> TEST -> VERIFY -> FIX -> RE-TEST -> REPORT`

For asynchronous operations, wait/poll for the terminal result or the defined timeout. For failures, diagnose and fix when safely possible, then re-test. Do not convert autonomous work into a sequence of artificial confirmation prompts.

An agent may stop only when:
- the logically connected task is complete;
- a real technical blocker prevents continuation;
- human/owner/legal approval is inherently required;
- a safety boundary forbids the operation; or
- a defined timeout/failure condition has been reached and cannot be safely resolved.

A missing subsequent `+` is NOT a stop signal while the agent is already executing a previously authorized logically connected batch. The `+` defines the desired autonomous interaction pattern, not a requirement for repeated confirmation.

See `docs/skills/PLUS_AUTONOMY_RULE.md` for the durable rule.

## Core operating rules
- Work from verified repository state, never assumptions.
- Preserve existing architecture unless evidence requires change.
- Every known failure must become a guard, test, documentation lesson, or equivalent durable protection.
- Before inventing a solution, search project knowledge and existing implementation.
- If blocked, stop and classify the blocker rather than guessing.
- Never record guesses as facts.
- Every failure must produce actionable evidence and, where appropriate, a regression guard.

## Remote Operator
Remote Operator is the server execution channel.

Execution chain:
`ChatGPT -> GitHub -> GitHub Actions -> Remote Operator -> SSH -> server -> command -> result -> GitHub -> ChatGPT`

If a required action cannot be performed through GitHub API/connector, use Remote Operator whenever technically possible. Do not claim dispatch or execution without terminal evidence.

Server commands may execute as root through the configured Remote Operator. Secrets remain only in GitHub Secrets and must never be printed, committed, or stored in project memory.

Every queued operation must wait for DONE/FAILED/TIMEOUT and verify workflow status, job status, exit code, stdout, stderr, `result.json`, artifacts, server identity, and duration where applicable.

Workflow launch success is not command success. Command success is not automatically a release PASS.

## Queue discipline
The Remote Operator queue is append-oriented. Do not silently rewrite historical requests or manually mark PENDING requests as DONE.

Historical orphan PENDING requests, malformed command IDs, missing timestamps, stale HEADs, and cancellation states must be classified from executor evidence. Queue reconciliation must not mutate history merely to make the queue look clean.

Workflow-dispatch broker execution must use the current queue state. Never rely on rerunning a broker job that checks out stale HEAD when a newer queue commit exists.

## Evidence and release gates
Use `docs/RELEASE_EVIDENCE_MATRIX.md`, `docs/DECISION_LOG.md`, and `docs/CHANGE_IMPACT_TEMPLATE.md` for consequential work.

Evidence statuses:
- VERIFIED
- PARTIALLY VERIFIED
- NOT VERIFIED
- NOT EXECUTED
- FAILED
- UNKNOWN

Unknown external conditions never PASS. Owner/legal/product decisions remain human decisions.

## Production safety
Before production changes, verify branch/HEAD, git state, health, backup/rollback, and required approvals. Afterward verify health, smoke tests, migrations/status, logs, and CI.

Do not touch unrelated Octopus/Liza infrastructure, unrelated PostgreSQL, existing Docker networks/volumes, host port 8000, global Docker cleanup, or UFW. Do not run production stress/load tests without an approved maintenance window and rollback plan. Isolated rehearsals must not use the production database.

## Learning loop
Every completed logical batch should follow:
`ANALYZE -> IMPLEMENT -> TEST -> VERIFY -> LEARN -> DOCUMENT -> RE-TEST -> REPORT`

If reusable verified knowledge appeared, record it in the appropriate durable project memory during the same logical batch whenever practical. If no new reusable knowledge appeared, do not create meaningless documentation churn.

The skill is never considered permanently finished. New agents must extend it with verified experience and correct obsolete lessons when evidence changes.

## Handoff invariant
Before completion, the agent must confirm the skill was loaded and applied, check existing lessons, preserve important evidence, and leave durable knowledge required by the next agent. A future agent should not have to rediscover an important known fact by repeating an already documented failure.
