# B10 External Provider Gate

## Push

**Provider: Firebase Cloud Messaging (FCM).** The repository now contains the FCM HTTP v1 sender, authenticated Android token registration, token refresh handling, invalid-token detection and bounded transient retries. `device_push_tokens` remains the authoritative token registry. Credentials stay outside Git via `GOOGLE_APPLICATION_CREDENTIALS`; the project is selected with `MADWORLD_FCM_PROJECT_ID`.

Implementation is **NOT VERIFIED for production delivery** until a configured Firebase project is exercised from a physical Android device. Required evidence: token registration, server-side send success, foreground receipt, background receipt, offline-device delivery after reconnect, and invalid/unregistered token disablement. Provider credentials and the Firebase console remain environment evidence and must never be committed.

Android release builds require `MADWORLD_FIREBASE_API_KEY`, `MADWORLD_FIREBASE_APP_ID`, `MADWORLD_FIREBASE_PROJECT_ID`, `MADWORLD_FIREBASE_SENDER_ID` in the build environment. These are configuration values, not proof of delivery.

## Crash reporting

Current repository state does not claim Crashlytics/Sentry or equivalent. The owner waiver remains applicable. Do not add a provider merely to make the checklist green.

## Analytics

Current repository state does not claim external analytics delivery. The owner waiver remains applicable. Do not add a provider merely to make the checklist green.

## Rule

Provider availability, credentials and external dashboards are environment evidence. Never mark these gates VERIFIED merely because a schema, dependency or placeholder exists.
