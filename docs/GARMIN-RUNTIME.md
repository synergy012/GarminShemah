# Verified Garmin runtime

The missing simulator libraries are resolved using an isolated **Ubuntu 22.04** Docker
runtime. The host is Debian 13. No Debian libraries were replaced, no TLS or package
signature verification was disabled, and no environment draft was edited or published.

## Current-instance evidence

- Official Connect IQ SDK **9.3.0**, downloaded from Garmin's HTTPS SDK index/archive.
- SDK location: `/workspace/.toolchains/garmin/9.3.0`.
- All `ldd` dependencies resolve inside the runtime, including WebKitGTK 4.0,
  JavaScriptCoreGTK 4.0, libsoup 2.4 and libjpeg 8.
- Compiler prints `Connect IQ Compiler version: 9.3.0` on the host and in the container.
- Xvfb opens a mapped **CIQ Simulator** window, 446 × 700 pixels.
- The official SDK shell connects to the simulator and answers `help` and `uptime`.
  The observed uptime after a fresh restart was `Up 0:00:04.293`.
- The saved build/start helper has been exercised; a fresh container also passed the
  GUI and shell checks. No app or target-specific firmware was loaded.

[Actual simulator startup screenshot](simulator/runtime-startup.png).
This is the simulator's empty startup window, not the application or a Hebrew proof.
The device identifier reported by the shell is generic; it does not establish FR970
or Venu 2 emulation.

The tested image ID is
`sha256:9f656be26ecb8320f5859965730a7a800f3c3dd70a73c2023cdfe16548006cc6`.
The Ubuntu base resolved to
`ubuntu:22.04@sha256:076e7bf82319619f28dd0aa9c02ab34b055ad37100395b4f49a2ffba04fb5e11`.
Repository package updates can produce a different image on a future rebuild.

## Reuse

From `/workspace/GarminShemah`, with access to the managed local Docker socket:

```sh
bash tools/ciq-runtime.sh build
bash tools/ciq-runtime.sh start
bash tools/ciq-runtime.sh status
bash tools/ciq-runtime.sh shell uptime
bash tools/ciq-runtime.sh screenshot
```

`build` mounts the current system CA bundle as a temporary, publicly readable BuildKit
secret for apt's sandbox user. It uses HTTPS and signed Ubuntu packages. That
session-specific CA is not copied into an image layer. `start` creates a non-root
container with its own virtual display. The SDK and project are mounted read-only;
simulator preferences/logs are retained in a separate writable state directory.
No network port is published.

Defaults:

| Setting | Default |
| --- | --- |
| `CONNECTIQ_HOME` | `/workspace/.toolchains/garmin/9.3.0` |
| `CIQ_RUNTIME_STATE` | `/workspace/.toolchains/garmin/runtime/state` |
| Container | `garmin-ciq-simulator` |
| Image | `garmin-ciq-runtime:ubuntu22.04` |

`start` recreates only containers carrying this helper's ownership label, preserving
state files and refreshing the inherited proxy configuration. It refuses to replace
an unrelated container with the same name. `bash tools/ciq-runtime.sh stop` stops the
owned simulator container. Live processes/images are not assumed to survive a future
environment restoration; rebuild/start as needed. Fresh-task restoration is untested.

The screenshot command writes the actual X11 window to
`$CIQ_RUNTIME_STATE/logs/simulator-startup.xwd`. It was converted without visual edits
to the linked PNG using ImageMagick on the host.

## Remaining device-package blocker — November 9 update

Compiling FR970 with the installed compiler and a local development-only DER signing
key fails with `Invalid device id specified: 'fr970'` because the target package is
absent. No source compilation or signing succeeded. Venu 2's package is also absent.
The key was generated outside the repository with restrictive permissions and is not
a release signing identity.

The official SDK Manager binary identifies the device endpoint as:

```text
https://api.gcs.garmin.com/ciq-product-onboarding/devices/fr970/ciqInfo
```

The current enforced policy now allows that destination. A fresh request reached the
Garmin service and returned **401 Unauthorized**. The SDK Manager's own onboarding text
requires a Garmin sign-in. No Garmin secret binding or relevant environment variable is
present. This is an authentication prerequisite, not another unresolved domain rule.
See [the handoff instructions](GARMIN-AUTH.md). Do not use fabricated device definitions
or bypass authentication to claim a successful build.

All three named bedtime source nodes have since been acquired, with edition-specific
permission evidence. Their reader preparation/review, actual Hebrew rendering,
application interactions, memory testing and both target builds remain unfinished.
