import copy
import hashlib
import tempfile
import subprocess
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image, features

from tools.content import ROOT, NUSCHAOT, fingerprint, read_json, report, validate
from tools.generate import generate
from tools.render import FONT, font, layout, wrap


class ContentTests(unittest.TestCase):
    def setUp(self):
        self.document = read_json(ROOT / 'content/fixtures/typography.json')

    def test_fixture_is_valid_but_never_a_release_nusach(self):
        self.assertEqual(validate(self.document), [])
        self.assertIn('Not a verified nusach', validate(self.document, release=True))

    def test_each_missing_nusach_is_an_explicit_release_failure(self):
        for name in NUSCHAOT:
            with self.subTest(nusach=name):
                document = read_json(ROOT / 'content/nuschaot' / f'{name}.json')
                self.assertEqual(document['id'], name)
                self.assertEqual(document['sections'], [])
                self.assertTrue(validate(document, release=True))

    def test_same_title_does_not_hide_nikud_difference(self):
        section = self.document['sections'][0]
        changed = copy.deepcopy(section)
        changed['paragraphs'][0] = changed['paragraphs'][0].replace('ֶ', '', 1)
        self.assertNotEqual(fingerprint(section), fingerprint(changed))

    def test_paragraph_boundaries_affect_comparison(self):
        section = self.document['sections'][0]
        changed = copy.deepcopy(section)
        changed['paragraphs'] = [' '.join(changed['paragraphs'])]
        self.assertNotEqual(fingerprint(section), fingerprint(changed))

    def test_duplicate_section_and_missing_attribution_fail(self):
        document = copy.deepcopy(self.document)
        document['sections'].append(copy.deepcopy(document['sections'][0]))
        document['sections'][0]['source_id'] = 'missing'
        errors = validate(document)
        self.assertTrue(any('duplicate' in e for e in errors))
        self.assertTrue(any('attribution' in e for e in errors))

    def test_markup_and_direction_override_require_review(self):
        for suffix in ('<b>text</b>', '\u202e'):
            with self.subTest(suffix=suffix):
                document = copy.deepcopy(self.document)
                document['sections'][0]['paragraphs'][0] += suffix
                self.assertTrue(any('editorial review' in e for e in validate(document)))

    def test_report_does_not_claim_acquisition_or_identical_nuschaot(self):
        text = report()
        for name in NUSCHAOT:
            self.assertIn(f'## {name}', text)
        self.assertIn('No comparison is possible yet', text)


class RenderingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = read_json(ROOT / 'content/fixtures/typography.json')
        cls.profiles = read_json(ROOT / 'config/devices.json')

    def test_shaping_engine_available(self):
        self.assertTrue(features.check_feature('raqm'))
        self.assertTrue(features.version_feature('harfbuzz'))
        self.assertTrue(features.version_feature('fribidi'))

    def test_vendored_font_rebuild_is_reproducible(self):
        result = subprocess.run([sys.executable, '-m', 'tools.prepare_font', '--check'],
                                cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_all_variants_retain_exact_words_nikud_and_paragraph_order(self):
        for device, profile in self.profiles.items():
            for size in range(3):
                with self.subTest(device=device, size=size):
                    lines, total = layout(self.document, profile, size)
                    self.assertGreater(total, profile['viewport_height'])
                    expected_order = []
                    for section in self.document['sections']:
                        for p, text in enumerate(section['paragraphs']):
                            pieces = [l for l in lines if l.section == section['id'] and l.paragraph == p]
                            self.assertEqual(' '.join(l.text for l in pieces), text)
                            self.assertEqual(pieces[0].word_start, 0)
                            self.assertEqual(pieces[-1].word_end, len(text.split(' ')))
                            expected_order += [(section['id'], p)]
                    actual_order = list(dict.fromkeys((l.section, l.paragraph) for l in lines if l.paragraph >= 0))
                    self.assertEqual(actual_order, expected_order)

    def test_diacritics_have_pixel_margins_in_every_bitmap(self):
        for profile in self.profiles.values():
            for size in range(3):
                lines, _ = layout(self.document, profile, size)
                for line in lines:
                    bounds = line.image.convert('RGB').getbbox()
                    self.assertIsNotNone(bounds)
                    self.assertGreaterEqual(bounds[0], 2)
                    self.assertGreaterEqual(bounds[1], 2)
                    self.assertLessEqual(bounds[2], line.image.width - 2)
                    self.assertLessEqual(bounds[3], line.image.height - 2)

    def test_reading_rectangle_stays_inside_round_display(self):
        for profile in self.profiles.values():
            self.assertLessEqual(profile['column_width'] ** 2 + profile['viewport_height'] ** 2, profile['diameter'] ** 2)

    def test_missing_glyph_is_an_error(self):
        document = copy.deepcopy(self.document)
        document['sections'][0]['paragraphs'][0] += ' \U0001f680'
        with self.assertRaisesRegex(ValueError, 'Missing glyphs'):
            layout(document, self.profiles['fr970'], 1)

    def test_unbreakable_word_and_nonstandard_whitespace_are_errors(self):
        for text in ('ש' * 100, 'שָׁלוֹם\tשָׁלוֹם'):
            with self.assertRaises(ValueError):
                wrap(text, font(31), 100)

    def test_generated_resources_are_complete_bounded_and_repeatable(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / 'generated'
            first = generate(output)
            files = sorted(output.rglob('*.png'))
            hashes = {str(p.relative_to(output)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
            second = generate(output)
            self.assertEqual(first, second)
            self.assertEqual(hashes, {str(p.relative_to(output)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files})
            for device, variants in first['devices'].items():
                ids = {b.attrib['id'] for b in ET.parse(output / device / 'resources/bitmaps.xml').getroot()}
                for variant in variants.values():
                    # Pixel estimate is not a device heap claim.
                    self.assertLess(variant['estimated_visible_pixel_bytes_4bpp'], 80 * 1024)
                    self.assertLessEqual(variant['max_visible_tiles'], 9)
                    for line in variant['lines']:
                        self.assertIn(line['resource'], ids)
                        path = output / device / 'resources/images' / f"{line['resource']}.png"
                        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), line['sha256'])
                        with Image.open(path) as im:
                            self.assertEqual(im.mode, 'P')
                            self.assertLessEqual(len(im.getcolors()), 16)
            old = (output / 'manifest.json').read_bytes()
            with self.assertRaises(ValueError):
                generate(output, release=True)
            self.assertEqual((output / 'manifest.json').read_bytes(), old)

    def test_generator_will_not_delete_user_directory(self):
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(ValueError, 'unrecognized'):
                generate(Path(temporary))


if __name__ == '__main__':
    unittest.main()
