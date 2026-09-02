# API migration: vehicle repair

## Legacy endpoint

`POST /api/v1/vehicles/{vehicle_id}/repair` is retired. It no longer mutates vehicle durability.

A call receives HTTP `410 Gone` and the following migration headers:

- `Deprecation: true`
- `Sunset: Wed, 30 Sep 2026 00:00:00 GMT`
- `X-MadWorld-Migration: vehicle-repair-v2`

Legacy usage is also emitted to the application telemetry logger as `legacy_repair_api_used` so the migration can be measured before the compatibility code is removed.

## Replacement

Use the authoritative persistent repair-job flow:

1. `POST /api/v1/vehicles/{vehicle_id}/repair-job`
2. Send `Idempotency-Key` and a body containing `inventory_id` and `amount`.
3. Wait for the authoritative completion time.
4. `POST /api/v1/repair-jobs/{job_id}/complete` with a fresh `Idempotency-Key`.

The repair-job flow consumes repair kits transactionally, uses server time, persists the job and applies durability only after the job is legitimately complete.

## Migration policy

The old endpoint is kept as an explicit tombstone rather than silently performing the old synchronous mutation. This prevents clients from accidentally bypassing the authoritative repair-job model while still giving them a machine-readable replacement and a sunset signal.

After all known clients have migrated, the tombstone route can be removed in a breaking API release.
