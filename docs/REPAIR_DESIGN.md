# MadWorld — Vehicle Repair Design

## Phase 1 selected slice

Repair is an authoritative, transactional long-running job. A repair request validates vehicle ownership, garage eligibility, current condition, required repair resources and an idempotency key, then reserves/consumes the required resources and creates a persistent repair job using canonical server time.

Repair completion is deterministic and guarded by a state transition. Reprocessing an already completed/cancelled job must not duplicate restoration or consume resources again.

## Hybrid extension point

The initial vehicle aggregate keeps total durability as the playable repair surface while the domain model exposes component-oriented repair metadata so future combat can migrate to component damage without rewriting the command contract.

Deferred until later accepted work:
- full component-aware damage model
- repair quality progression
- mechanic skills
- facility modifiers
- production repair UI
