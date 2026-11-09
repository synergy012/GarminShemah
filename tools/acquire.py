"""Preserve licensed bedtime excerpts verbatim; acquisition never approves reader text."""
import argparse
import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path

from tools.content import ROOT, read_json

SPECS = {
    'ashkenaz': {
        'filename': 'ashkenaz-The_Metsudah_siddur,_1981.json',
        'title': 'Siddur Ashkenaz',
        'version': 'The Metsudah siddur, 1981',
        'license_claim': 'CC-BY', 'license': 'CC-BY-3.0',
        'license_url': 'https://creativecommons.org/licenses/by/3.0/',
        'path': ['Weekday', 'Maariv', "Keri'at Shema al Hamita"],
    },
    'sefard': {
        'filename': 'Siddur_Sefard.json',
        'title': 'Siddur Sefard', 'version': 'Torat Emet 357',
        'license_claim': 'Public Domain', 'license': 'Public Domain',
        'license_url': 'https://www.sefaria.org/api/texts/versions/Siddur_Sefard',
        'path': ['Bedtime Shema'],
    },
    'edot_hamizrach': {
        'filename': 'Siddur_Edot_HaMizrach.json',
        'title': 'Siddur Edot HaMizrach', 'version': 'Torat Emet 357',
        'license_claim': 'Public Domain', 'license': 'Public Domain',
        'license_url': 'https://www.sefaria.org/api/texts/versions/Siddur_Edot_HaMizrach',
        'path': ['Bedtime Shema'],
    },
}


class ComparisonText(HTMLParser):
    """Only for comparison/reporting; the source HTML remains the primary excerpt."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.fragments = []

    def handle_starttag(self, tag, attrs):
        if tag not in {'b', 'big', 'small', 'br'}:
            raise ValueError(f'Unexpected markup requires review: {tag}')
        if tag == 'br':
            self.fragments.append('\n')

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_data(self, data):
        self.fragments.append(data)


def comparison_text(html):
    parser = ComparisonText()
    parser.feed(html)
    parser.close()
    return ''.join(parser.fragments).strip()


def extract(document, spec, download_url, raw_bytes, retrieved_on):
    for key, expected in [('title', spec['title']), ('versionTitle', spec['version']), ('license', spec['license_claim'])]:
        if document.get(key) != expected:
            raise ValueError(f'Unexpected {key}; review edition and permission before import')
    blocks = document['text']
    for component in spec['path']:
        blocks = blocks[component]
    if not isinstance(blocks, list) or not blocks or any(not isinstance(b, str) or not b.strip() for b in blocks):
        raise ValueError('The named edition has no complete nonempty source block list at the selected path')
    # Validate markup for comparison, never replace the stored source with this projection.
    for block in blocks:
        comparison_text(block)
    return {
        'schema_version': 1,
        'status': 'acquired_not_editorially_verified',
        'source': {
            'title': spec['title'], 'version_title': spec['version'],
            'download_url': download_url,
            'version_source': document.get('versionSource'),
            'retrieved_on': retrieved_on,
            'sha256': hashlib.sha256(raw_bytes).hexdigest(),
            'license_claim': spec['license_claim'], 'license': spec['license'],
            'license_url': spec['license_url'],
            'license_evidence_url': 'https://www.sefaria.org/api/texts/versions/' + spec['title'].replace(' ', '_'),
            'attribution': spec['title'] + ', ' + spec['version'] + ', via Sefaria. Original Hebrew/HTML excerpt retained without textual edits.',
        },
        'source_path': spec['path'],
        'review': {'text_verified': False, 'order_verified': False, 'reviewer': None},
        'blocks': [
            {'source_index': i + 1, 'html': block,
             'sha256': hashlib.sha256(block.encode('utf-8')).hexdigest(),
             'classification': 'unreviewed_source_block'}
            for i, block in enumerate(blocks)
        ],
        'unresolved': [
            'Source section acquired in full, but completeness relative to the intended minhag requires knowledgeable review.',
            'Prayer, instruction, repetition and alternative/custom boundaries have not been approved for the reader.',
            'No normalization, expansion of repetitions, omission or substitution is authorized by this acquisition.',
        ],
    }


def acquisition_report(documents):
    report_date = max(document['source']['retrieved_on'] for document in documents.values())
    lines = [f'# Prayer text acquisition and comparison — {report_date}', '',
             '**Acquired, not publication-ready.** The source block lists below are verbatim excerpts from named editions, including their editorial instructions. They are not an approved reader document.', '',
             'The application still uses its labelled typography fixture. These excerpts do not unlock a release build.', '']
    hashes = {}
    for identifier, document in documents.items():
        source = document['source']
        lines += [f'## {identifier}', '', f"- Edition: {source['title']} — {source['version_title']}",
                  f"- Catalog permission: {source['license']} ([evidence]({source['license_evidence_url']})).",
                  f"- Source path: {' → '.join(document['source_path'])}",
                  f"- Retrieved: {source['retrieved_on']}; whole-source SHA-256: `{source['sha256']}`.",
                  f"- Preserved source blocks: {len(document['blocks'])}. These include prose instructions, not just prayers.", '',
                  '### Source block order', '']
        for block in document['blocks']:
            text = comparison_text(block['html'])
            incipit = text.replace('\n', ' ')[:95].replace('|', '\\|')
            lines.append(f"{block['source_index']}. {incipit}…")
            digest = hashlib.sha256(text.encode()).hexdigest()
            hashes.setdefault(digest, []).append((identifier, block['source_index']))
        lines += ['', 'Unresolved:', ''] + ['- ' + item for item in document['unresolved']] + ['']
    lines += ['## Exact text shared between editions', '',
              'Comparison removes only `b`, `big`, `small` formatting tags, converts `br` to a newline, decodes HTML entities and trims source-edge whitespace. It does not normalize Unicode, nikud, punctuation, internal whitespace or divine names. The stored HTML is untouched.', '']
    shared = [items for items in hashes.values() if len({item[0] for item in items}) > 1]
    if shared:
        lines += ['- ' + ', '.join(f'{identifier} block {index}' for identifier, index in items) for items in shared]
    else:
        lines += ['No whole source blocks are identical under this conservative comparison. Similar titles or prayers are not treated as identical text.']
    lines += ['', 'Blocks absent from another edition are candidates for comparison, not automatic proof that the prayer is unique: that edition may divide or combine paragraphs differently.', '',
              '## Differences and customs requiring review', '',
              '- Ashkenaz/Metsudah has 37 source blocks and ends with separate Adon Olam stanzas. Several repetition instructions are separate blocks.',
              '- Sefard/Torat Emet has 27 blocks, includes Adon Olam as one block, then Psalms 1–4. These appended psalms are not silently dropped; their customary status needs review.',
              '- Edot HaMizrach/Torat Emet has 30 blocks: introductory instructions and Leshem Yichud, weekday versus Shabbat/festival Hashkivenu alternatives, Hamapil timing instructions, Vidui conditions, and weekday-labelled Ana Bekoach lines.',
              '- The Edot HaMizrach Yoshev Beseter block ends at “כִּי אַתָּה יְהֹוָה מַחְסִי”. It must not be silently completed with another edition. Confirm whether this is the intended abbreviated custom or an incomplete transcription.',
              '- Metsudah uses additional Hebrew marks and different spelling/punctuation from Torat Emet. No marks have been stripped to manufacture a match.',
              '- Edot HaMizrach contains instructions embedded inside liturgical blocks. A plain HTML-strip-and-render import would mix commentary with prayer and is not approved.', '',
              '## Licensing and attribution', '',
              'The export and live version metadata agree on the recorded license labels. Sefaria’s own `getLicenseMap` maps `CC-BY` to **CC BY 3.0**; this is not an assumption that all editions or translations share a license. The mapping evidence is recorded in `content/acquired/license-evidence.json`.', '',
              'Retain the source attribution, edition/version names, license link, provenance and any future change notices in every distribution containing these excerpts. The Ashkenaz content is CC BY 3.0; the two specified Torat Emet excerpts are cataloged as public domain. Unknown-license or empty Ashkenaz candidates were excluded.', '',
              'No knowledgeable human text/custom review is recorded. Milestone 1 remains incomplete until discrepancies, alternatives, completeness and intended defaults are resolved.', '']
    return '\n'.join(lines)


def acquire(research_dir, output, retrieved_on):
    candidates = read_json(ROOT / 'content/source-candidates.json')['editions']
    documents = {}
    for identifier, spec in SPECS.items():
        path = research_dir / spec['filename']
        raw_bytes = path.read_bytes()
        candidate = next(c for c in candidates if c['title'] == spec['title'] and c['versionTitle'] == spec['version'])
        document = extract(json.loads(raw_bytes), spec, candidate['json_url'], raw_bytes, retrieved_on)
        document['id'] = identifier
        documents[identifier] = document
    output.mkdir(parents=True, exist_ok=True)
    for identifier, document in documents.items():
        (output / f'{identifier}.json').write_text(json.dumps(document, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return documents


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--research-dir', type=Path, default=ROOT / 'build/research')
    parser.add_argument('--retrieved-on', required=True)
    args = parser.parse_args()
    documents = acquire(args.research_dir, ROOT / 'content/acquired', args.retrieved_on)
    (ROOT / 'docs/TEXT-ACQUISITION.md').write_text(acquisition_report(documents), encoding='utf-8')
    for identifier, document in documents.items():
        print(f"{identifier}: {len(document['blocks'])} verbatim source blocks; reader approval remains blocked")
