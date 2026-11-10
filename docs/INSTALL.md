# Build and simulator instructions

Active target: **FR970 only**. The current app is a source-review build, not an approved prayer release. See [current evidence](REVIEW-BUILD.md).

```sh
bash tools/setup.sh
CONNECTIQ_HOME=/workspace/.toolchains/garmin/9.3.0 \
  .venv/bin/python -m tools.build --review --device fr970 --key /secure/path/developer_key.der
```

Output: `build/fr970.review.prg` with matching debug XML. The wrapper checks the SDK/key, generates resources and promotes successful compiler output. It selects the uploaded device home automatically when available; `--sdk-user-home` overrides this. Keep signing keys outside Git. The local development key is not a release signing identity.

SDK 9.3.0 and the uploaded FR970 package are installed in this workspace. Simulator libraries are provided by the existing Ubuntu 22.04 container:

```sh
bash tools/ciq-runtime.sh status
```

If stopped, use `bash tools/ciq-runtime.sh start`. This replaces only this project's labelled simulator container. It does not change environment configuration. Run the PRG inside it:

```sh
env -u DOCKER_HOST -u DOCKER_CONTEXT -u DOCKER_TLS \
  -u DOCKER_TLS_VERIFY -u DOCKER_CERT_PATH \
  docker --host=unix:///var/run/docker.sock exec \
  -e JAVA_TOOL_OPTIONS=-Duser.home=/home/garmin garmin-ciq-simulator \
  /opt/connectiq/bin/monkeydo /workspace/GarminShemah/build/fr970.review.prg fr970
```

Wait for the `Reader restored` log before interacting. `bash tools/ciq-runtime.sh screenshot` captures the actual native simulator window. Shared English UI fonts can be restored with `.venv/bin/python -m tools.ciq_fonts`; this validates pinned download hashes and preserves existing files.

Controls: left-side UP/DOWN scroll. The bottom-right BACK button saves the reading position and exits immediately from anywhere in the document. The top-right START button has no action while reading; it still selects items in menus. Screen scrolling is the default: movement is immediate, aligned to whole lines and retains one line of context. Choose Scrolling to switch to line steps. Drag scrolls continuously. Hold the physical menu button for settings; choose Beginning, Text size, Nusach, Scrolling, Instructions, Shema paragraphs 2 + 3, Close or Text sources. Instructions start hidden; the Shema passages start shown. Toggle either setting to change visibility. Conditional prayer passages and small-print prayer text are retained. Back returns from submenus to settings, then the reader. Nusach selection retains each document's position. Hebrew is shaped bitmap text; native settings use English.

Add `--tests` to the review build command, then invoke `monkeydo build/fr970.tests.prg fr970 -t` in the container. Preserve both the VM test summary and the SDK client's process status; its known exit-1 anomaly must not be hidden.

`--review` permits unapproved content with a visible review notice. Omitting it builds the historical non-prayer typography fixture. `--release` is mutually exclusive and remains blocked by editorial validation:

```sh
.venv/bin/python -m tools.content --release
```

Physical-watch sideload and acceptance have not yet been verified. A future approved, device-specific PRG can be copied using Garmin's supported `GARMIN/APPS` file-transfer process. Signing identity, update behavior and store export still require release checks. No publishing is needed to run the local simulator.
