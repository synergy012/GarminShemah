# Milestones — 2026-11-05

| Gate | Implemented | Verified | Unresolved |
| --- | --- | --- | --- |
| 1. Text acquisition | Separate nusach documents, edition candidate index, source/license schema, exact paragraph comparison and release gate | Official Sefaria index has named editions for all three; missing texts fail release | No complete text acquired; edition licenses, order, differences, optional customs and knowledgeable review all pending |
| 2. Hebrew prototype | HarfBuzz/FriBidi line shaping, licensed font derivative, punctuation coverage, two device profiles, three sizes, continuous reader code | Host asset tests; SDK 9.3.0 compiler runs; simulator starts and responds to shell commands | No target device packages or app rendering screenshots; native rendering comparison and full resource/memory evaluation pending |
| 3. Functional app | Monkey C reader, visible-line cache, touch/button delegates, animated steps, persistent settings, resume timeout, word anchors | Host content/resource pipeline only | Monkey C has not compiled or run; full texts and every interaction/storage behavior remain unverified |
| 4. Compatibility/testing | Two declared products, independent resources, build wrapper, native test source and test procedure | 16 host tests passed | No FR970 or Venu 2 PRGs, simulator tests, long-scroll stress runs, device screenshots or store package |

**No milestone is complete.** The code is a development checkpoint, not a prayer app
ready for installation or publication. Optional models have not been added.

## Current runtime and device-package blocker

The published policy is enforced, and Garmin's SDK download host is reachable. The
official SDK **9.3.0** is installed at `/workspace/.toolchains/garmin/9.3.0`.
Its simulator requires WebKitGTK 4.0, JavaScriptCoreGTK 4.0, libsoup 2.4 and libjpeg 8,
which this Debian 13 host lacks. An isolated Ubuntu 22.04 runtime now supplies all
libraries and an Xvfb display. The actual simulator window opens, and its SDK shell
answers `help` and `uptime`. See [runtime evidence and commands](GARMIN-RUNTIME.md).

An FR970 compile attempt reached the installed compiler but stopped with
`Invalid device id specified: 'fr970'`. Neither target device package is installed.
The official SDK Manager identifies its device service as
`https://api.gcs.garmin.com/ciq-product-onboarding/…`; a request to the FR970 endpoint
was denied by the network proxy with `403 Forbidden`. Access to **api.gcs.garmin.com**
is needed to continue official device-package installation. Authentication requirements
have not been established because policy blocks the request first.

No environment draft was changed or published during runtime repair. The prior
publish instructions are no longer a pending action. Do not reapply them.

## Next actions

1. Once the device service is accessible, install the FR970 and Venu 2 packages.
   Inspect local API docs, actual memory/resource limits and application/store requirements.
   Record tool and device package versions. Compile the prototype before extending it.
2. Acquire named prayer editions, establish licenses and complete bedtime sections, and
   compare all three sequences without substituting or normalizing away differences.
3. Run the prototype in the FR970 simulator, resolve compiler/API issues, inspect pointed
   Hebrew at all sizes, and capture real scrolling screenshots. Measure heap and decoder
   behavior; change resource strategy if needed.
4. Integrate verified content, complete app/device tests on both targets, then produce
   testable PRGs and assess store publication requirements. Do not submit test prose.

## Known engineering risks

- Full-text flash/resource size and actual Venu 2 heap are unmeasured.
- Touch callbacks and button mappings require SDK/device verification; they are not
  validated by the Python tests.
- Native unit-test sources are unrun; no simulator leak, persistence or offline test has run.
- Source licensing and rabbinic/editorial completeness review may need a different edition
  or outside review even after network access is fixed.
- The current app UUID is a new project UUID. Preserve it for future updates and use a
  stable, securely retained developer key for release signing.
