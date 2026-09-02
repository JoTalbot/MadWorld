# Phase 6 — Trusted World Tick Worker

## Purpose

The Dynamic World simulation is authoritative and must advance independently of player traffic. `backend/scripts/world_tick_worker.py` is the trusted service entry point.

## Runtime contract

- `MADWORLD_DATABASE_URL` is required.
- `MADWORLD_WORLD_TICK_SECONDS` controls the interval; default is 60 seconds and values below 5 seconds are clamped to 5.
- The worker executes one transaction per tick.
- PostgreSQL `pg_try_advisory_xact_lock` prevents overlapping workers from advancing the same world clock concurrently.
- `world_simulation_state` remains row-locked inside `simulate_tick`.
- A failed tick rolls back completely and can be retried.
- Player API calls cannot advance the global tick. `/api/v1/world-simulation/tick` intentionally returns 403.

## Determinism and retries

Each `(season, tick)` receives a deterministic SHA-256-derived seed. Simulation decisions use that seed instead of process randomness.

A retry that supplies an already-completed `expected_tick` returns the persisted `world_simulation_ticks` record. A request for a future or otherwise stale tick is rejected.

## Operational command

From `backend/`:

```bash
PYTHONPATH=. python scripts/world_tick_worker.py
```

The worker is intentionally a separate process rather than FastAPI startup background work. This avoids one simulation clock per API replica, because apparently even fictional worlds deserve fewer split-brain incidents than production systems.

## Architecture boundary

The worker invokes the Phase 6 simulation core. The simulator may create authoritative world events, discoveries, disasters, catastrophe zones and dynamic missions, but does not directly mutate player wallets, inventories, vehicles or market orders. Future economy/territory/NPC integrations should consume explicit world events or domain commands transactionally.

## Next hardening layer

- deploy the worker as a dedicated service/process in production;
- add scheduler health/lag telemetry;
- add controlled catch-up policy after prolonged downtime;
- connect world events to economy and territory domain commands through the outbox/event pipeline.
