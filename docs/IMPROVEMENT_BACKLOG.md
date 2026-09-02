# MadWorld Improvement Backlog

> Policy: every new improvement records materially different implementation variants before selection. Product-changing mechanics require acceptance; bug fixes/refactors may be applied directly.

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
- Status: PLANNED
- Variants: Minimal fixed-price listings; Systemic regional order books; Advanced NPC liquidity + simulation; Hybrid regional order book first, NPC liquidity later.

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
- Selected: Hybrid. Reason: preserves transactional authority and leaves room for the later world/settlement systems without coupling onboarding to unfinished mechanics.
- Acceptance: authorized by project continuation workflow.

## IMP-069 — Player state snapshot API
- Status: ACCEPTED — Hybrid
- Goal: give Android clients one deterministic read model for reconnect/bootstrap instead of assembling state from multiple endpoints.
- Variants:
  1. Minimal: character + vehicles only.
  2. Systemic: character, vehicles, wallet, inventory and active jobs.
  3. Advanced: full world/session snapshot with versioned cursors.
  4. Hybrid: account gameplay state now, world/session feed later.
- Selected: Hybrid.
- Acceptance: authorized by project continuation workflow.

## IMP-070 — Android authoritative-state client
- Status: ACCEPTED — Hybrid
- Goal: connect the Android shell to the server's bootstrap/state contracts while keeping the client thin and authoritative-state driven.
- Variants:
  1. Minimal: HTTP client plus raw state screen.
  2. Systemic: typed API client, repository, ViewModel and persistent state cache.
  3. Advanced: offline command journal, reconnect cursor and optimistic UI reconciliation.
  4. Hybrid: typed client + repository + ViewModel + cache now; offline journal/reconciliation builds on IMP-027/028 later.
- Selected: Hybrid. Reason: establishes the correct client architecture without prematurely duplicating server simulation on Android.
- Acceptance: authorized by project continuation workflow.

## IMP-071 — Persistent player sessions
- Status: ACCEPTED — Hybrid
- Goal: replace the Android development UUID with a server-created persistent player identity and session credential.
- Variants:
  1. Minimal: anonymous player creation with a persistent player UUID.
  2. Systemic: player handle + expiring server session token + Android credential cache.
  3. Advanced: refresh/revocation/device binding and full account security flows.
  4. Hybrid: handle + 30-day server session + Android persistence now; refresh/revocation/device security later.
- Selected: Hybrid. The current slice adds the persistent session boundary while leaving production account security for the dedicated auth hardening phase.
- Acceptance: authorized by project continuation workflow.
- Implementation note: bearer-session enforcement is now wired into player bootstrap and player-state reads; requests cannot read or mutate another player's bootstrap/state by UUID alone.

## IMP-072 — Player-boundary session enforcement
- Status: ACCEPTED — Security hardening
- Goal: ensure the persistent session credential is actually authoritative at the player boundary rather than merely being stored and sent by Android.
- Variants:
  1. Minimal: enforce bearer token on state/bootstrap only.
  2. Systemic: enforce bearer identity across all player-owned commands and reads.
  3. Advanced: refresh/revocation/device binding plus scoped credentials.
  4. Hybrid: protect state/bootstrap immediately, then extend ownership enforcement across every player-owned command before production auth hardening.
- Selected: Hybrid. The first enforcement step is implemented now; broader command ownership enforcement remains next.
