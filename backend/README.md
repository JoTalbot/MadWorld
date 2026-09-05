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

## Abuse controls and horizontal scaling

Rate limiting, replay detection and abuse scoring have two interchangeable backends
(`app/infrastructure/abuse_controls.py`):

| `MADWORLD_ABUSE_CONTROL_BACKEND` | Storage | Safe for |
|---|---|---|
| `postgres` (default when `MADWORLD_DATABASE_URL` is set) | `abuse_control_*` tables (migration 034) | any number of API processes / replicas |
| `memory` (default otherwise; also used by the unit suite) | process memory | exactly one API process |

The PostgreSQL backend is **fail-open**: if the database is unreachable the request is
admitted and the failure is logged, so a control-plane outage does not turn into a full
API outage; `/health/ready` reports the database problem separately. Hot-path writes prune
expired rows for their own key; `prune_expired()` performs bulk cleanup for operators.

Tuning: `MADWORLD_RATE_LIMIT` (requests per 60 s per client, default 120).

## Sessions

- `POST /api/v1/sessions` – create/refresh a session for a handle (30-day TTL).
- `DELETE /api/v1/sessions/current` – log out the presented bearer token (204).
- `DELETE /api/v1/sessions` – log out everywhere; returns the number of revoked sessions.

## Health probes

- `GET /health` – liveness, no dependencies.
- `GET /health/ready` – 503 if PostgreSQL is unreachable; otherwise 200 with `status`
  `ok` or `degraded` (unmigrated schema, missing world state, or world tick older than
  `MADWORLD_READY_MAX_TICK_LAG_SECONDS`, default 900). Degraded tick lag is informational:
  the API stays ready while the world worker is recovered.

## Lint

`ruff check .` (config in `ruff.toml`) runs in CI. The rule set is intentionally narrow –
correctness, unused imports, import order and modern syntax – and does not enforce formatting.
