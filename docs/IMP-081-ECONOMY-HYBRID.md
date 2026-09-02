# IMP-081 — Phase 2 Economy Foundation

## Selected variant
- Status: ACCEPTED
- Variant: Hybrid
- Selected by user: `4`

## Goal
Build the authoritative Phase 2 economy core that connects settlement storage, refining, production, market history and facilities, while leaving NPC economy simulation and deeper logistics as compatible follow-up layers.

## Hybrid scope
1. Warehouse/storage boundary integrated with settlement and authoritative inventory.
2. Refining recipes and persistent refining jobs using server-authoritative time.
3. Production recipes and persistent production jobs with transactional input reservation and deterministic output.
4. Facility definitions, levels and capability/modifier foundations.
5. Market trade/price-volume history derived from authoritative trades.
6. Economy events, audit/outbox integration and idempotent command boundaries.
7. API and Android read models sufficient to expose economy state without trusting client mutations.
8. Extensibility points for later logistics, skills/specialization and NPC supply/demand simulation.

## Implementation order
Warehouse → Refining → Production → Facility foundation → Price/volume history → economy read models.

## Explicitly deferred
- NPC supply/demand simulation.
- Advanced skills and specialization progression.
- Full logistics/cargo contracts and route simulation.
- Insurance/recovery economy.
- Live economy-driven procedural contract generation.
- Advanced financial systems.

## Acceptance invariants
- Server remains authoritative for quantities, recipes, duration, facility capability and economic results.
- Inputs cannot be consumed twice or duplicated through retries.
- Production/refining completion is exactly-once.
- Failed commands leave no partial economic mutation.
- Market history is derived from committed trades, not client claims.
- Reconnect/read snapshots are deterministic.
- All material mutations remain auditable and compatible with the transactional outbox.

## Verification target
Backend unit/integration tests, idempotency/retry tests, concurrency tests, inventory conservation tests, job completion tests, market-history consistency tests and Android compile/contract tests.
