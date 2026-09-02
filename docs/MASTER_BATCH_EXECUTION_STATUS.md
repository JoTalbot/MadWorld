# MadWorld — Master Batch Execution Status

## Contract

The project has an accepted B1→B10 production completion program. The canonical scope is `docs/BATCH_IMPLEMENTATION_CONTRACT.md` and the persistent decision history is `docs/IMPROVEMENT_BACKLOG.md`.

## Execution state

- B1: NOT COMPLETE — execution preparation/audit started
- B2: NOT COMPLETE
- B3: NOT COMPLETE
- B4: NOT COMPLETE
- B5: NOT COMPLETE
- B6: NOT COMPLETE
- B7: NOT COMPLETE
- B8: NOT COMPLETE
- B9: NOT COMPLETE
- B10: NOT COMPLETE

## Non-negotiable rule

No batch may be marked COMPLETE because its design exists. Completion requires implementation, migrations where applicable, tests, security/invariant coverage, documentation, applicable Backend/Android CI verification, failure repair, and a final repository audit.

## Current technical baseline

Phase 6 already provides deterministic world simulation, persistent world state, faction/region state, regional resource pressure, world events, convoy/discovery/disaster/mission records, simulation history, a trusted world tick worker and authoritative world-state client surfaces. The next implementation work must integrate those foundations rather than duplicate them.

## B1 execution order

1. World→Economy event/outbox bridge
2. World→Territory effects
3. Convoy lifecycle state machine
4. Resource discovery lifecycle
5. Faction regional tick dynamics
6. Dynamic mission grammar and invalidation
7. Deterministic replay/state hashes
8. World lag/worker telemetry
9. Integration, concurrency, retry and invariant tests
10. Backend CI, repair, rerun and final audit

## B2→B10 gate discipline

Each subsequent batch begins only after the previous batch passes its exit gate. Cross-batch integration is allowed, but a failure in one domain must not be hidden by declaring another domain complete.

## Product-scope rule

New product-changing ideas discovered during implementation remain subject to the existing Minimal/Systemic/Advanced/Hybrid approval policy unless already covered by the accepted B1→B10 contract. Bugs, security fixes and non-product refactors may be fixed directly.
