# MadWorld — Implementation Roadmap

## Working rule: proposals vs commitments

Potential improvements are recorded in `docs/IMPROVEMENT_BACKLOG.md`. Only `ACCEPTED` items become implementation commitments. This prevents good ideas from silently expanding the scope of the current milestone.

## Master execution contract

The roadmap is executed through the finite production batches defined in `docs/BATCH_IMPLEMENTATION_CONTRACT.md`. Each batch is a coherent vertical/system integration unit and is not considered complete until its backend, persistence, API, Android, security, telemetry, tests and operational gates pass.

## Phase 0 — Foundation

- Repository structure
- Architecture decision record
- Backend service skeleton
- PostgreSQL migrations
- CI
- Environment configuration
- API versioning
- Domain IDs and audit model
- Idempotency primitives
- Optimistic concurrency/versioning strategy
- Transactional outbox design
- Canonical server time and job scheduler
- Observability/economic telemetry foundations
- Android Kotlin/Compose project skeleton

## Phase 1 — Vertical slice

- Authentication/session
- Character creation
- Player profile
- Starter vehicle
- Garage
- Inventory
- Five resources
- Gathering/scavenging
- Ten blueprints
- Crafting queue
- Repair
- Local market
- Currency ledger
- Five contracts
- One expedition
- Simple PvE vehicle combat
- Persistence and reconnect

Exit criteria: a new player can enter, gather resources, craft an upgrade, buy/sell goods, accept a contract, travel into danger and return with a persistent result.

## Phase 2 — Economy

- Regional markets
- Buy/sell order books
- Price history
- Refining chains
- Production facilities
- Skills and specialization
- Production bonuses
- Warehouses
- Logistics contracts
- Cargo capacity
- Route danger model
- Economic telemetry and balance tooling

## Phase 3 — Vehicles and combat

- Modular vehicle fitting
- Component damage
- Item condition/quality foundations
- Multiple chassis families
- Weapon systems
- Convoys
- Escort mechanics
- Salvage
- Recovery
- PvE faction encounters
- Combat telemetry

## Phase 4 — Social sandbox

- Corporations
- Roles and permissions
- Shared wallets
- Shared hangars
- Alliances
- Reputation
- Diplomacy
- Contracts between players/groups
- Corporate assets
- Manufacturers/brands and reputation, if accepted

## Phase 5 — Territory

- Settlements
- Territory claims
- Infrastructure ownership
- Road control
- Resource sites
- Scheduled strategic objectives
- Taxes
- Regional bonuses
- Territory warfare
- Dynamic geography foundations

## Phase 6 — Dynamic world

- NPC faction simulation
- Regional shortages
- Dynamic events
- Convoy events
- Resource discoveries
- Disasters
- Catastrophe zones
- World-state-driven mission generation
- World Simulation Layer
- Intelligence services/market, if accepted

## Phase 7 — Finance and advanced sandbox

- Secured credit
- Collateral
- Insurance
- Investment/financing instruments
- Default/recovery flows
- Asset provenance
- Advanced quality and manufacturer history
- Anti-abuse financial telemetry

Finance and advanced provenance should ship only after the core economy can measure money/item flows reliably.

## Phase 8 — Scale and polish

- Performance profiling
- Android device matrix
- Backend load tests
- Economy stress tests
- Abuse prevention
- Analytics dashboards
- Push notifications
- Localization
- Accessibility
- Onboarding
- Live operations tools
- Disaster recovery exercises

## Production batch sequence

### B1 — World Integration

Connect World Simulation to Economy, Territory, Convoys, Discoveries, Faction Regional Dynamics, Dynamic Missions, Outbox and Replay/Telemetry without allowing simulation code to bypass domain authority.

### B2 — Gameplay Integration

Connect travel, vehicles, cargo, combat, salvage, recovery, convoys, territory effects, faction encounters and persistent expeditions into one authoritative gameplay loop.

### B3 — Advanced Economy

Complete regional order books, economic state, production/refining, facilities, skills, warehouses, logistics and economic stress/invariant tooling.

### B4 — NPC Faction Simulation

Implement bounded strategic NPC observation, decision making, logistics, diplomacy and persistent faction actions through authoritative commands/events.

### B5 — Territory Warfare

Complete claims, infrastructure damage/repair, checkpoints, supply lines, strategic objective chains, reinforcement, siege/disruption and alliance warfare.

### B6 — Finance & Provenance

Implement secured credit, collateral, repayment/default/recovery, insurance, financing, provenance and advanced asset history after economic telemetry is sufficiently reliable.

### B7 — Full Android Game

Complete all critical MMO screens and flows, authoritative command handling, offline queue, reconnect/resume, stale-state handling, notifications, localization and accessibility foundations.

### B8 — Security, Anti-Abuse & Reliability

Perform a full mutation-endpoint audit and implement replay, duplication, race, impossible-state, market, financial and reward-abuse defenses plus rate limits, circuit breakers and regression tests.

### B9 — Scale, Operations & LiveOps

Finalize production services, world worker deployment, catch-up policy, observability, load/stress testing, device matrix, analytics, backup/restore and disaster recovery.

### B10 — Final Release Gate

Validate all critical gameplay loops, technical systems, security controls, Android release artifacts and production operations. Only this gate may declare the first complete production candidate release-ready.

## Definition of done for each feature

A feature is not complete when its screen works. It is complete when:

1. domain rules exist server-side
2. persistence is transactional
3. API is tested
4. client displays authoritative state
5. failure/reconnect cases are handled
6. telemetry exists for important mutations
7. exploit/duplication paths are tested
8. documentation is updated
9. accepted design decisions are reflected in tests/invariants

## Priority rule

Build systems that unlock other systems first. Inventory, item definitions, canonical time, wallet, idempotency, concurrency and transaction/audit primitives are foundational and therefore precede decorative content.
