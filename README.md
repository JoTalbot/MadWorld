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

## Current release status

MadWorld has completed the repository-side B1-B10 production program and is at the **B10 Release Candidate / GO AFTER OWNER ACTIONS** stage.

The repository contains the production-oriented implementation, release gates, CI contracts, Android build/test coverage, security hardening, operational procedures, backup/restore tooling, observability baselines and release evidence templates.

**Production release is intentionally not self-certified from repository state alone.** The remaining gates require real environment/owner evidence, including real-domain HTTPS, scheduled backup execution and measured RPO, fresh-host DR rehearsal, capacity validation, Android emulator/physical-device validation, external provider decisions, privacy/legal approval, incident ownership, final product approval of the severity-5 disaster clamp, and a final Release Gate run on the exact release commit.

See `ops/B10_ENVIRONMENT_HANDOFF.md` and `ops/B10_FINAL_BATCH_STATUS.md` for the executable remaining gates and evidence policy.

## Architecture and roadmap

See:

- `docs/GAME_DESIGN.md` - full game design document
- `docs/ARCHITECTURE.md` - technical architecture
- `docs/ECONOMY.md` - economy and production simulation
- `docs/CONTENT_PLAN.md` - world/content roadmap
- `docs/IMPLEMENTATION_ROADMAP.md` - staged development plan
- `docs/BATCH_IMPLEMENTATION_CONTRACT.md` - B1-B10 production execution contract
- `docs/IMPROVEMENT_BACKLOG.md` - accepted and deferred product improvements

## Production gate

The B10 contract is the final release gate. A working screen, endpoint, migration, APK or green repository-only test suite does not by itself constitute production readiness. The final release requires immutable evidence for every mandatory gate and a GO decision after all owner/environment dependencies are actually verified.
