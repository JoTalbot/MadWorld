# Incident 2026-09-08 — production API returns 502

**State: OPEN / UNRESOLVED at the time of writing (2026-09-08T01:05Z).**
**Impact: total outage of the public API `https://api.autosklo.org.ua` — every path, not a subset.**

## 1. Externally confirmed, live

Confirmed from outside the server, without Remote Operator, at 2026-09-08T01:0xZ:

| Path | Result | Cloudflare Ray ID |
|---|---|---|
| `/health` | 502 Bad gateway | `a37a06c54db70604` |
| `/health/ready` | 502 Bad gateway | `a37a07120ed0e5b2` |
| `/api/v1/world/state` | 502 Bad gateway | `a37a072f1f930d9d` |

The Cloudflare error page reports **Browser: Working, Cloudflare: Working, Host: Error** on all three
samples, taken through different edge PoPs. This eliminates the edge, DNS and TLS from the fault
domain: DNS resolves to Cloudflare (`104.21.76.233`, `2606:4700:3031::ac43:ca13`) and the edge is
healthy — the **origin** is failing.

## 2. Server-side terminal evidence (Remote Operator, `remote-operator-results` branch)

| COMMAND_ID | Terminal state | Evidence |
|---|---|---|
| `cmd-20260908-151500-server-runtime-current` | DONE, exit 0, root | `http://127.0.0.1/health` → 301 to HTTPS; operator service + sync timer `active`/`enabled` |
| `cmd-20260908-153700-server-runtime-followup` | FAILED, exit 60 | `curl -fsSL` rejects the self-signed loopback certificate — probe defect, no application evidence |
| `cmd-20260908-153800-server-runtime-followup` | FAILED, exit 60 | same probe defect |
| `cmd-20260908-154100-server-runtime-tls-followup` | DONE, exit 0, root | **`https://127.0.0.1/health` → 502**; memory 22 Gi/23 Gi used, ~1.2 Gi available; load 3.10 6.65 4.93; one failed unit `octopus-slo-checker.service` (co-tenant, out of scope) |
| `cmd-20260908-160000-production-502-diagnose` | **TIMEOUT** after 180 s, empty stdout | unbounded `nginx -T` / `docker ps` / `ss` in a 3-minute budget produced no diagnosis |

Host identity `arm-server-01` / `129.213.177.56`, root execution verified from `id -u` in the payload
output, not assumed from the SSH identity.

## 3. Fault localisation

`ops/docker-compose.deploy.yml` publishes the API as `127.0.0.1:${API_HOST_PORT:-8090}:8000`
(host port 8000 belongs to a co-tenant project) with a 768 MB container limit. Host nginx terminates
TLS and proxies to that loopback port.

nginx answers (301 on HTTP, 502 on HTTPS), so **nginx is up and the upstream `127.0.0.1:8090` is not
serving**. Combined with a host sitting at 22 Gi/23 Gi used, the leading hypothesis is an **API
container that is stopped, crash-looping or OOM-killed**.

Eliminated by evidence, do not re-investigate without new facts:

| Hypothesis | Why it is out |
|---|---|
| Cloudflare / edge / WAF | edge reports itself healthy on 3 samples from different PoPs |
| DNS or TLS | resolution and TLS handshake succeed; error is an origin 502 |
| nginx down | nginx answers 301/502 itself, `systemd is-active` reported `active` |
| Deployment not applied | `Deploy on Push` for `fe0d939` completed **success** on all steps |
| `/opt/madworld` missing git checkout | by design — `rsync --exclude='.git/'`; revision lives in `.github-deployed-sha` |
| Remote Operator dead | service and sync timer `active`/`enabled`; commands execute as root |

Note that `deploy-on-push.yml` never runs `docker compose up`, so no deployment can restart the API —
a green deploy is not evidence that the application is running.

## 4. Queued response

Both requests are queued on the working branch and require the PR to be merged into `main` before the
scheduled broker can consume them. Filename order guarantees diagnosis runs first.

1. `cmd-20260908-003000-prod-502-diag-v2` — **read-only**. Every probe individually `timeout`-wrapped;
   probes the 8090 upstream, `compose ps`, per-container `State.Status`/`OOMKilled`/`RestartCount`,
   nginx config and error log, `dmesg` OOM lines, RSS top, `.env` key names only.
2. `cmd-20260908-010500-prod-502-recover-v1` — **self-gating recovery**, aborts without mutation when:
   - the upstream already answers 200 (`DECISION=NOOP_ALREADY_HEALTHY`), or
   - host `MemAvailable` < 900 MB (`DECISION=BLOCKED_LOW_MEMORY`) — protects co-tenant services on the
     shared host from an OOM cascade, or
   - a required compose/env file is missing.

   Otherwise it starts **only** the `api` service of the MadWorld compose project with `--no-build`
   (no image build on a loaded host, migrator never started), then verifies the postcondition against
   `127.0.0.1:8090/health`, `/health/ready` and `https://127.0.0.1/health`.

   Rollback: `docker compose -f ops/docker-compose.production.yml -f ops/docker-compose.deploy.yml
   --env-file /opt/madworld/.env stop api`. No data is written and no migration is run, so the action
   is reversible.

## 5. Reconciliation with existing release evidence

`ops/FINAL_RELEASE_DECISION.md` (2026-09-07) records as verified:

> Public `https://api.autosklo.org.ua/health/ready` returned HTTP 200 with database ok and
> `migrations_applied=41`.

That statement was true when measured and is **now stale**: the same endpoint returns 502. This
document does not modify the owner's GO/NO-GO decision, which remains an owner decision. It records
the technical fact that any gate depending on public API availability must be re-measured after
recovery, and must not be treated as PASS from the 2026-09-07 evidence.

Affected gates in `ops/B10_RELEASE_GO_NO_GO_MATRIX.md`: **Production HTTPS** must be re-verified after
recovery before it can move away from `OPEN`.

## 6. Open questions for the diagnostic output

- Is the API container `exited`, `restarting` or absent, and is `State.OOMKilled` true?
- Does `dmesg` show an OOM kill naming the API container or another process?
- Is the 768 MB container limit the binding constraint, or is the host itself exhausted by co-tenant
  workloads?
- Does the API fail at startup (configuration/migration) rather than being killed?

Root cause is **not** established until that evidence is in. This document must be updated with the
terminal result of both commands before the incident is closed.
