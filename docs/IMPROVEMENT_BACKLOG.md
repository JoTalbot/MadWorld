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
- Implemented slice: PostgreSQL market orders, sell-item escrow, deterministic price/time/id tie-breaking, transactional matching, buy-side currency reservation, reserve refund after filled limit orders, regional order-book read API, trade history and request-level idempotency by player/key.
- API: `GET /api/v1/market/{region_id}/{item_definition_id}`, `POST /api/v1/market/buy`, `POST /api/v1/market/sell`.
- Deferred: cancellation/release flow, market fees/taxes, NPC liquidity, advanced price simulation, richer order types and production market UI.
- Verification: CI runs #173 and #174 passed after idempotency hardening and conflict regression coverage.
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
- Implementation: market order replay now validates that a reused player-scoped idempotency key represents the same request payload; mismatches return `IDEMPOTENCY_CONFLICT` without mutation.
- Verification: CI #174 passed with explicit conflicting-payload regression coverage.
- Status after implementation: COMPLETE for the selected slice.

## IMP-067 — In-memory transactional semantics
- Status: ACCEPTED — Hybrid
- Selected: snapshot/restore rollback semantics now; database remains authoritative for production.

## IMP-068 — Player bootstrap vertical slice
- Status: ACCEPTED — Hybrid
- Goal: make first login produce one coherent authoritative player state instead of requiring clients to orchestrate several independent commands.
- Variants:
  1. Minimal: client calls character creation and starter-vehicle creation separately.
  2. Systemic: one atomic server-side bootstrap command creates character, starter vehicle, wallet/inventory foundations and returns a snapshot.
  3. Advanced: bootstrap also provisions settlement, starter resources, tutorial state and region assignment.
  4. Hybrid: atomic character + starter vehicle + required account foundations now; settlement/tutorial/world provisioning remains separate.
- Selected: Hybrid. Account wallet and personal inventory foundations are now provisioned transactionally when a session is created or resumed for an existing player; character + starter vehicle remain atomic in bootstrap. Settlement/tutorial/world provisioning remains separate.

## IMP-069 — Player state snapshot API
- Status: ACCEPTED — Hybrid
- Goal: give Android clients one deterministic read model for reconnect/bootstrap instead of assembling state from multiple endpoints.
- Variants:
  1. Minimal: character + vehicles only.
  2. Systemic: character, vehicles, wallet, inventory and active jobs.
  3. Advanced: full world/session snapshot with versioned cursors.
  4. Hybrid: account gameplay state now, world/session feed later.
- Selected: Hybrid.
- Implementation: deterministic snapshot now returns character, vehicles, wallet, inventory stacks and active jobs; world/session feed remains later.
- Status after implementation: COMPLETE for the selected slice.

## IMP-070 — Android authoritative-state client
- Status: ACCEPTED — Hybrid
- Goal: connect the Android shell to the server's bootstrap/state contracts while keeping the client thin and authoritative-state driven.
- Variants:
  1. Minimal: HTTP client plus raw state screen.
  2. Systemic: typed API client, repository, ViewModel and persistent state cache.
  3. Advanced: offline command journal, reconnect cursor and optimistic UI reconciliation.
  4. Hybrid: typed client + repository + ViewModel + cache now; offline journal/reconciliation builds on IMP-027/028 later.
- Selected: Hybrid. The typed client, repository and cache now consume the expanded authoritative snapshot; offline journal/reconciliation remains later.

## IMP-071 — Persistent player sessions
- Status: ACCEPTED — Hybrid
- Goal: replace the Android development UUID with a server-created persistent player identity and session credential.
- Variants:
  1. Minimal: anonymous player creation with a persistent player UUID.
  2. Systemic: player handle + expiring server session token + Android credential cache.
  3. Advanced: refresh/revocation/device binding and full account security flows.
  4. Hybrid: handle + 30-day server session + Android persistence now; refresh/revocation/device security later.
- Selected: Hybrid. The current slice adds the persistent session boundary while leaving production account security for the dedicated auth hardening phase.
- Implementation note: bearer-session enforcement is now wired into player bootstrap and player-state reads; requests cannot read or mutate another player's bootstrap/state by UUID alone.

## IMP-072 — Player-boundary session enforcement
- Status: ACCEPTED — Security hardening — COMPLETE for selected slice
- Goal: ensure the persistent session credential is actually authoritative at the player boundary rather than merely being stored and sent by Android.
- Variants:
  1. Minimal: enforce bearer token on state/bootstrap only.
  2. Systemic: enforce bearer identity across all player-owned commands and reads.
  3. Advanced: refresh/revocation/device binding plus scoped credentials.
  4. Hybrid: protect state/bootstrap immediately, then extend ownership enforcement across every player-owned command before production auth hardening.
- Selected: Hybrid.
- Implementation: bearer authentication and ownership checks now cover wallet entries, inventory mutations, job creation/transitions, character creation/reads, vehicle creation/reads, plus bootstrap/state. Negative regression tests cover missing authentication and cross-player access.
- Remaining production auth work: refresh/revocation, device binding and scoped credentials remain intentionally deferred.

## IMP-073 — Regional market matching concurrency hardening
- Status: COMPLETE — Technical hardening
- Finding: cross-side concurrent buy/sell matching could deadlock if each transaction locked its own order row before attempting to synchronize the shared regional/item order book.
- Implementation: `_match` now resolves the order's `(region_id, item_definition_id)` first, acquires a PostgreSQL transaction-scoped advisory lock for that regional/item book, and only then acquires the order row lock and performs matching. This serializes matching per regional item without changing market behavior.
- Verification: corrected implementation committed as `367b950d6ab0b0c7d24c450a2f965dd257df7d4c`; CI run #177 passed migrations and the complete test suite.
