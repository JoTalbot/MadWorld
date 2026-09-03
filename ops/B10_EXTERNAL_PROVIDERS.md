# B10 External Provider Gate

## Push

Current repository state does not claim FCM/APNs delivery. `device_push_tokens` and local notification primitives are not proof of end-to-end delivery. Before release, select a provider, configure credentials outside Git, implement token registration/delivery/retry, and verify an offline-device delivery scenario.

## Crash reporting

Current repository state does not claim Crashlytics/Sentry or equivalent. Before release, select a provider, configure the SDK without committing secrets, submit a controlled test crash in a non-production track and verify the event appears with release/version metadata.

## Analytics

Current repository state does not claim external analytics delivery. Before release, select a provider, define minimum events and privacy basis, configure the SDK/endpoint, verify events arrive, and document retention/deletion behavior.

## Rule

Provider availability, credentials and external dashboards are environment evidence. Never mark these gates VERIFIED merely because a schema, dependency or placeholder exists.
