# Bedtime Shema for Garmin

An offline Connect IQ bedtime reader for **Forerunner 970**. Venu 2 was removed from the active scope at the user's request.

The **review build** contains separate Ashkenaz, Sefard and Edot HaMizrach source sequences, with three sizes, continuous scrolling, saved position and offline source notices. The reading screen has no review banner. Editorial and liturgical completeness review remains open. Release generation stays blocked until that review is recorded.

Read the Hebrew: [Ashkenaz](content/review/ashkenaz.md), [Sefard](content/review/sefard.md), [Edot HaMizrach](content/review/edot_hamizrach.md). See the [actual simulator screenshots](docs/REVIEW-BUILD.md#actual-simulator-images).

Reader settings now default to **screen scrolling** with immediate movement and a line of overlap, and **instructions hidden**. You can switch to line scrolling, show instructions, or hide Shema paragraphs 2 and 3 (shown by default). Use the left-side UP/DOWN buttons to scroll, hold UP/MENU for settings, and press bottom-right BACK to save your place and exit. Top-right START only selects menu items. [Download the review ZIP](downloads/README.md).

The full source sequences preserve 37 Ashkenaz, 27 Sefard and 30 Edot source blocks. Instructions and conditional passages are distinguished visually, with source text retained. See [review-build evidence and limitations](docs/REVIEW-BUILD.md), [source acquisition](docs/TEXT-ACQUISITION.md) and [text verification](docs/TEXT-VERIFICATION.md).

From this directory:

```sh
bash tools/setup.sh
CONNECTIQ_HOME=/workspace/.toolchains/garmin/9.3.0 \
  .venv/bin/python -m tools.build --review --device fr970 --key /secure/path/developer_key.der
```

The review artifact is `build/fr970.review.prg`. The SDK and signing key are external to Git. Setup checks the Hebrew font pipeline and runs host tests; it does not install Garmin's SDK. Generated resources and builds are ignored.

- [Current status](docs/STATUS.md)
- [Build and simulator commands](docs/INSTALL.md)
- [Rendering architecture](docs/ARCHITECTURE.md)
- [Content editing contract](content/README.md)

Hebrew uses the OFL-licensed Siddur Serif derivative, shaped off-device with HarfBuzz/FriBidi. Ashkenaz text is CC-BY-3.0; the selected Sefard/Edot editions are public domain according to their source metadata. Attribution, license links and display changes accompany the PRG in Text sources. See `content/acquired/NOTICE.md`.

No environment publishing, store submission or remote Git publication is part of this checkpoint. Earlier typography-prototype evidence remains under `docs/FR970-VALIDATION.md`.
