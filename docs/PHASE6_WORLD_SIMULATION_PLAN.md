# MadWorld — Phase 6 World Simulation Plan

## Variant decision

- Initial variants: Minimal / Systemic / Advanced / Hybrid.
- Selected: **Hybrid**.
- Approval: user approved the recommended Hybrid batch for IMP-117 → IMP-134.

## Architecture boundary

World simulation is a server-authoritative producer of world state and world events. It does **not** directly mutate player wallets, inventory, vehicles, ownership or market orders.

Flow:

`World State → Simulation Tick → World Event → Domain Consumer/Command → Transaction → Audit/Outbox → New State`

The Phase 6 foundation therefore separates simulation from player economy mutation and keeps a deterministic seed per `(season,tick)` for replayable tests.

## Hybrid scope implemented

- Persistent simulation season/tick/version state.
- NPC faction catalog and per-region influence, hostility and supply state.
- Regional resource pressure with bounded pressure/trend values.
- Deterministic world-event generation for shortages, convoys, discoveries and disasters.
- Convoy event records with cargo, danger and route endpoints.
- Resource discovery records with bounded quantities and expiry.
- Disaster and catastrophe-zone records with bounded hazard/travel/extraction effects.
- Event-generated supply missions with reward/risk/expiry.
- Simulation tick history and event log for replay/audit foundations.
- Authoritative read API for Android and future web clients.
- Android world-state models, repository, refresh flow and world panel.
- Public game clients cannot advance global simulation time; tick execution is exposed as a trusted service entry point for future scheduler/worker wiring.
- Invariant tests for deterministic seeds/catalog bounds and service-only tick control.

## Explicit non-goals

- Full autonomous grand-strategy AI.
- Full faction warfare resolution and alliance war simulation.
- Procedural geography/topology mutation.
- Direct automatic player payouts, inventory grants or market manipulation.
- Complex NPC production/supply-chain planning.
- Full intelligence market monetization.

These remain candidates for later Phase 6/7 iterations and must not be smuggled into the foundation merely because humans enjoy scope creep.

## Safety/invariants

- Simulation time advances only under a database row lock.
- A stale expected tick is rejected.
- A completed tick is persisted before the state advances.
- World-event generation is deterministic from season/tick seed.
- Numeric pressures, aggression, logistics and hazards are bounded by database checks.
- Player-facing tick mutation is rejected with HTTP 403.
- World events are persisted separately from player-domain aggregates.

## Implementation map

- Migration: `backend/migrations/022_phase6_world_simulation.sql`
- Simulation core: `backend/app/application/phase6_world.py`
- API: `backend/app/api/phase6_world_routes.py`
- Tests: `backend/tests/test_phase6_world.py`
- Android: `WorldState.kt`, `WorldRepository.kt`, `PlayerViewModel.kt`, `MainActivity.kt`

## Deferred follow-up

- Wire `run_world_tick()` into the existing trusted job scheduler/worker.
- Add faction diplomacy state transitions and controlled warfare consumers.
- Connect pressure to actual regional market supply/demand using domain commands.
- Add NPC encounters/convoy combat consumers.
- Add intelligence-service aggregation and player-facing market products.
- Add long-running deterministic replay and adversarial simulation tests.
