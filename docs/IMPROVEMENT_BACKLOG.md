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

### Phase 3 completion
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
- Implemented: typed state, authoritative API parsing, ViewModel refresh and territory panel.
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

## PHASE 6 — Dynamic World

### Variant decision record
- Initial variants: Minimal / Systemic / Advanced / Hybrid.
- Full variant comparison and acceptance boundary are preserved in `docs/PHASE6_WORLD_SIMULATION_PLAN.md`.
- Selected: **Hybrid**.
- Approval: user approved the recommended Hybrid batch for IMP-117 → IMP-134 as one batch.

### Phase 6 completion
- IMP-117 World Simulation Layer: COMPLETE — Hybrid foundation.
- IMP-118 NPC factions: COMPLETE — Hybrid foundation.
- IMP-119 Faction regional state and diplomacy: COMPLETE — Hybrid foundation.
- IMP-120 Regional shortages and surpluses: COMPLETE — Hybrid foundation.
- IMP-121 Dynamic world events: COMPLETE — Hybrid.
- IMP-122 Dynamic convoy events: COMPLETE — Hybrid foundation.
- IMP-123 Resource discoveries: COMPLETE — Hybrid foundation.
- IMP-124 Disasters: COMPLETE — Hybrid foundation.
- IMP-125 Catastrophe zones: COMPLETE — Hybrid foundation.
- IMP-126 World-state-driven missions: COMPLETE — Hybrid foundation.
- IMP-127 World simulation scheduler/ticks: COMPLETE — Hybrid service boundary.
- IMP-128 World event history/replayability: COMPLETE — Hybrid foundation.
- IMP-129 Economy ↔ world feedback loop: COMPLETE — Hybrid foundation.
- IMP-130 Territory ↔ NPC/world integration: COMPLETE — Hybrid foundation.
- IMP-131 Telemetry, anti-abuse and simulation safeguards: COMPLETE — Hybrid foundation.
- IMP-132 Android authoritative world-state client: COMPLETE — Hybrid foundation.
- IMP-133 Adversarial simulation/invariant tests: COMPLETE — Hybrid foundation.
- IMP-134 Intelligence services / market foundation: COMPLETE — Hybrid foundation.

## MASTER PRODUCTION BATCH PROGRAM

Status: **ACCEPTED — execute as the project's production completion sequence.**

The user approved the master implementation plan consisting of B1 → B10. Individual new product-changing expansions discovered during execution remain subject to the existing variant/approval policy unless they are already within the accepted batch scope.

### B1 — World Integration
- World → Economy feedback
- World → Territory effects
- Convoy lifecycle
- Resource discovery lifecycle
- Faction regional dynamics
- Dynamic mission grammar
- World event → outbox bridge
- Deterministic replay foundation
- World lag telemetry
- Integration/invariant tests

### B2 — Gameplay Integration
- Travel/economy integration
- Vehicle/world interaction
- Vehicle/territory interaction
- Combat/world encounters
- Convoy combat and escort
- Salvage/economy integration
- Recovery/reconnect-safe gameplay

### B3 — Advanced Economy
- Full regional order books
- Partial fills/matching correctness
- Price/volume/liquidity history
- Regional supply/demand accounting
- Refining/production chains
- Facility capacity and maintenance
- Skill specialization
- Warehouse/logistics economics
- Economy stress and reconciliation tests

### B4 — NPC Faction Simulation
- Strategic observation
- Priority evaluation
- Decision engine
- Military/economic/logistics actions
- Diplomacy transitions
- Persistent NPC consequences
- Deterministic bounded decision cadence

### B5 — Territory Warfare
- Claim costs/upkeep
- Contest/capture/abandonment
- Infrastructure damage/repair
- Checkpoints and supply lines
- Objective chains/reinforcement
- Siege/disruption foundations
- Alliance warfare
- Occupation economic effects

### B6 — Finance & Provenance
- Secured credit
- Collateral
- Repayment/default/recovery
- Insurance
- Financing/investment
- Asset provenance
- Quality/manufacturer history
- Financial abuse telemetry

### B7 — Full Android Game
**Status: COMPLETE — accepted exit gate passed.**
- Critical MMO state screens: implemented foundation for Base, World, Fleet, Market, Crew and Territory.
- Authoritative command flow: allowlisted offline dispatcher with idempotency keys.
- Offline queue: durable intent queue with deduplication and FIFO delivery.
- Reconnect/resume: queue drains after authenticated refresh; authoritative state is refreshed afterward.
- Stale-state handling: version guard protects settlement snapshots.
- Notifications: persistent local/in-app notification center for synchronization and failures.
- Localization/accessibility: resource foundation and core accessibility semantics.
- Verification: Android CI #64 green, including unit tests and debug APK assembly; Backend CI #492 green.
- Deferred: push/device tokens, full localization extraction, full accessibility audit, rich mutation screens and OS-level background worker. These remain explicit follow-up work and are not claimed as implemented.

### B8 — Security, Anti-Abuse & Reliability
**Status: COMPLETE — accepted exit gate passed.**
- Mutation endpoint audit completed across API route modules.
- Authentication/ownership boundary retained through authenticated-player dependencies and existing corporation membership checks.
- Existing database-backed idempotency remains authoritative for supported financial, inventory, market and social mutations.
- Transport-level replay guard added for repeated explicit mutation request identifiers with bounded TTL.
- Global bounded sliding-window rate limiting added at API boundary.
- Security response headers added for API responses.
- Bounded abuse-scoring foundation added with deterministic points and decay.
- Circuit-breaker primitive added with bounded failure threshold and recovery window.
- Security regression suite added for rate limiting, replay protection, circuit recovery, abuse decay and parameter validation.
- Existing transactional, uniqueness, row-lock and optimistic-concurrency defenses remain authoritative for money/item/race-sensitive mutations.
- Verification: Backend CI green on B8 completion boundary; Android was unchanged by this backend-only security batch.
- Deferred to B9: distributed rate-limit state, persistent abuse scoring/moderation, production circuit telemetry/tuning, advanced wash-trading/reward-farming classifiers, WAF/CDN controls and device fingerprinting.

### B9 — Scale, Operations & LiveOps
- Production service definitions
- Worker deployment
- Catch-up policy
- Observability and alerting
- Load/stress tests
- Android device matrix
- Analytics
- Push notifications
- Backup/restore
- Disaster recovery
- Live operations tooling

### B10 — Final Release Gate
- Full gameplay regression
- Backend/Android/integration CI
- Security and exploit regression
- Replay verification
- Load verification
- Backup/restore verification
- Release artifact verification
- Production configuration
- Rollback/incident procedures
- Release checklist

### Batch completion rule

No batch is marked COMPLETE merely because code exists. The batch must satisfy its exit gate, applicable Definition of Done, tests and CI verification. Deferred items remain explicitly recorded and are not silently treated as complete.
