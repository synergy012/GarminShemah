# FR970 typography prototype — 2026-11-09

The uploaded `fr970.zip` unblocked the FR970 target. The prototype now **compiles and
runs in the actual Garmin simulator**. This is still original typography test prose,
not a complete prayer app. The Venu 2 package is still needed.

## Package and runtime

- Supplied archive: 80 entries, CRC integrity checked, no absolute/traversal/symlink
  entries; `compiler.json` identifies `fr970`, Forerunner 970, 454 × 454 pixels.
- Archive SHA-256: `908fbcd010fbc2f1903d909437430928eccf6ca982611d1df2a56ff27ddbfde3`.
- Device package version: `2fd6344bcda9034f64198ee92abf3f1dc774e081`.
- Compiler: official Garmin SDK 9.3.0. Simulator title reports Forerunner 970 (6.0.2).
- Device resources are outside Git under
  `/workspace/.toolchains/garmin/runtime/state/.Garmin/ConnectIQ/Devices/fr970`.
- The package did not include shared fonts. The simulator initially exited with a
  segmentation fault while loading the target. Installing the corresponding upstream
  Roboto/Roboto Condensed English UI families into the shared Fonts directory resolved
  that failure. Sources, Apache 2.0 license and SHA-256 checks are recorded in
  `tools/ciq/fonts.json`. These are simulator-native UI fonts; the app's Hebrew remains
  shaped with its own Siddur Serif bitmap assets.

The build wrapper now creates a target-specific manifest/Jungle under ignored
`build/targets/`. It does not require the absent Venu 2 qualifier to build FR970, and
it keeps the shared two-device project declaration intact. Debug XML is promoted
alongside its matching PRG. Compiler warnings remain for gradual container typing and
the launcher's 64-to-65-pixel icon scaling; no warnings were suppressed.

## Verified behavior

Actual simulator screenshots:

- [Beginning / medium size](simulator/fr970/begin.png)
- [Touch-dragged middle](simulator/fr970/middle.png)
- [End of the continuous prototype](simulator/fr970/end.png)
- [Small text](simulator/fr970/small.png) and [large text](simulator/fr970/large.png)
- [Native settings menu](simulator/fr970/settings.png)

The screenshots show the actual simulator, device skin and application. They are not
host mockups. Each reader frame is visibly marked **NOT PRAYER**.

Checks executed using the device package's physical-button hit regions and touchscreen:

1. Down button changed the reading viewport; Up restored the identical viewport.
   Sending host keyboard arrows did not exercise these controls; that attempt was
   excluded from passing evidence.
2. A touchscreen drag moved through the same document without a page transition.
   Drag start/stop now use the documented `DragEvent.getType()` values. The tap handler
   was corrected to the SDK's `onTap`; minimum SDK is 3.3.0, matching drag API availability.
3. Forty down-button presses reached the end; forty up-button presses returned to an
   identical beginning viewport. Source section spacing remained part of one document.
4. The physical menu-button hold opened settings. Small, medium and large text were
   inspected. Large text rewrapped into fewer words per line; small text showed more
   lines with the same pointed characters and punctuation.
5. Closing and reopening retained size 0 (small) and the exact saved pixel offset 130,
   confirmed by prototype diagnostics. An earlier pre-menu-frame comparison was not
   identical and was not counted as an exact-frame resume pass; the final check used
   the actual save/restore values across closure.
6. The initial 33 ms animation request caused the SDK's minimum-interval warning.
   It was corrected to 50 ms, the supported default minimum, and button movement was
   rechecked without that warning. This is about 20 Hz, not a measured 30 FPS claim.

The sampled simulator VM indicator stayed around 25–27 KB while reading and visiting
menus. This is not a complete bitmap-resource measurement or proof of no long-term
leak. The native traversal test below exercises state/index logic, not 100 rendered
end-to-end traversals.

## Tests and limits

All **24 host tests pass**. The FR970 native runner reports **four PASS results**:
scroll bounds, continuous section boundaries, word anchoring across font sizes, and
100 document-state traversals at each of three sizes.

The SDK client returns **exit 1 despite its `PASSED (passed=4, failed=0, errors=0)`
summary**. The raw output, binary hash and unmodified exit status are retained under
`docs/simulator/fr970/`. Inspection found an embedded SDK passed-result pattern with
spacing that does not match the emitted result line, consistent with a client parsing
defect. The SDK was not patched, the exit was not changed to zero, and no assertion
was disabled. Treat the VM test reports and client exit anomaly as separate evidence.

Not yet verified: native-font Hebrew comparison, Venu 2, full approved prayer texts,
100 rendered traversal cycles, actual watch restarts/updates, session expiry after
45 minutes, or physical watch behavior. All three nuschaos remain unavailable in the
prototype until approved reader documents exist. No milestone is claimed fully
complete on the strength of this typography checkpoint.

## Reproduce

From `/workspace/GarminShemah`:

```sh
.venv/bin/python -m tools.ciq_fonts
CONNECTIQ_HOME=/workspace/.toolchains/garmin/9.3.0 \
  .venv/bin/python -m tools.build --device fr970 \
  --key /workspace/.toolchains/garmin/keys/development.der
bash tools/ciq-runtime.sh start
```

The font helper preserves existing SDK fonts. Missing files are copied from a verified
cache or downloaded through the inherited proxy/CA with fixed SHA-256 checks. On this
platform, a networked download may need the normal command escalation. Do not disable
verification to make it work.

The local development key is outside the repository and is not a release identity.
The build helper selects the installed runtime device home automatically; override
with `--sdk-user-home` if needed, preserving inherited Java options.

With the simulator ready, run inside its container:

```sh
env -u DOCKER_HOST -u DOCKER_CONTEXT -u DOCKER_TLS \
  -u DOCKER_TLS_VERIFY -u DOCKER_CERT_PATH \
  docker --host=unix:///var/run/docker.sock exec \
  -e JAVA_TOOL_OPTIONS=-Duser.home=/home/garmin garmin-ciq-simulator \
  /opt/connectiq/bin/monkeydo /workspace/GarminShemah/build/fr970.prototype.prg fr970
```

The SDK client normally stays connected while the app runs. Wait for the prototype's
`Reader restored` log before sending input; a mapped simulator window alone does not
establish that the app has loaded. `bash tools/ciq-runtime.sh screenshot` now locates
the native window by class and size, because the device title changes after loading.

For native tests, compile with `--tests` and invoke `monkeydo` on
`build/fr970.tests.prg fr970 -t`. Preserve the exit anomaly noted above. PRG checksums,
sizes and observed outcomes are in [evidence.json](simulator/fr970/evidence.json).
