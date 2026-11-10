import tempfile
import unittest
from pathlib import Path

from PIL import Image

from tools.content import ROOT, NUSCHAOT, read_json
from tools.generate import generate, EXTRA_SHEMA, reader_flags
from tools.render import layout


class ReviewResourceTests(unittest.TestCase):
    def test_all_text_sizes_fit_bitmap_limit_and_preserve_every_paragraph(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / 'generated'
            manifest = generate(output, review=True)
            self.assertEqual(manifest['mode'], 'review')
            profile = read_json(ROOT / 'config/devices.json')['fr970']
            images = output / 'fr970/resources/images'
            # One resource slot is reserved for the application launcher.
            self.assertLessEqual(len(list(images.glob('*.png'))) + 1, 2047)
            for identifier in NUSCHAOT:
                document = read_json(ROOT / 'content/nuschaot' / f'{identifier}.json')
                for size in range(3):
                    records = manifest['devices']['fr970'][f'{identifier}_{size}']['lines']
                    for section in document['sections']:
                        for index, paragraph in enumerate(section['paragraphs']):
                            actual = [r['text'] for r in records if r['section'] == section['id'] and r['paragraph'] == index]
                            self.assertEqual(' '.join(actual), paragraph)
                    # Verify first/last/central glyph rows against the real PNG atlas.
                    lines, _ = layout(document, profile, size)
                    for line, record in zip(lines, records):
                        self.assertEqual(record['reader_flags'], reader_flags(document, line))
                        self.assertEqual(bool(record['reader_flags'] & 2), line.section in EXTRA_SHEMA[identifier])
                    for index in sorted({0, 1, len(lines) // 2, len(lines) - 1}):
                        record = records[index]
                        with Image.open(images / f"{record['resource']}.png") as atlas:
                            crop = atlas.crop((0, record['source_y'], atlas.width, record['source_y'] + record['height']))
                            self.assertEqual(crop.convert('RGB').tobytes(), lines[index].image.convert('RGB').tobytes())
            self.assertEqual(generate(output, review=True, reuse=True), manifest)
            damaged = next(images.glob('*.png'))
            damaged.write_bytes(b'damaged generated resource')
            self.assertEqual(generate(output, review=True, reuse=True), manifest)
            with Image.open(damaged) as repaired:
                repaired.load()

    def test_optional_shema_blocks_match_passages_and_edot_closing(self):
        import unicodedata
        for identifier, sections in EXTRA_SHEMA.items():
            document = read_json(ROOT / 'content/nuschaot' / f'{identifier}.json')
            selected = [s for s in document['sections'] if s['id'] in sections]
            plain = [''.join(c for c in unicodedata.normalize('NFD', s['paragraphs'][0]) if not unicodedata.combining(c)) for s in selected]
            self.assertTrue(plain[0].startswith('והיה אם'))
            self.assertTrue(plain[1].startswith('ויאמר'))
            if identifier == 'edot_hamizrach':
                self.assertEqual(len(selected), 3)
                self.assertEqual(selected[2]['paragraphs'][1], 'יְהֹוָה אֱלֹהֵיכֶם אֱמֶת.')
            else:
                self.assertEqual(len(selected), 2)


if __name__ == '__main__':
    unittest.main()
