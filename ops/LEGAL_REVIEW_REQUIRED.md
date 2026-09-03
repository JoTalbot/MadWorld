# B10 Legal / Privacy Review Required

Status: **LEGAL REVIEW REQUIRED — UNVERIFIED (owner).** No Privacy Policy, Terms or
data-protection documentation exists in the repository. This cannot be resolved
from server evidence; it requires the product owner / legal reviewer. This
document enumerates the concrete items that must be addressed before a public
production launch.

## What the code does with data (factual, from code inspection)

- Players authenticate via session tokens (Bearer) issued by `/api/v1/sessions`;
  tokens are scoped to player state.
- Server-authoritative state is persisted in PostgreSQL (`madworld_db`): players,
  sessions, wallets, ledger entries, inventory, jobs, market orders, contracts,
  territory/corporation/social state, world events.
- An `analytics_events` table exists (event id, optional player id, event name,
  version, JSON properties, timestamp) but **no backend route writes to it and no
  external analytics/crash provider is integrated**. There is no debug telemetry
  sent off-server and no outbound HTTP from the backend.
- A `device_push_tokens` table exists (player id, token, platform=android,
  enabled) but **no push-delivery code, FCM/Firebase SDK, or registration route**
  is implemented. Notifications are local/in-app only (`NotificationCenter.kt`,
  SharedPreferences).
- The Android app requests only the `INTERNET` permission. No location, contacts,
  notifications, storage, camera, microphone or advertising permissions are
  requested. No advertising/tracker SDK is bundled (no Firebase/AdMob/Mixpanel/
  Amplitude/Crashlytics dependency).

## Required legal deliverables (LEGAL REVIEW REQUIRED)

1. **Privacy Policy** — published and linked (store listing + app). Must cover:
   - what personal data is collected (account/handle, device push token if push is
     ever enabled, game state, analytics/crash data if providers are added);
   - lawful basis, purpose and retention for each;
   - server location and hosting (this deployment runs on a cloud VM).
2. **Terms of Service / EULA** — acceptable use, virtual items/economy are
   game-world only, no real-money value unless explicitly offered, liability.
3. **Data collection disclosure** — explicit list in the store data-safety form
   and privacy policy; currently no data leaves the server except to the host.
4. **Analytics disclosure** — only required once an analytics provider is added;
   today analytics events are internal-only and unwritten. Do not claim analytics
   that does not exist.
5. **Crash reporting disclosure** — required before enabling any external crash
   provider (none today).
6. **Account/data deletion requirements** — GDPR/CCPA-style deletion and export
   path must be defined and implemented if offered in the EU/CA/UK; the backend has
   no delete-account endpoint today (needs product + engineering decision).
7. **Third-party provider disclosure** — list every external processor
   (hosting/PostgreSQL, and any future push/analytics/crash). None besides the
   cloud host is currently used.
8. **Permissions rationale** — `INTERNET` is required for API play; document it.
   Push notifications permission (Android 13+ `POST_NOTIFICATIONS`) will need a
   rationale if push is implemented; not requested today.
9. **Age ratings / content rating** — complete store content questionnaire.
10. **Retention/deletion policy** for backups and logs.

## How to satisfy

These are owner/legal actions, not code claims:

- Draft Privacy Policy and Terms (owner/legal) and host them.
- Implement account-deletion/data-export if required for target jurisdictions.
- Only after external providers are configured, update the data-safety disclosures
  to match.

Until these are completed, the release remains a **Release Candidate** with a
documented legal gate, not a public production launch.
