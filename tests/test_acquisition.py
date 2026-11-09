import copy
import hashlib
import json
import unittest

from tools.acquire import SPECS, acquisition_report, comparison_text, extract
from tools.content import ROOT, read_json, validate
from tools.render import FONT
from fontTools.ttLib import TTFont


class AcquisitionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.documents = {identifier: read_json(ROOT / 'content/acquired' / f'{identifier}.json') for identifier in SPECS}

    def test_all_source_blocks_are_preserved_and_hashes_match(self):
        for identifier, expected in [('ashkenaz', 37), ('sefard', 27), ('edot_hamizrach', 30)]:
            document = self.documents[identifier]
            with self.subTest(nusach=identifier):
                self.assertEqual(len(document['blocks']), expected)
                self.assertEqual([b['source_index'] for b in document['blocks']], list(range(1, expected + 1)))
                for block in document['blocks']:
                    self.assertEqual(hashlib.sha256(block['html'].encode()).hexdigest(), block['sha256'])
                    self.assertTrue(comparison_text(block['html']))

    def test_acquisition_does_not_unlock_release(self):
        for identifier, document in self.documents.items():
            with self.subTest(nusach=identifier):
                self.assertEqual(document['status'], 'acquired_not_editorially_verified')
                self.assertFalse(document['review']['text_verified'])
                self.assertTrue(validate(document, release=True))
                approved = read_json(ROOT / 'content/nuschaot' / f'{identifier}.json')
                self.assertTrue(validate(approved, release=True))

    def test_recorded_permissions_match_live_version_evidence(self):
        evidence = read_json(ROOT / 'content/acquired/license-evidence.json')
        records = {r['id']: r for r in evidence['versions']}
        self.assertEqual(evidence['license_mapping']['mapping']['CC-BY'], SPECS['ashkenaz']['license_url'])
        for identifier, document in self.documents.items():
            with self.subTest(nusach=identifier):
                self.assertEqual(document['source']['license_claim'], records[identifier]['license_claim'])
                self.assertEqual(document['source']['version_title'], records[identifier]['version_title'])
                self.assertEqual(document['source']['license'], SPECS[identifier]['license'])

    def test_comparison_preserves_nikud_punctuation_and_internal_spacing(self):
        source = '<b>שָׁלוֹם</b>  <small>עֲלֵיכֶם</small><br>מְנוּחָה: '
        self.assertEqual(comparison_text(source), 'שָׁלוֹם  עֲלֵיכֶם\nמְנוּחָה:')
        self.assertNotEqual(comparison_text(source), comparison_text(source.replace('ָ', '', 1)))

    def test_unexpected_markup_is_not_silently_dropped(self):
        with self.assertRaisesRegex(ValueError, 'Unexpected markup'):
            comparison_text('<script>text</script>')

    def test_extraction_rejects_changed_permissions_and_empty_sections(self):
        spec = SPECS['sefard']
        source = {'title': spec['title'], 'versionTitle': spec['version'], 'license': 'Public Domain',
                  'text': {'Bedtime Shema': ['<b>שָׁלוֹם</b>  עֲלֵיכֶם: ']}}
        raw = json.dumps(source, ensure_ascii=False).encode()
        imported = extract(source, spec, 'https://source.example/edition', raw, '2026-11-09')
        self.assertEqual(imported['blocks'][0]['html'], source['text']['Bedtime Shema'][0])
        changed = copy.deepcopy(source)
        changed['license'] = 'unknown'
        with self.assertRaisesRegex(ValueError, 'permission'):
            extract(changed, spec, 'https://source.example/edition', raw, '2026-11-09')
        changed = copy.deepcopy(source)
        changed['text']['Bedtime Shema'] = []
        with self.assertRaisesRegex(ValueError, 'nonempty'):
            extract(changed, spec, 'https://source.example/edition', raw, '2026-11-09')

    def test_acquisition_report_matches_current_sources(self):
        self.assertEqual((ROOT / 'docs/TEXT-ACQUISITION.md').read_text(), acquisition_report(self.documents))

    def test_font_covers_source_letters_marks_and_punctuation(self):
        with TTFont(FONT) as font:
            supported = font.getBestCmap()
        for identifier, document in self.documents.items():
            with self.subTest(nusach=identifier):
                text = ''.join(comparison_text(block['html']) for block in document['blocks'])
                missing = {f'U+{ord(c):04X}' for c in text if not c.isspace() and ord(c) not in supported}
                self.assertEqual(missing, set())


if __name__ == '__main__':
    unittest.main()
