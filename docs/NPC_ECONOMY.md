# MadWorld — NPC Economy

## Goal

NPC factions and settlements are economic actors with bounded resources and objectives. They should create demand, supply and conflict without replacing players as the primary economic force.

## NPC actor model

An actor can have:

- treasury/resources;
- production capacity;
- consumption needs;
- inventories;
- preferred goods;
- faction relationships;
- strategic objectives;
- risk tolerance;
- known information;
- infrastructure;
- active contracts.

## Decisions

At simulation ticks, an NPC may choose to:

1. procure missing inputs;
2. produce needed goods;
3. move goods between locations;
4. repair infrastructure;
5. change prices or demand;
6. issue/accept contracts;
7. defend or contest strategic locations;
8. react to shortages, attacks or discoveries.

Decisions must be bounded by budgets and deterministic ordering.

## Economic behavior

NPCs should have needs and constraints rather than infinite inventories. A settlement with a damaged refinery can genuinely become fuel-poor. A faction losing a route can pay more for alternate logistics.

NPC buy/sell behavior must avoid creating a universal price floor/ceiling that destroys player markets.

## Faction differentiation

Factions should differ in priorities rather than simply having different colored uniforms. Examples:

- Settlement Coalition: stability, food, water and trade;
- Road Wardens: route security and toll infrastructure;
- Iron Dogs: industrial output and heavy vehicles;
- Dust Reavers: raids, salvage and disruption;
- Ash Covenant: rare resources and strategic control.

These are starting design identities, not final lore requirements.

## Player interaction

Players can exploit, cooperate with or compete against NPCs through:

- contracts;
- market orders;
- faction reputation;
- logistics;
- espionage/intelligence;
- defense and combat;
- infrastructure.

## Safety valves

NPC simulation must include:

- bounded money/item creation;
- explicit sinks;
- maximum stock levels where appropriate;
- production cooldowns/capacity;
- anti-exploit audit events;
- emergency recovery rules for pathological market states.

## Vertical-slice boundary

The first slice can model NPC demand and a small set of scheduled procurement/contract decisions. Full faction strategy, war planning and territory simulation should follow only after the economic core is measurable.
