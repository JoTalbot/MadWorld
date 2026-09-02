# MadWorld Improvement Backlog

## Working policy — persistent across chats

This file is the persistent source of truth for improvement proposals and implementation decisions. A new chat must read and follow this policy instead of requiring the user to restate it.

1. Record useful improvements immediately.
2. For product-changing improvements, record materially different Minimal, Systemic, Advanced and Hybrid variants where applicable.
3. New product-changing improvements start as `PLANNED`.
4. Present new product-changing improvements in chat and do not silently implement them.
5. After the user selects a variant, change the item to `ACCEPTED`, record it and implement it.
6. Bugs, security fixes and non-product refactors may be applied directly.
7. Record implementation status, deferred work and verification after implementation.
8. Preserve accepted/planned decision history.

## Completed foundation and previous decisions

- IMP-020 Authoritative time + due-job scheduling: ACCEPTED — Hybrid.
- IMP-023 Versioned domain events: ACCEPTED — Hybrid.
- IMP-026 Observability foundation: ACCEPTED — Hybrid.
- IMP-027 Reconnect/resume: ACCEPTED — Hybrid.
- IMP-028 Offline command delivery: ACCEPTED — Hybrid.
- IMP-029 Regional player markets: COMPLETE — Hybrid selected slice.
- IMP-061 Inventory authority: ACCEPTED.
- IMP-062 Item definitions: ACCEPTED.
- IMP-063 Wallet/ledger authority: ACCEPTED.
- IMP-064 Crafting jobs: ACCEPTED.
- IMP-065 Outbox delivery: ACCEPTED.
- IMP-066 API idempotency: COMPLETE for selected slice.
- IMP-067 In-memory transactional semantics: ACCEPTED — Hybrid.
- IMP-068 Player bootstrap vertical slice: ACCEPTED — Hybrid.
- IMP-069 Player state snapshot API: ACCEPTED — Hybrid.
- IMP-070 Android authoritative-state client: ACCEPTED — Hybrid.
- IMP-071 Persistent player sessions: ACCEPTED — Hybrid.
- IMP-072 Player-boundary session enforcement: COMPLETE for selected slice.
- IMP-073 Regional market matching concurrency hardening: COMPLETE — Technical hardening.
- IMP-074 Vehicle repair vertical slice: COMPLETE — Hybrid.
- IMP-075 Legacy vehicle repair API migration: COMPLETE — Hybrid.
- IMP-076 Component-aware vehicle damage: COMPLETE — Advanced + Systemic.
- IMP-077 Contract system: COMPLETE — Advanced + Systemic.
- IMP-078 Expedition system: COMPLETE — Advanced + Systemic.
- IMP-079 Settlement / base-point gameplay loop: COMPLETE — Hybrid.
- IMP-080 Android settlement gameplay client: COMPLETE — Hybrid.
- IMP-081 Phase 2 Economy Foundation: COMPLETE — Hybrid.
- IMP-082 Economy-to-Gameplay Integration: COMPLETE — Hybrid.

## PHASE 3 — Vehicles & Combat

- IMP-083 Modular vehicle fitting: COMPLETE — Hybrid foundation.
- IMP-084 Vehicle stats and systems: COMPLETE — Hybrid foundation.
- IMP-085 Weapon system: COMPLETE — Hybrid foundation.
- IMP-086 Authoritative vehicle combat: COMPLETE — Advanced + Systemic foundation.
- IMP-087 Salvage: COMPLETE — Hybrid foundation.
- IMP-088 Vehicle recovery: COMPLETE — Hybrid foundation.
- IMP-089 Convoys: COMPLETE — Hybrid foundation.
- IMP-090 Phase 3 Android integration: COMPLETE — Hybrid foundation.
- Phase 3: implemented as one batch; production hardening remains follow-up work.

## PHASE 4 — Social Sandbox

- IMP-091 Corporations / gangs: COMPLETE — Hybrid foundation.
- IMP-092 Roles and permissions: COMPLETE — Hybrid foundation.
- IMP-093 Shared wallets: COMPLETE — Hybrid.
- IMP-094 Shared hangars and corporate assets: COMPLETE — Hybrid.
- IMP-095 Alliances: COMPLETE — Hybrid social-core lifecycle.
- IMP-096 Diplomacy: COMPLETE — Advanced foundation.
- IMP-097 Social contracts: COMPLETE — Hybrid.
- IMP-098 Social reputation: COMPLETE — Hybrid social-core slice.
- IMP-099 Manufacturers / brands: COMPLETE — Hybrid.
- IMP-100 Phase 4 Android integration: COMPLETE — Hybrid social management surface.
- IMP-101 Social lifecycle hardening: COMPLETE — Hybrid.
- IMP-102 Social database integrity hardening: COMPLETE — Technical hardening.
- IMP-103 Authoritative financial/social operations: COMPLETE — Hybrid social-core scope.
- Phase 4 verification: Backend CI #330 and Android CI #37 were green on the Phase 4 completion boundary.

## PHASE 5 — Territory

### Variant decision record
- Initial variants: Minimal / Systemic / Advanced / Hybrid.
- Full variant comparison and acceptance boundary are preserved in `docs/PHASE5_TERRITORY_PLAN.md`.
- Selected: **Hybrid**.
- Approval: user selected Hybrid for IMP-104 → IMP-116 as one batch.

### IMP-104 — Regions and settlement territorial identity
- Status: COMPLETE — Hybrid.
- Implemented: stable `world_regions` with seeded authoritative region identity compatible with settlement regions.
- Deferred: full city-builder simulation.

### IMP-105 — Territory authority and controller state
- Status: COMPLETE — Hybrid.
- Implemented: `territory_control` and reconstructible control history with one controller per target scope.
- Deferred: dynamic NPC pressure and staged grand-strategy simulation.

### IMP-106 — Claims and ownership lifecycle
- Status: COMPLETE — Hybrid.
- Implemented: corporation claims, target conflict prevention, optimistic versions and idempotent authoritative commands.
- Deferred: complex claim-cost economy and full warfare prerequisites.

### IMP-107 — Infrastructure ownership and upkeep
- Status: COMPLETE — Hybrid.
- Implemented: typed infrastructure, controller, condition and bounded upkeep state.
- Deferred: infrastructure damage/repair queues and dependency chains.

### IMP-108 — Road control and route effects
- Status: COMPLETE — Hybrid.
- Implemented: explicit route segments with bounded travel-time and risk modifiers.
- Deferred: checkpoints, disruption and supply-line warfare.

### IMP-109 — Resource-site control and extraction
- Status: COMPLETE — Hybrid.
- Implemented: persistent resource sites, capacity/remaining/renewal state, extraction limits, controller authorization and row locking.
- Deferred: world-wide scarcity simulation and discovery generation.

### IMP-110 — Territory taxes and economic/travel modifiers
- Status: COMPLETE — Hybrid foundation.
- Implemented: bounded modifier schema compatible with existing corporate tax and financial authority.
- Deferred: richer policy, exemptions and multi-layer economic simulation.

### IMP-111 — Strategic objectives and scheduled warfare
- Status: COMPLETE — Hybrid foundation.
- Implemented: server-time scheduled/open/contested/resolved/closed objective lifecycle and authoritative resolution.
- Deferred: objective chains, reinforcements and full alliance warfare simulation.

### IMP-112 — Territory concurrency and anti-abuse hardening
- Status: COMPLETE — Hybrid/technical.
- Implemented: uniqueness, row locks, optimistic versions, bounded values, corporate membership authorization and idempotency.
- Deferred: automated abuse scoring/containment.

### IMP-113 — Territory telemetry and audit
- Status: COMPLETE — Hybrid.
- Implemented: persistent territory events plus existing audit/outbox integration.

### IMP-114 — Android Territory state/client
- Status: COMPLETE — Hybrid foundation.
- Implemented: typed state, authoritative API parsing, ViewModel refresh and mobile territory panel.
- Deferred: rich strategic map and complete territory mutation-management UI.

### IMP-115 — Territory exploit/invariant test suite
- Status: COMPLETE — Hybrid foundation.
- Implemented: server-side validation coverage for claims, infrastructure, roads, resources and objective windows.
- Deferred: long-running adversarial simulation suite.

### IMP-116 — Dynamic geography foundation
- Status: COMPLETE — Hybrid extension point.
- Implemented: stable region/entity identifiers and event-oriented territory model suitable for Phase 6 consumers.
- Deferred: procedural topology mutation and autonomous NPC grand strategy.

### Phase 5 verification note
- Migration: `backend/migrations/021_phase5_territory.sql`.
- API: `backend/app/api/phase5_territory_routes.py`.
- Android: `TerritoryState.kt`, territory API parsing, ViewModel refresh and territory panel.
- Tests: `backend/tests/test_phase5_territory.py`.
- Final CI verification is required before declaring the batch green.
