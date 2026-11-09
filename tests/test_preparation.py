import hashlib
import unittest

from tools.acquire import comparison_text
from tools.content import ROOT, NUSCHAOT, read_json, validate
from tools.prepare_content import prepare, whitespace


class PreparationTests(unittest.TestCase):
    def test_every_source_block_and_character_survives_preparation(self):
        for identifier in NUSCHAOT:
            acquired = read_json(ROOT / 'content/acquired' / f'{identifier}.json')
            prepared = read_json(ROOT / 'content/nuschaot' / f'{identifier}.json')
            with self.subTest(nusach=identifier):
                self.assertEqual(len(acquired['blocks']), len(prepared['sections']))
                self.assertEqual(validate(prepared), [])
                self.assertTrue(validate(prepared, release=True))
                for block, section in zip(acquired['blocks'], prepared['sections']):
                    self.assertEqual(block['source_index'], section['source_index'])
                    self.assertEqual(hashlib.sha256(block['html'].encode()).hexdigest(), section['source_block_sha256'])
                    self.assertEqual(whitespace(comparison_text(block['html'])), whitespace(' '.join(section['paragraphs'])))
                    self.assertFalse(section['optional'])

    def test_import_is_repeatable_and_never_invents_a_human_review(self):
        for identifier in NUSCHAOT:
            actual = read_json(ROOT / 'content/nuschaot' / f'{identifier}.json')
            self.assertEqual(prepare(identifier), actual)
            self.assertFalse(actual['review']['text_verified'])
            self.assertIsNone(actual['review']['reviewer'])

    def test_small_prayer_print_is_not_mistaken_for_instructions(self):
        documents = {n: read_json(ROOT / 'content/nuschaot' / f'{n}.json') for n in NUSCHAOT}
        self.assertEqual(documents['ashkenaz']['sections'][5]['paragraph_kinds'], ['prayer'])
        self.assertEqual(documents['sefard']['sections'][23]['paragraph_kinds'], ['source_small'])
        edot = documents['edot_hamizrach']['sections']
        self.assertEqual(edot[5]['paragraph_kinds'], ['instruction', 'source_small', 'instruction', 'source_small'])
        self.assertEqual(edot[12]['paragraph_kinds'], ['prayer', 'instruction', 'prayer', 'instruction', 'prayer'])


if __name__ == '__main__':
    unittest.main()
