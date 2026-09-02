# MadWorld — Vehicle Repair Design

## Phase 1 selected slice

Repair is an authoritative, transactional long-running job. A repair request validates vehicle ownership, garage eligibility, current condition, required repair resources and an idempotency key, then reserves/consumes the required resources and creates a persistent repair job using canonical server time.

Repair completion is deterministic and guarded by a state transition. Reprocessing an already completed/cancelled job must not duplicate restoration or consume resources again.

## Component-aware damage

IMP-076 is accepted at Advanced + Systemic scope. Vehicles now expose four authoritative components: engine, hull, wheels and fuel system. Each component has condition, maximum condition and armor. Damage supports kinetic, explosive, fire and impact types, applies armor mitigation, updates aggregate durability and can transition a vehicle to destroyed state.

Component condition also drives gameplay effects: engine condition affects power, wheel condition affects mobility, and fuel-system condition affects fuel efficiency. Component-specific repair restores condition and keeps aggregate durability synchronized.

Persistence is transactional through the `vehicle_components` table and the API exposes idempotent damage and component-repair commands.

## Deferred

- weapon-specific penetration tables
- richer hit-location simulation
- repair quality progression
- mechanic skills
- facility modifiers
- production repair UI
- advanced combat telemetry
