# B10 Android Device Matrix

Required release evidence, with no simulated PASS:

| API | Emulator | Physical | Required checks |
|---|---|---|---|
| 26 | UNVERIFIED | UNVERIFIED | install, launch, login, API, offline/reconnect |
| 29–32 | UNVERIFIED | UNVERIFIED | same + lifecycle/rotation |
| 33–35 | UNVERIFIED | UNVERIFIED | same + notification/runtime permissions |

For each device record OS/API, ABI, app version, backend URL, install result, login result, authoritative-state refresh, offline queue/reconnect, rotation/background, network-loss recovery, notification behavior and evidence timestamp. A missing device is `UNVERIFIED`, never PASS.
