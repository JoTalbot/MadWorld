# MadWorld — B4/B5 Implementation Status

## Batch B4 — NPC Faction Simulation

Implemented in main:
- deterministic bounded faction observation and action selection;
- persistent planned/executed faction actions;
- faction diplomacy state persistence;
- replay-safe action execution event record;
- authenticated faction API for observation, planning, execution and diplomacy;
- faction decision inputs are derived from authoritative faction and regional pressure state.

## Batch B5 — Territory Warfare

Implemented in main:
- claim cost/upkeep extension points;
- territory checkpoints;
- supply-line persistence with bounded disruption state;
- warfare operations and event history;
- infrastructure damage/repair with optimistic row locking;
- active-operation requirement for infrastructure damage;
- siege/disruption/assault/reinforcement operation types;
- objective resolution can transfer territory control through authoritative state transitions;
- authenticated corporation membership for warfare commands;
- warfare state/query API.

## Security / authority boundary

NPC simulation and territory warfare never write player wallet/inventory state directly. Commands operate through domain-owned persistence and authenticated corporation membership. Infrastructure damage is bound to an active warfare operation in the same region.

## Verification

- Contract tests cover B4/B5 migration, engine and API registration boundaries.
- Backend CI run #465 (`33738715012`) passed on the final B5 correction head `82fca7f50fbd5a4d6db5929f8782b87413979740`.
- Database migrations, application module resolution and the full backend test step all completed successfully.
- B4/B5 are release-gated complete for the current backend scope.

## Deferred / not silently expanded

- sophisticated multi-hop logistics optimization;
- full diplomacy graph and AI personality learning;
- automated upkeep charging and taxation policy engine;
- procedural map topology mutation;
- large-scale alliance battle simulation and client strategic map.

These remain explicit follow-up work rather than hidden scope expansion.
