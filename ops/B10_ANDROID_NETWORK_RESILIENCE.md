# B10 Android Network Resilience Verification

## Repository-side gate
The Android client must treat the backend as an external dependency and recover safely from temporary network loss.

Required automated/test-plan scenarios:

- initial API failure does not permanently brick the session;
- retry path is available and idempotent;
- reconnect refreshes authoritative server state;
- stale/local state is not presented as authoritative after reconnect;
- background/foreground lifecycle does not lose the session unexpectedly;
- release builds use HTTPS and never depend on emulator-only `10.0.2.2` routing;
- debug cleartext remains local-development-only;
- physical devices use a reachable LAN/production API URL.

## Evidence rule
CI can validate configuration and unit-level behavior, but it cannot claim physical-device PASS without a real device run. Missing physical evidence remains `UNVERIFIED`.

## Release interpretation
Repository-side network-resilience preparation: **PASS**.
Physical Android network-loss verification: **UNVERIFIED** until executed on target devices.
