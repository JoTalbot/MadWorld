# B10 Scheduled Backup + Measured RPO — Evidence Record

Date: 2026-09-04
Scope: MadWorld production backup automation (`/opt/madworld`) only.
Repo HEAD during this batch: `ec213ceaff60a4c5ee7f7afe992c303c22374049`

## Result

**FAIL — NOT EXECUTED (environment blocked).** No production backup was
produced by this batch, no timer state was observed on the production host, and
**no RPO is claimed**. The two mandatory gates
(Scheduled backup + actual RPO, Fresh-host DR + RTO) remain **OPEN**.

This batch was executed from the Arena Agent sandbox. The sandbox has:

- no SSH key material for `129.213.177.56` (no `~/.ssh`, no agent, no keys anywhere in the sandbox);
- no application-layer connectivity to the production host (see trace below);
- no `docker`, `psql`, `pg_dump` or `pg_restore` binaries;
- no copy of any production dump in the workspace (`/opt`, `/home`, `/var/backups` searched — none found).

Per the repository rule, repository/CI artifacts or scripts existing on HEAD do
not count as production evidence. This record therefore intentionally records
**no PASS** for the backup/RPO gate.

## Attempted actions (verbatim trace, UTC)

Verification window: `2026-09-04T10:07Z`–`2026-09-04T10:09:46Z`.

Consolidated trace captured `2026-09-04T10:09:46Z`:

```
[1] UTC clock: 2026-09-04T10:09:46Z

[2] SSH attempts (BatchMode=yes, publickey only, 12s connect timeout):
    ssh root@129.213.177.56:    Connection closed by 129.213.177.56 port 22
    ssh ubuntu@129.213.177.56:  Connection closed by 129.213.177.56 port 22
    ssh madworld@129.213.177.56:Connection closed by 129.213.177.56 port 22
    (same result for admin@ and deploy@; repeated attempts)
    SSH detail: TCP connect succeeds, then reset at kex_exchange_identification.

[3] TCP connect probe:
    port 22:  handshake OK (0ms)
    port 80:  handshake OK (0ms)
    port 443: handshake OK (0ms)
    port 5433: handshake OK (0ms)
    port 8000: handshake OK (0ms)
    port 8090: handshake OK (0ms)
    => every probed port completes a TCP handshake instantly. This is the
       signature of an egress interception filter (SYN-ACK for any destination),
       not of services being reachable.

[4] Application-layer probes:
    GET https://api.autosklo.org.ua/health/ready -> HTTP 000 err=35 (SSL_ERROR_SYSCALL)
    GET https://129.213.177.56/                    -> "Connected ... SSL_connect:
       SSL_ERROR_SYSCALL" (server-side or filter-side reset before TLS handshake)
    => no application protocol completes against the production target.
       NOTE: unrelated Cloudflare-fronted IPs are also unreachable from this
       sandbox, so this does NOT prove the production API is down; it proves
       this sandbox cannot reach it.

[5] Local tooling present in sandbox:
    docker    ABSENT
    psql      ABSENT
    pg_dump   ABSENT
    pg_restore ABSENT

[6] Repository artifact validation (this environment only):
    bash -n ops/backup_daily.sh    -> OK (syntax valid)
    bash -n ops/backup_restore.sh  -> OK (syntax valid)
    systemd-analyze verify ops/madworld-backup.{service,timer}
      -> only error is that /opt/madworld/ops/backup_daily.sh does not exist
         HERE (expected: this sandbox is not the production host)
    systemctl is-enabled/is-active madworld-backup.timer
      -> cannot run: no systemd bus in this sandbox
```

## Required Part-A record fields

| Item | Value recorded |
|---|---|
| Backup UTC start timestamp | NONE — no backup executed (host unreachable) |
| Backup UTC completion timestamp | NONE |
| Dump filename | NONE produced |
| Dump size | N/A |
| SHA-256 of dump | N/A (no dump) |
| `pg_restore --list` validation | N/A (no dump) |
| Available disk space on host | N/A — host not reachable; not measured |
| Retention configuration | Repository default: `RETENTION_DAYS=14`, `MIN_FREE_MB=1024`, `OnCalendar=*-*-* 03:15:00 UTC`, `Persistent=true`, `RandomizedDelaySec=10m`. Host-installed values NOT verified. |
| Timer state (`is-enabled` / `is-active` / `list-timers`) | NOT OBSERVED — production host unreachable; sandbox has no systemd bus |

## Repository-side static validation performed (PASS, but NOT host evidence)

- `ops/backup_daily.sh` exists on HEAD and passes `bash -n`.
- Script logic reviewed: fails closed when free space `< 1024 MiB` (exit 20),
  refuses zero-byte dumps (exit 21), writes `<stamp>.dump` + `<stamp>.dump.sha256`
  with `umask 077`, validates the dump with `pg_restore --list`, purges files
  older than 14 days.
- `ops/madworld-backup.service` + `ops/madworld-backup.timer` exist on HEAD and
  are well-formed systemd units (static parse). Schedule: daily 03:15 UTC.
- `sha256sum -c` and `pg_restore --list` verification of a real dump:
  **NOT RUN** — requires the host or a copy of a production dump.

These checks validate the *repository artifacts only*. They do not prove the
timer is installed, enabled, or producing dumps on `129.213.177.56`.

## Measured RPO

**NOT MEASURED.** Per the batch instructions, an RPO <= 24h is NOT claimed:
no scheduled run was observed, and no backup timestamp versus verification time
could be computed.

## PASS/FAIL summary

| Check | Result |
|---|---|
| Inspect backup scripts/units on host | FAIL — NOT EXECUTED (no host access) |
| Timer installed/enabled/active on host | FAIL — NOT OBSERVED (no host access) |
| One real production backup executed | FAIL — NOT EXECUTED (no host access) |
| Dump filename/size/SHA-256 recorded | FAIL — no dump |
| `pg_restore --list` validation of dump | FAIL — no dump |
| `sha256sum -c` on a real dump | FAIL — no dump |
| Retention/disk-guard behavior observed | FAIL — NOT OBSERVED (no host access) |
| Measured RPO from a real backup | FAIL — NOT MEASURED |
| Repository scripts syntactically valid | PASS (static only, this environment) |

## What was NOT tested

- Nothing on the production host was tested, changed, or observed.
- No scheduled or manual backup was executed; no dump/checksum exists.
- Host disk-space guard, retention purge, timer persistence and
  low-disk fail-closed behavior were not observed.
- The `sha256sum -c` and `pg_restore --list` acceptance steps in the batch
  instructions (Part A steps 5–6) were not run against any dump.

## Safety statement

- No MadWorld production resource was modified.
- Production DB (`127.0.0.1:5433` per prior evidence) remained online/untouched.
- No Docker resource was created, deleted or altered.
- Octopus/liza services, unrelated networks/volumes/PostgreSQL, public ports
  8000/8090 and the host itself were not touched.

## What is required to close this gate

1. SSH access to `129.213.177.56` (key material provisioned into the executing
   environment) or execution of the backup service directly on the host.
2. Run Part A steps 2–6 on the host and attach the outputs to this record.
