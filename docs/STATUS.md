# Current status — 2026-11-10

**FR970 review app with progress arc, single-row screen overlap and persistent settings menus integrated; human text review and physical-watch acceptance remain open.** Venu 2 is excluded at the user's request. There is no pending environment publish action.

| Area | Current result | Remaining work |
| --- | --- | --- |
| Sources | All 94 acquired blocks mapped into three separate review documents; pinned hashes, attribution and license evidence retained | Review completeness, instructions, alternatives and custom defaults; resolve the abbreviated Edot passage |
| Rendering | All nine nusach/size variants compile together; two-line bitmap atlases fit the SDK resource ceiling | Knowledgeable Hebrew-reader assessment and physical-watch legibility |
| Reader | Continuous scrolling, word anchors, per-document saved position, size/nusach settings and offline source notices | Physical watch, restart/update and prolonged rendered stress checks |
| Validation | 29 host tests pass; nine native tests report PASS; see current native and simulator evidence in REVIEW-BUILD.md | SDK native-client exit anomaly remains visible; release approval remains blocked |

See [progress and settings update](PROGRESS-SETTINGS.md) for the latest behavior and simulator evidence.

See [reader controls update](READER-OPTIONS.md) for current behavior and evidence.

See [review build](REVIEW-BUILD.md) for artifacts, commands, evidence and precise test limits. Historical prototype and runtime repair reports remain available in [FR970-VALIDATION.md](FR970-VALIDATION.md) and [GARMIN-RUNTIME.md](GARMIN-RUNTIME.md).

The next product step is a knowledgeable review of the three source sequences, especially source instructions, both weekday/Shabbat alternatives and the truncated Edot Yoshev Beseter. Do not silently fill passages from another nusach. Once decisions are recorded, regenerate the documents and repeat affected checks. Physical FR970 testing follows; no store submission has been made.
