# IMP-082 — Economy-to-Gameplay Integration

## Status

**COMPLETE — Hybrid, selected by user as the next full implementation section.**

## Goal

Turn the Phase 2 economy foundation into a single authoritative gameplay loop visible to the Android client without introducing a second source of truth.

## Implemented

- Added `GET /api/v1/economy/overview`.
- Composed authoritative settlement state, warehouse usage/capacity, facilities, active production/refining jobs, contract availability, vehicle readiness and recent market activity into one read model.
- Added deterministic `next_action` prioritization:
  1. active production/refining job
  2. available/active contract
  3. expedition-ready vehicle
  4. market activity
  5. resource gathering
- Added typed Android economy models.
- Added authenticated Android API parsing and repository integration.
- Added an Economy Loop panel to the main mobile screen.
- Kept all gameplay state authoritative on the backend; the Android client only renders the server read model.
- Added focused backend tests for action prioritization.

## Design boundaries

The endpoint is intentionally read-oriented. Existing authoritative mutations remain responsible for production/refining job creation and completion, contracts, market actions, vehicle repair/damage and expeditions. This avoids duplicating domain rules in a dashboard layer.

## Deferred follow-ups

- Direct Android controls for starting/completing economy jobs.
- Full cargo/logistics contract execution.
- Skills and specialization modifiers.
- NPC supply/demand simulation.
- Insurance/recovery economy.
- Procedural economy-driven contracts.

These remain separate product slices and must not be silently folded into IMP-082.

## Verification

- Unit coverage added for the gameplay-loop prioritization rules.
- Backend CI must pass migrations and the complete pytest suite on the resulting `main` head.
- Android CI must compile the new economy model/API/ViewModel/UI path.
