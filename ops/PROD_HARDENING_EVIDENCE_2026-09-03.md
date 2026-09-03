# MadWorld Production Hardening Evidence

Date: 2026-09-03
Scope: MadWorld production infrastructure only.

## Result

Production HTTPS/reverse-proxy hardening is VERIFIED from the Arena Agent server audit.

## Server topology verified

- MadWorld API container: `madworld-api-1`
- Container API port: `8000`
- Host binding: `127.0.0.1:8090 -> 8000`
- Public API is not directly exposed on host ports 8000/8090.
- PostgreSQL remains bound to `127.0.0.1:5433`.
- Unrelated infrastructure was not modified.

## Reverse proxy

`https://api.autosklo.org.ua` -> nginx -> `127.0.0.1:8090`

TLS certificate:

- Issuer: Cloudflare Origin CA
- SAN: `api.autosklo.org.ua`
- Valid through: 2041-08-30

## DNS

Cloudflare proxied DNS resolves to:

- `104.21.76.233`
- `172.67.202.19`

## Health verification

Public `/health/ready` returned HTTP 200 with:

`{"database":"ok","migrations_applied":41}`

## Network hardening

- nftables INPUT policy is DROP.
- Allowed public ports include 80 and 443.
- Host ports 8000 and 8090 are not publicly allowed.
- Direct non-proxied HTTPS access is denied.
- Domain access is routed through the intended proxy path.

## Finding and remediation

A hardening discrepancy was found on HTTP port 80: nginx `return 301` executed in the rewrite phase before the access-phase allow/deny check, causing non-allow-listed clients to receive a redirect instead of 403.

The redirect was moved behind access control using the configured named-location/`try_files` flow.

Post-fix verification:

- external HTTP access to the server IP: HTTP 403
- `nginx -t`: successful
- public HTTPS `/health/ready`: HTTP 200

## Restart verification

- nginx is enabled under systemd.
- MadWorld containers use `restart: unless-stopped`.
- A live `systemctl restart nginx` was performed successfully.
- `/health/ready` remained HTTP 200 after restart.

## Host reboot limitation

A full host reboot was intentionally not performed because the host contains co-tenant services. Reboot persistence is therefore not directly proven by a live reboot. Service enablement and container restart policy were verified instead.

## Evidence timestamp

Arena Agent recorded the audit window as approximately `2026-09-03T21:35Z` through `2026-09-03T21:41Z`.

## Release interpretation

This evidence closes only the real-domain HTTPS/reverse-proxy gate. It does not certify backups/RPO, fresh-host DR/RTO, capacity, Android device/matrix validation, provider decisions, legal approval, on-call ownership, rollback rehearsal, owner approval, or final release readiness.

The final exact-head Release Gate must be rerun after this evidence commit before production release.
