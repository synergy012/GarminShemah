# Milestones — 2026-11-09

| Gate | Implemented | Verified | Unresolved |
| --- | --- | --- | --- |
| 1. Text acquisition | Verbatim bedtime source nodes for all three nuschaos, source-order comparison, attribution/license evidence and release gate | 37 Ashkenaz, 27 Sefard and 30 Edot source blocks; catalog licenses cross-checked against live metadata | Instructions, alternatives, abbreviated passages and intended defaults still need review; no approved reader text |
| 2. Hebrew prototype | Shaped bitmap reader, device profiles and three sizes | FR970 compiles/runs; actual pointed-Hebrew screenshots and continuous traversal | Native-font comparison, full-text capacity and Venu 2 rendering pending |
| 3. Functional app | Reader, settings, position storage, word anchors | FR970 prototype button/touch scrolling, all sizes and saved/restored offset 130/size 0 | Approved prayer integration, complete app/session/update validation pending |
| 4. Compatibility/testing | Target-specific build metadata and test workflow | 24 host tests pass; 4 FR970 native tests report PASS; prototype PRG produced | SDK native-test client exits 1 despite PASS summary; Venu 2, rendered stress and physical watch tests pending |

**No milestone is complete.** The code is a development checkpoint, not a prayer app
ready for installation or publication. Optional models have not been added.

## Current runtime and device-package authentication blocker

**FR970 update:** the uploaded `fr970.zip` is installed and the prototype builds and
runs. Missing shared English UI fonts caused the first target-load crash; corresponding
upstream Roboto fonts resolved it. See [FR970 validation](FR970-VALIDATION.md) for actual
screenshots, input/state checks, artifacts and the native test-client anomaly.
The authentication/package notes below now apply to **Venu 2** or future downloads.

The published policy is enforced, and Garmin's SDK download host is reachable. The
official SDK **9.3.0** is installed at `/workspace/.toolchains/garmin/9.3.0`.
Its simulator requires WebKitGTK 4.0, JavaScriptCoreGTK 4.0, libsoup 2.4 and libjpeg 8,
which this Debian 13 host lacks. An isolated Ubuntu 22.04 runtime now supplies all
libraries and an Xvfb display. The actual simulator window opens, and its SDK shell
answers `help` and `uptime`. See [runtime evidence and commands](GARMIN-RUNTIME.md).

Before the upload, an FR970 compile attempt reached the installed compiler but stopped with
`Invalid device id specified: 'fr970'`. That FR970 package is now installed; Venu 2 is not.
The official SDK Manager identifies its device service as
`https://api.gcs.garmin.com/ciq-product-onboarding/…`. The published policy now allows
**api.gcs.garmin.com**. A fresh FR970 request on November 9 reached the service and
returned **401 Unauthorized**, replacing the previous proxy-policy denial. No Garmin
credential binding or Garmin/Connect IQ environment variable is present. The official
SDK Manager's onboarding requires Garmin sign-in.

This chat has no shared-desktop control/open tool, and its managed display has not
started. The simulator's private Xvfb display is not an interactive user sign-in path.
Do not ask for passwords or copied tokens in chat. See [the authentication handoff](GARMIN-AUTH.md).

No environment draft was changed or published during runtime repair. The prior
publish instructions are no longer a pending action. Do not reapply them.

## Next actions

1. Import the Venu 2 package from the user's existing SDK Manager installation, then
   compile and exercise the same prototype on that mandatory secondary target.
   Inspect local API docs, actual memory/resource limits and application/store requirements.
   Record tool and device package versions. Compile the prototype before extending it.
2. Review the [acquired source sequences](TEXT-ACQUISITION.md), resolve instruction/custom
   boundaries and the abbreviated Edot passage, and prepare the approved reader documents.
3. Run the prototype in the FR970 simulator, resolve compiler/API issues, inspect pointed
   Hebrew at all sizes, and capture real scrolling screenshots. Measure heap and decoder
   behavior; change resource strategy if needed.
4. Integrate verified content, complete app/device tests on both targets, then produce
   testable PRGs and assess store publication requirements. Do not submit test prose.

## Known engineering risks

- Full-text flash/resource size and actual Venu 2 heap are unmeasured.
- Touch callbacks and button mappings require SDK/device verification; they are not
  validated by the Python tests.
- Four FR970 native tests report PASS, but the SDK client exits 1; rendered leak,
  physical watch, restart/update and full-prayer offline tests are still pending.
- Source licensing and rabbinic/editorial completeness review may need a different edition
  or outside review even after network access is fixed.
- The current app UUID is a new project UUID. Preserve it for future updates and use a
  stable, securely retained developer key for release signing.
