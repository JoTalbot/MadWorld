# MadWorld

## Post-apocalyptic persistent sandbox MMO for Android

MadWorld is a persistent online sandbox set in a brutal post-apocalyptic world. The game is inspired by the depth and systemic gameplay of space-economy MMOs: player-driven industry, logistics, markets, corporations, territorial conflict, scouting, risk, specialization and long-term progression.

The design goal is not to copy another game's setting or content. It is to translate the strongest systemic ideas of a deep sandbox MMO into a wasteland of armored vehicles, scarce resources, settlements, convoys, gangs and player-controlled territories.

## Core fantasy

> Build something valuable in a world where almost everything is scarce, move it through dangerous territory, and defend it from people who know exactly how much it is worth.

## Pillars

- Persistent online world
- Player-driven economy and regional markets
- Deep crafting and production chains
- Salvage, gathering, scavenging and refining
- Vehicles as customizable economic and combat assets
- Convoys, hauling, smuggling and logistics
- Corporations, alliances, contracts and reputation
- Territory control and infrastructure
- PvE factions, dynamic world events and hazards
- Risk/reward zones with meaningful loss
- Mobile-first controls and readable information architecture
- Server-authoritative simulation with anti-cheat controls

## Initial technical direction

- Android client: Kotlin + Jetpack Compose
- Game/runtime layer: modular systems architecture designed to support a lightweight 3D renderer later
- Backend: Kotlin/Ktor or Go services behind a versioned API
- PostgreSQL for authoritative persistent state
- Redis for cache, locks and transient coordination
- Object storage for media/build artifacts
- Deterministic server-side economic and market calculations
- Automated tests and GitHub Actions CI

## Repository roadmap

See:

- `docs/GAME_DESIGN.md` - full game design document
- `docs/ARCHITECTURE.md` - technical architecture
- `docs/ECONOMY.md` - economy and production simulation
- `docs/CONTENT_PLAN.md` - world/content roadmap
- `docs/IMPLEMENTATION_ROADMAP.md` - staged development plan

The first milestone is a playable vertical slice: account/session, character, garage, vehicle assembly, resource gathering, crafting, local market and one dangerous expedition loop.
