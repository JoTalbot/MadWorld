# MadWorld — Finance & Risk

Finance is an optional strategic layer over the physical economy. It must not become a faucet that creates unlimited currency.

## Candidate instruments

- secured credit;
- collateralized loans;
- trade/expedition financing;
- insurance;
- corporate investment;
- future-delivery financing;
- controlled bonds or debt instruments.

## Capital sources

Every credit instrument must have an explicit capital source. Candidate sources are:

- NPC financial pools with bounded balances;
- player/corporate capital;
- controlled system liquidity for specific economic functions.

No loan may simply mint unrestricted currency without an offsetting liability and economic sink.

## Collateral

Collateral must be:

- explicitly owned;
- valued by a server-controlled rule;
- reserved while pledged;
- protected from double-pledging;
- released or liquidated atomically.

## Default and recovery

A default should produce a deterministic state transition such as:

```text
active → overdue → defaulted → recovery/liquidation → closed
```

Recovery must respect asset location, destruction and ownership rules.

## Insurance

Insurance should price risk rather than erase it. Premiums, deductibles, coverage limits, exclusions and claim cooldowns are economic controls.

Potential covered outcomes include vehicle recovery, cargo loss and specific infrastructure damage. Coverage must never guarantee a profitable outcome.

## Inflation controls

Financial systems require:

- issuance limits;
- interest/fees as sinks;
- collateral requirements;
- default losses;
- transaction taxes where justified;
- telemetry for money supply and leverage.

## Anti-abuse

Finance requires strong ownership, idempotency and audit checks. Suspicious circular loans, self-funded laundering loops, rapid collateral swaps and duplicate claims should be detectable.

## Mobile UX

Players should see principal, total obligation, deadline, collateral, risk and worst-case outcome without opening a financial textbook disguised as a phone screen.

## Implementation boundary

Do not put finance in the first vertical slice unless it directly supports a tested gameplay loop. The initial schema and ledger must nevertheless avoid assumptions that would make secured obligations impossible later.
