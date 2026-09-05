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

## Local development and tests

```bash
cd backend
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt pytest
python -m pytest -q -m "not integration"      # unit suite, no database required
MADWORLD_DATABASE_URL=postgresql://madworld:madworld@localhost:5432/madworld_test \
  python scripts/migrate.py && python -m pytest -q   # full suite incl. PostgreSQL integration
```

Notes:

- `requirements.txt` pins `httpx2` because Starlette's `TestClient` now targets it; installing the legacy `httpx` alongside only produces a deprecation warning.
- Every HTTP handler reads storage through the `UnitOfWork` port (`app/application/ports.py`). The account snapshot (`PlayerStateRepository`) and the session boundary (`app/infrastructure/sessions.py`) have both PostgreSQL and in-memory implementations, so the whole API layer is testable without a database.
- Migration files must have a unique, monotonically increasing numeric prefix. `discover_migrations` rejects duplicates; the historical duplicates (`003`, `009`, `010`, `011`, `012`) are grandfathered because their order is already recorded in production `schema_migrations` history.

## Scaling constraint: in-process abuse controls

The rate limiter, replay guard and abuse scorer in `app/main.py` keep state in process memory. They protect a single API process. Running several uvicorn workers or API replicas multiplies the effective limits and makes replay detection per-process. Until these primitives are backed by PostgreSQL or Redis, production must run exactly one API process (as `ops/docker-compose.production.yml` does), or the edge (reverse proxy / WAF) must enforce equivalent limits.
