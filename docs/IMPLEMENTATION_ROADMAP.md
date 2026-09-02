# MadWorld — Implementation Roadmap

## Phase 0 — Foundation

- Repository structure
- Architecture decision record
- Kotlin/Android project
- Backend service skeleton
- PostgreSQL migrations
- CI
- Environment configuration
- API versioning
- Domain IDs and audit model

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
- Skills
- Production bonuses
- Warehouses
- Logistics contracts
- Cargo capacity
- Route danger model

## Phase 3 — Vehicles and combat

- Modular vehicle fitting
- Component damage
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

## Phase 6 — Dynamic world

- NPC faction simulation
- Regional shortages
- Dynamic events
- Convoy events
- Resource discoveries
- Disasters
- Catastrophe zones
- World-state-driven mission generation

## Phase 7 — Scale and polish

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

## Priority rule

Build systems that unlock other systems first. Inventory, item definitions, time, wallet and transaction/audit primitives are foundational and therefore precede decorative content.
