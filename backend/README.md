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

Rate-limit keys: every request is budgeted twice – per **network origin** and, when a bearer
token is present, per **session** (hashed token). Behind a reverse proxy set
`MADWORLD_TRUSTED_PROXIES` (comma-separated IPs/CIDRs) so `X-Forwarded-For` from that proxy is
honoured; from any other peer the header is ignored. Invalid entries are logged and skipped.

Tuning: `MADWORLD_RATE_LIMIT` (requests per 60 s per key, default 120). Active sessions per
player are capped at `MAX_ACTIVE_SESSIONS` (5); creating a new one revokes the oldest.
The world tick worker runs `prune_expired()` after each owned tick.

## Sessions

- `POST /api/v1/sessions` – create/refresh a session for a handle (30-day TTL).
- `DELETE /api/v1/sessions/current` – log out the presented bearer token (204).
- `DELETE /api/v1/sessions` – log out everywhere; returns the number of revoked sessions.

## Metrics

`GET /metrics` – Prometheus text format, no external dependency:
`madworld_http_requests_total{method,route,status}`, `madworld_http_request_duration_seconds`
(histogram), `madworld_abuse_events_total{kind}`, plus DB-backed gauges
`madworld_world_tick`, `madworld_world_tick_lag_seconds`, `madworld_abuse_control_rows{table}`.
Counters are per process; scrape every replica.

## Health probes

- `GET /health` – liveness, no dependencies.
- `GET /health/ready` – 503 if PostgreSQL is unreachable; otherwise 200 with `status`
  `ok` or `degraded` (unmigrated schema, missing world state, or world tick older than
  `MADWORLD_READY_MAX_TICK_LAG_SECONDS`, default 900). Degraded tick lag is informational:
  the API stays ready while the world worker is recovered.

## Quality gates

- `ruff check .` (config in `ruff.toml`). Intentionally narrow – correctness, unused
  imports, import order and modern syntax; formatting is not enforced.
- `mypy` (config in `mypy.ini`). Covers `app/domain`, all of `app/application` and the
  new infrastructure modules. Legacy application modules are listed with
  `disallow_incomplete_defs = False`; real type errors are still reported there.
  Remove a module from that list once its signatures are complete.
- `python scripts/export_android_golden.py` (needs PostgreSQL) regenerates the golden JSON
  under `android/app/src/test/resources/golden/` consumed by Android `GoldenParserTest`.
- `python scripts/export_openapi.py --check` – `contracts/openapi.json` is the committed
  Android-facing API contract. After an intentional API change run the script without
  `--check` and review the JSON diff in the PR.
