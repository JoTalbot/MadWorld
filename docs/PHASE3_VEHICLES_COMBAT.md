# MadWorld — Phase 3: Vehicles & Combat

## Scope
Phase 3 turns the existing vehicle and component-damage foundation into a coherent vehicle gameplay layer: chassis, modular fitting, weapons, authoritative combat, salvage, recovery and convoy foundations.

## Implemented in this batch
- Chassis definitions and module slots.
- Persistent vehicle fitting records.
- Weapon definitions and vehicle weapon slots.
- Combat engagement/action persistence with idempotency keys.
- Component-targeted combat using the existing kinetic/explosive/fire/impact damage model.
- Salvage and recovery persistence boundaries.
- Convoy and convoy-member persistence foundations.
- Android Phase 3 state model.
- API boundary for capabilities, combat, salvage preview and recovery commands.

## Authority rules
- PostgreSQL remains authoritative for production state.
- Vehicle ownership must be validated server-side.
- Combat damage is applied through the domain vehicle component model.
- Recovery is time-based and must be resolved by the authoritative scheduler/clock.
- Idempotency keys prevent duplicate combat/recovery mutations.
- Android does not invent combat, damage, fuel or recovery state.

## Gameplay loop
Garage → fit vehicle → arm vehicle → expedition → encounter/combat → component damage → salvage/recovery → repair → refit → next expedition.

## Deferred follow-up layers
- Full NPC encounter AI and tactical behavior.
- Full PvP matchmaking/session orchestration.
- Ballistic penetration tables and hit-location simulation.
- Dynamic convoy routes and convoy combat simulation.
- Insurance claims and economic recovery pricing.
- Advanced weapon ammunition/heat/reload systems.
- Rich 3D vehicle presentation and map combat UI.

These are compatible extensions, not hidden assumptions about the current slice.
