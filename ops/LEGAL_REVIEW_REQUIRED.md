# B10 Legal / Privacy Review Required

Status: **LEGAL REVIEW REQUIRED — UNVERIFIED (owner).** No Privacy Policy, Terms or data-protection documentation exists in the repository. This cannot be resolved from server evidence; it requires the product owner / legal reviewer. This document enumerates the concrete items that must be addressed before a public production launch.

## What the code does with data (factual, from code inspection)

- Players authenticate via session tokens (Bearer) issued by `/api/v1/sessions`; tokens are scoped to player state.
- Server-authoritative state is persisted in PostgreSQL (`madworld_db`): players, sessions, wallets, ledger entries, inventory, jobs, market orders, contracts, territory/corporation/social state, world events.
- An `analytics_events` table exists (event id, optional player id, event name, version, JSON properties, timestamp) but no external analytics provider is integrated and no backend route currently writes analytics events. There is no debug telemetry sent off-server and no outbound analytics/crash HTTP from the backend.
- A `device_push_tokens` table exists (player id, token, platform=android, enabled). FCM HTTP v1 sender code and authenticated push-token registration/disable routes are implemented, but **production push delivery remains unverified** and no real provider credentials are stored in the repository.
- Android Firebase initialization is conditional on the required release configuration values. The messaging service registers refreshed FCM tokens against the authenticated MadWorld session and deliberately does not log token values or credentials.
- Crash reporting is intentionally not implemented and remains an owner waiver. No Crashlytics/Sentry/etc. SDK is claimed.
- The Android app currently requests only the `INTERNET` permission. `POST_NOTIFICATIONS` is not currently requested by the app, so notification permission behavior on Android 13+ remains part of the physical-device verification gate.

## Required legal deliverables (LEGAL REVIEW REQUIRED)

1. **Privacy Policy** — published and linked (store listing + app). Must cover:
   - what personal data is collected (account/handle, device push token if push is enabled, game state, and any future analytics/crash data);
   - lawful basis, purpose and retention for each;
   - server location and hosting (this deployment runs on a cloud VM).
2. **Terms of Service / EULA** — acceptable use, virtual items/economy are game-world only, no real-money value unless explicitly offered, liability.
3. **Data collection disclosure** — explicit list in the store data-safety form and privacy policy; push-token processing must be disclosed if FCM is enabled in production.
4. **Analytics disclosure** — only required if an analytics provider is added; today analytics events are internal-only and unwritten. Do not claim analytics that does not exist.
5. **Crash reporting disclosure** — required before enabling any external crash provider; none is currently configured.
6. **Account/data deletion requirements** — GDPR/CCPA-style deletion and export path must be defined and implemented if required for target jurisdictions; the backend has no delete-account endpoint today and needs a product + engineering decision.
7. **Third-party provider disclosure** — list every external processor (hosting and Firebase/FCM if enabled, plus any future analytics/crash providers).
8. **Permissions rationale** — `INTERNET` is required for API play. If notifications are enabled for Android 13+, document the `POST_NOTIFICATIONS` rationale and runtime behavior.
9. **Age ratings / content rating** — complete store content questionnaire.
10. **Retention/deletion policy** for backups, logs and device push-token records.

## Provider status

- **FCM / Firebase Cloud Messaging:** implementation present; production configuration and physical delivery evidence are still required before public launch.
- **Crash reporting:** not required per owner decision; waiver remains active.
- **Analytics:** not required per owner decision; waiver remains active.

## How to satisfy

These are owner/legal actions, not code claims:

- Draft Privacy Policy and Terms (owner/legal) and host them.
- Implement account-deletion/data-export if required for target jurisdictions.
- Configure the approved Firebase project and production credentials outside Git, then execute the physical-device push verification matrix.
- Only after external providers are configured, update the data-safety disclosures to match actual behavior.

Until these are completed, the release remains a **Release Candidate** with a documented legal gate, not a public production launch.
