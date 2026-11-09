# Bedtime Shema for Garmin

An offline Connect IQ siddur project for **Forerunner 970** and **Venu 2**.

**Development checkpoint, not a usable prayer app.** No verified prayer text is
bundled yet. The current prototype contains original Hebrew typography test prose,
clearly marked **NOT PRAYER**. All three requested nuschaos are explicitly blocked;
none silently uses another nusach or the test prose.

Verbatim bedtime excerpts for all three nuschaos have now been acquired in
`content/acquired/`, with edition-specific permission evidence and source hashes.
See [the acquisition report](docs/TEXT-ACQUISITION.md). Instructions, alternatives
and completeness still need review before these sources enter the reader.

The dedicated checkout is `/workspace/GarminShemah`, with origin
`https://github.com/synergy012/GarminShemah`. No watch-face project is used.

Run the tested host workflow from this directory:

```sh
bash tools/setup.sh
```

This prepares a Python virtual environment, checks the licensed Hebrew font build,
generates three sizes for each device and runs the host tests. Pillow must have
libraqm, HarfBuzz and FriBidi support. The setup does not install a Garmin SDK.

The Monkey C implementation now **compiles and runs on the FR970 simulator** using
the uploaded device package. Continuous scrolling, button/touch input, three text sizes
and brief-interruption resume have been exercised with the typography fixture.
[Actual screenshots, build instructions and test limits](docs/FR970-VALIDATION.md).
The Venu 2 package and testing are still outstanding. Garmin's download API requires
authentication, but an uploaded `venu2` package can be reused without that login.

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
