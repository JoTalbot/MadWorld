# Android API configuration

`MADWORLD_API_URL` is supplied at build time through a Gradle property or environment variable.

## Emulator

- Default debug fallback: `http://10.0.2.2:8000`.
- `10.0.2.2` is the Android Emulator alias for the host machine. It does **not** point to your PC from a physical phone.

## Physical Android phone for local development

The phone and the development server must be on the same reachable network.

1. Find the development server's LAN address, for example `192.168.1.50`.
2. Make sure the backend listens on `0.0.0.0:8000` and that the host firewall permits TCP/8000 from the local network.
3. Build the debug APK with the LAN address:

```bash
cd android
./gradlew assembleDebug -PMADWORLD_API_URL=http://192.168.1.50:8000
```

Replace `192.168.1.50` with the actual server address. Do not use `10.0.2.2` on a physical phone.

Debug builds allow cleartext HTTP specifically for local development. Release builds keep cleartext HTTP disabled, so production must use HTTPS.

## Production

Pass a fully qualified HTTPS API URL through Gradle property `MADWORLD_API_URL` or environment variable `MADWORLD_API_URL`.

```bash
./gradlew assembleRelease -PMADWORLD_API_URL=https://api.example.invalid
```

Never commit production URLs containing credentials or secrets. CI should provide the production URL through repository/environment configuration when a release build is enabled.

The application reads `BuildConfig.MADWORLD_API_URL`; no runtime secret is stored in the APK.

## Gradle version pinning

`android/gradle/wrapper/gradle-wrapper.properties` is the single source of truth for the Gradle version. Android CI parses `distributionUrl` from that file instead of hard-coding a version. To bump Gradle, change `distributionUrl` only.

The wrapper binary (`gradlew`, `gradle-wrapper.jar`) is not yet committed; generate it locally with `gradle wrapper` (the task reads the pinned version from the properties file) and commit both files once available.

