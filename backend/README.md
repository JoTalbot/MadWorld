# MadWorld Backend

Server-authoritative MMO backend foundation.

## Initial domain services

- authentication / player identity
- wallet and immutable ledger
- inventory and item stacks
- assets and vehicles
- stations / settlements
- market orders and trade matching
- industry jobs and recipes
- contracts and logistics
- expeditions and encounters
- corporations and territory

The backend owns all authoritative state. Android is a client and never decides balances, item ownership, completed jobs, or combat outcomes.

## MVP API

Planned REST surface:

- `GET /api/v1/me`
- `GET /api/v1/wallet`
- `GET /api/v1/inventory`
- `GET /api/v1/market/orders`
- `POST /api/v1/market/orders`
- `POST /api/v1/industry/jobs`
- `GET /api/v1/industry/jobs`
- `POST /api/v1/contracts`
- `POST /api/v1/expeditions`
- `GET /api/v1/world`

Realtime events will use WebSocket connections for market updates, expedition results, corporation activity and combat state.
