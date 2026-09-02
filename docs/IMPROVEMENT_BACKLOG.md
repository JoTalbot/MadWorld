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
| IMP-011 | Transactional outbox for domain events | ACCEPTED | Required foundation for reliable asynchronous world/event processing |
| IMP-012 | Optimistic concurrency/version checks on mutable aggregates | ACCEPTED | Required foundation before concurrent commands target the same asset |
| IMP-013 | Explicit asset state machines | ACCEPTED | Required to prevent illegal transitions for jobs and persistent assets |
| IMP-014 | Content versioning and feature flags | PROPOSED | Needed for safe live balancing and staged rollout |
| IMP-015 | Reproducible simulation seeds and audit snapshots | PROPOSED | Needed for debugging contested world/economy outcomes |
| IMP-016 | Economic abuse detection and anomaly scoring | PROPOSED | Needed before meaningful player-driven markets and finance |
| IMP-017 | Economic telemetry and balance dashboards | PROPOSED | Needed to balance inflation, scarcity, destruction and concentration |
| IMP-018 | Disaster/recovery strategy for authoritative state | PROPOSED | Needed before persistent player assets become valuable |
| IMP-019 | Server-side notification/event feed | PROPOSED | Needed for offline jobs, market changes, contracts and world events |
| IMP-020 | Deterministic time/job scheduler | ACCEPTED | Required foundation for offline production, repair, contracts and simulation ticks |
| IMP-021 | Authentication, sessions and device/account security | PROPOSED | Required player-facing identity layer; include refresh/revocation and abuse controls |
| IMP-022 | API contract versioning and generated client models | PROPOSED | Reduce Android/backend drift and make migrations safer |
| IMP-023 | Domain event envelope and schema registry | PROPOSED | Stable event contracts for outbox, workers, analytics and future service extraction |
| IMP-024 | Rate limiting and command budgets | PROPOSED | Protect authoritative commands and reduce automation abuse |
| IMP-025 | Anti-cheat trust model and server-side action validation | PROPOSED | Harden economy, movement, combat, timers and rewards against manipulated clients |
| IMP-026 | Structured observability: logs, metrics, traces and correlation IDs | PROPOSED | Diagnose production failures without inspecting player state manually |
| IMP-027 | Reconnect/resume protocol with authoritative state reconciliation | PROPOSED | Mobile networks disconnect; sessions must resume without duplication or rollback |
| IMP-028 | Offline action journal and retry semantics | PROPOSED | Make mobile command retries safe across timeouts and reconnects |
| IMP-029 | Market order lifecycle, escrow and deterministic matching | PROPOSED | Formalize reservations, partial fills, cancellation and settlement |
| IMP-030 | Regional price history and market analytics | PROPOSED | Give players useful information without creating a global auction house |
| IMP-031 | Logistics route planner with risk/cost/time trade-offs | PROPOSED | Turn geography and danger into meaningful economic decisions |
| IMP-032 | Convoy command, escort roles and shared cargo risk | PROPOSED | Extend hauling into cooperative logistics gameplay |
| IMP-033 | Combat replay and authoritative incident timeline | PROPOSED | Explain losses, support appeals and enable debugging of combat outcomes |
| IMP-034 | Component-level vehicle damage and repair dependencies | PROPOSED | Make vehicle configuration economically meaningful rather than cosmetic |
| IMP-035 | Reputation graph across players, settlements, factions and corporations | PROPOSED | Make trust, access and criminality persistent gameplay systems |
| IMP-036 | Corporation governance, permissions and treasury controls | PROPOSED | Prevent shared-asset gameplay from becoming an all-or-nothing trust model |
| IMP-037 | Alliance diplomacy, treaties and transit rights | PROPOSED | Enable political gameplay beyond simple clan membership |
| IMP-038 | Fog of war, scouting and information freshness | PROPOSED | Make intelligence valuable while preserving uncertainty |
| IMP-039 | Dynamic mission generation from world/economic state | PROPOSED | Replace static quest spam with systemic objectives |
| IMP-040 | Seasonal/live-world configuration with controlled state transitions | PROPOSED | Support long-term world evolution without wiping persistent assets |
| IMP-041 | Content authoring pipeline and validation | PROPOSED | Allow large data-driven item, blueprint, POI and mission catalogs safely |
| IMP-042 | Localization architecture and runtime text versioning | PROPOSED | Prepare Android UX for multilingual deployment without hardcoded strings |
| IMP-043 | Accessibility-first mobile interaction layer | PROPOSED | Support scalable text, contrast, touch targets, reduced motion and assistive technology |
| IMP-044 | Push notifications and player alert priorities | PROPOSED | Surface completed jobs, attacks, contracts and market events while offline |
| IMP-045 | Player-driven contracts with escrow and dispute rules | PROPOSED | Turn logistics, manufacturing and recovery into player-to-player economic services |
| IMP-046 | Insurance/recovery risk model | PROPOSED | Provide loss mitigation without removing meaningful destruction and risk |
| IMP-047 | Resource depletion and regeneration model | PROPOSED | Prevent permanent exhaustion while preserving regional scarcity |
| IMP-048 | Weather, disasters and environmental modifiers | PROPOSED | Make travel, production and combat respond to persistent world conditions |
| IMP-049 | POI ownership/access-control model | PROPOSED | Define who can operate, tax, repair, refuel or extract at strategic locations |
| IMP-050 | Infrastructure maintenance and degradation | PROPOSED | Prevent permanent snowballing from player-built infrastructure |
| IMP-051 | NPC demand, production and trade feedback loops | PROPOSED | Give NPCs bounded economic agency without infinite item generation |
| IMP-052 | Bot-resistant market and behavior telemetry | PROPOSED | Detect scripted patterns while avoiding punitive false positives |
| IMP-053 | Economy simulation sandbox and replayable balance tests | PROPOSED | Test inflation, scarcity and market shocks before live rollout |
| IMP-054 | Deterministic world-state snapshots and rollback checkpoints | PROPOSED | Recover from simulation defects without arbitrary player restoration |
| IMP-055 | Backup verification and disaster-recovery drills | PROPOSED | Prove backups are restorable rather than merely existing |
| IMP-056 | Data retention, archival and privacy boundaries | PROPOSED | Keep audit/history useful while limiting unnecessary long-term personal data |
| IMP-057 | Admin/operator action audit and privileged-command controls | PROPOSED | Make support and moderation actions traceable and reversible where safe |
| IMP-058 | Moderation, reporting and anti-harassment tooling | PROPOSED | Necessary for a persistent social sandbox at scale |
| IMP-059 | Player safety controls and communication preferences | PROPOSED | Give players control over notifications, chat exposure and social interactions |
| IMP-060 | Analytics/event taxonomy with privacy-safe aggregation | PROPOSED | Measure retention and systems health without coupling gameplay to invasive tracking |
| IMP-061 | Deterministic SQL migration runner and schema history | PROPOSED | Replace CI-only ordered glob execution with authoritative migration tracking |
| IMP-062 | Transaction boundary ownership | PROPOSED | Move commit/rollback ownership from individual services to the command/request boundary |
| IMP-063 | Generic API idempotency store | PROPOSED | Standardize replay protection across future authoritative commands |
| IMP-064 | Outbox leasing, retry and dead-letter processing | PROPOSED | Turn persisted outbox rows into reliable asynchronous delivery |
| IMP-065 | Stable API error envelope | PROPOSED | Give Android a predictable machine-readable error contract |

## Variant policy

For every new improvement, record all materially different implementation variants before choosing one. A proposal may therefore contain several approaches:

1. **Minimal/MVP** — smallest implementation that validates the gameplay or architectural need.
2. **Systemic** — deeper simulation with persistent interactions and stronger emergence.
3. **Advanced** — high-fidelity version intended for mature/live-world operation.
4. **Hybrid** — staged approach where MVP foundations remain compatible with later systemic expansion.

The chosen variant must be recorded in the decision entry before product behavior is enabled. Technical bug fixes and invariant-preserving refactors remain exempt from product approval.

## Variant notes for newly discovered technical improvements

### IMP-061 — Deterministic SQL migration runner

- **Minimal/MVP:** ordered SQL files plus a `schema_migrations` table storing migration name and applied timestamp.
- **Systemic:** migration metadata with checksums, dependency/order validation and startup/CI verification.
- **Advanced:** checksums plus repair tooling, drift detection, deployment gates and explicit recovery metadata.
- **Hybrid:** ordered SQL + checksums + CI verification, with no destructive automatic rollback.

### IMP-062 — Transaction boundary ownership

- **Minimal/MVP:** keep service-level commits and prohibit multi-command UoW reuse.
- **Systemic:** command/application boundary owns commit and rollback; services only mutate the UoW.
- **Advanced:** explicit nested transactions/savepoints and composable command pipelines.
- **Hybrid:** application boundary owns transaction lifecycle, with savepoints added only where composition requires them.

### IMP-063 — Generic API idempotency store

- **Minimal/MVP:** per-command idempotency keys using existing domain tables.
- **Systemic:** shared idempotency table keyed by actor + command + key, storing canonical response metadata.
- **Advanced:** distributed idempotency service with retention policies and replay diagnostics.
- **Hybrid:** shared PostgreSQL table first, compatible with later distributed extraction.

### IMP-064 — Outbox leasing and retries

- **Minimal/MVP:** poll unpublished rows and mark `published_at` after successful delivery.
- **Systemic:** row leasing with ownership/expiry and retry counters.
- **Advanced:** exponential backoff, dead-letter state, poison-event isolation and operational replay.
- **Hybrid:** lease + retry/backoff first, dead-letter and advanced replay later.

### IMP-065 — Stable API error envelope

- **Minimal/MVP:** `{code, message, request_id}` for all application errors.
- **Systemic:** typed error codes with field violations, retryability and domain metadata.
- **Advanced:** versioned machine-readable error catalog shared with Android SDK generation.
- **Hybrid:** stable envelope + typed codes now, generated catalog later.

## Selection policy

When a new improvement is discovered, add it here before implementation if it changes a core rule, persistent data model, economy, combat model, social contract or player progression.

Small bug fixes, refactors and test improvements do not require a product decision unless they alter player-visible behavior or a locked invariant.

The implementation plan should reference accepted IDs. This keeps the project ambitious without turning every good idea into accidental scope creep. Humanity has invented enough scope creep already.
