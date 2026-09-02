# Phase 5 — Territory Plan

## Status

**PLANNED — product-changing design.** No Phase 5 gameplay mutation is considered approved until a variant is selected.

## Goal

Turn the existing regional economy and player settlement foundation into a persistent territorial layer where settlements, infrastructure, roads and resource sites create meaningful strategic control, while keeping all authoritative ownership, taxation, travel and economic effects on the server.

The design must remain compatible with Phase 6 World Simulation and the existing social/economic systems.

## Current foundation

- Player settlements already persist a region, levels and gameplay capabilities.
- Regional markets already establish the economic-region boundary.
- Corporations, alliances, diplomacy and permissions exist as social foundations.
- Authoritative time, scheduling, transactions, audit/outbox and optimistic concurrency already exist.
- Territory is currently a design boundary rather than a complete domain.

## Recommended domain model

Do **not** collapse the system into one `territories(owner_id)` table. Model a graph of world entities and derive control from authoritative state:

`region -> settlement -> infrastructure/resource sites -> roads/routes -> claims -> controller`

Recommended core entities:

- `world_regions`: stable geographic/economic regions.
- `settlements`: existing player home-point foundation extended with world settlement identity where appropriate.
- `territory_claims`: explicit claim records with claimant, target, lifecycle and concurrency state.
- `infrastructure`: depots, wells, mines, workshops, relay stations and other controllable facilities.
- `roads`: directed/undirected route segments connecting strategic nodes.
- `resource_sites`: persistent extraction locations with resource definitions and depletion/renewal state.
- `territory_control`: authoritative controller state and historical transitions.
- `territory_objectives`: scheduled strategic objectives with contest windows and resolution state.
- `territory_modifiers`: bounded economic/travel modifiers derived from controlled assets.
- `territory_events`: auditable state transitions and future world-simulation inputs.

## Core invariants

- A target has at most one authoritative active controller for a given control scope.
- Claims cannot overlap in a way that creates ambiguous ownership.
- Ownership/control mutations are transactional and optimistic-concurrency protected.
- Corporate actions require the appropriate Phase 4 permission and membership boundary.
- Taxes and economic modifiers are server-derived, bounded and auditable.
- A player/client cannot directly declare ownership, control, tax rate or economic bonus.
- Strategic objectives have explicit open/contest/resolve/closed states and server time determines transitions.
- Historical control is append-only or otherwise reconstructible from authoritative events.
- Territory effects cannot mint currency or bypass wallet/ledger invariants.
- Route and resource-site effects cannot bypass expedition, inventory or market authority.
- All state-changing commands support idempotency where retries can repeat side effects.

## Variant matrix

### Minimal

Implement:

- regions and settlement ownership boundary;
- basic corporate territory claims;
- controller state;
- simple infrastructure ownership;
- authoritative APIs and Android read-only territory view;
- audit and concurrency tests.

Defer meaningful road control, resource-site simulation, taxation, scheduled warfare and economic modifiers.

**Benefit:** fastest playable territory proof.

**Cost:** weak strategic depth and limited foundation for Phase 6.

### Systemic

Implement the full durable foundation:

- region graph;
- settlements;
- claims and control history;
- infrastructure;
- roads/routes;
- resource sites;
- bounded taxes and regional economic modifiers;
- scheduled strategic objectives;
- authoritative territory events;
- telemetry, audit, anti-abuse and invariant tests;
- Android authoritative territory state and management surface.

**Benefit:** strong reusable foundation for economy, logistics, social play and World Simulation.

**Cost:** larger initial implementation and balancing surface.

### Advanced

Implement Systemic plus:

- contested territory and staged control transitions;
- supply-line and route-control mechanics;
- infrastructure condition/upkeep;
- resource depletion/renewal pressure;
- dynamic control pressure;
- alliance participation rules;
- richer strategic objective types;
- deeper territory/economy telemetry;
- preparation hooks for NPC faction pressure and dynamic geography.

**Benefit:** territory becomes a major persistent strategic game system immediately.

**Cost:** substantial balance, simulation and exploit surface before World Simulation exists.

### Hybrid — recommended

Implement the **Systemic core** plus the highest-leverage Advanced mechanisms:

- stable region graph;
- settlement integration;
- corporate/alliance claims and controller history;
- infrastructure ownership and upkeep state;
- road control as a first-class route modifier;
- resource sites with bounded extraction state;
- bounded taxes and economic/travel modifiers;
- scheduled strategic objectives with contest/resolution lifecycle;
- authoritative territory event stream;
- anti-abuse/concurrency/ledger-boundary hardening;
- telemetry and invariant tests;
- Android authoritative territory map/state and core management actions;
- explicit extension points for Phase 6 NPC/world simulation.

Defer highly dynamic warfare simulation, complex supply-chain simulation and fully procedural geography until Phase 6 can consume the territory events safely.

**Why this is recommended:** it creates the persistent territorial skeleton that the economy, logistics, corporations and future world simulation can actually use, without prematurely building an entire grand-strategy simulator inside an Android MMO. Humanity has suffered enough from over-engineered MVPs.

## Phase 5 acceptance boundary

Phase 5 is complete when:

- a corporation can claim an eligible territorial object through an authoritative command;
- the server prevents conflicting ownership and stale concurrent writes;
- settlements, infrastructure, roads and resource sites expose authoritative control state;
- controlled territory can produce bounded, auditable economic/travel effects;
- taxes/upkeep settle through existing financial authority rather than parallel balances;
- strategic objectives transition according to server time;
- every material control mutation is auditable and recoverable;
- Android renders authoritative territory state and never invents control;
- exploit/invariant tests cover ownership, concurrency, idempotency, taxes, modifiers and objective transitions;
- territory events can later feed the Phase 6 World Simulation Layer.

## Explicit non-goals for Phase 5

- Full procedural world generation.
- Autonomous NPC faction grand strategy.
- Unlimited economic modifiers.
- Client-authoritative map/control logic.
- Real-money purchase of competitive territory power.
- Full vehicle/item legal ownership transfer merely because an asset enters a territory.

## Dependency order

1. Region identity and territory schema.
2. Claims/control lifecycle.
3. Infrastructure and resource-site custody/control.
4. Roads and route effects.
5. Taxes/upkeep and economic modifiers.
6. Scheduled strategic objectives.
7. Territory events and telemetry.
8. Android state/read/write surface.
9. Exploit and concurrency suite.
10. Phase 6 integration contracts.
