# Expeditions

Expeditions are persistent server-side jobs that turn travel into a risk/reward activity.

## Flow

1. The player selects a vehicle, inventory, region, distance and risk tier.
2. The server validates ownership and fuel, computes authoritative duration and fuel cost, consumes fuel and creates a persistent job.
3. The job remains active while the player is offline.
4. Completion is accepted only at or after the authoritative completion timestamp.
5. The deterministic outcome stored in job metadata resolves loot and vehicle damage exactly once.
6. `expedition.completed` is written to audit/outbox and can advance contracts.

## Risk tiers

| Risk | Fuel multiplier | Gameplay intent |
|---|---:|---|
| low | 1.00x | safer scouting and resource runs |
| medium | 1.25x | balanced return/risk |
| high | 1.60x | expensive but better loot potential |
| extreme | 2.10x | maximum exposure |

Duration is distance-based and authoritative. Outcomes are deterministic from the expedition inputs and idempotency key, so retries cannot reroll the expedition.

## API

`POST /api/v1/expeditions`

Body:

```json
{
  "vehicle_id": "uuid",
  "inventory_id": "uuid",
  "region": "dust_basin",
  "distance_km": 100,
  "risk": "high"
}
```

Requires `Idempotency-Key` and an authenticated player session.

`POST /api/v1/expeditions/{job_id}/complete`

Completion is authoritative and fails before the stored `completes_at` timestamp. A resolved job returns the same result without granting loot or damage again.

## Deliberately deferred

Dynamic route generation, NPC encounter/combat simulation, convoy expeditions, weather/disaster modifiers, insurance/recovery and live economy-driven loot generation remain future product slices.
