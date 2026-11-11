"""Generate device resources, line indexes, host proofs and an auditable asset manifest."""
import argparse
import hashlib
import json
import shutil
import xml.etree.ElementTree as ET
from PIL import Image
from pathlib import Path

from tools.content import NUSCHAOT, ROOT, read_json, validate
from tools.render import FONT, layout, preview

# Exact source blocks, including Edot's separate closing repetition.
EXTRA_SHEMA = {
    'ashkenaz': {'source-008', 'source-009'},
    'sefard': {'source-007', 'source-008'},
    'edot_hamizrach': {'source-012', 'source-013', 'source-014'},
}


def reader_flags(document, line):
    section = next(s for s in document['sections'] if s['id'] == line.section)
    paragraph = line.paragraph if line.paragraph >= 0 else -2 - line.paragraph
    kinds = section.get('paragraph_kinds', ['prayer'] * len(section['paragraphs']))
    instruction = line.paragraph != -1 and kinds[paragraph] == 'instruction'
    return int(instruction) + (2 if line.section in EXTRA_SHEMA.get(document['id'], set()) else 0)


def generate(output, release=False, review=False, reuse=False):
    if release and review:
        raise ValueError('Review and release modes are mutually exclusive')
    profiles = read_json(ROOT / "config/devices.json")
    if release or review:
        documents = [read_json(ROOT / "content/nuschaot" / f"{n}.json") for n in NUSCHAOT]
    else:
        documents = [read_json(ROOT / "content/fixtures/typography.json")]
    for doc in documents:
        errors = validate(doc, release)
        if errors:
            raise ValueError(f"{doc['id']}: {'; '.join(errors)}")
    output = Path(output)
    inputs = hashlib.sha256(json.dumps([profiles, documents, release, review], ensure_ascii=False, sort_keys=True).encode())
    for path in (FONT, Path(__file__), ROOT / 'tools/render.py', ROOT / 'tools/divine_names.py', ROOT / 'content/divine-name-policy.json'):
        inputs.update(path.read_bytes())
    input_hash = inputs.hexdigest()
    if reuse and (output / 'manifest.json').exists():
        cached = read_json(output / 'manifest.json')
        if cached.get('input_sha256') == input_hash:
            expected = dict(cached.get('output_hashes', {}))
            for device, variants in cached['devices'].items():
                for variant in variants.values():
                    for line in variant['lines']:
                        expected[f"{device}/resources/images/{line['resource']}.png"] = line['sha256']
            if expected and all((output / name).is_file() and hashlib.sha256((output / name).read_bytes()).hexdigest() == digest for name, digest in expected.items()):
                return cached
    if output.exists() and not (output / ".generated-by-garminshemah").exists():
        raise ValueError("Refusing to overwrite an unrecognized output directory")
    output.mkdir(parents=True, exist_ok=True)
    (output / ".generated-by-garminshemah").touch()
    manifest = {"mode": "release" if release else "review" if review else "prototype", "font_sha256": hashlib.sha256(FONT.read_bytes()).hexdigest(), "input_sha256": input_hash, "output_hashes": {}, "devices": {}}
    for device, profile in profiles.items():
        device_dir = output / device
        if device_dir.exists():
            shutil.rmtree(device_dir)
        resources = device_dir / "resources"
        images = resources / "images"
        images.mkdir(parents=True)
        xml = ET.Element("resources")
        code = ["// GENERATED. Edit content JSON or tools, never this file.", "using Toybox.Lang;", "module DocumentData {",
                f"const WIDTH = {profile['column_width']};", f"const VIEWPORT = {profile['viewport_height']};",
                'const TEXT_VERSION = 2;',
                f"const PROTOTYPE = {'false' if release or review else 'true'};", f"const REVIEW = {'true' if review else 'false'};", "function available(id) {",
                "return " + " || ".join(f'id.equals("{d["id"]}")' for d in documents) + ";", "}",
                "function load(id, size) {"]
        device_manifest = {}
        helpers = []
        tiles = {}
        for doc in documents:
            for size in range(3):
                lines, total = layout(doc, profile, size)
                records = []
                entries = []
                prefix = f"{doc['id']}_{size}"
                atlas_for_line = {}
                for start in range(0, len(lines), 2):
                    group = lines[start:start + 2]
                    atlas = Image.new('P', (profile['column_width'], sum(line.height for line in group)), 0)
                    atlas.putpalette(group[0].image.getpalette())
                    source_y = 0
                    for local, line in enumerate(group):
                        atlas.paste(line.image, (0, source_y))
                        atlas_for_line[start + local] = [atlas, source_y]
                        source_y += line.height
                for index, line in enumerate(lines):
                    flags = reader_flags(doc, line)
                    atlas, source_y = atlas_for_line[index]
                    digest = hashlib.sha256(str(atlas.size).encode() + atlas.tobytes()).hexdigest()[:24]
                    resource_id = 'tile_' + digest
                    path = images / f"{resource_id}.png"
                    if resource_id not in tiles:
                        atlas.save(path, bits=4, optimize=False)
                        ET.SubElement(xml, "bitmap", {"id": resource_id, "filename": f"images/{path.name}", "compress": "true"})
                        tiles[resource_id] = hashlib.sha256(path.read_bytes()).hexdigest()
                    records.append({"resource": resource_id, "y": line.y, "height": line.height, "section": line.section,
                                    "paragraph": line.paragraph, "word_start": line.word_start, "word_end": line.word_end,
                                    "text": line.text, "source_y": source_y, "atlas_height": atlas.height, "sha256": tiles[resource_id], "reader_flags": flags})
                    # Entries support a stable paragraph/word anchor across font-size changes.
                    entries.append(f'[Rez.Drawables.{resource_id},{line.y},{line.height},"{line.section}",{line.paragraph},{line.word_start},{line.word_end},{source_y},{flags}]')
                code += [f'if (id.equals("{doc["id"]}") && size == {size}) {{', 'var lines = [];']
                for chunk in range(0, len(entries), 48):
                    name = f'append_{prefix}_{chunk // 48}'
                    code.append(f'{name}(lines);')
                    helpers += [f'function {name}(lines) {{', 'lines.addAll([' + ',\n'.join(entries[chunk:chunk + 48]) + ']);', '}']
                code += [f'return {{:height=>{total}, :lines=>lines}};', '}']
                max_visible_bytes = 0
                max_visible_tiles = 0
                # Exact worst-case active tile window (one-bit offsets at each entry/exit event).
                offsets = {0, max(0, total - profile["viewport_height"])}
                for line in lines:
                    offsets.update([max(0, line.y - profile["viewport_height"] + 1), line.y + line.height - 1])
                for offset in offsets:
                    visible = {r['resource']: r for r in records if r['y'] < offset + profile['viewport_height'] and r['y'] + r['height'] > offset}
                    max_visible_tiles = max(max_visible_tiles, len(visible))
                    max_visible_bytes = max(max_visible_bytes, sum((profile['column_width'] * r['atlas_height'] + 1) // 2 for r in visible.values()))
                device_manifest[prefix] = {"document_height": total, "lines": records,
                                           "estimated_visible_pixel_bytes_4bpp": max_visible_bytes,
                                           "max_visible_tiles": max_visible_tiles,
                                           "caveat": "CIQ decoder format, resource overhead and VM heap require simulator measurement"}
                proof_dir = output / "proofs"
                proof_dir.mkdir(exist_ok=True)
                for frame, offset in enumerate((0, total // 3, max(0, total - profile['viewport_height']))):
                    preview(lines, profile, offset, notice='REVIEW COPY / HOST PROOF' if review else 'TYPE TEST / HOST PROOF' if not release else 'HOST PROOF').save(proof_dir / f"{device}_{prefix}_{frame}.png")
        attribution = ['Text sources / attribution']
        for doc in documents:
            attribution.append(doc['id'].replace('_', ' ').title())
            for source in doc.get('sources', []):
                attribution += [source.get('attribution', source.get('version_title', source.get('title', ''))),
                                'License: ' + source.get('license', 'unknown'), source.get('license_url', ''), source.get('url', '')]
        if review:
            attribution += ['Display changes: markup parsed, whitespace normalized, instructions separated and labelled. Divine Names are displayed as he followed by Hebrew geresh; other wording and pointing retained. Reader settings can hide instructions or Shema paragraphs 2 and 3.',
                            'REVIEW COPY: source instructions and alternatives are retained. Publication review is incomplete.',
                            'Edot HaMizrach: the selected source abbreviates Yoshev Beseter. No missing verses were borrowed from another nusach.']
        code += ["return null;", "}", *helpers, 'function sourceLines() { return [' + ','.join(json.dumps(line, ensure_ascii=True) for line in attribution if line) + ']; }', "}"]
        (device_dir / "DocumentData.mc").write_text("\n".join(code) + "\n")
        ET.indent(xml)
        ET.ElementTree(xml).write(resources / "bitmaps.xml", encoding="unicode")
        for path in (device_dir / 'DocumentData.mc', resources / 'bitmaps.xml'):
            manifest['output_hashes'][str(path.relative_to(output))] = hashlib.sha256(path.read_bytes()).hexdigest()
        manifest["devices"][device] = device_manifest
    (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--release", action="store_true")
    mode.add_argument("--review", action="store_true")
    parser.add_argument("--output", type=Path, default=ROOT / "generated")
    args = parser.parse_args()
    try:
        manifest = generate(args.output, args.release, args.review)
    except ValueError as exc:
        parser.exit(1, str(exc) + "\n")
    print(f"Generated {manifest['mode']} resources for {', '.join(manifest['devices'])}")
