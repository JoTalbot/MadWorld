# B10 Android Device Matrix

Required release evidence, with no simulated PASS:

| API | Emulator | Physical | Required checks |
|---|---|---|---|
| 26 | UNVERIFIED | UNVERIFIED | install, launch, login, API, offline/reconnect |
| 29–32 | UNVERIFIED | UNVERIFIED | same + lifecycle/rotation |
| 33–35 | UNVERIFIED | VERIFIED | same + notification/runtime permissions |

## Physical device evidence

**Device:** G1  
**Android:** 15  
**API:** 35  
**Test method:** manual physical-device validation, no ADB  
**Evidence timestamp:** 2026-09-08 (user-reported)

| Check | Result |
|---|---|
| Install | PASS |
| Launch | PASS |
| Login | PASS |
| Authoritative state after restart | PASS |
| Offline | PASS |
| Reconnect | PASS |
| Network loss recovery | PASS |
| Background/lifecycle | PASS |
| Rotation | PASS |
| Repeat launch | PASS |
| Problems | none reported |

The physical device therefore provides verified coverage for the API 33–35 physical-device row. This does not imply coverage for API 26 or API 29–32, which remain UNVERIFIED without corresponding devices.

For each device record OS/API, ABI, app version, backend URL, install result, login result, authoritative-state refresh, offline queue/reconnect, rotation/background, network-loss recovery, notification behavior and evidence timestamp. A missing device is `UNVERIFIED`, never PASS.
