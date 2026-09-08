# B10 External Provider Gate

## Push

**Provider: none.** Firebase Cloud Messaging (FCM) is explicitly removed from MadWorld. The Android application does not include the Firebase Messaging SDK or service, the backend does not provide FCM delivery, and release builds require no Firebase configuration or credentials.

The obsolete `device_push_tokens` registry is removed by migration `035_remove_firebase_push_tokens.sql`. No provider token registration or external push-delivery evidence is required for this release.

## Crash reporting

Current repository state does not claim Crashlytics/Sentry or equivalent. The owner waiver remains applicable. Do not add a provider merely to make the checklist green.

## Analytics

Current repository state does not claim external analytics delivery. The owner waiver remains applicable. Do not add a provider merely to make the checklist green.

## Rule

External providers are optional and must not be introduced solely to satisfy a release checklist. Firebase/FCM is not part of the current release architecture.
