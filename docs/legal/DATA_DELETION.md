# MadWorld Account Data Deletion

**Status:** release-process definition; implementation verification required before public launch.  
**Last updated:** 2026-09-08

## Scope

A player may request deletion of the MadWorld account and personal data associated with the player identity.

## Data in scope

The deletion process covers, where present:

- player identity and handle;
- active and historical authentication sessions;
- device push tokens;
- player-linked game state and personal metadata;
- player-linked operational records where deletion is technically and legally appropriate.

## Records that may require retention

Some records may need limited retention where required for security, fraud prevention, financial/accounting obligations, legal claims, auditability or backup integrity. Such retention must be documented, minimized and deleted when the retention basis expires.

## Request workflow

1. Verify that the request is authorized by the account holder.
2. Disable active sessions and push tokens.
3. Delete or irreversibly anonymize player-linked data according to the approved retention schedule.
4. Preserve only records with a documented legal/security retention basis.
5. Record the deletion operation without storing unnecessary personal data.
6. Apply the same policy to recoverable production copies when their retention period expires.
7. Confirm completion through the official support channel.

## Engineering gate

The backend currently exposes session revocation endpoints, but the repository must not claim that a complete account-deletion endpoint exists unless it has been implemented and covered by database integration tests. Before public release, the deletion workflow must therefore be implemented or an explicitly approved manual/legal process must be documented and operationally tested.

## Backup handling

A deletion request does not require destructive rewriting of an immutable backup. Instead, the live database must remove/anonymize data and the backup retention schedule must ensure that expired copies are eventually destroyed. Restores must not silently reintroduce a deleted account into production without applying the current deletion ledger/process.

## Verification checklist

- [ ] Identity/request verification defined.
- [ ] Live account deletion/anonymization implementation verified.
- [ ] Push-token removal verified.
- [ ] Cascading/linked-record behavior verified on PostgreSQL.
- [ ] Backup retention period approved.
- [ ] Restore/delete reconciliation tested.
- [ ] Public privacy-policy contact published.
- [ ] Legal review completed for target jurisdictions.
