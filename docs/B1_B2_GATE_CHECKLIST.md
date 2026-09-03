# B1/B2 Gate Checklist

## Gate scope

B1 and B2 are considered complete only when the integrated world/gameplay path is authoritative, transactional, idempotent, ownership-guarded, and covered by automated tests.

## B1

- [x] World simulation tick produces deterministic state.
- [x] World events bridge transactionally into outbox.
- [x] World event consumption has an idempotency fence.
- [x] Economy signals and territory effects are derived from world events.
- [x] World region identifiers are bridged to gameplay region identifiers before territory writes/reads.
- [x] Convoy and discovery lifecycles advance through the world tick pipeline.
- [x] Dynamic mission generation has source-event uniqueness.
- [x] Replay/state hashing and telemetry are persisted.
- [x] Resource seed activates scrap, fuel, and water for every world region.

## B2

- [x] Travel plan is server-authoritative and ownership guarded.
- [x] Travel risk incorporates world and territory modifiers.
- [x] Departure atomically consumes reserved vehicle fuel.
- [x] Active travel uniqueness prevents concurrent vehicle travel sessions.
- [x] Terminal travel outcomes require an active TRAVELLING session, except explicit cancellation.
- [x] Encounters require a TRAVELLING session.
- [x] Encounter resolution is idempotent at the state-transition boundary.
- [x] LOST travel creates an idempotent recovery case.
- [x] Recovery claim is ownership guarded and transactionally coupled to the authoritative wallet ledger.
- [x] Recovery cost cannot create an invalid zero-value ledger entry.
- [x] Combat uses the authoritative vehicle damage service for persisted damage/events.
- [x] Salvage/recovery uses existing vehicle state primitives rather than a parallel asset model.
- [x] Reconnect/retry paths are safe through idempotent command boundaries.

## Verification

- CI must apply all migrations from 001 through the current migration and pass the complete backend test suite.
- CI must run against PostgreSQL, not only mocks.
- The gate must record the exact HEAD SHA and workflow result.
- A previous green run on an older SHA does not satisfy the gate.

## Remaining gate action

Run and verify CI for the final B1/B2 HEAD. Do not merge until the workflow is completed successfully on that exact SHA.
