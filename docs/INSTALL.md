# Development, build and installation

This checkpoint has no testable Garmin binary yet. The commands below distinguish the
tested host workflow from the blocked SDK workflow.

## Tested host workflow

From `/workspace/GarminShemah`:

```sh
bash tools/setup.sh
```

The current cloud runtime supplies Python 3.12, Pillow 13.0.0 with libraqm/HarfBuzz/FriBidi,
and fonttools 4.61.1. The local virtual environment reuses installed packages and pins
their versions. On a different machine, install the pinned packages and confirm that
Pillow has libraqm; setup fails rather than using incorrect RTL fallback. Fonts are
vendored under OFL. No phone or internet is used by the generated reader resources.

Generated data lives under ignored `generated/`; build outputs, research downloads and
test logs live under ignored `build/`. Source edits belong in `source/`, `content/`,
`config/` or `tools/`, not the generated resources.

## Official SDK workflow — not executed here

After network access is applied, use Garmin's official SDK/SDK Manager from
<https://developer.garmin.com/connect-iq/sdk/>. Follow its Linux prerequisites and
install the **fr970** and **venu2** device packages. Keep artifact/TLS verification
enabled. Inspect the installed tool help, device metadata, API reference and store
requirements before executing the commands below. Set `CONNECTIQ_HOME` to the SDK
directory containing `bin/monkeyc`; add its `bin` to `PATH` if desired.

Garmin builds need a local developer signing key. Reuse a securely stored existing key
when one is available. For an initial development-only key, Garmin commonly uses an
RSA private key encoded as unencrypted PKCS#8 DER. Verify that format against the
installed SDK's instructions. Generate it outside this repository with restrictive
permissions, retain it securely and never commit or paste it. A proxy-backed API secret
cannot substitute for a local signing-key file.

Compile the prototype separately for each device:

```sh
.venv/bin/python -m tools.build --device fr970 --key /secure/path/developer_key.der
.venv/bin/python -m tools.build --device venu2 --key /secure/path/developer_key.der
```

`tools.build` checks for the SDK and key, generates the device resources, invokes
`monkeyc`, and only promotes a fresh successful output to `build/<device>.prototype.prg`.
These commands have **not** been verified against an installed Garmin SDK. Resolve
API/type/resource compiler errors before treating the prototype as runnable.

Start the SDK simulator with its documented `connectiq` command, then use its
`monkeydo` command to run the appropriate PRG. Common SDK invocation:

```sh
monkeydo build/fr970.prototype.prg fr970
monkeydo build/venu2.prototype.prg venu2
```

Compile native tests using `--tests`; the typical SDK test invocation is
`monkeydo build/fr970.tests.prg fr970 /t`. Confirm flags with the installed SDK help.
Capture screenshots with the actual simulator's screenshot feature; save them under
`docs/simulator/` only after recording device and SDK versions. Do not move host proofs
there or represent them as simulator output.

## Intended input behavior — awaiting simulator validation

- Upward swipe: move forward; downward swipe: move back.
- Drag: move text with the finger.
- Next/previous behavior buttons: move forward/back by a small amount.
- Select button: move forward. Back button: move back, or leave from the beginning.
- Menu/long menu gesture: settings, text size, nusach, beginning and close reader.

Verify these mappings on both products; do not assume Venu 2 has FR970's physical keys.
Nuschaos lacking verified assets are visibly unavailable. Settings use English native
text; the Hebrew document uses shaped bitmap resources.

## Release and physical installation — gated

Only after text verification and simulator/device testing:

```sh
.venv/bin/python -m tools.content --release
.venv/bin/python -m tools.build --release --device fr970 --key /secure/path/developer_key.der
.venv/bin/python -m tools.build --release --device venu2 --key /secure/path/developer_key.der
```

These commands intentionally fail on the present unverified content. After a genuine
successful build, follow Garmin's documented sideload process, normally copying the
device-specific PRG into the watch's `GARMIN/APPS` directory via its supported file
transfer mechanism. The two builds are not interchangeable. Keep prototype files off
a device used for prayer. Store export, metadata, screenshots, licensing notices,
device acceptance, developer agreements and submission still need review; no store
package or submission has been produced.
