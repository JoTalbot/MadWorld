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
6. `docs/skills/PLUS_AUTONOMY_RULE.md`
7. `docs/skills/AUTONOMY_ADVANCED_RULES.md`

A worker that has not loaded the skill and its autonomy companions is NOT READY TO MODIFY THE REPOSITORY.

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

## Autonomous operating model

### 1. Goal Lock
At batch start, derive and retain one explicit logical goal and its acceptance criteria. Every subsequent action MUST be classified as one of:
- required to reach the goal;
- required to verify the goal;
- required to recover from a failure on the path to the goal; or
- required to preserve safety/evidence.

Do not silently expand scope into unrelated improvements. A useful idea that is outside the locked goal becomes a documented follow-up, not an excuse to interrupt the batch.

### 2. No-Confirmation Loop
Once the goal is authorized, internal milestones do not require user confirmation. Completion of a command, test, workflow, or subtask is an input to the next step, not a pause point.

### 3. Async Wait Invariant
For every asynchronous operation whose result matters, the owner agent MUST wait until `DONE`, `FAILED`, `TIMEOUT`, `CANCELLED`, `INTERRUPTED`, or `INVALID`. A dispatch acknowledgement is never terminal evidence.

Polling must be bounded by a defined timeout. If the operation is still non-terminal at timeout, classify it explicitly and preserve the evidence.

### 4. No Premature Success
Never report success because:
- a workflow was accepted;
- a job started;
- one command returned `exit 0`;
- one test passed;
- a service appears reachable; or
- an expected artifact was merely created.

Success requires the complete acceptance criteria and evidence chain for the locked goal.

### 5. Fresh-State Rule
Before each substantial dependent action, retry, or dispatch, re-check the state that can invalidate the decision: branch, HEAD, queue, existing results, deployment state, and relevant server state. Never build a new decision on stale state when fresh state is available.

### 6. Single Source of Truth
Use GitHub for repository code, workflows, and durable documentation. Use Remote Operator result records and server evidence for server state. When sources disagree, stop treating the disputed claim as verified, classify the discrepancy, and reconcile it before relying on it.

### 7. No Dead-End Success
A successful intermediate step is not a valid final state if it leaves the logical goal unfinished. After every major milestone, identify the next required dependency and continue automatically unless a stop condition applies.

### 8. Automatic Dependency Graph
Represent the batch mentally as a dependency graph rather than a checklist of isolated commands. When step A completes, automatically execute every newly unblocked step B required by the goal. Parallelize independent safe checks when doing so reduces time, but serialize steps that can conflict or invalidate one another.

### 9. Retry Intelligence
On failure, distinguish transient, deterministic, stale-state, configuration, dependency, permission, and safety failures before retrying. Retry only when the failure class makes retry meaningful. Prefer fix -> test -> verify over blind repetition.

### 10. Stale Execution Protection
A workflow or server command tied to an old commit, queue snapshot, deployment version, or request identity MUST NOT be treated as evidence for newer state. If the current state matters, execute or verify against the current state.

### 11. Result Ownership
The agent that authorizes a logical batch owns the result chain. It must collect terminal outcomes of dependent operations and reconcile them into one final status. Handing work to another agent, workflow, or server does not transfer responsibility for verifying completion.

### 12. Crash Recovery
If the agent or workflow resumes after interruption, reconstruct state from durable evidence before continuing. Reuse verified terminal evidence where safe, detect already-completed operations, and avoid duplicate side effects.

### 13. Human Approval Boundary
Autonomy ends only where a decision inherently belongs to a human/owner/legal authority, or where a documented safety boundary forbids automation. Technical inconvenience, missing convenience tooling, or a preference for manual clicking is not by itself a valid stop reason.

When escalation is necessary, state the exact approval/action required and continue all independent safe work first.

### 14. Autonomy Budget
Each batch should have bounded execution resources: timeouts, retry limits, polling limits, and a clear stop condition. The budget prevents runaway loops without turning ordinary recoverable failures into premature stops.

### 15. Circuit Breaker
If repeated failures show that continued execution risks duplicate side effects, data corruption, infrastructure damage, secret exposure, or violation of a safety boundary, stop the affected path immediately. Preserve evidence and classify the blocker instead of escalating retries.

### 16. Invariant Checkpoints
At major milestones, verify the invariants that must remain true for the goal to be safe: correct repository/branch, intended commit, queue integrity, idempotency, server identity, isolation boundaries, health, and required artifacts/evidence. A broken invariant blocks dependent work until repaired or explicitly classified.

### 17. Parallel Work Control
Independent read-only checks may run in parallel. Mutating operations that can conflict must be serialized or protected by explicit idempotency/concurrency controls. Parallel execution must never weaken evidence ordering or make terminal ownership ambiguous.

### 18. Final Autonomous Sweep
Before reporting completion, perform one final sweep of the locked goal: required steps, terminal results, acceptance criteria, regressions, evidence, documentation, and remaining blockers. If the sweep finds unfinished work inside scope, continue it automatically.

### 19. Strongest principle
**AGENT OWNS THE WORKFLOW, NOT JUST THE COMMAND.**

Once a logically connected operation is authorized, the agent owns the whole chain to the acceptance criteria within the defined safety boundaries. It must wait, inspect, recover, verify, and continue without requiring repeated user confirmations.

## Advanced autonomy safeguards

The complete advanced safeguard layer is defined in `docs/skills/AUTONOMY_ADVANCED_RULES.md` and is mandatory. It adds:

1. **Intent Preservation**: preserve the original goal while allowing only verified re-locking when requirements materially change.
2. **Authority Boundary**: distinguish autonomous technical actions, required human/owner/legal decisions, and forbidden actions.
3. **Human Interrupt / Stop**: an explicit current stop/cancel instruction overrides autonomous continuation while safely containing in-flight side effects.
4. **Side-Effect Ledger**: track consequential mutations as planned, started, applied, verified or compensated/rolled back.
5. **Compensation / Recovery Plan**: recover partial mutations from actual state instead of blindly rerunning them.
6. **Concurrency Locking**: serialize overlapping mutations or use explicit concurrency/idempotency controls.
7. **Lease / Ownership TTL**: bound locks and claims and provide stale-owner recovery.
8. **Context Recovery**: restore goal, decisions, commands, evidence, blockers and checkpoints after interruption.
9. **Change Budget**: bound expected change scope and re-evaluate unexpected architectural expansion.
10. **Risk Escalation Ladder**: increase verification rigor from read-only work through irreversible/data-destructive operations.
11. **Invariant Before Side Effect**: verify critical preconditions before consequential mutation.
12. **Postcondition Verification**: verify actual resulting state, not merely command success.
13. **Decision Journal**: preserve concise evidence-backed records for consequential autonomous decisions without secrets.
14. **Negative Knowledge**: retain verified failed approaches and known limitations to prevent repeating invalid paths.
15. **Cost Awareness**: bound time, compute, API usage, retries and operational risk.
16. **Priority Arbitration**: resolve competing goals using intent, safety, dependency criticality and deadlines.
17. **Stale Intent Detection**: detect when a long-running goal or its assumptions are obsolete before continuing.
18. **Autonomous End-State**: prove goal satisfaction, terminal dependencies, verified postconditions, accounted side effects, reconciled evidence and absence of remaining in-scope work.

Governing principle: **AUTONOMY IS CONTINUOUS, BUT SCOPE IS LOCKED.**

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

## Verified lessons (negative knowledge)

Durable, evidence-backed facts. Do not rediscover them by repeating the failure.

### L1. `/opt/madworld` has no `.git` — this is expected, not a defect
`deploy-on-push.yml` deploys with `rsync -a --checksum --exclude='.git/'` and writes the deployed revision to `/opt/madworld/.github-deployed-sha`. Remote probes reporting `GIT_DIR=absent` / `GIT_HEAD=unknown` are therefore normal. Verify the deployed revision with `cat /opt/madworld/.github-deployed-sha`, never with `git -C /opt/madworld rev-parse HEAD`.
Evidence: `cmd-20260908-151500-server-runtime-current`, `cmd-20260908-153800-server-runtime-followup`.

### L2. Local HTTP/HTTPS probes on the server need explicit flags
Host nginx answers `http://127.0.0.1/...` with `301` to HTTPS, and the local certificate is self-signed, so `curl -fsSL` fails with exit `60` before any application evidence is collected. Use `curl -k` for loopback checks (or probe the upstream port directly over plain HTTP) and keep the public-hostname check as a separate probe.
Evidence: `cmd-20260908-153700/153800-server-runtime-followup` (exit 60), `cmd-20260908-154100-server-runtime-tls-followup` (exit 0, 502 observed).

### L3. Wrap every remote probe in `timeout(1)` — a single hang burns the whole budget
`cmd-20260908-160000-production-502-diagnose` ran unbounded `nginx -T`, `ss` and `docker ps` inside a 3-minute budget, hit the broker's `subprocess` timeout and returned `TIMEOUT` with **empty stdout** — zero diagnostic value. Bound each probe individually (`timeout 10 ...`), prefer a bounded `grep` over `/etc/nginx/sites-enabled` to a full `nginx -T`, and size `TIMEOUT_MINUTES` above the sum of the per-probe budgets. Under memory pressure `docker` calls are the most likely hang.

### L4. The API upstream is `127.0.0.1:8090`, not `8000`
`ops/docker-compose.deploy.yml` publishes the API container as `127.0.0.1:${API_HOST_PORT:-8090}:8000` because host port 8000 belongs to another project on the shared host. An nginx `502` means that loopback upstream is unreachable. Diagnose with `curl http://127.0.0.1:8090/health` plus container `State.Status` / `State.OOMKilled` / `RestartCount`. The API container has a 768 MB memory limit on a host that has been observed at 22 Gi/23 Gi used.

### L5. `deploy-on-push.yml` does not restart the application
It rsyncs files, restarts `madworld-remote-operator.service`, runs the executor and triggers the queue broker. It never runs `docker compose up`. A green deploy run is therefore **not** evidence that the API is running, and merging to `main` does not by itself repair or restart a downed API.

### L6. An agent without `actions: write` must reach the queue through `main`
`remote-operator-workflow-dispatch.yml` checks out `ref: main` and only reads `.github/remote-operator/REQUESTS/` from `main` (push to `main` + cron `*/5`). A restricted agent token gets `HTTP 403: Resource not accessible by integration` from `POST /actions/workflows/{id}/dispatches`. The working path is: commit the request record on the working branch, open a PR to `main`, and let the scheduled broker consume it after merge. Do not report `NOT EXECUTED` before that route has been offered.

### L7. Agent tokens cannot push `.github/workflows/**` — ship a *fresh* patch instead
A GitHub App / Arena token push containing a workflow file is rejected with `refusing to allow a GitHub App to create or update workflow ... without workflows permission`. The repository's sanctioned workaround is `docs/patches/` (see its README). Two traps verified on 2026-09-08:
- the stored patch had gone **stale** (`git apply --check` failed on both hunks), so the documented recovery path silently did not work — always re-verify `git apply --check` against current `HEAD` and refresh the patch;
- `backend/tests/test_workflow_yaml_validity.py` marks the affected workflow **strict-xfail while the patch file exists**, so a stale-but-present patch keeps CI green and hides the breakage. Refreshing the patch (not deleting it) preserves the guard; deleting it after the owner applies the fix is what flips the guard back to enforcing.

Resolved instance (2026-09-08): `.github/workflows/remote-operator.yml` was invalid YAML on `main` (heredoc body/terminator at column 0 inside `run: |`), producing zero-job startup-failure runs and making the documented `remote-operator.yml` SSH path undispatchable. Repaired directly on `main` by commit `7190ccd` (heredoc indentation); verified 15/15 workflows parse at `6ec1c4b` and all guard tests pass. The stale patch files (including `remote-operator-yaml-heredoc-fix.patch`) were removed in PR #23 and `test_workflow_yaml_validity.py` no longer applies the pending-patch strict-xfail — the guard now enforces unconditionally. Never reintroduce a pending-patch marker that can silently xfail a genuinely broken workflow.

## Handoff invariant
Before completion, the agent must confirm the skill was loaded and applied, check existing lessons, preserve important evidence, and leave durable knowledge required by the next agent. A future agent should not have to rediscover an important known fact by repeating an already documented failure.
