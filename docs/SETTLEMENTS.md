# Settlements

IMP-079 adds the persistent player settlement foundation. A settlement is the player's stable home point and the integration boundary for the core gameplay loop.

## Current slice

Each player has at most one settlement state. The initial state exposes five interaction capabilities:

- `garage`: vehicle storage and vehicle-facing services
- `warehouse`: persistent inventory/storage boundary
- `workshop`: repair and future production boundary
- `contracts`: contract acquisition/progression boundary
- `market`: regional market interaction boundary

The first slice stores the settlement region, level, module levels and optimistic-concurrency version in PostgreSQL. Creation emits `settlement.created` through the existing audit and outbox infrastructure.

## API

`GET /api/v1/settlement` is authenticated and lazily provisions the player's settlement if it does not exist. The response is authoritative and includes module levels plus boolean interaction capabilities.

## Design boundary

The settlement is intentionally an extensible foundation, not a full city-builder. Building upgrades, NPC services, production chains, settlement population, territory control and deeper economic modifiers are deferred follow-up improvements.
