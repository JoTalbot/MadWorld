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
## IMP-023 — Versioned domain events
- Status: ACCEPTED — Hybrid
## IMP-026 — Observability foundation
- Status: ACCEPTED — Hybrid
## IMP-027 — Reconnect/resume
- Status: ACCEPTED — Hybrid
## IMP-028 — Offline command delivery
- Status: ACCEPTED — Hybrid
## IMP-029 — Regional player markets
- Status: COMPLETE — Hybrid selected slice.
## IMP-061 — Inventory authority
- Status: ACCEPTED
## IMP-062 — Item definitions
- Status: ACCEPTED
## IMP-063 — Wallet/ledger authority
- Status: ACCEPTED
## IMP-064 — Crafting jobs
- Status: ACCEPTED
## IMP-065 — Outbox delivery
- Status: ACCEPTED
## IMP-066 — API idempotency
- Status: COMPLETE for selected slice.
## IMP-067 — In-memory transactional semantics
- Status: ACCEPTED — Hybrid
## IMP-068 — Player bootstrap vertical slice
- Status: ACCEPTED — Hybrid
## IMP-069 — Player state snapshot API
- Status: ACCEPTED — Hybrid
## IMP-070 — Android authoritative-state client
- Status: ACCEPTED — Hybrid
## IMP-071 — Persistent player sessions
- Status: ACCEPTED — Hybrid
## IMP-072 — Player-boundary session enforcement
- Status: COMPLETE for selected slice.
## IMP-073 — Regional market matching concurrency hardening
- Status: COMPLETE — Technical hardening.
## IMP-074 — Vehicle repair vertical slice
- Status: COMPLETE — Hybrid.
## IMP-075 — Legacy vehicle repair API migration
- Status: COMPLETE — Hybrid.
## IMP-076 — Component-aware vehicle damage
- Status: COMPLETE — Advanced + Systemic.
## IMP-077 — Contract system
- Status: COMPLETE — Advanced + Systemic.
## IMP-078 — Expedition system
- Status: COMPLETE — Advanced + Systemic.
## IMP-079 — Settlement / base-point gameplay loop
- Status: COMPLETE — Hybrid.
## IMP-080 — Android settlement gameplay client
- Status: COMPLETE — Hybrid.
## IMP-081 — Phase 2 Economy Foundation
- Status: COMPLETE — Hybrid.
## IMP-082 — Economy-to-Gameplay Integration
- Status: COMPLETE — Hybrid.

## PHASE 3 — Vehicles & Combat
### IMP-083 — Modular vehicle fitting
- Status: COMPLETE — Hybrid foundation.
### IMP-084 — Vehicle stats and systems
- Status: COMPLETE — Hybrid foundation.
### IMP-085 — Weapon system
- Status: COMPLETE — Hybrid foundation.
### IMP-086 — Authoritative vehicle combat
- Status: COMPLETE — Advanced + Systemic foundation.
### IMP-087 — Salvage
- Status: COMPLETE — Hybrid foundation.
### IMP-088 — Vehicle recovery
- Status: COMPLETE — Hybrid foundation.
### IMP-089 — Convoys
- Status: COMPLETE — Hybrid foundation.
### IMP-090 — Phase 3 Android integration
- Status: COMPLETE — Hybrid foundation.
### Phase 3 verification note
- Status: IMPLEMENTED as one batch on `main`; production hardening remains tracked by follow-up work.

## PHASE 4 — Social Sandbox

### IMP-091 — Corporations / gangs
- Status: COMPLETE — Hybrid foundation selected by user command to execute Phase 4 as one batch.
- Implemented: corporation identity, owner boundary, code/name/tax invariants, membership persistence.

### IMP-092 — Roles and permissions
- Status: COMPLETE — Hybrid foundation.
- Implemented: canonical role set and permission vocabulary with domain validation.

### IMP-093 — Shared wallets
- Status: COMPLETE — Hybrid.
- Implemented: corporation-owned wallet support, authoritative balance/transfer commands, deterministic locking, immutable ledger, idempotency, audit/outbox integration.
- Deferred product work: funding policies and richer treasury/reporting UI.

### IMP-094 — Shared hangars and corporate assets
- Status: COMPLETE — Hybrid.
- Implemented: hangar capacity, custody registration/move/assignment, row locking, optimistic version checks and manufacturer provenance binding.
- Deferred product work: full physical vehicle/item ownership transfer semantics.

### IMP-095 — Alliances
- Status: COMPLETE — Hybrid social-core lifecycle.
- Implemented: alliance creation, invitations, accept/decline/leave lifecycle, membership overview and authoritative persistence.
- Deferred product work: alliance-level territorial/economic effects and richer governance.

### IMP-096 — Diplomacy
- Status: COMPLETE — Advanced foundation.
- Implemented: directed relations, standings, trade/transit flags and hostile-trade invariant.
- Deferred product work: world/NPC/market effects.

### IMP-097 — Social contracts
- Status: COMPLETE — Hybrid.
- Implemented: participant validation, authoritative lifecycle, escrow creation, wallet locking, balanced ledger settlement, release/refund, idempotency, audit/outbox and state-integrity enforcement.
- Deferred product work: physical delivery verification beyond the accepted social-core financial settlement.

### IMP-098 — Social reputation
- Status: COMPLETE — Hybrid social-core slice.
- Implemented: bounded authoritative mutation, immutable history and contract-driven reputation propagation on successful settlement.
- Deferred product work: world/NPC/economy-wide propagation.

### IMP-099 — Manufacturers / brands
- Status: COMPLETE — Hybrid.
- Implemented: corporation brand identity, bounded quality rating and asset manufacturer provenance binding.

### IMP-100 — Phase 4 Android integration
- Status: COMPLETE — Hybrid social management surface.
- Implemented: typed social state, capability discovery, corporation creation/overview, corporate wallet balance/refresh and manufacturer/brand creation UI.
- Deferred product work: full alliance, asset and contract mutation screens.

### IMP-101 — Phase 4 social lifecycle hardening
- Status: COMPLETE — Hybrid.
- Implemented: contract transition invariants, reputation mutation invariants, escrow/invitation state validation and persistence for escrow/history/invitations.

### IMP-102 — Phase 4 social database integrity hardening
- Status: COMPLETE — Technical hardening.
- Implemented: partial unique indexes for reputation targets, one-primary-corporation membership constraint, escrow transition trigger and escrow-backed contract state consistency trigger.

### IMP-103 — Phase 4 authoritative financial/social operations
- Status: COMPLETE — Hybrid social-core scope.
- Implemented: corporate wallet operations, alliance lifecycle, hangar/asset accounting, escrow settlement, contract-driven reputation propagation, manufacturer provenance and Android social-management surface.
- Product-changing expansions remain deferred and preserved as future work.

### Phase 4 verification note
- Main branch head before Phase 5 planning: `e67349854c903637fcf4f4a0b1d9b15f146d6d40`.
- Backend CI #330: SUCCESS on the exact Phase 4 completion head.
- Android CI #37: SUCCESS. Debug APK assembled successfully.
- Phase 4 social core is COMPLETE. Remaining items listed above are product expansions that intentionally cross into broader world/economic gameplay rather than unfinished Phase 4 correctness.

## PHASE 5 — Territory

> Product-changing Phase 5 design. All items below are `PLANNED` until a variant is explicitly selected. Full design and acceptance boundary: `docs/PHASE5_TERRITORY_PLAN.md`.

### IMP-104 — Settlements and regional identity
- Status: PLANNED.
- Minimal: formalize region/settlement identity around the existing player settlement.
- Systemic: introduce stable world regions and settlement identities usable by economy, logistics and territory.
- Advanced: settlement population/services/condition and strategic value.
- Hybrid: systemic region identity + extensible settlement authority, without premature city-builder simulation.

### IMP-105 — Territory authority model
- Status: PLANNED.
- Minimal: controller field per eligible territory object.
- Systemic: claims + controller state + historical transitions with authoritative lifecycle.
- Advanced: contested control pressure and staged transitions.
- Hybrid: systemic control lifecycle plus extension points for dynamic pressure.

### IMP-106 — Claims and ownership
- Status: PLANNED.
- Minimal: corporation claim/release.
- Systemic: eligibility, conflicts, concurrency, lifecycle and corporate permission enforcement.
- Advanced: claim cost, contest windows and strategic prerequisites.
- Hybrid: systemic claims + bounded contest hooks.

### IMP-107 — Infrastructure ownership
- Status: PLANNED.
- Minimal: ownership of depots/wells/mines.
- Systemic: typed infrastructure, condition, upkeep and control effects.
- Advanced: infrastructure damage, repair queues and strategic dependencies.
- Hybrid: systemic ownership/condition foundation with selected upkeep mechanics.

### IMP-108 — Road and route control
- Status: PLANNED.
- Minimal: route ownership flag.
- Systemic: explicit route graph and controller-derived travel/risk effects.
- Advanced: checkpoints, supply-line pressure and route disruption.
- Hybrid: systemic route graph + bounded control modifier, with disruption deferred.

### IMP-109 — Resource sites
- Status: PLANNED.
- Minimal: persistent resource-site ownership.
- Systemic: typed sites, extraction state and bounded depletion/renewal.
- Advanced: scarcity pressure, discoveries and dynamic regeneration.
- Hybrid: systemic extraction foundation + Phase 6-compatible pressure hooks.

### IMP-110 — Territory taxes and economic modifiers
- Status: PLANNED.
- Minimal: static tax value.
- Systemic: bounded tax/upkeep rules and derived regional economic/travel modifiers.
- Advanced: layered modifiers, exemptions and strategic economic policy.
- Hybrid: bounded systemic modifiers + selected policy hooks, always settled through existing ledger authority.

### IMP-111 — Strategic objectives and scheduled warfare
- Status: PLANNED.
- Minimal: scheduled capture objective.
- Systemic: open/contest/resolve/closed objective lifecycle using authoritative server time.
- Advanced: objective chains, reinforcement windows and alliance participation.
- Hybrid: systemic objective lifecycle + a small set of high-leverage objective types.

### IMP-112 — Territory concurrency and anti-abuse hardening
- Status: PLANNED.
- Minimal: optimistic version checks.
- Systemic: row locking, idempotency, permission checks, invariant tests and replay safety.
- Advanced: abuse scoring, anomaly detection and automated containment.
- Hybrid: systemic correctness + telemetry hooks without speculative automated punishment.

### IMP-113 — Territory telemetry and audit
- Status: PLANNED.
- Minimal: audit each mutation.
- Systemic: typed territory events, control history and economic-effect telemetry.
- Advanced: strategic analytics and anomaly correlation.
- Hybrid: systemic events/telemetry + Phase 6 event contracts.

### IMP-114 — Android Territory state/client
- Status: PLANNED.
- Minimal: read-only territory state.
- Systemic: authoritative map/state plus core claim/control actions.
- Advanced: strategic map, objective planning and rich corporation/alliance controls.
- Hybrid: systemic state + essential mutation actions; richer command UI later.

### IMP-115 — Territory exploit/invariant test suite
- Status: PLANNED.
- Minimal: ownership and concurrency tests.
- Systemic: ownership, claims, taxes, modifiers, objectives, idempotency and financial-boundary tests.
- Advanced: adversarial simulations and long-running state-transition tests.
- Hybrid: systemic invariant suite + selected adversarial cases.

### IMP-116 — Dynamic geography foundation
- Status: PLANNED.
- Minimal: stable graph extension points.
- Systemic: versioned world graph/events consumable by Phase 6.
- Advanced: mutable geography and procedural topology changes.
- Hybrid: versioned graph/event contracts only; actual dynamic geography deferred to World Simulation.

### Phase 5 recommendation
- Recommended variant: **Hybrid**.
- Rationale: implement the durable Systemic territory core plus only the Advanced mechanisms that unlock economy, logistics, social control and Phase 6 World Simulation. Avoid prematurely building a second strategy game inside the MMO.
- Approval boundary: no product-changing Phase 5 implementation is implied by this recommendation. Once Hybrid is selected, the corresponding items can move to `ACCEPTED` and implementation can proceed as one batch.
