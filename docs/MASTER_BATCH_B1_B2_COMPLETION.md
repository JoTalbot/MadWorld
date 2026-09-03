# Master Batch B1 → B2

## Scope implemented in this batch

### B1 World Integration
- Authoritative `world_events` are bridged transactionally into the existing outbox.
- Persistent per-consumer idempotency fence prevents duplicate application.
- World resource seed covers scrap, fuel and water for every world region.
- World→Economy normalized signals are persisted without allowing the simulator to mutate player wallets/orders.
- World→Territory effects are bounded and represented as durable modifiers.
- Convoy lifecycle has spawn/travel/resolution timing and deterministic arrival/loss progression.
- Discovery lifecycle has tick-based expiry.
- Faction influence, hostility and logistics supply move deterministically with bounded values.
- Dynamic mission grammar covers shortage, convoy escort, discovery recovery and disaster response.
- Replay checkpoints contain canonical state/event hashes.
- World tick duration/lag and integration counters are persisted as telemetry.
- Worker runs the integrated pipeline under the existing PostgreSQL advisory lock.

### B2 Gameplay Integration
- Authoritative player travel sessions: planned → travelling → resolved.
- Idempotent travel planning and authenticated vehicle ownership checks.
- Route danger incorporates world/territory modifiers with hard bounds.
- Travel encounter records cover faction, convoy, disaster, ambush and discovery outcomes.
- Encounter `LOST` is an authoritative terminal outcome that resolves the linked travel session in the same PostgreSQL transaction.
- Lost travel destroys the vehicle, zeroes persisted component condition, and produces a durable salvage/recovery case with an idempotency fence.
- Recovery claims are player-scoped, wallet-locked, state guarded, and exactly-once debited by idempotency key.
- Recovery restores the destroyed vehicle to `stored` and persisted components to a valid recovered minimum.
- Travel/encounter/recovery retries are idempotent for the same terminal state.
- Vehicle cargo capacity is enforced during travel planning through the authoritative `vehicles.cargo_capacity` field.
- B2 travel/encounter/recovery API is registered under `/api/v1/travel`.
- World simulation remains separated from player-owned inventory, wallet and vehicle mutation.

## Verification

- Migration invariant tests cover B1/B2 schema additions, travel state guards, encounter guards, and cargo capacity.
- B2 API registration test covers the public route surface.
- Travel validation tests cover invalid command rejection and recovery behavior.
- PostgreSQL integration tests exercise persisted encounter loss, travel loss, vehicle/component destruction, recovery creation, duplicate terminal requests, exactly-once recovery debit, retry behavior, and cargo-capacity boundary enforcement.
- Final CI must be checked on the latest batch head before merging.

## Architectural guardrails

1. World simulation owns world state only.
2. Domain consumers claim world events transactionally before applying side effects.
3. Player asset mutation requires an authenticated gameplay command.
4. Retries must be safe and idempotent.
5. All bounded simulation values are constrained both in application logic and PostgreSQL.
6. Replay hashes are audit signals, not client authority.
7. Encounter loss and travel loss share one authoritative transactional state transition.

## Remaining work after B2

- B3 advanced economy: full order-book/liquidity/history and production economics.
- B4 autonomous NPC faction decision engine and diplomacy.
- B5 territory warfare.
- B6 finance/provenance.
- B7 full Android gameplay surfaces.
- B8 security/anti-abuse hardening.
- B9 production-scale operations.
- B10 final release gate.
