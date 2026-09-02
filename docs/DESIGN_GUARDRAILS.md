# MadWorld — Design Guardrails

These decisions are locked early because changing them after the economy and player assets exist would be spectacularly unpleasant.

## 1. Loss must matter, but loss must not erase motivation

Vehicles, cargo and modules can be damaged, destroyed, salvaged or recovered. Protection, insurance and safe routes reduce risk but never remove it completely.

## 2. Information is a resource

Scouting, market intelligence, route knowledge, faction standings and reports should create economic value. Do not reveal the entire world state for free.

## 3. The economy is regional

Avoid one global auction house. Regional markets create hauling, arbitrage, specialization and strategic geography.

## 4. Production is capacity-limited

Factories, skills, energy, inputs, queues and maintenance constrain output. Infinite crafting from a menu is forbidden.

## 5. Vehicles are economic identities

A combat build, hauler, scout and smuggler should have meaningful trade-offs. There must not be one universally best vehicle.

## 6. Corporations are real economic actors

Groups need permissions, treasury, assets, taxes, contracts, hangars, audit history and governance. Social systems must affect the economy and world.

## 7. PvP is opt-in only where appropriate, not globally safe

Security levels should create different risk profiles. High-value activity belongs in places where interception is possible.

## 8. Offline progress is strategic

Manufacturing, research, repair and other approved jobs continue on the server while the player is away. Real-time combat decisions remain interactive.

## 9. No pay-to-win

Paid products may provide appearance or convenience. Competitive power, territory and economic dominance cannot simply be purchased.

## 10. Mobile-first does not mean shallow

Complexity belongs in information architecture, automation and queues, not in requiring the player to tap through 40 screens.

## 11. Emergence over quest quantity

A refinery failure, shortage, war or convoy loss should be capable of creating missions and economic opportunities automatically.

## 12. Anti-bot design from day one

Important mutations require server validation, rate limits, idempotency and anomaly telemetry. Client automation must not be able to manufacture currency or items.

## 13. World state persists

Player actions should change stock, prices, infrastructure, territory, faction relations and future opportunities. The world is not a static backdrop.

## 14. EVE-inspired systems, original MadWorld identity

We borrow high-level sandbox principles such as specialization, player markets, industry, logistics, corporations and territorial conflict. We do not copy proprietary characters, assets, terminology, lore or content.

## 15. The world map is dynamic

Roads, bridges, checkpoints, settlements, resource sites and danger levels can change through persistent world events and player activity. Navigation is a strategic system, not a static wallpaper.

## 16. Specialization must be meaningful

A character or corporation can become exceptionally good at a narrow discipline, but broad mastery carries opportunity cost. Build diversity must matter economically and operationally.

## 17. Items have quality and history

Meaningful assets can have quality, wear, repair state, manufacturing origin and provenance. High-value items can become recognizable assets rather than anonymous stack counts.

## 18. Manufacturers and brands can matter

Players and corporations may eventually create branded components and vehicles. Reputation, quality consistency and production history can become part of market value without becoming mandatory complexity for every item.

## 19. Finance is a risk system, not free money

Credit, collateral, insurance, investment and other financial instruments are potential economic tools. Every instrument must have a controlled source of capital, risk, sink, default/recovery behavior and anti-inflation rules.

## 20. NPC factions are economic agents

NPC factions and settlements should gather, produce, consume, trade, suffer shortages, lose assets and react to world events. NPC activity must be bounded and simulated rather than functioning as an infinite item/currency faucet.

## 21. Infrastructure is an economic asset

Player-built garages, workshops, warehouses, depots, fuel/water facilities and fortified posts should create real strategic value, upkeep costs and vulnerabilities.

## 22. Intelligence can be a tradable service

Route reports, price intelligence, resource discoveries, convoy sightings and strategic information can be valuable outputs of scouting and networks. Information must age, have uncertainty and avoid becoming an omniscient UI feed.

## 23. Simulation must be deterministic enough to audit

World ticks, NPC decisions, market effects and scheduled events should use canonical server time, versioned rules and reproducible inputs where practical. Important state transitions must remain explainable from logs.

## 24. Improve continuously, but separate proposals from commitments

During development, every meaningful improvement discovered by engineering, design, testing or player-flow analysis is recorded in `docs/IMPROVEMENT_BACKLOG.md`. A proposal is not automatically implemented. It is explicitly marked as accepted, rejected or deferred before it changes a locked system.
