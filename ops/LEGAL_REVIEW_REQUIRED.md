# B10 Legal / Privacy Review

Status: **DRAFTS PREPARED — FINAL LEGAL REVIEW STILL REQUIRED.**

On 2026-09-08 the release owner requested that the project prepare the privacy, terms and deletion documentation autonomously. Drafts are now in:

- `docs/legal/PRIVACY_POLICY.md`
- `docs/legal/TERMS_OF_SERVICE.md`
- `docs/legal/DATA_DELETION.md`

These documents are intentionally factual about the current implementation and do not claim providers or processing that are not configured. They still require final jurisdiction-specific legal review and publication of a valid operator/support contact before public launch.

## Current data processing boundary

- Players authenticate via Bearer session tokens issued by `/api/v1/sessions`.
- Server-authoritative state is persisted in PostgreSQL, including player/game state, sessions, wallets, inventory, jobs, market orders, contracts and social/world state where applicable.
- `analytics_events` exists in the schema, but no external analytics provider is configured and the current backend does not claim external analytics delivery.
- `device_push_tokens` stores Android FCM tokens when push is enabled. The API does not return the token and the application avoids logging token values.
- External crash reporting is not configured and is excluded from the release scope.
- The Android application currently requires `INTERNET`; Android 13+ notification permission behavior remains part of device verification.

## Owner decisions recorded

- **Push notifications:** required for the release scope. Production FCM configuration and a real physical-device delivery test remain required evidence.
- **Crash reporting:** not required for this release.
- **Analytics:** not required for this release.
- **Privacy/Terms:** draft prepared; legal publication/review remains mandatory.
- **Deletion:** a documented deletion workflow is prepared, but the repository must not claim complete automated account deletion until the implementation and PostgreSQL integration behavior are verified.

## Remaining external/legal gate

1. Publish the final Privacy Policy and Terms with a valid operator/support contact.
2. Complete store data-safety/content declarations consistently with the final production configuration.
3. Verify account deletion implementation or approve and operationally test the documented deletion process.
4. Configure the approved Firebase project outside GitHub Secrets/repository contents and complete physical-device FCM delivery verification.
5. Complete the applicable age/content and jurisdictional review.

Until these are evidenced, the build remains a Release Candidate rather than a public production release.
