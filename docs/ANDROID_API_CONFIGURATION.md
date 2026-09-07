# Android API configuration

`MADWORLD_API_URL` is supplied at build time through a Gradle property or environment variable.

## Physical Android phone / public test build

The default debug endpoint is the public production API:

```text
https://api.autosklo.org.ua
```

The public server is currently reached through the external address `129.213.177.56`; the application should use the HTTPS hostname rather than the raw IP because the production TLS certificate is issued for the hostname.

Therefore a physical phone must **not** use the Android Emulator-only address `10.0.2.2`. That address points to the emulator host and is not the public server.

For a production-like/public debug build, the endpoint can be made explicit:

```bash
cd android
./gradlew assembleDebug -PMADWORLD_API_URL=https://api.autosklo.org.ua
```

## Local emulator / LAN development

For an Android Emulator connected to a backend running on the development host, `10.0.2.2` is the special emulator alias for the host machine. It must not be used on a physical phone.

For a physical phone connected to a local development server, use the server's reachable LAN address and HTTP only for local development, for example:

```bash
cd android
./gradlew assembleDebug -PMADWORLD_API_URL=http://192.168.1.50:8000
```

Replace `192.168.1.50` with the actual development-server address. The backend must listen on the reachable interface and the host firewall must permit the development port.

Debug builds allow cleartext HTTP only when the selected debug URL starts with `http://`. Release builds keep cleartext HTTP disabled and require HTTPS.

## Production

Pass a fully qualified HTTPS API URL through Gradle property `MADWORLD_API_URL` or environment variable `MADWORLD_API_URL`. The requirement is enforced only when a release task is scheduled (`gradle.taskGraph.whenReady`), so `testDebugUnitTest` and `assembleDebug` run without an explicit property.

```bash
./gradlew assembleRelease -PMADWORLD_API_URL=https://api.autosklo.org.ua
```

Never commit production URLs containing credentials or secrets. CI should provide the production URL through repository/environment configuration when a release build is enabled.

The application reads `BuildConfig.MADWORLD_API_URL`; no runtime secret is stored in the APK.

## Gradle version pinning

`android/gradle/wrapper/gradle-wrapper.properties` is the single source of truth for the Gradle version. Android CI parses `distributionUrl` from that file instead of hard-coding a version. To bump Gradle, change `distributionUrl` only.

The wrapper binary (`gradlew`, `gradle-wrapper.jar`) is not yet committed; generate it locally with `gradle wrapper` (the task reads the pinned version from the properties file) and commit both files once available.

## Unit tests

Client-side stores (`OfflineCommandQueue`, `NotificationCenter`) take a `KeyValueStore`;
production uses `SharedPreferencesStore`, tests use `InMemoryKeyValueStore`, so the queue,
drainer, dispatcher allowlist and notification history are covered by plain JVM tests
(`./gradlew :app:testDebugUnitTest`). `org.json` is added as a test dependency because the
Android SDK stub throws "Method ... not mocked" on the JVM.

