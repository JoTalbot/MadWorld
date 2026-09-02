# MadWorld — Phase 4 Social Sandbox

## Scope

Phase 4 establishes the authoritative social-sandbox foundation:

- corporations / gangs / trading groups
- role and permission model
- shared wallet ownership boundary
- shared hangar and corporate asset model
- alliances and membership
- diplomacy and standings
- player/group social contracts
- player and corporation reputation records
- manufacturer / brand identity and reputation
- Android capability discovery and typed social state model

## Design

Social state is server-authoritative. A client may request a mutation, but ownership, role, permission, relation and counterparty invariants belong on the server.

### Default roles

`LEADER`, `DIRECTOR`, `QUARTERMASTER`, `TRADER`, `FLEET_COMMANDER`, `RECRUITER`, `DIPLOMAT`, `MECHANIC`, `MEMBER`.

### Core invariants

- corporation codes are unique
- tax is bounded to 0..10000 basis points
- membership is unique per corporation/player
- a corporation cannot establish diplomacy with itself
- hostile/war diplomacy cannot simultaneously enable trade
- a social contract has exactly one counterparty type
- standings are bounded to -10000..10000
- manufacturer identity belongs to one corporation

## API boundary

`GET /api/v1/social/capabilities` advertises the Phase 4 surface.

Validation endpoints expose the domain rules without inventing client-side authority. Full transactional mutation wiring remains behind the repository/UoW boundary and must be completed before production claims of feature completeness.

## Android

`Phase4State.kt` provides typed state for corporation, diplomacy, social contracts and manufacturer identity. `MadWorldApi` can discover social capabilities from the authoritative backend.

## Verification

`backend/tests/test_phase4_social.py` covers corporation creation, role validation, permission validation, diplomatic invariants and social-contract counterparty invariants.

## Deferred / next hardening

- transactional repository implementations for every Phase 4 table
- wallet and hangar mutation endpoints with role authorization
- alliance create/join/leave mutations
- full reputation mutation/event integration
- corporate UI and social management screens
- manufacturer integration into item provenance and quality
- economic settlement of social contracts
- diplomacy effects on NPC and market systems
