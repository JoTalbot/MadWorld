# MadWorld Decision Log

This is the durable rationale record for consequential architecture and operational decisions. Chat history is not authoritative.

## Decision format

Each consequential decision should record:

- **Date**
- **Decision**
- **Context**
- **Alternatives considered**
- **Reason**
- **Evidence**
- **Impact**
- **Revisit condition**
- **Status**

Do not record secrets or sensitive credentials.

## D-001 — Remote Operator is the canonical server channel

- **Date:** 2026-09-07
- **Decision:** use GitHub -> Actions -> SSH -> server -> command -> result -> GitHub for MadWorld server operations.
- **Context:** multiple server-access paths existed during earlier development.
- **Alternatives considered:** ad-hoc SSH; TRIGGERcmd; manual terminal execution.
- **Reason:** one auditable execution path with terminal evidence, bounded execution and root verification.
- **Evidence:** `.github/workflows/remote-operator.yml`, reusable workflow, queue protocol and verified E2E runs.
- **Impact:** server operations must use Remote Operator unless technically impossible or requiring inherent owner/legal approval.
- **Revisit condition:** only if a replacement provides equal or stronger execution, audit and evidence guarantees.
- **Status:** VERIFIED.

## D-002 — Project Skill is mandatory and evolving

- **Date:** 2026-09-07
- **Decision:** `docs/skills/MADWORLD_AGENT_SKILL.md` is required onboarding and durable project memory for every agent.
- **Context:** important operational experience was previously distributed across chats and logs.
- **Alternatives considered:** chat-only memory; static README instructions; optional agent notes.
- **Reason:** preserve verified experience and prevent repeated failures across agents.
- **Evidence:** `AGENTS.md`, `docs/CHATGPT_AGENT_RULES.md`, project Skill.
- **Impact:** new reusable verified knowledge must be added during the same logical work batch.
- **Revisit condition:** only if a stronger durable project-memory mechanism replaces it without losing compatibility.
- **Status:** VERIFIED.

## D-003 — Command queue remains append-only

- **Date:** 2026-09-07
- **Decision:** `.github/remote-operator/COMMANDS.txt` is immutable audit history; execution state belongs to the executor/result system.
- **Context:** rewriting historical PENDING records could fabricate execution history.
- **Alternatives considered:** rewriting PENDING to CANCELLED; deleting stale records; sorting/compacting the queue.
- **Reason:** preserve auditability and prevent accidental execution/state fabrication.
- **Evidence:** queue protocol, state-manager behavior and stale-PENDING audit.
- **Impact:** stale history requires explicit executor-owned quarantine/retirement logic.
- **Revisit condition:** only with a verifiable append-only lifecycle preserving historical records.
- **Status:** VERIFIED.

## D-004 — Isolated rehearsals must not touch production data

- **Date:** 2026-09-07
- **Decision:** capacity and DR rehearsals use isolated ephemeral infrastructure.
- **Context:** production safety must coexist with meaningful operational evidence.
- **Alternatives considered:** live production stress; direct production restore tests.
- **Reason:** measure behavior without risking production data or service stability.
- **Evidence:** DR and full-capacity Remote Operator results explicitly report production DB untouched.
- **Impact:** isolated results remain environment-specific and cannot invent production thresholds.
- **Revisit condition:** production testing requires an explicit maintenance window, rollback plan and owner authorization.
- **Status:** VERIFIED.

## D-005 — Release evidence is gate-based, not narrative-based

- **Date:** 2026-09-07
- **Decision:** important release gates require concrete evidence references and explicit status.
- **Context:** a green command/workflow does not imply release readiness.
- **Alternatives considered:** single global green flag; prose-only release summary.
- **Reason:** technical execution, live environment checks and owner/legal decisions are independent predicates.
- **Evidence:** `ops/FINAL_RELEASE_DECISION.md` and accumulated CI/Remote Operator evidence.
- **Impact:** unknown or external gates remain `NOT VERIFIED`, `UNKNOWN` or `PARTIALLY VERIFIED` until actually evidenced.
- **Revisit condition:** if release governance changes, update the gate model and this log together.
- **Status:** VERIFIED.

## D-006 — Bound Android smoke execution without weakening release gates

- **Date:** 2026-09-08
- **Decision:** move the emulator boot/install/launch lifecycle into a locally testable helper with deadlines, terminal evidence and owned-process cleanup; deliver the workflow wiring through the existing permission-aware patch process.
- **Context:** four old Release Gate runs remained at emulator boot while current CI was queued; the live wait and parts of the older patch's diagnostics were unbounded. Direct cancellation returned HTTP 403.
- **Alternatives rejected:** another stale rerun; an unbounded software-emulator fallback; dropping API jobs or marking fixture tests as device PASS; bypassing workflow-write restrictions.
- **Impact:** keep API 26/29/32/35 and final gate dependencies; cap parallel runner use and cancel superseded per-ref candidates only after the workflow change is applied. Production and owner decisions are unchanged.
- **Evidence:** `ops/B10_ANDROID_MATRIX_RECOVERY_2026-09-08.md`, helper regression tests and pending-patch/live-workflow contract guards.
- **Status:** PARTIALLY VERIFIED — local behavior verified; patch application and actual Android CI remain required.

## Maintenance

When a consequential decision changes, append a new decision rather than silently rewriting history. Mark superseded decisions and link the replacement when applicable.
