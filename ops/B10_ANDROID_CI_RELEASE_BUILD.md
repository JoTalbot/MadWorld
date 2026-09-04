# B10 Android CI Release Build Gate

Date: 2026-09-04

## Purpose

B10 requires the repository CI to verify a production-configured Android release build, not only a debug APK.

## CI contract

- Java 17.
- Gradle 8.10.
- Android unit tests run before packaging.
- Debug APK remains covered.
- Release APK is assembled with `MADWORLD_API_URL=https://api.autosklo.org.ua`.
- Release APK SHA-256 is generated and uploaded as CI evidence.
- Release builds must keep Android cleartext HTTP disabled.

## Runtime boundary

CI build success does not certify execution on Android API 26, API 29-32, API 33-35, or a physical device. Those remain runtime evidence gates.

## Production safety

The release build must use the production HTTPS API URL. The emulator-only `10.0.2.2` fallback is not production evidence and must not be used as a physical-device endpoint.
