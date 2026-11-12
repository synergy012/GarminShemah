# Divine-name display substitutions

Only the four-letter Name displays as **ה׳**. Every other Name remains exactly as it appears in the source, including its spelling, vowels, prefixes and endings. No kuf substitutions or added dashes are applied. Original acquired and reader-input JSON remains verbatim for provenance. Substitutions apply only at pinned four-letter Name spans. Attached prefixes remain unchanged; the four-letter Name itself becomes unpointed ה׳. All other source text is unchanged.

Ordinary prepositions/negations, angel/personal names, descriptive words and the Shema reference to other gods are not Divine Names and remain unchanged. This is a display convention, not a change to source certification.

| Nusach | Replacements | By name family |
| --- | ---: | --- |
| ashkenaz | 49 | {'tetragrammaton': 49} |
| sefard | 65 | {'tetragrammaton': 65} |
| edot_hamizrach | 27 | {'tetragrammaton': 27} |

The policy in `content/divine-name-policy.json` records each exact source span, replacement, exception and text digest. Preparation/generation rejects changed source text until the mapping is reviewed. Saved positions migrate by word anchor after this reflow. Prefixes and replacements keep the same word count.
