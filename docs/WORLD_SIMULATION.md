# MadWorld — World Simulation Layer

## Purpose

The World Simulation Layer connects player activity, NPC activity, resources, logistics, markets, infrastructure and conflict into a persistent feedback system.

The goal is not to simulate every atom of the wasteland. The goal is to simulate the causes of economically and strategically meaningful change.

## Core loop

```text
resources
  ↓
extraction / salvage
  ↓
production
  ↓
stock + consumption
  ↓
logistics
  ↓
regional markets
  ↓
prices / shortages / margins
  ↓
player + NPC decisions
  ↓
expansion / competition / conflict
  ↓
damage / destruction / recovery
  ↓
new scarcity and opportunities
  └───────────────────────────────┘
```

## Tick model

The server owns canonical time. Simulation work is processed in bounded ticks rather than requiring every player to be online.

A tick may evaluate:

1. completed production and repair jobs;
2. cargo and contract arrivals;
3. resource extraction and regeneration rules;
4. NPC production, consumption and procurement;
5. market supply/demand changes;
6. infrastructure condition and upkeep;
7. faction objectives and territory pressure;
8. scheduled world events;
9. information expiry and intelligence quality;
10. telemetry and audit snapshots.

Real-time combat remains a separate interactive path with authoritative server validation.

## Determinism and auditability

Each simulation tick has:

- canonical tick ID;
- rules/content version;
- server timestamp;
- bounded input set;
- deterministic ordering of affected aggregates;
- event/audit records for important mutations.

Where randomness is necessary, use a versioned seed derived from server-controlled inputs. Randomness must not be supplied by the client.

## Bounded simulation

NPCs and world systems must have explicit budgets:

- maximum decisions per tick;
- maximum inventory/value creation per tick;
- bounded pathfinding and market scans;
- bounded event fan-out;
- bounded historical retention for hot state.

The world should feel alive without becoming a CPU-powered tribute to poor architectural decisions.

## Player impact

Player actions can influence simulation through validated aggregates:

- extraction changes regional stock;
- manufacturing changes supply;
- hauling changes location and availability;
- destruction removes or transforms assets;
- infrastructure changes capacity and safety;
- corporations alter demand, production and strategic control;
- intelligence changes the information available to other actors.

The simulation never trusts a client-reported outcome.

## Event generation

World events should be generated from state, not merely from a list of disconnected quests. Examples:

- sustained water shortage → emergency water contracts;
- refinery failure → fuel shortage and repair demand;
- repeated convoy losses → escort contracts and route rerouting;
- faction expansion → defensive missions and price changes;
- rare discovery → temporary resource rush;
- infrastructure destruction → reconstruction demand.

## Failure handling

A failed tick must be retryable without duplicating economic effects. Important simulation mutations therefore require idempotency keys, transactional boundaries and durable event/audit records.

## Initial implementation boundary

For the vertical slice, implement only a small deterministic simulation loop around jobs, inventories, wallets, regional stock and market effects. The architecture must leave room for NPC economy, dynamic geography and territory without requiring them all in the first playable build.
