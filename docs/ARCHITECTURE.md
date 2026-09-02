# MadWorld — Technical Architecture

## Principles

1. Server is authoritative for all mutations.
2. Client is a presentation/input layer, never a source of truth.
3. Every economic mutation is transactional, idempotent and auditable.
4. Gameplay content is data-driven and versioned.
5. Long-running jobs use server time, not device time.
6. Reconnects must be safe and produce the same final state as a single successful request.
7. The first implementation is a modular monolith, designed so high-load domains can later split into services.

## Runtime

Android:
- Kotlin
- Jetpack Compose
- local read cache
- REST for ordinary commands/queries
- WebSocket for live state/events

Backend:
- FastAPI during foundation/vertical-slice development
- PostgreSQL as source of persistent truth
- Redis only for transient cache/coordination, never authoritative balances
- background worker for jobs, events and simulation ticks

## Domain modules

```text
api
 ├── auth
 ├── player
 ├── inventory
 ├── wallet
 ├── vehicles
 ├── industry
 ├── market
 ├── contracts
 ├── logistics
 ├── expedition
 ├── combat
 ├── corporation
 ├── territory
 └── world

domain
 ├── item
 ├── economy
 ├── vehicle
 ├── combat
 ├── world
 └── social

infrastructure
 ├── postgres
 ├── redis
 ├── events
 └── telemetry
```

## Identity and IDs

Use UUID/ULID-style opaque IDs for player-owned entities. Never expose sequential database IDs as security boundaries.

Every mutable aggregate has:
- id
- version
- created_at
- updated_at

Commands carry an idempotency key. Duplicate commands return the original outcome instead of applying the mutation twice.

## Time

The server owns canonical time. Client clocks are advisory only.

Long-running activities store:
- started_at
- completes_at
- cancelled_at when applicable
- state

A worker may process an expired job more than once, therefore completion must be guarded by a transaction/state transition.

## Inventory invariants

An item cannot exist in two containers simultaneously.

Transfers use an atomic transaction:

```text
lock source
validate ownership/capacity
remove quantity
create destination movement
append audit event
commit
```

Item creation and destruction require an explicit reason code.

## Wallet invariants

Balances are projections of an append-only ledger.

A transaction contains:
- id
- idempotency_key
- debit_account
- credit_account
- amount
- currency
- reason
- actor
- timestamp

No endpoint directly edits a balance.

## Market invariants

Order placement reserves the required asset or currency before the order becomes active.

Matching is deterministic. A trade either completes all required mutations or none of them complete.

## Offline jobs

Crafting, refining, repairs, travel and training can continue while the client is offline. The server computes completion from canonical timestamps when the player reconnects.

## Security

Never trust the Android client for:
- price
- item quantity
- wallet amount
- travel duration
- damage
- cooldowns
- skill requirements
- reward amount

Rate limits, authorization checks, replay protection and audit logs are mandatory for mutations.

## Scalability strategy

Start as one deployable backend with strict domain boundaries. Split only when measurements justify it.

Likely future extraction boundaries:
- market matching
- world simulation
- realtime combat
- notifications

PostgreSQL remains the authoritative transactional store until a measured scaling requirement says otherwise.

## Mobile UX architecture

The main navigation is organized around player intent:

- Map
- Vehicle
- Cargo
- Market
- Production
- Contracts
- Corporation
- Alerts

Every important screen should answer: what can I do now, what will it cost, what can I gain, and what can go wrong?
