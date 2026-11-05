# Bedtime Shema for Garmin

An offline Connect IQ siddur project for **Forerunner 970** and **Venu 2**.

**Development checkpoint, not a usable prayer app.** No verified prayer text is
bundled yet. The current prototype contains original Hebrew typography test prose,
clearly marked **NOT PRAYER**. All three requested nuschaos are explicitly blocked;
none silently uses another nusach or the test prose.

The dedicated checkout is `/workspace/GarminShemah`, with origin
`https://github.com/synergy012/GarminShemah`. No watch-face project is used.

Run the tested host workflow from this directory:

```sh
bash tools/setup.sh
```

This prepares a Python virtual environment, checks the licensed Hebrew font build,
generates three sizes for each device and runs the host tests. Pillow must have
libraqm, HarfBuzz and FriBidi support. The setup does not install a Garmin SDK.

The Monkey C implementation includes a continuous pixel-offset reader, visible-line
bitmap caching, touch and button delegates, settings, and position storage. It is
**not compiled or simulator-tested** on either target. The official SDK 9.3.0 compiler
now runs, and the simulator launches in a compatible Ubuntu container and answers
shell commands. The device packages are still missing; their official API is blocked
by runtime policy. See [the runtime procedure](docs/GARMIN-RUNTIME.md).

- [Milestones and remaining work](docs/STATUS.md)
- [Text sources, licensing and verification](docs/TEXT-VERIFICATION.md)
- [Build, install and simulator instructions](docs/INSTALL.md)
- [Rendering and content architecture](docs/ARCHITECTURE.md)
- [Validation evidence](docs/VALIDATION.md)
- [Content editing contract](content/README.md)

`generated/proofs/` contains **host raster proofs**, not Garmin simulator screenshots.
Representative proofs are retained in [docs/proofs](docs/proofs).

The release generator intentionally fails until all three complete nuschaos and
their permissions have been verified:

```sh
.venv/bin/python -m tools.content --release
.venv/bin/python -m tools.generate --release
```

The fonts and derivative are distributed under [SIL OFL 1.1](fonts/OFL.txt).
The original non-prayer test prose is dedicated to CC0. Future prayer text licenses
must be recorded separately. No store submission or remote Git publication has
been performed.
