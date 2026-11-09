"""Install missing English simulator fonts from the corresponding upstream family.

These fonts affect native simulator UI only; the app's Hebrew uses its own bitmaps.
Existing SDK-provided files are preserved. Downloads retain TLS and hash checks.
"""
import argparse
import hashlib
import os
from pathlib import Path
import urllib.request

from tools.content import ROOT, read_json


def install(state, cache):
    manifest = read_json(ROOT / 'tools/ciq/fonts.json')
    destination = state / '.Garmin/ConnectIQ/Fonts'
    destination.mkdir(parents=True, exist_ok=True)
    cache.mkdir(parents=True, exist_ok=True)
    for item in manifest['files']:
        output = destination / item['filename']
        if output.exists():
            print(f'Preserved existing {output.name}')
            continue
        cached = cache / item.get('cache_filename', Path(item['source_path']).name)
        if cached.exists():
            data = cached.read_bytes()
        else:
            with urllib.request.urlopen(manifest['source_root'] + item['source_path'], timeout=40) as response:
                data = response.read(5 * 1024 * 1024 + 1)
        if len(data) > 5 * 1024 * 1024 or hashlib.sha256(data).hexdigest() != item['sha256']:
            raise ValueError(f'Unexpected font artifact: {item["filename"]}; nothing installed for this file')
        if not cached.exists():
            cached.write_bytes(data)
        with output.open('xb') as handle:
            handle.write(data)
        print(f'Installed {output.name} (verified SHA-256)')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--state', type=Path, default=Path(os.environ.get('CIQ_RUNTIME_STATE', '/workspace/.toolchains/garmin/runtime/state')))
    parser.add_argument('--cache', type=Path, default=Path('/workspace/.toolchains/garmin/runtime/font-research'))
    args = parser.parse_args()
    install(args.state, args.cache)
