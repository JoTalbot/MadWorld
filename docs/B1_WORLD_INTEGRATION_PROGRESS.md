# B1 World Integration Progress

## Completed in this batch

- Transactional `world_events` → existing `outbox_events` bridge via PostgreSQL trigger.
- Persistent `world_event_consumptions` idempotency fence for domain consumers.
- Consumer helper that claims an event and applies a caller-supplied domain command in the same transaction.
- Regional resource pressure seed expanded from scrap-only to scrap, fuel and water without overwriting existing state.
- Migration-level and unit-level invariant coverage for the new foundation.

## Verified

- Backend CI run `33694132268` completed successfully for the initial B1 bridge commit, including PostgreSQL migrations and the complete pytest suite.

## Still gated before B1 completion

- Concrete Economy consumer and market supply/demand integration.
- Concrete Territory consumer and territorial effects.
- Convoy lifecycle transitions and domain commands.
- Discovery lifecycle depletion/expiry.
- Faction influence/hostility/supply dynamics.
- Dynamic mission grammar and invalidation.
- Deterministic replay/state hashes.
- Worker lag/throughput telemetry.
- Full integration/concurrency/retry/adversarial coverage.
- Final CI verification on the complete B1 head.

B1 remains **NOT COMPLETE** until every gate above is implemented and verified.
