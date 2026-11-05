"""Generate device resources, line indexes, host proofs and an auditable asset manifest."""
import argparse
import hashlib
import json
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

from tools.content import NUSCHAOT, ROOT, read_json, validate
from tools.render import FONT, layout, preview


def generate(output, release=False):
    profiles = read_json(ROOT / "config/devices.json")
    if release:
        documents = [read_json(ROOT / "content/nuschaot" / f"{n}.json") for n in NUSCHAOT]
    else:
        documents = [read_json(ROOT / "content/fixtures/typography.json")]
    for doc in documents:
        errors = validate(doc, release)
        if errors:
            raise ValueError(f"{doc['id']}: {'; '.join(errors)}")
    output = Path(output)
    if output.exists() and not (output / ".generated-by-garminshemah").exists():
        raise ValueError("Refusing to overwrite an unrecognized output directory")
    output.mkdir(parents=True, exist_ok=True)
    (output / ".generated-by-garminshemah").touch()
    manifest = {"mode": "release" if release else "prototype", "font_sha256": hashlib.sha256(FONT.read_bytes()).hexdigest(), "devices": {}}
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
                f"const PROTOTYPE = {'false' if release else 'true'};", "function available(id) {",
                "return " + " || ".join(f'id.equals("{d["id"]}")' for d in documents) + ";", "}",
                "function load(id, size) {"]
        device_manifest = {}
        for doc in documents:
            for size in range(3):
                lines, total = layout(doc, profile, size)
                records = []
                entries = []
                prefix = f"{doc['id']}_{size}"
                for index, line in enumerate(lines):
                    resource_id = f"line_{prefix}_{index}"
                    path = images / f"{resource_id}.png"
                    line.image.save(path, bits=4, optimize=False)
                    ET.SubElement(xml, "bitmap", {"id": resource_id, "filename": f"images/{path.name}"})
                    records.append({"resource": resource_id, "y": line.y, "height": line.height, "section": line.section,
                                    "paragraph": line.paragraph, "word_start": line.word_start, "word_end": line.word_end,
                                    "text": line.text, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
                    # Entries support a stable paragraph/word anchor across font-size changes.
                    entries.append(f'[Rez.Drawables.{resource_id},{line.y},{line.height},"{line.section}",{line.paragraph},{line.word_start},{line.word_end}]')
                code += [f'if (id.equals("{doc["id"]}") && size == {size}) {{',
                         f'return {{:height=>{total}, :lines=>[' + ",\n".join(entries) + "]};", "}"]
                max_visible_bytes = 0
                max_visible_tiles = 0
                # Exact worst-case active tile window (one-bit offsets at each entry/exit event).
                offsets = {0, max(0, total - profile["viewport_height"])}
                for line in lines:
                    offsets.update([max(0, line.y - profile["viewport_height"] + 1), line.y + line.height - 1])
                for offset in offsets:
                    visible = [l for l in lines if l.y < offset + profile["viewport_height"] and l.y + l.height > offset]
                    max_visible_tiles = max(max_visible_tiles, len(visible))
                    max_visible_bytes = max(max_visible_bytes, sum((profile['column_width'] * l.height + 1) // 2 for l in visible))
                device_manifest[prefix] = {"document_height": total, "lines": records,
                                           "estimated_visible_pixel_bytes_4bpp": max_visible_bytes,
                                           "max_visible_tiles": max_visible_tiles,
                                           "caveat": "CIQ decoder format, resource overhead and VM heap require simulator measurement"}
                proof_dir = output / "proofs"
                proof_dir.mkdir(exist_ok=True)
                for frame, offset in enumerate((0, total // 3, max(0, total - profile['viewport_height']))):
                    preview(lines, profile, offset).save(proof_dir / f"{device}_{prefix}_{frame}.png")
        code += ["return null;", "}", "}"]
        (device_dir / "DocumentData.mc").write_text("\n".join(code) + "\n")
        ET.indent(xml)
        ET.ElementTree(xml).write(resources / "bitmaps.xml", encoding="unicode")
        manifest["devices"][device] = device_manifest
    (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--release", action="store_true")
    parser.add_argument("--output", type=Path, default=ROOT / "generated")
    args = parser.parse_args()
    try:
        manifest = generate(args.output, args.release)
    except ValueError as exc:
        parser.exit(1, str(exc) + "\n")
    print(f"Generated {manifest['mode']} resources for {', '.join(manifest['devices'])}")
