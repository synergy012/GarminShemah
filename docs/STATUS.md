# Milestones — 2026-11-05

| Gate | Implemented | Verified | Unresolved |
| --- | --- | --- | --- |
| 1. Text acquisition | Separate nusach documents, edition candidate index, source/license schema, exact paragraph comparison and release gate | Official Sefaria index has named editions for all three; missing texts fail release | No complete text acquired; edition licenses, order, differences, optional customs and knowledgeable review all pending |
| 2. Hebrew prototype | HarfBuzz/FriBidi line shaping, licensed font derivative, punctuation coverage, two device profiles, three sizes, continuous reader code | Host asset tests and raster inspection | No SDK, simulator, device packages or actual Garmin screenshots; native rendering comparison and full resource/memory evaluation pending |
| 3. Functional app | Monkey C reader, visible-line cache, touch/button delegates, animated steps, persistent settings, resume timeout, word anchors | Host content/resource pipeline only | Monkey C has not compiled or run; full texts and every interaction/storage behavior remain unverified |
| 4. Compatibility/testing | Two declared products, independent resources, build wrapper, native test source and test procedure | 16 host tests passed | No FR970 or Venu 2 PRGs, simulator tests, long-scroll stress runs, device screenshots or store package |

**No milestone is complete.** The code is a development checkpoint, not a prayer app
ready for installation or publication. Optional models have not been added.

## Concrete environment blocker

`monkeyc` and the Garmin simulator are absent. HTTPS requests to
`developer.garmin.com`, `www.sefaria.org` and `opensiddur.org` returned proxy
`403 Forbidden`. GitHub read access succeeds through the platform proxy when the
command sandbox permits networking. No additional GitHub token is required by those
successful read operations. The configured source repository was empty at the start;
there is no existing watch-face source here.

The environment draft now requests access to:

- `developer.garmin.com`, `download.garmin.com`
- `sefaria.org`, `www.sefaria.org`, `opensiddur.org`
- `storage.googleapis.com` (official Sefaria export bucket)
- `api.github.com` (repository/source metadata)

Existing package-manager presets are preserved. Saving the draft does not apply its
network rules. Review/save the changes in environment settings and publish the environment
as requested by that UI. Recheck runtime readiness and the affected URLs afterwards.
Any additional official download redirect must be diagnosed and added through settings;
do not bypass the proxy or turn off TLS verification.

## Next actions once access is active

1. Obtain the official Connect IQ SDK and install the FR970 and Venu 2 device packages.
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
