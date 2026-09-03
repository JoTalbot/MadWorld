# B7 — Full Android Game Status

## Scope
B7 is the accepted Full Android Game batch. The existing authoritative backend remains the source of truth for player, economy, territory, world and social state.

## Implemented
- Dedicated `GameActivity` launcher.
- Bottom navigation for Base, World, Fleet, Market, Crew and Territory.
- Loading, signed-out, error/retry and offline/cached-state presentation.
- Reconnect refreshes through `PlayerViewModel` and repositories.
- Durable offline command-intent queue with idempotency-key deduplication.
- Allowlisted authoritative offline command dispatcher.
- FIFO queue drain after successful authenticated reconnect/session refresh; failed commands remain queued.
- Manufacturer creation now carries an idempotency key like the other supported social mutations.
- Authoritative settlement snapshots are protected against stale versions with `StaleStateGuard`.
- Local/in-app persistent notification center for queue synchronization and failure feedback.
- Accessibility semantics on core loading, connection, retry, offline, notification and navigation controls.
- Localization resource foundation in `strings.xml`.
- No authoritative balances, inventory results or server outcomes are stored in the offline queue.
- Existing typed authoritative state models remain the UI boundary.

## Verification
- Backend CI remains green through B6 and subsequent B7-triggered backend runs.
- Android CI #58 passed after the Compose context fix.
- The latest B7 integration changes require a fresh Android and Backend CI verification before B7 can be marked COMPLETE.

## Deferred within B7
- Push notification delivery and device-token registration.
- Full localization resource extraction for all remaining UI copy.
- Full accessibility audit and automated semantics coverage beyond the core controls.
- Rich command screens for every gameplay mutation.
- OS-level background queue worker. Queue draining is currently tied to authenticated reconnect/session refresh rather than a background worker.

These are explicitly deferred rather than silently treated as complete.
