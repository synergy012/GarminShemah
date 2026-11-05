# Prayer content contract

`nuschaot/` contains separate documents for Ashkenaz, Chassidic Sefard, and
Edot HaMizrach. They currently have **no sections**. Empty files are explicit gaps,
not transcriptions or claims of completeness. The typography fixture is independent.

Each document records schema version, stable nusach ID, Hebrew title, status,
sources, ordered sections, review, and unresolved issues. Sections have a stable ID,
Hebrew heading, an explicit `optional` boolean, `source_id` and a list of logical-order
Hebrew paragraphs. Required passages cannot be disabled. Optional passages currently
remain included; a reviewed minhag selector is future work.

Acquire a specific named edition, not a merged file with unknown version provenance.
Use `python -m tools.research` to download the indexed Torat Emet candidate editions
to ignored `build/research/` once the official export host is reachable. This is
research material, not automatically approved distributable text. Preserve the raw
download and its hash locally. Inspect the full edition metadata, its license and
the relevant source site; a public URL alone does not grant reuse rights.

Before adding an edition, establish its complete bedtime sequence. Preserve spelling,
nikud, punctuation and paragraph boundaries. Do not normalize Unicode, replace divine
names, strip cantillation, or discard editorial instructions silently. Record deliberate
source transformations and keep a source-to-paragraph mapping. Nonstandard whitespace,
HTML and directional overrides require review; the generator fails rather than guessing.

Source records for release require:

```json
{
  "id": "stable-edition-id",
  "url": "https://authoritative.example/exact-edition",
  "version_title": "Exact edition title",
  "license": "CC-BY-4.0",
  "license_verified": true,
  "license_url": "https://authoritative.example/permission",
  "retrieved_on": "YYYY-MM-DD",
  "sha256": "hash-of-original-source-bytes"
}
```

The license example is a schema example, not permission for any located siddur.
Keep attribution and license/changes notices with every incorporated edition. Share-alike
content needs the corresponding distribution notices. Licenses outside the explicitly
supported set require a reviewed policy change; do not relabel them to pass validation.

Set `status: verified`, record the actual reviewer and affirmative text/order checks,
and clear issues only after resolving them. Run `python -m tools.content` to regenerate
the report. Exact paragraph hashes identify candidates for shared content without
equating similar titles or stripping nikud. A knowledgeable nusach review remains
necessary to establish order, optionality and liturgical equivalence.
