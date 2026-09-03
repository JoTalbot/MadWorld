# Android API configuration

The release build must not embed the Android emulator host address. `MADWORLD_API_URL` is supplied at build time.

- Default/debug fallback: `http://10.0.2.2:8000` for the Android emulator only.
- Production: pass a fully qualified HTTPS API URL through Gradle property `MADWORLD_API_URL` or environment variable `MADWORLD_API_URL`.
- Example: `./gradlew assembleRelease -PMADWORLD_API_URL=https://api.example.invalid`
- Never commit production URLs containing credentials or secrets.
- CI should provide the production URL through repository/environment configuration when a release build is enabled.

The application reads `BuildConfig.MADWORLD_API_URL`; no runtime secret is stored in the APK.
