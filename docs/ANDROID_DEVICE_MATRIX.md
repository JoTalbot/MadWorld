# Android Device Verification Matrix

B9 establishes a repeatable device matrix rather than claiming every Android device is tested.

| Tier | Profile | Minimum checks |
|---|---|---|
| A | API 26, low-memory emulator | launch, sign-in, offline queue, reconnect |
| B | API 29-32, mid-range profile | navigation, state refresh, notifications |
| C | API 33-35, modern profile | full smoke flow, accessibility semantics |
| D | Physical Android device | install/upgrade, network loss, background/foreground |

## Gate

Every release candidate must pass the available automated emulator tier. Physical-device verification is required before public production rollout when a physical device is available.

Record device API level, build variant, test date, result and known limitations. Do not represent emulator coverage as universal hardware coverage.
