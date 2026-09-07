# MadWorld Agent Skill

**Status:** REQUIRED / EVOLVING  
**Scope:** all AI agents, coding agents, reviewers, operators, release workers, and automated agents working on `JoTalbot/MadWorld`.

## 1. Mandatory use

Every new worker/agent MUST read and apply, before making changes:

1. `AGENTS.md`
2. `docs/CHATGPT_AGENT_RULES.md`
3. `docs/REMOTE_OPERATOR.md`
4. `.github/remote-operator/QUEUE.md`
5. this skill: `docs/skills/MADWORLD_AGENT_SKILL.md`

A worker that has not loaded this skill is **NOT READY TO MODIFY THE REPOSITORY**.

The skill is part of the repository's operating contract, not optional onboarding material.

## 2. Evolving project knowledge

This file is a living operational skill and durable project memory. It must become better as the project is worked on.

Whenever an agent discovers experience that is useful beyond the immediate task, the agent MUST capture it in this skill during the same logical work batch whenever practical.

Examples of knowledge worth preserving:

- a failure mode and its verified cause;
- a reliable diagnostic or verification procedure;
- an important repository/server dependency;
- a CI/CD or deployment trap;
- a Remote Operator behavior or limitation;
- a recovery or rollback procedure that was actually verified;
- a test pattern that prevents a previously observed regression;
- a release-gate lesson;
- a security or operational invariant;
- a non-obvious constraint that future agents must know;
- a failed approach that should not be repeated.

Do not record guesses as experience. Record verified facts, evidence, and explicitly marked hypotheses separately.

## 3. Learning loop

For every non-trivial task:

`ANALYZE -> IMPLEMENT -> TEST -> VERIFY -> LEARN -> DOCUMENT -> RE-TEST -> REPORT`

The `LEARN` and `DOCUMENT` stages are mandatory when new reusable knowledge appears.

The agent must ask itself:

- What did we learn?
- Would another agent benefit from knowing this before touching the project?
- Did an unexpected failure reveal a reusable rule?
- Did we discover a better verification method?
- Did an existing rule become obsolete or incomplete?

If yes, update this skill immediately rather than leaving the knowledge only in chat, an issue, or an ephemeral log.

## 4. Safe skill maintenance

- Preserve existing useful knowledge.
- Prefer additive, precise changes over wholesale rewrites.
- Remove or correct obsolete knowledge only when the new fact is verified.
- Never store secrets, credentials, tokens, private keys, cookies, personal data, or sensitive server values.
- Never claim a procedure is verified unless evidence exists.
- Include concise evidence references where useful, such as workflow/run IDs, commit SHAs, filenames, or test names.
- Keep operationally important lessons close to the relevant section.

## 5. Required structure for new lessons

Add reusable lessons under `## 7. Project Experience and Lessons` using this format:

### YYYY-MM-DD — Short lesson title

- **Situation:** what happened.
- **Finding:** verified cause or behavior.
- **Rule:** what future agents must do.
- **Verification:** test/run/commit/evidence.
- **Status:** `VERIFIED`, `PARTIALLY VERIFIED`, `NOT VERIFIED`, `FAILED`, or `UNKNOWN`.

If a lesson is only a temporary hypothesis, label it explicitly as such and do not turn it into a mandatory rule until verified.

## 6. New-agent completion requirement

Before declaring a task complete, every agent must:

- confirm that this skill was loaded;
- apply its relevant rules;
- add newly discovered reusable knowledge;
- check whether any existing lesson needs correction;
- leave the repository in a state where the next agent can continue without relying on private chat history.

The repository is the durable memory of the project. Chat is not.

## 7. Project Experience and Lessons

### 2026-09-07 — Repository is the durable project memory

- **Situation:** MadWorld has been developed through many autonomous work cycles involving code, CI, deployment, server operations, Android, release gates and recovery.
- **Finding:** important operational knowledge is easily lost when it exists only in a chat session.
- **Rule:** every reusable verified lesson from project work belongs in this skill and in the appropriate permanent documentation. New agents must recover project context from the repository before acting.
- **Verification:** this skill and the mandatory references in `AGENTS.md` and `docs/CHATGPT_AGENT_RULES.md`.
- **Status:** VERIFIED.

### 2026-09-07 — Autonomous work means complete the connected stage

- **Situation:** the project repeatedly required multi-step audit/fix/test/deploy/verify work.
- **Finding:** stopping after the first defect or after merely starting an operation leaves the system in an ambiguous state.
- **Rule:** for `+`, one-batch, do-everything and equivalent requests, continue through `ANALYZE -> IMPLEMENT -> TEST -> VERIFY -> FIX -> RE-TEST -> REPORT`; add `LEARN -> DOCUMENT` whenever new experience appears.
- **Verification:** `AGENTS.md` and `docs/CHATGPT_AGENT_RULES.md`.
- **Status:** VERIFIED.

### 2026-09-07 — Remote Operator is the server channel

- **Situation:** server access was standardized around GitHub Actions, SSH and the server-side queue executor.
- **Finding:** ad-hoc SSH creates a second execution path and weakens auditability.
- **Rule:** server-side technical actions intended for MadWorld must use Remote Operator: GitHub -> Actions -> SSH -> server -> command -> result -> GitHub.
- **Verification:** `.github/workflows/remote-operator.yml`, `.github/workflows/remote-operator-reusable.yml`, `docs/REMOTE_OPERATOR.md` and verified E2E runs.
- **Status:** VERIFIED.

### 2026-09-07 — Remote Operator runs as root when configured

- **Situation:** production deployment and Remote Operator evidence showed root execution on `arm-server-01`.
- **Finding:** SSH transport user identity alone is insufficient proof of root runtime.
- **Rule:** verify actual runtime EUID/executor evidence. The configured Remote Operator may use the SSH account and `sudo -n` path to execute as root.
- **Verification:** deployment evidence recorded `transport_euid=0` and root runtime; workflow result records include `run_as: root`.
- **Status:** VERIFIED.

### 2026-09-07 — Never treat workflow dispatch as command success

- **Situation:** a workflow can be successfully dispatched while the actual server command later fails, times out, or never produces a result.
- **Finding:** workflow launch status is not terminal command evidence.
- **Rule:** wait for workflow status, job status, terminal execution state, exit code, stdout, stderr, result.json/result record, artifacts, executor/server identity and duration.
- **Verification:** Remote Operator result protocol and workflow-dispatch broker.
- **Status:** VERIFIED.

### 2026-09-07 — Workflow-dispatch broker provides a connector-independent path

- **Situation:** direct workflow dispatch of the old Remote Operator path returned HTTP 422 despite the workflow containing `workflow_dispatch`.
- **Finding:** the available connector did not reliably provide direct dispatch for that workflow.
- **Rule:** use the repository's workflow-dispatch broker/queue path when direct connector dispatch is unavailable. Never claim manual dispatch if it was not actually performed.
- **Verification:** successful wrapper E2E: workflow run `34116823670`, job `101729418126`, artifact `remote-operator-result`, result exit code 0, root on `129.213.177.56`.
- **Status:** VERIFIED.

### 2026-09-07 — Remote Operator command queue is append-only

- **Situation:** `.github/remote-operator/COMMANDS.txt` is the canonical human/agent-facing command queue.
- **Finding:** rewriting queue history destroys auditability and can fabricate execution state.
- **Rule:** append new commands only; unique immutable `COMMAND_ID`; new records start `PENDING`; do not reorder/delete/rewrite history; terminal state is executor-owned.
- **Verification:** `.github/remote-operator/COMMANDS.txt` and `.github/remote-operator/QUEUE.md`.
- **Status:** VERIFIED.

### 2026-09-07 — Historical orphan PENDING commands are dangerous

- **Situation:** old queue entries remained `PENDING` without executor state files, including historical production-final diagnostics.
- **Finding:** the previous executor behavior could treat an orphan `PENDING` entry as executable on a later scan.
- **Rule:** historical/orphan `PENDING` entries must never be silently executed. Reconciliation must distinguish fresh submissions from stale history and preserve the append-only queue.
- **Verification:** repository audit; `ops/remote-operator/executor.sh`; reconciliation tooling; `ops/remote-operator/RECONCILIATION.md`.
- **Status:** PARTIALLY VERIFIED. Code-level guard/audit exists; final server E2E reconciliation still requires verification.

### 2026-09-07 — Missing CREATED_AT makes historical PENDING disposition ambiguous

- **Situation:** older queue records lack `CREATED_AT`, while the canonical format requires it for new commands.
- **Finding:** age-based stale detection cannot safely infer creation time for legacy records.
- **Rule:** do not fabricate timestamps. Legacy orphan entries without `CREATED_AT` require explicit safe disposition/quarantine logic rather than automatic execution or invented age.
- **Verification:** queue audit and reconciliation test fixture.
- **Status:** VERIFIED.

### 2026-09-07 — Queue reconciliation must not mutate history

- **Situation:** a tempting fix would rewrite old `PENDING` records to `CANCELLED`.
- **Finding:** doing so would fabricate executor state and violate the audit-trail rule.
- **Rule:** reconciliation audit is read-only until an executor-owned retirement/quarantine mechanism can create a verifiable terminal record without rewriting history.
- **Verification:** `ops/remote-operator/RECONCILIATION.md`, reconciliation workflow and Issue #18.
- **Status:** VERIFIED.

### 2026-09-07 — Cancellation is executor-state based

- **Situation:** `state-manager.sh request-cancel` only accepts `RUNNING` state.
- **Finding:** it cannot safely cancel an arbitrary orphan `PENDING` command because no execution attempt exists.
- **Rule:** do not call `request-cancel` as a fake cleanup mechanism for orphan PENDING records. Add a dedicated, auditable quarantine/retirement lifecycle if automatic handling is needed.
- **Verification:** `ops/remote-operator/state-manager.sh`.
- **Status:** VERIFIED.

### 2026-09-07 — Remote Operator has bounded execution and timeout behavior

- **Situation:** commands may be sync or async and can hang.
- **Finding:** executor tracks process state, deadline, cancellation, timeout and terminal result.
- **Rule:** every dependent operation waits for terminal result or timeout; timeout must be explicitly recorded and process state checked.
- **Verification:** `ops/remote-operator/executor.sh` and Remote Operator workflows.
- **Status:** VERIFIED.

### 2026-09-07 — Result evidence belongs in result records/artifacts

- **Situation:** stdout/stderr can become large and runtime evidence must survive queue processing.
- **Finding:** queue is an audit trail, while result records/artifacts hold detailed runtime output.
- **Rule:** preserve command identity in queue and store full stdout/stderr plus structured result in the dedicated result/artifact path. Do not dump secrets into either location.
- **Verification:** `result-manager.sh`, Remote Operator workflow artifacts and `remote-operator-results` branch.
- **Status:** VERIFIED.

### 2026-09-07 — Root/server result must identify executor, server and duration

- **Situation:** identical commands may run on different workers or at different times.
- **Finding:** an exit code without execution identity is insufficient operational evidence.
- **Rule:** verify command ID, attempt ID, server, executor, timestamps, duration, exit code, stdout/stderr and result path.
- **Verification:** Remote Operator `result.json` schema and successful E2E results.
- **Status:** VERIFIED.

### 2026-09-07 — Deployment verification must prove exact commit

- **Situation:** a deployment workflow may succeed while deploying an unexpected revision if branch/head assumptions are stale.
- **Finding:** release verification needs exact source revision plus service/runtime evidence.
- **Rule:** before and after production deployment, verify branch/HEAD, deployed commit, service health, systemd state, runtime executor identity and smoke tests.
- **Verification:** deployment run `33980832923`, deployment evidence on `arm-server-01`, and later deployment run `34123308558`.
- **Status:** VERIFIED.

### 2026-09-07 — Deployment fixed world-tick defects and regression coverage matters

- **Situation:** real deployment exposed two world-tick defects that were not adequately represented by earlier isolated checks.
- **Finding:** production deployment revealed runtime behavior that required code fixes and regression tests.
- **Rule:** after production fixes, rerun deployment verification and retain regression coverage protecting the discovered behavior. Do not assume isolated tests cover all deployed runtime paths.
- **Verification:** release decision evidence records the two world-tick defects, their deployment fixes and regression coverage.
- **Status:** VERIFIED.

### 2026-09-07 — Backend and Android CI gates are separate evidence

- **Situation:** MadWorld has backend and Android components with separate build/test requirements.
- **Finding:** a green backend run does not prove Android readiness, and vice versa.
- **Rule:** inspect backend tests/CI and Android unit/debug/release build gates separately before release.
- **Verification:** verified backend CI success and Android unit/debug/release APK build evidence.
- **Status:** VERIFIED.

### 2026-09-07 — Node deprecation warning did not equal CI failure

- **Situation:** GitHub Actions emitted a Node 20 deprecation warning while the relevant CI execution still succeeded.
- **Finding:** warning and failure must not be conflated.
- **Rule:** inspect actual step conclusion and exit status; treat warnings as technical debt unless they cause a failed gate.
- **Verification:** prior Backend/Actions run with successful job conclusion despite Node warning.
- **Status:** VERIFIED.

### 2026-09-07 — DR rehearsal must not touch production database

- **Situation:** backup/restore was rehearsed using isolated PostgreSQL 16 containers.
- **Finding:** recovery capability can be measured safely without modifying production data.
- **Rule:** DR rehearsal uses an isolated ephemeral environment; explicitly verify `PRODUCTION_DATABASE_TOUCHED=false`.
- **Verification:** command `cmd-20260907-162000-dr-isolated-rehearsal-direct-v4`, workflow run `34119610023`, job `101734376559`, result commit `897a980`.
- **Status:** VERIFIED.

### 2026-09-07 — DR restore verification is concrete

- **Situation:** isolated backup/restore rehearsal executed `pg_dump`, `pg_restore`, `SELECT 1`, and migration count checks.
- **Finding:** a successful restore is more useful when the restored database is queried after restore.
- **Rule:** require `restore_verified=1`, migration count, and `backup_restore_verified=true` in recovery evidence.
- **Verification:** migration_count `3`, restore_verified `1`, backup_restore_verified=true.
- **Status:** VERIFIED.

### 2026-09-07 — Measured DR RTO was about one second in isolation

- **Situation:** the isolated DR rehearsal completed rapidly.
- **Finding:** measured RTO is useful evidence but is environment-specific.
- **Rule:** record measured RTO with environment details and never present an isolated RTO as guaranteed production RTO.
- **Verification:** `MEASURED_RTO_SECONDS=1.015`, `ENVIRONMENT=ephemeral_postgres16_containers`.
- **Status:** VERIFIED.

### 2026-09-07 — Read-only capacity rehearsal results

- **Situation:** isolated PostgreSQL 16 + API + world worker was exercised with 20 concurrent read-only clients for 30 seconds.
- **Finding:** the environment processed 5060/5060 successful requests with 168.667 RPS, p50 90.835 ms, p95 126.978 ms, p99 219.084 ms; DB connections 12; world tick lag 0.
- **Rule:** preserve measured throughput/latency as evidence, but do not invent a production threshold from it.
- **Verification:** `cmd-20260907-123000-capacity-isolated-v8`; production DB untouched.
- **Status:** VERIFIED.

### 2026-09-07 — Rate limiting successfully bounded abusive read traffic

- **Situation:** isolated read-only test used a normal 120/minute rate limit.
- **Finding:** 6620 attempts produced 120 successes and 6500 rejections, demonstrating containment rather than backend overload.
- **Rule:** capacity testing must include rate-limit behavior and distinguish rejected abuse from server errors.
- **Verification:** `cmd-20260907-122000-capacity-isolated-v6`; production DB untouched.
- **Status:** VERIFIED.

### 2026-09-07 — Mutation capacity was measured separately

- **Situation:** isolated POST `/api/v1/sessions` mutation test ran 20 concurrent clients for 15 seconds.
- **Finding:** 2496 successes, 0 errors, 166.400 RPS, p50 115.976 ms, p95 156.161 ms, p99 196.668 ms; unauthenticated access returned 401.
- **Rule:** read-only capacity is not sufficient. Measure mutation latency, error rate and authentication behavior separately.
- **Verification:** `cmd-20260907-164500-mutation-capacity-v5`, duration 24.41 s.
- **Status:** VERIFIED.

### 2026-09-07 — Idempotency and replay protection were explicitly tested

- **Situation:** authenticated bootstrap/mutation requests were repeated with identical idempotency/request identifiers.
- **Finding:** identical idempotency replay returned the same successful result, while X-Request-ID replay was contained with first `201` and second `409`.
- **Rule:** capacity and release testing must verify both idempotent replay semantics and duplicate-request containment.
- **Verification:** `cmd-20260907-170000-full-capacity-v5`; `IDEMPOTENCY_REPLAY_PASS=true`; replay containment true.
- **Status:** VERIFIED.

### 2026-09-07 — Full isolated capacity rehearsal combined the important gates

- **Situation:** an isolated rehearsal combined API readiness, authenticated idempotency, concurrent mutation, authentication rejection, duplicate-request containment and world tick.
- **Finding:** 2515/2515 mutation requests succeeded, 167.667 RPS, p50 116.065 ms, p95 154.022 ms, p99 181.860 ms, 0 errors; DB connections 12; world tick lag 0.
- **Rule:** use a combined rehearsal to detect interactions between API, database, auth/idempotency and world worker, while keeping the environment isolated.
- **Verification:** `cmd-20260907-170000-full-capacity-v5`, duration 26.387 s, production DB untouched.
- **Status:** VERIFIED.

### 2026-09-07 — Isolated capacity does not close the production capacity gate by itself

- **Situation:** isolated capacity and mutation tests are healthy and measured.
- **Finding:** release still requires a production-equivalent threshold decision and distinct queue-depth/unbounded-growth evidence.
- **Rule:** keep B10 capacity at `PARTIALLY VERIFIED` until those gates are explicitly defined and evidenced. Never invent thresholds.
- **Verification:** `ops/FINAL_RELEASE_DECISION.md` and B10 evidence.
- **Status:** VERIFIED.

### 2026-09-07 — World tick must remain serialized and authoritative

- **Situation:** capacity rehearsals ran API traffic concurrently with the world worker.
- **Finding:** worker ticks remained bounded, serialized and showed zero lag in the isolated tests.
- **Rule:** preserve a single authoritative world-tick execution path and verify tick duration/lag under concurrent API load.
- **Verification:** read-only and full-capacity rehearsals; world ticks 1–7 and 1–4 respectively with lag 0.
- **Status:** VERIFIED.

### 2026-09-07 — Android production matrix remains a separate release gate

- **Situation:** Android unit/debug/release builds pass, but the production server has no adb/emulator and the device/API-level matrix is not fully exercised there.
- **Finding:** build success does not equal physical-device compatibility or push/crash/analytics readiness.
- **Rule:** keep Android matrix, physical-device behavior, push, crash and analytics gates explicitly separate and do not mark them passed without evidence.
- **Verification:** `ops/FINAL_RELEASE_DECISION.md` release-gate state.
- **Status:** VERIFIED as a release-process rule; the Android production matrix itself remains UNVERIFIED.

### 2026-09-07 — Public API/TLS health was verified before release decision

- **Situation:** production API was checked after deployment.
- **Finding:** public `/health/ready` returned HTTP 200 with DB health and migrations applied; TLS verification returned code 0 with Google Trust Services; no failed systemd units were present.
- **Rule:** public release verification must include API readiness, database health, migration status, TLS trust and systemd health.
- **Verification:** release decision evidence: public `https://api.autosklo.org.ua/health/ready` HTTP 200, `migrations_applied=41`, TLS Verify return code 0.
- **Status:** VERIFIED.

### 2026-09-07 — Backup automation is a release prerequisite

- **Situation:** production backup timer was checked as part of release readiness.
- **Finding:** daily backup timer was active/enabled and latest backup checksum was verified.
- **Rule:** verify both backup scheduler state and the latest backup artifact/checksum before treating production recovery readiness as healthy.
- **Verification:** `ops/FINAL_RELEASE_DECISION.md` production audit evidence.
- **Status:** VERIFIED.

### 2026-09-07 — Release decision correctly remains GO AFTER REMAINING OWNER ACTIONS

- **Situation:** technical baseline is green for many gates, but external and owner-controlled gates remain.
- **Finding:** technical health alone does not authorize public release.
- **Rule:** preserve `GO AFTER REMAINING OWNER ACTIONS` until capacity threshold decision, Android matrix/device evidence, privacy/terms/data-safety/deletion legal review, incident/on-call and rollback ownership, and severity-5 disaster-clamp interpretation are resolved where release-required.
- **Verification:** `ops/FINAL_RELEASE_DECISION.md` current release decision.
- **Status:** VERIFIED.

### 2026-09-07 — Unknown external conditions are never PASS

- **Situation:** some release gates require owner/legal/product decisions or external device/provider conditions.
- **Finding:** absence of evidence is not evidence of success.
- **Rule:** use `NOT VERIFIED`, `PARTIALLY VERIFIED`, `NOT EXECUTED` or `UNKNOWN` as appropriate. Never turn an unknown gate into PASS for convenience.
- **Verification:** release decision documentation and project operating rules.
- **Status:** VERIFIED.

### 2026-09-07 — No production stress without an approved maintenance window

- **Situation:** capacity evidence was gathered in isolated environments.
- **Finding:** production stress could affect real users and data and is unnecessary while isolated evidence is available.
- **Rule:** never perform production load/stress testing without the required owner-approved maintenance window, rollback plan and evidence requirements.
- **Verification:** `ops/LOAD_TEST_PLAN.md`, isolated capacity rehearsals.
- **Status:** VERIFIED.

### 2026-09-07 — Production database must remain outside isolated rehearsals

- **Situation:** DR and capacity work used isolated PostgreSQL 16 containers.
- **Finding:** production DB integrity can be preserved while testing recovery and load behavior.
- **Rule:** isolated rehearsals must explicitly prove production DB was not touched; do not substitute production DB access for a missing test environment.
- **Verification:** DR and full-capacity result records explicitly report production DB untouched.
- **Status:** VERIFIED.

### 2026-09-07 — Preserve safety boundaries around unrelated infrastructure

- **Situation:** MadWorld server shares infrastructure with unrelated systems.
- **Finding:** broad cleanup or infrastructure changes can damage unrelated services even if MadWorld itself is healthy.
- **Rule:** do not touch Octopus/Liza infrastructure, unrelated PostgreSQL, existing Docker networks/volumes, host port 8000, UFW, or perform global Docker cleanup unless explicitly required and authorized.
- **Verification:** repeated operational constraints used during MadWorld work.
- **Status:** VERIFIED.

### 2026-09-07 — TRIGGERcmd was retired in favor of Remote Operator

- **Situation:** server control initially involved TRIGGERcmd/Tailscale/terminal alternatives.
- **Finding:** the project standardized on Remote Operator as the auditable server execution channel.
- **Rule:** do not reintroduce TRIGGERcmd for MadWorld server execution. Use Remote Operator and improve that path when a capability is missing.
- **Verification:** project operating decisions and current Remote Operator architecture.
- **Status:** VERIFIED.

### 2026-09-07 — Human manual steps should become automation where technically possible

- **Situation:** several deployment, diagnostics and server-management tasks could otherwise require manual terminal work.
- **Finding:** manual steps are harder to reproduce and audit.
- **Rule:** automate technical manual steps through Remote Operator whenever technically possible. Reserve manual intervention for technical impossibility or inherently required owner/legal approval.
- **Verification:** `AGENTS.md`, `docs/CHATGPT_AGENT_RULES.md` and Remote Operator workflow.
- **Status:** VERIFIED.

### 2026-09-07 — Connector limitations must be reported honestly

- **Situation:** the GitHub connector did not expose every Actions operation, including direct workflow dispatch in some paths.
- **Finding:** pretending a missing connector capability succeeded creates false operational evidence.
- **Rule:** if the connector cannot execute an operation, mark it `NOT EXECUTED` and route through Remote Operator/broker or improve the operator path first.
- **Verification:** observed 422 direct-dispatch limitation and successful broker E2E.
- **Status:** VERIFIED.

### 2026-09-07 — Secrets never belong in project memory

- **Situation:** Remote Operator depends on SSH secrets and production infrastructure credentials.
- **Finding:** project memory and agent skill are durable repository content and therefore unsafe places for credentials.
- **Rule:** secrets remain only in GitHub Secrets; never copy them into skill, queue, logs, artifacts, issues, commits or reports.
- **Verification:** Remote Operator secret contract.
- **Status:** VERIFIED.

### 2026-09-07 — Keep RC intact until final release gates are actually closed

- **Situation:** the repository has a release candidate and technical gates can become green before all external gates are ready.
- **Finding:** changing release metadata prematurely creates false readiness.
- **Rule:** preserve the RC while required release gates remain open. Do not create a final release solely because CI/deployment is green.
- **Verification:** current `v0.1.0-rc1` prerelease state and `FINAL_RELEASE_DECISION.md`.
- **Status:** VERIFIED.

### 2026-09-07 — A successful command is not automatically a release PASS

- **Situation:** Remote Operator can execute a command successfully while the broader release gate remains unresolved.
- **Finding:** execution evidence proves execution, not product/release approval.
- **Rule:** evaluate each release gate independently using its own evidence and preserve owner/legal/product decisions as human-controlled.
- **Verification:** release gate documentation and Remote Operator evidence rules.
- **Status:** VERIFIED.

### 2026-09-07 — Documentation must evolve with architecture

- **Situation:** Remote Operator, queue semantics, release gates and recovery procedures changed during development.
- **Finding:** stale documentation can cause a new agent to use a retired path or unsafe assumption.
- **Rule:** whenever operational behavior changes, update `AGENTS.md`, the permanent operating rules, Remote Operator docs, queue docs and this skill as applicable in the same logical work cycle.
- **Verification:** current synchronized documentation set.
- **Status:** VERIFIED.

### 2026-09-07 — Current project completion is a release-gate problem, not a basic deployment problem

- **Situation:** backend, Android builds, deployment, production health, backup, TLS, DR and isolated capacity have substantial positive evidence.
- **Finding:** remaining blockers are mostly release-governance, external-matrix and production-equivalent capacity evidence rather than inability to deploy the software.
- **Rule:** do not keep changing working production code merely to manufacture progress. Focus next work on the actual remaining gates and their evidence.
- **Verification:** current `ops/FINAL_RELEASE_DECISION.md`.
- **Status:** VERIFIED.

## 8. Current agent checklist

Before changing MadWorld:

- [ ] Read `AGENTS.md`.
- [ ] Read `docs/CHATGPT_AGENT_RULES.md`.
- [ ] Read `docs/REMOTE_OPERATOR.md`.
- [ ] Read `.github/remote-operator/QUEUE.md`.
- [ ] Read this skill.
- [ ] Determine current branch and HEAD from GitHub.
- [ ] Inspect relevant code/tests/workflows before editing.
- [ ] Identify whether the task requires Remote Operator.
- [ ] Never expose or persist secrets.

During work:

- [ ] Use ANALYZE -> IMPLEMENT -> TEST -> VERIFY -> FIX -> RE-TEST.
- [ ] For server tasks, queue through Remote Operator.
- [ ] Wait for terminal result or timeout.
- [ ] Verify stdout/stderr/exit code/result/artifacts.
- [ ] Keep production and isolated environments clearly separated.
- [ ] Preserve append-only queue history.
- [ ] Do not treat unknown gates as PASS.
- [ ] Record new reusable experience in this skill.

Before completion:

- [ ] Re-run relevant tests after fixes.
- [ ] Verify exact commit/head.
- [ ] Verify CI/deployment where applicable.
- [ ] Update affected documentation.
- [ ] Update this skill with new verified lessons.
- [ ] Leave enough durable evidence for the next agent.
- [ ] Report STATUS / REPOSITORY / BRANCH / COMMIT / OPERATION / SERVER / VERIFIED / FAILED / EVIDENCE / REMAINING.

## 9. Maintenance rule

This skill is intentionally never "finished". New agents are expected to extend it with verified experience, while preserving historical lessons and correcting obsolete rules when evidence requires it.

**Project memory rule:** if a future agent has to rediscover an important operational fact by repeating a failure that a previous agent already experienced, the skill/documentation process has failed and must be improved.
