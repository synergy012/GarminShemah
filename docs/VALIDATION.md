# Validation evidence — 2026-11-05

## Executed in this cloud instance

`bash tools/setup.sh` completed, including all **16 host tests** in
`tests/test_pipeline.py`. No tests were skipped or expected to fail. The workflow
was exercised repeatedly to check repeatability. It generated three font sizes and
three host proof frames per size for both device profiles.

The tests cover exact logical-order text reconstruction after wrapping, paragraph
and section order, nikud-sensitive hashes, explicit source/optional-section metadata,
glyph coverage, unbreakable-word failure, diacritic margins, round-screen bounds,
complete bitmap/resource references, deterministic regeneration, bounded visible-pixel
estimates, and preservation of an existing prototype when a release check fails.

Direct negative checks also behaved as required:

| Command | Exit | Meaning |
| --- | --- | --- |
| `python -m tools.content --release` | 1 | All three incomplete/unverified nuschaos rejected |
| `python -m tools.generate --release` | 1 | No distributable prayer resources generated |
| `python -m tools.build --device fr970 --key <absent-test-key>` | 2 | Missing official SDK reported before any compilation or key use |

The last check establishes the missing compiler prerequisite, not key validation or a
successful build. Full logs and current gate results are in ignored `build/` when
captured. Test output is also returned by the setup command.

Host raster inspection caught punctuation boxes in Noto Serif Hebrew; the renamed font
derivative supplies the missing glyphs. Updated proofs were inspected for pointed Hebrew
and punctuation. This is not a definitive human liturgical/typographic review.

## Representative host proofs

The following are **host-generated raster layouts, not simulator screenshots**. Each
shows original non-prayer test prose and carries a visible host-proof label. Frames
sample the same continuous document at the beginning, middle, and end. They establish
asset layout, not working watch interaction or frame rate.

- FR970: [beginning](proofs/fr970_prototype_1_0.png), [middle](proofs/fr970_prototype_1_1.png), [end](proofs/fr970_prototype_1_2.png)
- Venu 2: [beginning](proofs/venu2_prototype_1_0.png), [middle](proofs/venu2_prototype_1_1.png), [end](proofs/venu2_prototype_1_2.png)

## Not executed

Monkey C compilation, native unit tests, actual simulator rendering, native Hebrew
comparison, touch/button input, all-three-nusach loading, persisted settings/resume,
watch restart/update behavior, full-document offline reading, performance/leak stress,
and physical-device testing are **unrun**. There are no device builds or Garmin
simulator screenshots. Full text and source licenses remain unverified.

## Required device protocol

For each device and each size, with recorded SDK/device package versions:

1. Compile and execute native tests; confirm the runner reports actual passing tests.
2. Inspect Hebrew letter order, shin/sin dots, dagesh, vowels, mixed punctuation and
   paragraph wrapping. Compare the native-font experiment with pre-rendered resources.
3. Swipe and drag forward/backward across every section boundary. Check small button
   steps, held/repeated keys, drag/swipe event duplication, reading edges and exit behavior.
4. Traverse the full verified sequence for each nusach. Reconstruct the observed section
   order against the report. No phone/network connection may be required.
5. Change sizes mid-paragraph and confirm the same word remains near the top. Confirm
   preferences and position after close/reopen and simulated restart. Reopen within
   45 minutes to resume; reopen after expiry to start at the beginning. Test clock rollback.
6. Repeat full-document scrolling at least 100 times, recording heap before/after and
   peak usage. Check that bitmap cache size tracks the visible window and that resource
   count/flash fit both products. A monotonic leak, allocation failure or crash blocks release.
7. Capture actual start/middle/end screenshots and note any manual failures. Check on
   physical AMOLED displays before choosing final typography and store screenshots.
