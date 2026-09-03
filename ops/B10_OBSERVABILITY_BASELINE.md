# B10 Observability Baseline

Observability is isolated to MadWorld and does not modify or depend on Octopus monitoring.

## Signals

- API liveness: `/health`.
- API readiness: `/health/ready` with database and migration count.
- World worker: tick progression, lag and failure/restart counters.
- Database: connectivity, migration count, backup success, free disk.
- Security: rate-limit/replay responses and authentication failures without logging credentials.

## Operational evidence

For a release candidate capture UTC timestamp, app/backend version, container image/tag, readiness response, latest worker tick, backup age and disk free space. Provider-specific crash/analytics/push dashboards are external gates and are not fabricated here.

## Boundary

Do not touch `/opt/octopus`, `/var/lib/octopus`, `/etc/octopus`, Octopus networks/volumes, or global host monitoring configuration from MadWorld deployment automation.
