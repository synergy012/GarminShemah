# Divine-name display substitutions

The app displays **ה׳** (he followed by Hebrew geresh) for Divine Names. Original acquired and reader-input JSON remains verbatim for provenance. Names, including their attached vowels/accents, are replaced only at pinned source spans; attached prefixes and all other text remain unchanged.

Ordinary prepositions/negations, angel/personal names, descriptive words and the Shema reference to other gods are not Divine Names and remain unchanged. This is a display convention, not a change to source certification.

| Nusach | Replacements | By name family |
| --- | ---: | --- |
| ashkenaz | 77 | {'adonai': 1, 'el': 5, 'elohim_forms': 21, 'shaddai': 1, 'tetragrammaton': 49} |
| sefard | 96 | {'adonai': 2, 'el': 4, 'elohim_forms': 24, 'shaddai': 1, 'tetragrammaton': 65} |
| edot_hamizrach | 50 | {'el': 4, 'elohim_forms': 18, 'shaddai': 1, 'tetragrammaton': 27} |

The policy in `content/divine-name-policy.json` records each exact source span, replacement, exception and text digest. Preparation/generation rejects changed source text until the mapping is reviewed. Saved positions migrate by word anchor after this reflow. Prefixes and replacements keep the same word count.
