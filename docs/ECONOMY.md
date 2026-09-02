# MadWorld — Economy Specification

## Economic objective

Create a closed-loop economy where gathering, processing, manufacturing, logistics, combat losses and NPC demand continuously create reasons to produce, transport and trade.

## Currency

Primary currency: Scrap Credits (SC).

Secondary non-currency resources are physical goods and never appear as unlimited abstract numbers.

Currency ledger rules:

- balances cannot become negative unless an explicitly supported credit instrument exists
- every transfer has immutable ledger records
- taxes and fees are sinks
- NPC contracts inject currency in controlled amounts
- destruction and repairs create additional sinks

## Item lifecycle

```text
Discovery/Gathering
      ↓
Raw Material
      ↓
Sorting/Refining
      ↓
Intermediate Material
      ↓
Manufacturing
      ↓
Equipment / Vehicle / Facility
      ↓
Use / Damage
      ↓
Repair or Salvage
      ↓
Recovered Material
      ↓
Market or Production
```

## Scarcity

Scarcity is regional. The same resource should have different effective availability and price depending on geography, extraction infrastructure, NPC events and player activity.

## Market model

Each market region owns an order book per tradable item.

Order types:

- limit buy
- limit sell
- immediate market purchase
- contract-based procurement

Matching priority:

1. compatible price
2. older order first
3. deterministic tie-breaker

Market history stores:

- timestamp
- unit price
- quantity
- region
- anonymous trade reference

## Pricing inputs

A player-visible price can emerge from orders, while NPC demand acts as a stabilizing sink/source.

The simulation tracks:

- stock level
- production rate
- consumption rate
- transport arrivals
- route risk
- tax rate
- historical volatility
- event modifiers

No hidden NPC vendor should be able to create unlimited perfect-price goods.

## Production economics

Blueprint cost is affected by:

- inputs
- facility efficiency
- worker/skill efficiency
- energy/fuel
- maintenance
- waste
- batch size
- quality
- opportunity cost

Production has a time component so industrial capacity becomes a strategic asset.

## Logistics economics

The rational hauling price is not simply distance × mass.

It includes:

- fuel
- expected damage
- expected loss
- escort cost
- route fees
- time value
- storage fees
- insurance premium

This makes dangerous shortcuts and secure long routes economically distinct.

## Contracts

Contract types:

- delivery
- buy order fulfillment
- manufacturing
- salvage
- escort
- emergency supply

Contract escrow holds payment until completion or a defined failure state.

## Corporation economy

Corporations can have:

- treasury
- member tax
- corporate wallets
- asset hangars
- dividends
- infrastructure budgets
- war budgets

Corporate ledger entries must identify actor, reason and timestamp.

## Anti-inflation controls

Primary currency sinks:

- market tax
- sales fees
- repair
- fuel
- facility maintenance
- territory upkeep
- contract collateral
- NPC services

Resource sinks:

- manufacturing
- repairs
- ammunition
- fuel
- construction
- salvage loss

## Anti-duplication invariants

For every transaction:

`total_currency_after = total_currency_before + authorized_injections - authorized_sinks`

For every item transfer:

`source_loss + destination_gain = 0` unless the operation explicitly creates or destroys inventory.

Every create/destroy operation has a domain reason and an audit event.

## Economic telemetry

Operators should be able to inspect:

- money supply
- item supply
- transaction volume
- top traded goods
- regional spreads
- production concentration
- resource inflation
- destruction rate
- bot-like order patterns
- suspicious creation/destruction events

## Example profitable loop

1. Scout discovers a region with excess scrap and shortage of processed alloy.
2. Buy scrap in the cheap region.
3. Refine near an efficient workshop.
4. Manufacture armor components.
5. Haul to a frontier market.
6. Sell under current demand.
7. Revenue funds another production run.
8. A rival notices the spread and creates competition.

The economy remains interesting because player behavior changes the conditions that created the opportunity.
