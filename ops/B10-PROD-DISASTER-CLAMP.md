# Product Decision Record — B10-PROD-DISASTER-CLAMP

> Status: **OWNER DECISION RECORDED — ACCEPT CURRENT CLAMP FOR RELEASE.**
> Decision date: 2026-09-08.
> No game coefficient is changed by this decision.

## Decision

For the B10 release, severity 5 uses the schema-authoritative cap of **+5000 bps (+50%) travel risk**, **-5000 bps (-50%) extraction**, and **+4000 bps (+40%) travel time**.

The raw travel-risk formula remains `severity * 1200`, so severity 5 calculates 6000 bps before the mandatory persistence clamp. The clamp is accepted as the intended release behavior because the database invariant and the bounded-territory contract both define ±5000 bps as the representable range.

This is a safety/invariant decision, not a silent rebalance. Coefficients remain 1200/800/1000. Severity 1–4 remain unchanged.

## Technical background

The world disaster → territory signal path writes modifiers in basis points into `territory_modifiers` and `world_region_effects`. The authoritative database CHECK constraints bound the relevant modifier columns to **[-5000, 5000] bps**.

Before the fix, severity 5 produced `travel_risk_bps = 6000`, causing PostgreSQL to reject the transaction and the world tick to roll back. A separate foreign-key keying defect in the same path was also corrected.

## Effective release behavior

| Severity | travel risk | travel time | extraction |
|---|---:|---:|---:|
| 1 | +1200 bps | +800 bps | -1000 bps |
| 2 | +2400 bps | +1600 bps | -2000 bps |
| 3 | +3600 bps | +2400 bps | -3000 bps |
| 4 | +4800 bps | +3200 bps | -4000 bps |
| 5 | **+5000 bps** | +4000 bps | **-5000 bps** |

## Future change boundary

Changing severity 5 to represent +60% travel risk would require a separate balance/product change, schema constraint change and review of every downstream consumer. It is explicitly outside this release decision.

## Verification

- Integration regression covers severity-5 bounded persistence and world-region FK keying.
- Full backend suite previously passed on PostgreSQL 16.
- Production world-tick worker was verified advancing after the fix with zero observed tick failures and zero lag in the captured verification.
