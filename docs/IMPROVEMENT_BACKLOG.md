# MadWorld — Improvement Backlog

This is the decision register for meaningful improvements discovered during development.

**Rule:** a proposal is recorded first. It is implemented only after it is marked `ACCEPTED`. `DEFERRED` means intentionally postponed. `REJECTED` means it conflicts with the product direction or creates unacceptable complexity/risk.

## Decision states

- `ACCEPTED` — approved for implementation and may become an architectural dependency.
- `PROPOSED` — worth considering; do not silently implement it.
- `DEFERRED` — useful, but not for the current milestone.
- `REJECTED` — explicitly excluded.

## Initial proposal set

| ID | Improvement | Status | Notes |
|---|---|---|---|
| IMP-001 | Dynamic world map: roads, bridges, checkpoints, POIs and danger can change | PROPOSED | Persistent geography and strategic navigation |
| IMP-002 | Meaningful character/corporation specialization | PROPOSED | Strong opportunity cost; avoid universal mastery |
| IMP-003 | Item quality, wear and condition | PROPOSED | Same item type can have materially different economic value |
| IMP-004 | Player/corporate manufacturers and brands | PROPOSED | Reputation and production consistency can affect value |
| IMP-005 | Asset provenance and history | PROPOSED | Track meaningful ownership/manufacturing/repair events |
| IMP-006 | Finance: credit, collateral, investment and insurance | PROPOSED | Must include capital sources, defaults and anti-inflation controls |
| IMP-007 | NPC factions as bounded economic agents | PROPOSED | Production, consumption, shortages, war and territorial effects |
| IMP-008 | Player-created infrastructure | PROPOSED | Garages, factories, warehouses, depots, fuel/water and defenses |
| IMP-009 | Intelligence market | PROPOSED | Tradeable but uncertain and aging route/price/resource information |
| IMP-010 | World Simulation Layer | PROPOSED | Deterministic tick-based feedback loop connecting economy, logistics, NPCs and conflict |

## Additional candidates discovered during implementation

| ID | Improvement | Status | Trigger for review |
|---|---|---|---|
| IMP-011 | Transactional outbox for domain events | PROPOSED | Needed before reliable asynchronous world/event processing |
| IMP-012 | Optimistic concurrency/version checks on mutable aggregates | PROPOSED | Needed when concurrent commands can target the same asset |
| IMP-013 | Explicit asset state machines | PROPOSED | Needed to prevent illegal transitions for cargo, vehicles, jobs and facilities |
| IMP-014 | Content versioning and feature flags | PROPOSED | Needed for safe live balancing and staged rollout |
| IMP-015 | Reproducible simulation seeds and audit snapshots | PROPOSED | Needed for debugging contested world/economy outcomes |
| IMP-016 | Economic abuse detection and anomaly scoring | PROPOSED | Needed before meaningful player-driven markets and finance |
| IMP-017 | Economic telemetry and balance dashboards | PROPOSED | Needed to balance inflation, scarcity, destruction and concentration |
| IMP-018 | Disaster/recovery strategy for authoritative state | PROPOSED | Needed before persistent player assets become valuable |
| IMP-019 | Server-side notification/event feed | PROPOSED | Needed for offline jobs, market changes, contracts and world events |
| IMP-020 | Deterministic time/job scheduler | PROPOSED | Needed for offline production, repair, contracts and simulation ticks |

## Selection policy

When a new improvement is discovered, add it here before implementation if it changes a core rule, persistent data model, economy, combat model, social contract or player progression.

Small bug fixes, refactors and test improvements do not require a product decision unless they alter player-visible behavior or a locked invariant.

The implementation plan should reference accepted IDs. This keeps the project ambitious without turning every good idea into accidental scope creep. Humanity has invented enough scope creep already.
