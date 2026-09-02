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
- Status: COMPLETE — Hybrid
- Goal: retire the legacy direct vehicle-repair endpoint without breaking existing clients unexpectedly.
- Selected: compatibility tombstone + explicit migration response + deprecation/sunset headers + usage telemetry; removal after migration criteria are met.
- Implementation: legacy `POST /api/v1/vehicles/{vehicle_id}/repair` no longer mutates durability and returns `410 Gone` with machine-readable replacement guidance. The authoritative `repair-job` flow remains the supported mutation path.
- Telemetry: legacy calls emit `legacy_repair_api_used` through the application logger with request ID.
- Documentation: `docs/api-migration.md` defines the migration sequence and sunset policy.
- Verification: dedicated API migration regression test added; existing persistent repair-job tests remain the authoritative behavior coverage.
- Deferred: final deletion of the tombstone after client migration and a future breaking API release.

## IMP-076 — Component-aware vehicle damage
- Status: COMPLETE — Advanced + Systemic; maximum-option scope
- Goal: replace total-durability-only damage with persistent component condition, armor-aware damage types, component destruction and gameplay effects while retaining total durability as the aggregate compatibility surface.
- Variants considered: Minimal, Systemic, Advanced and Hybrid.
- Selected by user: `3 + 2`, interpreted as Advanced + Systemic, with maximum available options included in the implementation scope.
- Implementation: engine, hull, wheels and fuel-system components; kinetic/explosive/fire/impact damage types; per-component armor; destruction state; component-derived aggregate durability; engine/mobility/fuel-efficiency effects; component repair; authoritative API and transactional persistence adapter.
- Verification: PR #3 merged to `main` as merge commit `61ae299ea6380f0b945a8c6a860190190bf4f982da4`.
- Deferred: richer hit-location simulation, weapon-specific penetration tables, repair quality progression, mechanic skills, facility modifiers and advanced combat telemetry.

## IMP-077 — Contract system
- Status: COMPLETE — Advanced + Systemic; maximum-option scope
- Selected by user: `3 + 2`.
- Implementation: persistent contract templates and player instances; lifecycle state machine; authoritative deadlines; sequential multi-objective progression; prerequisite chains; faction/reputation requirements and rewards; risk tiers; deterministic wallet rewards with idempotent reward keys; PostgreSQL persistence; player contract API; gathering-event integration; contract design documentation.
- Verification: dedicated contract lifecycle/progression tests added. Full CI verification runs on the PR.
- Deferred by design: fully procedural world-generated contracts, complex branching narrative content and live economy-driven contract generation.

## IMP-078 — Expedition system
- Status: COMPLETE — Advanced + Systemic; maximum-option scope
- Selected by user: `3 + 2`.
- Variants considered: Minimal, Systemic, Advanced and Hybrid.
- Goal: turn travel into a persistent risk/reward gameplay loop connecting vehicles, fuel, regions, inventory, damage and contracts.
- Implementation: persistent server-side expedition jobs; region/distance/risk planning; authoritative duration and fuel consumption; deterministic stored outcomes; deterministic loot and component-aware vehicle damage; guarded time-based completion with exactly-once resolution; completion audit/outbox event; contract progression hook; authenticated/idempotent API; ownership validation for vehicle and inventory; focused domain/application tests; expedition design documentation.
- Verification: PR #8 merged to `main` as merge commit `63c6b60bddd48912801e5edb493721fb83fd06bd`. PR CI #233 passed with 68 tests passed and 0 failures before merge.
- Deferred by design: dynamic world-generated routes, NPC encounters/combat, convoy/group expeditions, weather/disaster modifiers, insurance/recovery and live-economy-driven loot generation.

## IMP-079 — Settlement / base-point gameplay loop
- Status: COMPLETE — Hybrid
- Goal: add a persistent player home/base that ties vehicle storage, inventory, repair/workshop access, contract acquisition and regional market interaction into a repeatable gameplay loop.
- Variants considered: Minimal, Systemic, Advanced and Hybrid.
- Selected by user: `4`, interpreted as Hybrid.
- Selected scope: persistent settlement foundation with region identity, level, extensible module state and authoritative interaction capabilities for garage, warehouse, workshop, contracts and market; settlement API and transactional PostgreSQL persistence. Building progression, NPC services, production chains and deeper economy modifiers remain extensible follow-up layers.
- Implementation: persistent player settlement state, settlement domain/application boundary, PostgreSQL and in-memory repositories with optimistic concurrency, authenticated settlement snapshot endpoint with lazy provisioning, versioned `settlement.created` audit/outbox event, migration, tests and design documentation.
- Verification: PR #9 merged to `main` as merge commit `a0c1b3701a2e2dc6cc6b67a7dd4399aa5dfbe933`; PR CI #238 passed successfully after fixing a SQLAlchemy migration bind-parsing issue.
- Deferred by design: building upgrade progression, NPC services/population, production chains, territory control and deeper settlement economy modifiers.

## IMP-080 — Android settlement gameplay client
- Status: COMPLETE — Hybrid
- Goal: expose the persistent settlement as the player's primary Android base-point interface and connect the existing authoritative player/session state to settlement capabilities.
- Variants considered: Minimal, Systemic, Advanced and Hybrid.
- Selected by user: `4`, interpreted as Hybrid.
- Selected scope: typed settlement state, authenticated settlement API client, repository/cache support, ViewModel integration and a functional settlement UI showing region, level, module levels and authoritative capabilities for garage, warehouse, workshop, contracts and market. The client remains read-oriented for settlement state and does not fabricate gameplay state locally.
- Implementation: `SettlementState`, settlement fetch/ownership validation in `MadWorldApi`, persistent settlement cache in `PlayerRepository`, settlement refresh in `PlayerViewModel`, and Compose settlement panel integrated into the main player screen. Fixed Compose `RowScope.weight` compilation issue in `CapabilityButton`.
- Verification: PR #10 merged to `main` as merge commit `2334378a7f11b4e5a46069641c910b6ff3ff81be`. Android CI #21 passed; Backend CI #242 passed.
- Deferred by design: building/world visualization, settlement mutation commands, offline settlement command journal/reconciliation, rich building interactions and world-map navigation. These require separate product slices and remain subject to backlog approval.
