# Prayer source notices

These JSON files preserve the selected Hebrew bedtime source blocks **verbatim**,
including HTML and commentary, from Sefaria's named editions. They are research/input
documents, not an approved siddur or silently imported application content.

## Ashkenaz

**Siddur Ashkenaz — The Metsudah siddur, 1981**, Hebrew edition via Sefaria.

- Source: <https://www.sefaria.org/Siddur_Ashkenaz%2C_Weekday%2C_Maariv%2C_Keri'at_Shema_al_Hamita>
- Edition/version source supplied by Sefaria: <https://www.nli.org.il/he/books/NNL_ALEPH002211687>
- License: **Creative Commons Attribution 3.0 Unported (CC BY 3.0)**,
  <https://creativecommons.org/licenses/by/3.0/>.
- Attribution: retain the work and version names, the source and license links, and
  this notice with distributions containing these excerpts. Do not imply endorsement.
- Changes: an excerpt of the named bedtime node was extracted into indexed JSON;
  its Hebrew/HTML string values and source block order were not changed.

The license label `CC-BY` appears in both the export and Sefaria's live version metadata.
Sefaria's own license map resolves that label to CC BY 3.0. Evidence hashes and links
are recorded in `license-evidence.json`; no license was inferred from the edition title.

## Chassidic Sefard and Edot HaMizrach

**Siddur Sefard — Torat Emet 357** and
**Siddur Edot HaMizrach — Torat Emet 357**, Hebrew editions via Sefaria.

- Sefard: <https://www.sefaria.org/Siddur_Sefard%2C_Bedtime_Shema>
- Edot HaMizrach: <https://www.sefaria.org/Siddur_Edot_HaMizrach%2C_Bedtime_Shema>
- Original version source supplied by Sefaria:
  <http://www.toratemetfreeware.com/index.html?downloads>.
- Both specified editions are labeled **Public Domain** by the export and live version
  metadata. This statement does not extend to other editions, translations or merged files.
- Changes: the named bedtime nodes were extracted into indexed JSON; their Hebrew/HTML
  string values and source block order were not changed.

## Verification boundary

Whole-download and per-block SHA-256 hashes are recorded. The comparison report removes
formatting only in a derived comparison view; it does not alter the source records.
The whole siddur downloads remain in ignored `build/research/`; only the bedtime
excerpts and provenance are included here. Unknown-license and empty Ashkenaz candidates
were excluded. Source/custom review and safe separation of instructions from liturgy
are unresolved, so release remains blocked.
