"""Offline Hebrew shaping. The watch draws indexed PNG scanlines, not Unicode."""
import math
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, features
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]
FONT = ROOT / "fonts/SiddurSerif-Regular.ttf"
WARM = (242, 230, 205)


@dataclass
class Line:
    text: str
    section: str
    paragraph: int
    word_start: int
    word_end: int
    y: int
    height: int
    heading: bool
    image: Image.Image


def font(size):
    if not features.check_feature("raqm"):
        raise RuntimeError("Pillow with libraqm/HarfBuzz/FriBidi is required; no reversal fallback")
    return ImageFont.truetype(str(FONT), size, layout_engine=ImageFont.Layout.RAQM)


def extent(text, face):
    box = face.getbbox(text, direction="rtl", language="he", anchor="lt")
    return max(face.getlength(text, direction="rtl", language="he"), box[2] - box[0])


def wrap(text, face, width):
    """Wrap logical-order words; preserve original characters, never split combining marks."""
    words = text.split(" ")
    if any(not w or any(c.isspace() for c in w) for w in words):
        raise ValueError("Nonstandard whitespace needs explicit editorial handling")
    result = []
    start = 0
    for i, word in enumerate(words):
        if extent(word, face) > width:
            raise ValueError(f"Unbreakable word exceeds reading width: {word!r}")
        candidate = " ".join(words[start:i + 1])
        if extent(candidate, face) > width:
            result.append((" ".join(words[start:i]), start, i))
            start = i
    result.append((" ".join(words[start:]), start, len(words)))
    return result


def bitmap(text, face, width, height, heading=False, muted=False):
    # Shape whole logical-order lines. Bounding boxes include nikud above and below.
    box = face.getbbox(text, direction="rtl", language="he", anchor="lt")
    ink_height = box[3] - box[1]
    if ink_height + 8 > height or box[2] - box[0] + 8 > width:
        raise ValueError("Glyph bounds exceed tile; refuse to clip diacritics")
    mask = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(mask)
    left = (width - (box[2] - box[0])) // 2 if heading else width - 4 - box[2] + box[0]
    draw.text((left - box[0], (height - ink_height) // 2 - box[1]), text, font=face,
              fill=190 if heading or muted else 255, direction="rtl", language="he", anchor="lt")
    # 4-bit palette keeps antialiasing and bounds decoded pixel storage.
    paletted = mask.point(lambda value: round(value / 17)).convert("P")
    palette = []
    for level in range(256):
        palette.extend(round(v * min(level, 15) / 15) for v in WARM)
    paletted.putpalette(palette)
    return paletted


def layout(document, profile, size):
    with TTFont(FONT) as tt:
        supported = tt.getBestCmap()
    text = ''.join(s['heading_he'] + ''.join(s['paragraphs']) for s in document['sections'])
    missing = sorted({ord(c) for c in text if ord(c) not in supported})
    if missing:
        raise ValueError(f"Missing glyphs: {[f'U+{c:04X}' for c in missing]}")
    face = font(profile["font_sizes"][size])
    heading_face = font(max(20, profile["font_sizes"][size] - 5))
    note_face = font(max(22, profile['font_sizes'][size] - 5))
    height = math.ceil(profile["font_sizes"][size] * 1.7)
    y = 12
    lines = []
    for section in document["sections"]:
        # Optional sections stay included until a reviewed per-minhag UI is implemented.
        for text, start, end in (wrap(section['heading_he'], heading_face, profile['column_width'] - 8) if section['heading_he'] else []):
            lines.append(Line(text, section["id"], -1, start, end, y, height, True,
                              bitmap(text, heading_face, profile["column_width"], height, True)))
            y += height
        y += 8
        for index, paragraph in enumerate(section["paragraphs"]):
            kind = section.get('paragraph_kinds', ['prayer'] * len(section['paragraphs']))[index]
            if kind in {'instruction', 'conditional'}:
                label = 'הוראה' if kind == 'instruction' else 'אמירה לפי ההוראה'
                lines.append(Line(label, section['id'], -2 - index, 0, 1, y, height, True,
                                  bitmap(label, heading_face, profile['column_width'], height, True)))
                y += height
            paragraph_face = note_face if kind in {'instruction', 'conditional', 'source_small'} else face
            for text, start, end in wrap(paragraph, paragraph_face, profile["column_width"] - 8):
                lines.append(Line(text, section["id"], index, start, end, y, height, False,
                                  bitmap(text, paragraph_face, profile["column_width"], height, muted=kind != 'prayer')))
                y += height
            y += 18
        y += 12
    return lines, y + 12


def preview(lines, profile, offset=0, dim=False, notice='TYPE TEST / HOST PROOF'):
    """Host raster proof only. This function does not simulate Garmin firmware."""
    d = profile["diameter"]
    image = Image.new("RGB", (d, d), "black")
    width, height = profile["column_width"], profile["viewport_height"]
    viewport = Image.new("RGB", (width, height), "black")
    for line in lines:
        y = line.y - offset
        if y < height and y + line.height > 0:
            tile = line.image.convert("RGB")
            if dim:
                tile = tile.point(lambda v: round(v * .65))
            viewport.paste(tile, (0, y))
    image.paste(viewport, ((d - width) // 2, (d - height) // 2))
    draw = ImageDraw.Draw(image)
    # Visible notice distinguishes this from a prayer and from a simulator screenshot.
    label = notice
    label_font = ImageFont.load_default(size=13)
    draw.text((d // 2, 35), label, font=label_font, fill=WARM, anchor="mt")
    return image
