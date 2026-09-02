# MadWorld Improvement Backlog

## Working policy — persistent across chats

This file is the persistent source of truth for improvement proposals and implementation decisions. A new chat must read and follow this policy instead of requiring the user to restate it.

1. When a materially useful improvement is discovered during analysis or implementation, record it in this backlog immediately.
2. For every product-changing improvement, record materially different implementation variants before selecting one. At minimum consider Minimal, Systemic, Advanced and Hybrid where applicable.
3. New product-changing improvements start as `PLANNED`; they are not considered approved merely because they appear in the backlog.
4. In the chat, present newly discovered improvements and ask the user whether to apply them. Do not silently implement product-changing improvements.
5. After the user selects a variant, change the item to `ACCEPTED`, record the selected variant and implement it.
6. Bug fixes, security fixes and non-product-changing refactors may be applied directly when they improve correctness or safety without changing the intended game design.
7. When implementation is complete, record the implementation status, important deferred parts and tests/verification in the backlog.
8. Never delete an accepted or planned improvement merely because it is deferred. Preserve the decision history.

## IMP-020 — Authoritative time + due-job scheduling
- Status: ACCEPTED — Hybrid
- Selected: injectable authoritative clock + deterministic due-job scheduler now; durable worker orchestration later.

## IMP-023 — Versioned domain events
- Status: ACCEPTED — Hybrid
- Selected: stable event envelope + schema registry now; compatibility/migration tooling later.

## IMP-026 — Observability foundation
- Status: ACCEPTED — Hybrid
- Selected: structured command records + metrics primitives now; production telemetry pipeline later.

## IMP-027 — Reconnect/resume
- Status: ACCEPTED — Hybrid
- Selected: explicit resume cursor + deterministic reconciliation result now; persisted session/event feed later.

## IMP-028 — Offline command delivery
- Status: ACCEPTED — Hybrid
- Selected: stable UUID journal + exact-retry semantics now; durable mobile queue/richer conflict handling later.

## IMP-029 — Regional player markets
- Status: ACCEPTED — Hybrid
- Selected: regional player order book first, NPC liquidity/simulation later.
- Status after implementation: COMPLETE for the selected slice.

## IMP-061 — Inventory authority
- Status: ACCEPTED
- Selected: server-authoritative inventory with transactional persistence and idempotent mutations.

## IMP-062 — Item definitions
- Status: ACCEPTED
- Selected: stable UUID item definitions with immutable identity and condition-aware stacks.

## IMP-063 — Wallet/ledger authority
- Status: ACCEPTED
- Selected: append-only ledger plus authoritative wallet balance and idempotent commands.

## IMP-064 — Crafting jobs
- Status: ACCEPTED
- Selected: persistent jobs with authoritative timestamps and deterministic scheduler.

## IMP-065 — Outbox delivery
- Status: ACCEPTED
- Selected: transactional outbox with leases, retries and dead-letter handling.

## IMP-066 — API idempotency
- Status: ACCEPTED
- Selected: request-hash checked idempotency records with exact replay.
- Status after implementation: COMPLETE for the selected slice.

## IMP-067 — In-memory transactional semantics
- Status: ACCEPTED — Hybrid
- Selected: snapshot/restore rollback semantics now; database remains authoritative for production.

## IMP-068 — Player bootstrap vertical slice
- Status: ACCEPTED — Hybrid
- Selected: atomic character + starter vehicle + required account foundations now; settlement/tutorial/world provisioning remains separate.

## IMP-069 — Player state snapshot API
- Status: ACCEPTED — Hybrid
- Selected: deterministic gameplay snapshot now; world/session feed later.
- Status after implementation: COMPLETE for the selected slice.

## IMP-070 — Android authoritative-state client
- Status: ACCEPTED — Hybrid
- Selected: typed client + repository + ViewModel + cache now; offline journal/reconciliation later.

## IMP-071 — Persistent player sessions
- Status: ACCEPTED — Hybrid
- Selected: persistent session boundary now; production auth security later.

## IMP-072 — Player-boundary session enforcement
- Status: ACCEPTED — Hybrid — COMPLETE for selected slice
- Remaining production auth work: refresh/revocation, device binding and scoped credentials.

## IMP-073 — Regional market matching concurrency hardening
- Status: COMPLETE — Technical hardening
- Verification: commit `367b950d6ab0b0c7d24c450a2f965dd257df7d4c`; CI #177 passed.

## IMP-074 — Vehicle repair vertical slice
- Status: COMPLETE — Hybrid
- Selected: systemic repair job + extensible component/quality foundations for later combat.
- Implementation: authoritative repair jobs, resource consumption, server time, idempotency and guarded completion.
- Verification: PR #2 merged to `main`; CI #206 passed after the early-completion durability regression was fixed.
- Deferred: full component-aware combat damage, repair-quality progression, mechanic skills and facility modifiers.

## IMP-075 — Legacy vehicle repair API migration
- Status: PLANNED — Product/API change; not approved
- Goal: retire the legacy direct vehicle-repair endpoint without breaking existing clients unexpectedly.
- Variants:
  1. Minimal: remove it in the next breaking API release.
  2. Systemic: redirect/translate legacy requests into authoritative repair jobs and document migration.
  3. Advanced: versioned migration with compatibility window, telemetry, deprecation headers and sunset release.
  4. Hybrid: compatibility adapter + deprecation headers/telemetry now, removal after migration criteria are met.
- Recommendation: Hybrid.
- Acceptance: requires explicit product decision.

## IMP-076 — Component-aware vehicle damage
- Status: COMPLETE — Advanced + Systemic; maximum-option scope
- Goal: replace total-durability-only damage with persistent component condition, armor-aware damage types, component destruction and gameplay effects while retaining total durability as the aggregate compatibility surface.
- Variants considered:
  1. Minimal: component data only.
  2. Systemic: persistent component state and component-specific damage/repair.
  3. Advanced: damage types, armor mitigation, destruction states and gameplay effects.
  4. Hybrid: systemic persistence plus advanced combat model incrementally.
- Selected by user: `3 + 2`, interpreted as Advanced + Systemic, with maximum available options included in the implementation scope.
- Implementation: engine, hull, wheels and fuel-system components; kinetic/explosive/fire/impact damage types; per-component armor; destruction state; component-derived aggregate durability; engine/mobility/fuel-efficiency effects; component repair; authoritative API and transactional persistence adapter.
- Verification: PR #3 merged to `main` as merge commit `61ae299ea6380b0f945a8c6a860190bf4f982da4`.
- Deferred after this slice: richer hit-location simulation, weapon-specific penetration tables, repair quality progression, mechanic skills, facility modifiers and advanced combat telemetry.

## IMP-077 — Authoritative Contract System
- Status: ACCEPTED — Hybrid
- Selected by user: Hybrid, with systemic architecture and maximum useful Phase 1 vertical-slice scope.
- Goal: establish server-authoritative contracts as a persistent gameplay/economic boundary that can later support logistics, factions, corporations and dynamic-world systems.
- Variants considered:
  1. Minimal: contract templates, lifecycle, reward and five starter contracts.
  2. Systemic: immutable terms, escrow/reservation, cancellation/expiration, partial execution, penalties, concurrency and economic events.
  3. Advanced: dynamic generation, NPC/faction/player/corporate issuers, reputation, collateral, multi-objective and multi-stage contracts, route constraints and analytics.
  4. Hybrid: systemic contract boundary now, with Phase 1 delivery validation and five deterministic templates; richer issuers, escrow, partial execution and dynamic generation added as later slices.
- Implementation status: Phase 1 vertical slice implemented using the existing authoritative transactional job boundary, inventory authority and wallet ledger. Five deterministic templates, acceptance, ownership checks, immutable terms in job metadata, deadline, cancellation, delivery validation, cargo consumption, reward payment, idempotency and contract events are included.
- Verification pending: CI.
- Deferred: dedicated contract persistence/repository, escrow and collateral, partial execution, penalties, player/NPC/corporate issuers, reputation, multi-objective contracts, dynamic generation, route constraints and advanced contract telemetry.
