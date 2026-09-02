# MadWorld — Game Design Document

## 1. Vision

MadWorld is a persistent Android sandbox MMO about survival, ownership, production, logistics and conflict in a ruined world. The player begins as a scavenger with a barely functioning vehicle and can eventually become a manufacturer, hauler, trader, gang leader, settlement owner or regional power broker.

The game uses a systemic design: resources have sources and sinks, items have manufacturing chains, markets respond to supply and demand, transportation creates risk, and conflict changes economic conditions.

## 2. Translation of deep sandbox MMO mechanics into the wasteland

| Sandbox MMO concept | MadWorld implementation |
|---|---|
| Spacecraft | Cars, trucks, armored vehicles, bikes, utility rigs |
| Modules/fittings | Engines, armor, tires, suspension, weapons, fuel systems, radios, cargo modules |
| Ore mining | Scrap yards, abandoned mines, wreck fields, industrial ruins |
| Refining | Sorting, dismantling, smelting, chemical processing |
| Manufacturing | Parts, ammunition, tools, vehicles, structures, consumables |
| Stations | Settlements, garages, workshops, depots and fortified hubs |
| Regions | Wasteland regions connected by roads and dangerous routes |
| Trade hubs | Regional markets in settlements |
| Hauling | Convoys and cargo runs |
| Missions | Contracts, faction jobs, courier jobs, salvage expeditions |
| Corporations | Gangs, clans, trading companies and settlements |
| Alliances | Regional pacts and military/economic coalitions |
| Territorial sovereignty | Control of roads, wells, mines, depots and settlements |
| Scouting | Recon vehicles, informants, radio intelligence |
| Null/low/high security space | Safe settlements, contested frontier, lawless wasteland |
| Fleet combat | Convoy combat, raids, ambushes and settlement assaults |
| Insurance | Vehicle recovery/insurance systems with meaningful limits |
| Skills | Character disciplines and certifications |
| Market orders | Buy/sell orders with regional pricing and taxes |
| Contracts | Delivery, procurement, manufacturing and recovery contracts |

## 3. Player progression

### 3.1 Starting state

The player owns:

- basic survivor character
- damaged starter vehicle
- small storage container
- handheld tools
- limited fuel
- access to a protected settlement

### 3.2 Major careers

Players can combine careers; no class lock is required.

- Scavenger: salvage and exploration
- Gatherer: raw materials and water
- Mechanic: vehicle repair and component production
- Manufacturer: industrial production
- Trader: arbitrage and regional markets
- Hauler: cargo logistics and convoy work
- Mercenary: combat contracts
- Raider: high-risk player and NPC attacks
- Scout: reconnaissance and intelligence
- Smuggler: restricted cargo and clandestine routes
- Settlement operator: infrastructure and services
- Fleet commander: group combat and convoy operations
- Broker: contracts, financing and resource intermediation

## 4. Vehicle system

Vehicles are the equivalent of player assets and the central material object in the world.

### Chassis families

- motorcycle
- buggy
- compact car
- sedan
- muscle car
- pickup
- light truck
- heavy truck
- armored carrier
- utility tanker
- mobile workshop
- convoy command vehicle

### Vehicle attributes

- mass
- durability
- armor
- acceleration
- top speed
- fuel consumption
- handling
- heat
- cargo capacity
- towing capacity
- power generation
- electrical capacity
- weapon hardpoints
- utility hardpoints
- crew capacity
- sensor/radio range

### Modular components

- engine
- transmission
- radiator
- fuel system
- battery
- suspension
- wheels/tires
- chassis armor
- windows/plates
- cargo container
- fuel tank
- water tank
- winch
- turret
- machine gun
- autocannon
- harpoon
- mining/salvage tools
- radio
- sensor package

Every meaningful component is an economic item that can be made, traded, damaged, repaired, salvaged and replaced.

## 5. World structure

### Security layers

1. Sanctuary: strong NPC protection, lower rewards.
2. Frontier: partial protection, active faction conflict.
3. Lawless wasteland: maximum risk, maximum resource quality.
4. Catastrophe zones: temporary extreme-risk events and rare materials.

### Points of interest

- settlements
- fuel stations
- wells
- scrap fields
- abandoned factories
- mines
- garages
- military depots
- wreck sites
- underground facilities
- radio towers
- checkpoints
- bandit camps
- faction bases
- rare-event locations

The world should be data-driven so new locations and regional economies can be added without code changes.

## 6. Resource hierarchy

Raw resources:

- ferrous scrap
- non-ferrous scrap
- rare metals
- polymers
- glass
- rubber
- chemicals
- electronic components
- fuel fractions
- water
- food
- medicine ingredients

Intermediate resources:

- steel plates
- alloys
- wire
- circuits
- batteries
- glass panels
- rubber compounds
- fuels
- lubricants
- explosives components

Advanced goods:

- engines
- transmissions
- armor panels
- weapons
- ammunition
- sensors
- radios
- vehicle modules
- settlement modules

## 7. Production

Manufacturing follows multi-stage blueprints rather than one-click item generation.

Example:

Scrap -> sorted metal -> refined alloy -> steel plate -> armor panel -> armored door -> vehicle assembly.

Recipes can have:

- material requirements
- labor time
- facility requirements
- skill requirements
- tool requirements
- quality ranges
- research requirements
- regional bonuses
- batch sizes
- energy/fuel requirements
- waste/by-products

Factories consume inputs and create outputs over time. Production can continue while the player is offline.

## 8. Facilities

Player/group facilities include:

- workshop
- garage
- refinery
- machine shop
- foundry
- chemical plant
- ammo plant
- vehicle assembly yard
- warehouse
- fuel depot
- water purifier
- radio station
- fortified checkpoint

Facilities have power, fuel, maintenance, capacity and security requirements.

## 9. Economy

The economy is player-driven but supported by NPC sinks and dynamic supply generation.

### Market features

- regional order books
- buy/sell orders
- market taxes
- transaction fees
- price history
- volume history
- item quality/condition where relevant
- regional scarcity
- hauling premiums
- NPC baseline demand
- contracts
- auctions for rare assets

### Economic principle

Distance + danger + scarcity = price differentiation.

A player should be able to make money by identifying an imbalance, taking the risk to move or transform the goods, and exploiting the price difference.

## 10. Logistics

Cargo is physical and capacity constrained.

- cargo volume
- cargo mass
- fuel requirements
- route distance
- route danger
- checkpoint risk
- convoy size
- escort strength
- cargo insurance
- interdiction risk

Players can accept:

- courier contracts
- bulk haulage contracts
- timed deliveries
- fragile cargo contracts
- faction logistics contracts
- emergency resupply missions
- high-value smuggling contracts

## 11. Combat

Combat should reward preparation and information rather than raw reflex alone.

### Combat layers

- vehicle-to-vehicle
- convoy-vs-convoy
- settlement defense
- ambushes
- escort missions
- NPC faction attacks
- territory battles

### Damage

Vehicles use component-aware damage. Damage may affect:

- mobility
- steering
- weapons
- cargo integrity
- fuel efficiency
- sensors
- radio
- armor

Destruction may produce salvage and partial recovery rather than simply removing every economic trace.

## 12. PvP risk model

Not every location has the same consequences.

Protected zones discourage indiscriminate attacks. Frontier zones permit conflict with penalties. Lawless zones allow high-risk combat.

High-value cargo must therefore create meaningful strategic tension.

## 13. Corporations / gangs

A group can own:

- shared wallet
- hangars
- warehouses
- vehicles
- facilities
- territory claims
- contracts
- reputation

Roles:

- leader
- director
- quartermaster
- trader
- fleet commander
- recruiter
- diplomat
- mechanic

Group systems include permissions, taxes, shared assets, dividends, internal contracts and audit logs.

## 14. Alliances and politics

Groups can:

- sign treaties
- share markets
- create transit agreements
- impose embargoes
- contest territory
- defend allies
- maintain neutral standings
- negotiate access to infrastructure

Diplomatic standings should affect NPC reactions and market access.

## 15. Territory

Control is not merely a cosmetic flag. A controlled region can provide:

- tax income
- safer roads
- resource extraction bonuses
- facility bonuses
- market discounts
- repair/refuel services
- intelligence

Territory can be contested through scheduled strategic objectives rather than requiring players to be online 24/7.

## 16. Missions and dynamic content

A mission generator creates jobs from world state.

Inputs include:

- local shortages
- damaged facilities
- faction wars
- resource discoveries
- convoy losses
- weather/disaster conditions
- settlement demand
- market prices

This allows missions to emerge from simulation instead of being a static quest list.

## 17. Research and skills

Skills improve efficiency rather than acting only as character levels.

Skill families:

- driving
- mechanics
- metallurgy
- electronics
- chemistry
- logistics
- trading
- scouting
- combat
- leadership
- diplomacy

Offline progression can be supported through queued training, subject to progression rules.

## 18. Reputation

Separate reputation values exist for:

- major NPC factions
- settlements
- corporations
- individual contracts
- criminal status

Reputation unlocks services, missions, production rights, discounts and political access.

## 19. Survival systems

Keep survival systems focused on strategic gameplay rather than tedious micromanagement.

Core survival resources:

- health
- fuel
- water
- food
- vehicle condition

Optional advanced systems can include heat, dust, radiation and weather hazards.

## 20. Offline and mobile-first design

A player must be able to perform economically meaningful actions in short sessions.

The mobile UI centers on:

- current asset state
- market watchlist
- production queues
- contracts
- map
- notifications
- fleet/vehicle status

Long-running activities continue server-side.

## 21. Endgame

Endgame emerges through ownership and specialization.

Examples:

- dominant manufacturing group
- regional logistics network
- trade empire
- mercenary corporation
- territorial warlord
- settlement federation
- intelligence network
- specialist vehicle manufacturer

There is no single mandatory victory condition. The world itself is the competition.

## 22. Monetization principles

Avoid pay-to-win power sales.

Potential monetization:

- cosmetics
- vehicle skins
- banners/decals
- account convenience that does not create combat/economic dominance
- optional subscription with quality-of-life features

Competitive assets must remain obtainable through gameplay.

## 23. MVP

The first playable milestone contains:

- account/session
- one character
- one starter vehicle
- one settlement
- one regional map
- five resources
- 15 crafted items
- garage and repair
- basic gathering/scavenging
- crafting queue
- local market
- five contracts
- one PvE expedition
- vehicle combat prototype
- persistence
- server-authoritative inventory

## 24. Design rule

Every major feature should answer at least one of these questions:

1. What does the player make?
2. What does the player risk?
3. What does the player trade?
4. Who needs the player's service?
5. What changes in the world because the player acted?

Features that answer none of these should be treated with suspicion. Human beings have enough useless menus already.
