"""Retrieve candidate editions for LOCAL review, never for automatic publication."""
import argparse
import hashlib
import json
import urllib.request

from tools.content import ROOT, read_json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', default='Torat Emet 357')
    args = parser.parse_args()
    candidates = read_json(ROOT / 'content/source-candidates.json')['editions']
    output = ROOT / 'build/research'
    output.mkdir(parents=True, exist_ok=True)
    for item in candidates:
        if item['versionTitle'] != args.version:
            continue
        path = output / (item['title'].replace(' ', '_') + '.json')
        request = urllib.request.Request(item['json_url'], headers={'User-Agent': 'GarminShemah-source-review/0.1'})
        # Inherited proxy and default certificate verification remain enabled.
        try:
            with urllib.request.urlopen(request, timeout=40) as response:
                data = response.read(20 * 1024 * 1024 + 1)
            if len(data) > 20 * 1024 * 1024:
                raise ValueError('Unexpectedly large edition; review download manually')
            document = json.loads(data)
        except Exception as exc:
            parser.exit(1, f"{item['title']}: {exc}\nNo text incorporated.\n")
        path.write_bytes(data)
        metadata = {**item, 'sha256': hashlib.sha256(data).hexdigest(),
                    'license_claim': document.get('license'), 'distribution_approved': False}
        path.with_suffix('.metadata.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n')
        print(f"Saved {path.name} for local review; license claim: {document.get('license', 'not present')}")
    print('Do not copy into content/nuschaot until source, wording, section order, optional customs and reuse permission are verified.')


if __name__ == '__main__':
    main()
