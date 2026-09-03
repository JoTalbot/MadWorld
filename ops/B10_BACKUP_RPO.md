# Backup automation and RPO

## Target

Daily PostgreSQL custom-format backup under `/opt/madworld/backups`, retained for 14 days by default. The service fails closed when free disk space is below 1 GiB and validates the dump with `pg_restore --list` plus SHA-256 metadata.

## Install on the intended host

```bash
sudo install -m 0755 ops/backup_daily.sh /opt/madworld/ops/backup_daily.sh
sudo install -m 0644 ops/madworld-backup.service /etc/systemd/system/madworld-backup.service
sudo install -m 0644 ops/madworld-backup.timer /etc/systemd/system/madworld-backup.timer
sudo systemctl daemon-reload
sudo systemctl enable --now madworld-backup.timer
sudo systemctl start madworld-backup.service
sudo systemctl status madworld-backup.timer
```

Do not place credentials in these unit files. `/opt/madworld/.env` remains owner-managed and must stay mode 600.

## Verification

```bash
sudo journalctl -u madworld-backup.service --since today
sudo ls -lh /opt/madworld/backups
sudo sha256sum -c /opt/madworld/backups/*.dump.sha256
```

A successful backup is not a successful disaster-recovery rehearsal. Periodically restore the newest dump into an isolated PostgreSQL database and run the existing `ops/backup_restore.sh` verification flow.

## RPO

With a daily schedule, the operational target is **RPO <= 24 hours**, subject to successful execution and disk availability. For a stricter RPO, increase the schedule frequency only after measuring storage, database load and restore time. The repository does not claim a production RPO until the timer is installed and at least one scheduled run is evidenced on the intended host.
