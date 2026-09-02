# MadWorld — Master Batch Implementation Contract

## Purpose

This document turns the implementation roadmap into a finite sequence of production-oriented batches. Each batch is executed as a coherent vertical/system integration unit rather than as isolated tickets.

The contract is subordinate to the persistent improvement policy in `docs/IMPROVEMENT_BACKLOG.md`: product-changing work must have an explicit accepted scope/variant; bugs, security fixes and non-product refactors may be fixed directly.

## Global execution rules

Every batch must:

1. audit the current repository before changing code
2. reconcile the batch scope with the improvement backlog
3. preserve existing authoritative boundaries
4. implement database/domain/API/client changes together where required
5. add migrations before consuming new persistent state
6. preserve transactional semantics and idempotency
7. emit/audit important authoritative mutations
8. test happy paths, invalid input, authorization, concurrency, retries and duplication
9. handle reconnect/failure cases for client-facing flows
10. add telemetry for important mutations and operational failure modes
11. update architecture/operational documentation
12. update backlog status and deferred work
13. commit coherent changes
14. run applicable Backend CI and Android CI
15. repair failures and rerun CI
16. perform a final repository audit before declaring the batch complete

## Universal Definition of Done

### Backend

- domain rules are server-authoritative
- persistence is transactional
- migrations are deterministic and reversible where practical
- API contracts are versioned and tested
- authentication and authorization are enforced
- idempotency is preserved for commands
- optimistic/concurrency controls are enforced where needed
- audit/outbox behavior is present for important mutations
- canonical server time is used for time-sensitive rules
- failure and retry behavior is deterministic or explicitly bounded

### Tests

- unit tests
- API/integration tests
- persistence tests
- authorization tests
- duplicate/idempotency tests
- concurrency/race tests
- stale-version tests
- rollback/retry tests
- invariant/exploit tests
- deterministic replay tests where simulation is involved

### Android

- authoritative typed state models
- repository/API integration
- ViewModel state handling
- loading/error/retry states
- reconnect/stale-state handling
- user-visible command outcome
- no client-side authority over economy, combat, inventory, world or territory state

### Operations

- structured logs
- metrics for critical paths
- worker health/lag where applicable
- backup/restore implications documented
- deployment/configuration documented
- safe failure mode defined

### Documentation

- roadmap updated
- improvement backlog updated
- architecture decision recorded where the boundary changes
- API/domain behavior documented
- deferred work explicitly recorded
- release notes updated when the batch affects player-visible behavior

---

# B1 — World Integration

## Goal

Turn the Phase 6 world simulation foundation into a real producer/consumer system that changes gameplay and economy without allowing the simulation to bypass authoritative domain boundaries.

## Scope

### World → Economy

- regional pressure becomes an explicit economic input
- shortage/surplus/discovery/disaster/convoy outcomes become domain events
- economy consumes events idempotently
- market state receives bounded supply/demand/scarcity modifiers
- simulator never directly mutates player wallets, inventory or market orders

### World → Territory

- disasters affect roads and travel risk
- catastrophe zones affect extraction/travel
- faction influence/supply can be consumed by territory systems
- resource discoveries expose temporary extraction opportunities
- strategic objectives may react to world events

### Convoy lifecycle

- SPAWNED → PREPARING → TRAVELLING → ENCOUNTER → ARRIVED/DAMAGED/LOST
- authoritative location/progress
- route and danger evaluation
- deterministic encounter outcome
- cargo outcome
- event emission
- replay-safe transitions

### Resource discoveries

- DISCOVERED → AVAILABLE → DEPLETING → EXPIRED/DEPLETED
- link to resource sites
- extraction interaction
- territory authorization
- economic effect

### Faction regional dynamics

- influence drift
- supply consumption/recovery
- hostility changes
- regional priorities
- bounded faction pressure

### Dynamic mission grammar

- supply
- convoy escort
- scouting
- faction conflict
- disaster response
- territory defense
- recovery
- exploration
- catastrophe extraction
- world-state validity/expiry

### Event/outbox bridge

- atomic simulation + event + outbox transaction
- idempotent consumers
- event versioning
- correlation/causation identifiers
- ordering rules
- retry and poison-event behavior

### Replay and telemetry

- deterministic state hash
- replay executor foundation
- tick duration
- lag
- skipped ticks
- retries
- lock contention
- event processing metrics

## Tests

- event duplication
- concurrent consumers
- rollback
- replay determinism
- convoy transitions
- discovery expiry/depletion
- disaster effects
- faction drift bounds
- mission invalidation
- economy consumer idempotency

## Exit gate

A world tick can produce authoritative events that are consumed by economy, territory and gameplay systems without direct cross-domain database mutation or duplicate side effects.

---

# B2 — Gameplay Integration

## Goal

Connect vehicles, travel, combat, salvage, territory, logistics and the dynamic world into one persistent gameplay loop.

## Scope

- regional travel
- fuel/cargo consumption
- route danger
- territory road modifiers
- controlled routes/checkpoints foundations
- faction encounters
- convoy attack/escort/defense
- combat outcomes linked to world events
- salvage linked to economy
- recovery after destruction
- reputation/faction consequences
- persistent expedition outcomes
- reconnect-safe travel/combat state

## Exit gate

A player can take a vehicle from a settlement, acquire cargo, travel through dynamic regions, encounter world/NPC threats, fight, salvage/recover, and return with authoritative persistent consequences.

---

# B3 — Advanced Economy

## Goal

Turn the economy foundation into a coherent regional player-driven economy.

## Scope

- regional order books
- partial fills
- matching correctness
- price/volume history
- liquidity/spread/volatility metrics
- regional supply/demand state
- production/consumption accounting
- refining chains
- production facilities
- capacity/efficiency/maintenance
- skill specialization
- warehouse economics
- logistics contracts
- cargo and route economics
- economic telemetry and balance tooling
- anti-duplication invariants

## Exit gate

Resource, production, logistics and market flows reconcile through authoritative ledger/item state and can be measured economically by region.

---

# B4 — NPC Faction Simulation

## Goal

Make NPC factions active economic, territorial and military actors.

## Scope

- faction state model
- strategic observation
- priority evaluation
- decision selection
- action validation
- attack/defend/expand/retreat
- trade/raid/escort
- scouting
- resource exploitation
- blockade foundations
- diplomacy transitions
- faction economy/logistics
- deterministic bounded decision cadence

## Exit gate

NPC factions make persistent, explainable, replayable decisions that alter world state through the same authoritative command/event boundaries as players.

---

# B5 — Territory Warfare

## Goal

Turn territorial control into a persistent strategic conflict system.

## Scope

- claim costs/upkeep
- contest lifecycle
- capture/abandonment
- infrastructure damage/repair
- defenses
- checkpoints
- supply lines
- strategic objective chains
- reinforcement
- attack/defense windows
- siege/disruption foundations
- alliance warfare
- economic consequences of occupation
- territory telemetry

## Exit gate

Corporations and alliances can contest, defend, capture and economically exploit territory with authoritative resolution and anti-abuse protections.

---

# B6 — Finance & Provenance

## Goal

Add advanced financial instruments only after economy telemetry is reliable.

## Scope

- secured credit
- collateral
- repayment
- default
- recovery
- insurance
- claims
- investment/financing instruments
- corporate financing
- asset provenance
- quality/manufacturer history
- financial abuse telemetry

## Exit gate

Every financed asset/liability has authoritative lifecycle history, balanced accounting and recoverable state transitions.

---

# B7 — Full Android Game

## Goal

Convert the current authoritative Android surfaces into a complete MMO client.

## Scope

- authentication
- character/profile
- garage
- vehicle
- inventory
- market
- production
- warehouse
- contracts
- expedition
- world
- map
- territory
- corporation
- alliance
- combat
- convoy
- missions
- finance
- notifications
- settings
- offline command queue
- reconnect/resume
- stale-state handling
- accessibility/localization foundations

## Exit gate

All critical gameplay loops are playable end-to-end on Android using authoritative server state.

---

# B8 — Security, Anti-Abuse & Reliability

## Goal

Treat the game as an adversarial distributed system.

## Scope

- endpoint authorization audit
- ownership/membership checks
- replay protection
- idempotency abuse
- impossible movement
- impossible resources
- impossible combat
- race-condition exploitation
- money duplication
- item duplication
- market manipulation
- wash-trading detection foundations
- corporate wallet abuse
- reward farming
- rate limiting
- circuit breakers
- abuse scoring foundations
- security regression suite

## Exit gate

Critical mutations have tested authorization, concurrency, replay and duplication defenses, with operational containment for abnormal behavior.

---

# B9 — Scale, Operations & LiveOps

## Goal

Make the system operable at production scale.

## Scope

- production Docker/service definitions
- PostgreSQL operational hardening
- world worker deployment
- catch-up policy
- health checks
- metrics/traces/logging
- alert thresholds
- load tests
- economy stress tests
- world simulation stress tests
- Android device matrix
- analytics dashboards
- push notifications
- live operations tooling
- backup automation
- restore verification
- disaster recovery exercises

## Exit gate

The service can be deployed, observed, restarted, backed up, restored and load-tested with known capacity and failure behavior.

---

# B10 — Final Release Gate

## Goal

Release the first complete MadWorld production candidate.

## Product verification

- onboarding
- gathering
- refining
- crafting
- market
- logistics
- travel
- combat
- salvage
- recovery
- missions
- territory
- corporations
- alliances
- convoys
- dynamic world
- NPC factions
- finance where enabled

## Technical verification

- all migrations clean
- backend tests green
- Android tests/build green
- integration tests green
- concurrency tests green
- exploit tests green
- replay tests green
- load tests green
- backup/restore verified
- production configuration verified
- release artifact reproducible

## Release checklist

- privacy/legal requirements reviewed
- crash reporting
- analytics
- localization
- accessibility
- onboarding
- server capacity
- rollback plan
- incident response
- release notes
- versioning
- database migration plan

## Final definition

MadWorld is release-ready only when the complete player loop, economy, dynamic world, social/territory systems, Android client, security controls and production operations pass their respective gates. A working screen, endpoint or migration alone never constitutes completion.
