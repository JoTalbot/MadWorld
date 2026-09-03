# B7 — Full Android Game Status

## Scope
B7 is the accepted Full Android Game batch. The existing authoritative backend remains the source of truth for player, economy, territory, world and social state.

## Implemented in this slice
- Dedicated `GameActivity` launcher.
- Bottom navigation for Base, World, Fleet, Market, Crew and Territory.
- Loading, signed-out, error/retry and offline/cached-state presentation.
- Reconnect refreshes through the existing `PlayerViewModel` and repositories.
- Durable offline command-intent queue with idempotency-key deduplication.
- No authoritative balances, inventory results or server outcomes are stored in the offline queue.
- Existing typed authoritative state models remain the UI boundary.

## Verification
- Backend CI B6: green, including migrations, module resolution and 143 tests.
- Android CI is required after the B7 Android changes before B7 can be marked COMPLETE.

## Deferred within B7
- Push notification delivery and device-token registration.
- Full localization resource extraction.
- Accessibility audit and automated semantics checks.
- Rich command screens for every gameplay mutation.
- Background queue worker that drains queued commands against authenticated API endpoints.

These are explicitly deferred rather than silently treated as complete.
