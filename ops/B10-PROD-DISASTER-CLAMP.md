# Product Decision Record — B10-PROD-DISASTER-CLAMP

> Status: **PRODUCT-OWNER DECISION REQUIRED** (technical fix applied; gameplay
> balance interpretation pending owner sign-off).
> Raised during the B10 production deployment, 2026-09-03.
> This record is informational; no game coefficient is changed by it.

## Summary

The world disaster → territory signal path wrote modifier values in basis points
(bps) into `territory_modifiers` and `world_region_effects`. Those columns are
protected by database CHECK constraints with an authoritative range of
**[-5000, 5000] bps** (i.e. ±50%). The computed value for `travel_risk_bps` at
maximum disaster severity **exceeded that range**, so PostgreSQL rejected the
transaction and the entire world tick rolled back.

This is logged as a product decision because the *safe technical clamp* and the
*intended gameplay effect* of a maximum disaster are related but separate
questions. The agent has applied the minimal technical fix required for the
release candidate to function; the gameplay interpretation must be confirmed by
the product owner.

## Why the runtime reached 6000

The signal computation (backend `app/application/master_b1_b2.py`,
`apply_territory_signal`) maps disaster severity (1–5) to three modifiers:

| Modifier | Formula | At severity 5 (raw) | Schema CHECK bound |
|---|---|---|---|
| travel_risk_bps | `severity * 1200` | **6000** | `[-5000, 5000]` → **violation** |
| travel_time_bps | `severity * 800`  | 4000 | `[-5000, 5000]` → OK |
| extraction_bps  | `-(severity * 1000)` | -5000 | `[-5000, 5000]` → OK (at the edge) |

At severity 5 the raw `travel_risk_bps = 5 × 1200 = 6000` (i.e. +60% travel
risk), which violates `territory_modifiers_travel_risk_bps_check` /
`world_region_effects_travel_risk_modifier_bps_check` (max 5000). The failing
INSERT aborted the tick transaction on the first max-severity disaster, visible
as `CheckViolation: new row for relation "world_region_effects" violates check
constraint ... travel_risk_modifier_bps_check`.

A second defect was found at the same path (fixed independently): the modifier
row was keyed by `world_region_bindings.gameplay_region_id` (a gameplay UUID)
while the column references `world_regions(id)` (the text world-region id),
producing a foreign-key violation. Both defects were covered by no
DB-executing test, which is why the repository CI was green while the live
worker failed on every disaster event.

## Why the clamp is necessary

- The schema CHECK constraints are the authoritative invariant: modifier
  columns for travel risk, travel time and extraction are bounded to ±5000 bps.
  Any value outside that range cannot be persisted regardless of intent.
- The function is documented as producing a **"bounded territory modifier"**.
- Without the clamp, a single severity-5 disaster aborts the world tick
  transaction every minute (the worker retries and fails forever), so the
  dynamic world never advances. The release candidate cannot run.

## Technical value now in effect (commit `26b9d22`)

The computed modifiers are clamped to the schema-authoritative bounds:

```python
risk       = clamp(severity * 1200 if disaster else 0, -5000, 5000)
extraction = clamp(-(severity * 1000) if disaster else 0, -5000, 5000)
travel     = clamp(severity * 800 if disaster else 0, -5000, 5000)
```

Effective values by severity (disaster):

| Severity | travel_risk_bps | travel_time_bps | extraction_bps |
|---|---|---|---|
| 1 | 1200 | 800 | -1000 |
| 2 | 2400 | 1600 | -2000 |
| 3 | 3600 | 2400 | -3000 |
| 4 | 4800 | 3200 | -4000 |
| 5 | **5000** (raw 6000 → capped) | 4000 | **-5000** (raw -5000 → at edge) |

The clamp is the only behavioral change. **No coefficient (1200/800/1000) was
altered.** Severity 1–4 produce identical values to the pre-fix code; only the
severity-5 overshoot (6000 → 5000) changes.

## Proposed gameplay interpretation (for owner decision)

A maximum disaster (severity 5) is intended to be the most severe region hazard.
Two coherent interpretations exist:

1. **Cap at the schema ceiling (current technical behavior):** a severity-5
   disaster yields the maximum representable travel-risk penalty (+50%) and
   extraction penalty (-50%), alongside +40% travel time. The schema bound is
   treated as the game's intended worst case. *Recommended as the smallest,
   already-shipping interpretation.*
2. **Make severity 5 mean "+60% risk":** this would require a *separate product
   change* to raise the CHECK bound (e.g. to ±10000 bps like the supply column),
   review every consumer of travel risk, and re-tune downstream effects. This is
   out of scope for the technical fix and must be explicitly designed — it
   changes game balance.

## Potential impact

- **Players:** in a max-severity disaster region, travel risk/extraction
  penalties cap at ±50% rather than attempting +60%. Effectively the worst
  hazard is the strongest the data model can represent; severities 1–4 are
  unchanged.
- **Economy/extraction:** extraction in a disaster region drops by up to 50%
  (already at the schema edge), consistent with hazard scarcity design.
- **World simulation:** ticks no longer abort; disaster events persist and are
  consumed exactly once (idempotent consumer fence), so the dynamic world
  advances and recovery/escrow logic receives bounded signals.
- **Contractors/market:** market-fee modifier column has a tighter ±2500 bps
  bound and is not driven by this path; unaffected.

## Recommendation

- **Keep the clamp** (it is mandatory for correctness and is the documented
  "bounded" behavior).
- Ask the product owner to confirm interpretation (1) for B10 release, or open a
  balance ticket for interpretation (2) with the appropriate schema + consumer
  design work.
- Until an owner decision is recorded, this remains a documented assumption, not
  a silent balance choice.

## Verification evidence

- Integration regression `backend/tests/test_b2_territory_signal_integration.py`
  asserts severity-5 persistence within bounds (`travel_risk_bps == 5000`,
  `extraction_bps == -5000`, world-region FK keying) and fails on the pre-fix
  candidate with IntegrityError.
- Full backend suite: 169 passed on PostgreSQL 16.
- Live worker: ticks advancing (observed past tick 77) with `lag_ms=0`, 0 tick
  failures after the fix.
