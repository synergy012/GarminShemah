"""Build an OFL derivative with Hebrew shaping plus matching serif punctuation."""
from fontTools.merge import Merger
from fontTools.ttLib import TTFont
from tools.content import ROOT
import argparse
import tempfile
from pathlib import Path


def prepare(output=None):
    paths = [ROOT / 'fonts/NotoSerifHebrew-Regular.ttf', ROOT / 'fonts/NotoSerif-Regular.ttf']
    merged = Merger().merge([str(p) for p in paths])
    # Merger creates a fresh head table with the wall-clock time. Retain the
    # primary source's timestamps so independent builds have identical bytes.
    with TTFont(paths[0]) as primary:
        merged['head'].created = primary['head'].created
        merged['head'].modified = primary['head'].modified
    # Do not use the upstream family name for the modified derivative.
    names = {1: 'Siddur Serif', 2: 'Regular', 3: 'SiddurSerif-2026',
             4: 'Siddur Serif Regular', 6: 'SiddurSerif-Regular'}
    for record in merged['name'].names:
        if record.nameID in names:
            record.string = names[record.nameID].encode(record.getEncoding())
    merged.recalcTimestamp = False
    merged.save(output or ROOT / 'fonts/SiddurSerif-Regular.ttf')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true', help='Verify the bundled derivative without modifying it')
    args = parser.parse_args()
    if args.check:
        with tempfile.TemporaryDirectory() as temporary:
            result = Path(temporary) / 'font.ttf'
            prepare(result)
            if result.read_bytes() != (ROOT / 'fonts/SiddurSerif-Regular.ttf').read_bytes():
                parser.exit(1, 'Bundled derivative differs from the source-font build; review before updating.\n')
    else:
        prepare()
