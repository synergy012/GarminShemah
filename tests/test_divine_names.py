import copy
import json
import re
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools import divine_names as names


class DivineNameTests(unittest.TestCase):
    def display(self, text):
        document = {'id': 'ashkenaz', 'sections': [{'id': 'source-001', 'heading_he': '', 'paragraphs': [text]}]}
        with tempfile.TemporaryDirectory() as directory:
            policy = Path(directory) / 'policy.json'
            policy.write_text(json.dumps(names.make_policy([document]), ensure_ascii=False))
            with patch.object(names, 'POLICY', policy):
                return names.display_document(document)['sections'][0]['paragraphs'][0]

    def test_only_four_letter_name_changes_and_other_names_are_original(self):
        self.assertEqual(self.display('יְהֹוָה אֱלֹהֵינוּ אֲדֹנָי אֵל שַׁדַּי'), 'ה׳ אֱלֹהֵינוּ אֲדֹנָי אֵל שַׁדַּי')
        self.assertEqual(self.display('לַיהֹוָה וֵאלֹהֵי בֵאֱלֹהִים'), 'לַה׳ וֵאלֹהֵי בֵאֱלֹהִים')
        self.assertEqual(self.display('יְ֯הֹוָה אֱלֺהֵֽינוּ אֵֽל'), 'ה׳ אֱלֺהֵֽינוּ אֵֽל')
        original = 'אֱלֹהֶיךָ אֱלֹהֵיכֶם אֵל שַׁדַּי אֲדֹנָי'
        self.assertEqual(self.display(original), original)

    def test_ordinary_words_angels_and_other_gods_are_preserved(self):
        ordinary = 'אֵלֶּה הָאֵלֶּה אֱלָהוּתוּ הָיָה יִשְׂרָאֵל מִיכָאֵל אֶל וְאַל'
        self.assertEqual(self.display(ordinary), ordinary)
        self.assertEqual(self.display('אֱלֹהִים אֲחֵרִים וְאֵל'), 'אֱלֹהִים אֲחֵרִים וְאֵל')

    def test_corpus_masks_four_letter_names_and_preserves_all_other_characters(self):
        marks = r'[\u0591-\u05bd\u05bf\u05c1\u05c2\u05c4\u05c5\u05c7]*'
        four_letter = re.compile(''.join(letter + marks for letter in 'יהוה'))
        expected = {'ashkenaz': 49, 'sefard': 65, 'edot_hamizrach': 27}
        expected_he = {'ashkenaz': 49, 'sefard': 65, 'edot_hamizrach': 27}
        policy = json.loads(names.POLICY.read_text())
        for identifier in names.IDS:
            document = json.loads((names.ROOT / 'content/nuschaot' / f'{identifier}.json').read_text())
            original = copy.deepcopy(document)
            displayed = names.display_document(document)
            self.assertEqual(document, original)
            replacements = sum(len(f['replacements']) for f in policy['documents'][identifier]['fields'])
            self.assertEqual(replacements, expected[identifier])
            for field in policy['documents'][identifier]['fields']:
                self.assertTrue(all(span['kind'] == 'tetragrammaton' for span in field['replacements']))
            marker_count = 0
            other_gods = 0
            for before, after in zip(document['sections'], displayed['sections']):
                for raw, text in zip([before['heading_he'], *before['paragraphs']], [after['heading_he'], *after['paragraphs']]):
                    self.assertEqual(text, four_letter.sub('ה׳', raw))
                    self.assertEqual(len(raw.split(' ')), len(text.split(' ')))
                    self.assertFalse(names.name_spans(text)[0], (identifier, after['id']))
                    other_gods += sum(s['reason'] == 'other_gods_not_a_name_of_Hashem' for s in names.name_spans(text)[1])
                    marker_count += text.count('ה׳')
            self.assertEqual(marker_count, expected_he[identifier])
            self.assertEqual(other_gods, 1)

    def test_changed_source_requires_a_reviewed_span_policy(self):
        document = json.loads((names.ROOT / 'content/nuschaot/ashkenaz.json').read_text())
        document['sections'][0]['paragraphs'][0] += ' יְהֹוָה'
        with self.assertRaisesRegex(ValueError, 'policy needs review'):
            names.display_document(document)


if __name__ == '__main__':
    unittest.main()
