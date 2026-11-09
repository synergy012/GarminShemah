"""Prepare source-mapped review documents. Never approve a publication by import."""
import hashlib
import json
import re
from html.parser import HTMLParser

from tools.content import ROOT, NUSCHAOT, read_json

# Outer small-span roles were checked against the complete source strings.
# Unknown/new spans fail closed instead of inferring meaning from font size.
EDITORIAL_MAP = read_json(ROOT / 'content/editorial-map.json')
ROLES = {
    identifier: {tuple(map(int, key.split(':'))): role for key, role in mapping['small_roles'].items()}
    for identifier, mapping in EDITORIAL_MAP.items()
}


def whitespace(text):
    return re.sub(r'\s+', ' ', text).strip()


class SourceParser(HTMLParser):
    def __init__(self, identifier, index):
        super().__init__(convert_charrefs=True)
        self.identifier, self.index = identifier, index
        self.depth = 0
        self.small_index = -1
        self.kind = 'prayer'
        self.parts = []
        self.buffer = []
        self.seen = set()

    def flush(self):
        text = whitespace(''.join(self.buffer))
        if text:
            self.parts.append((text, self.kind))
        self.buffer = []

    def handle_starttag(self, tag, attrs):
        if tag not in {'small', 'b', 'big', 'br'}:
            raise ValueError(f'Unsupported source markup: {tag}')
        if tag == 'small':
            if self.depth == 0:
                self.flush()
                self.small_index += 1
                key = (self.index, self.small_index)
                self.kind = ROLES[self.identifier][key]
                self.seen.add(key)
            self.depth += 1
        elif tag == 'br':
            self.flush()

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag):
        if tag == 'small':
            if self.depth <= 0:
                raise ValueError('Unbalanced small-print markup')
            self.depth -= 1
            if self.depth == 0:
                self.flush()
                self.kind = 'prayer'

    def handle_data(self, data):
        self.buffer.append(data)


def prepare(identifier):
    acquired = read_json(ROOT / 'content/acquired' / f'{identifier}.json')
    editorial = EDITORIAL_MAP[identifier]
    if acquired['source']['sha256'] != editorial['source_sha256']:
        raise ValueError('The source edition changed; review the editorial map before preparing it')
    document = read_json(ROOT / 'content/nuschaot' / f'{identifier}.json')
    source = acquired['source']
    document['status'] = 'source_review'
    document['sources'] = [{
        'id': identifier + '-edition', 'url': source['download_url'],
        'version_title': source['version_title'], 'license': source['license'],
        'license_verified': True, 'license_url': source['license_url'],
        'retrieved_on': source['retrieved_on'], 'sha256': source['sha256'],
        'attribution': source['attribution'],
    }]
    document['sections'] = []
    seen = set()
    for block in acquired['blocks']:
        if hashlib.sha256(block['html'].encode()).hexdigest() != block['sha256']:
            raise ValueError('Source block integrity check failed')
        parser = SourceParser(identifier, block['source_index'])
        parser.feed(block['html'])
        parser.close()
        parser.flush()
        if parser.depth:
            raise ValueError('Unclosed small-print markup')
        seen.update(parser.seen)
        section = {
            'id': f"source-{block['source_index']:03}",
            'heading_he': 'קריאת שמע שעל המיטה' if block['source_index'] == 1 and identifier != 'edot_hamizrach' else '',
            'optional': False,
            'source_id': identifier + '-edition',
            'source_index': block['source_index'], 'source_block_sha256': block['sha256'],
            'paragraphs': [text for text, kind in parser.parts],
            'paragraph_kinds': [kind for text, kind in parser.parts],
            'custom_policy': 'All source material retained; conditional alternatives follow the source instructions. No automatic omission or repetition expansion.',
        }
        document['sections'].append(section)
    if seen != set(ROLES[identifier]):
        raise ValueError('Source small-print structure changed; explicit mapping needs review')
    document['transformations'] = [
        'HTML entities decoded; b/big styling omitted; br retained as paragraph boundaries.',
        'Outer small spans split into separately classified paragraphs using explicit source-index mappings.',
        'Display whitespace collapsed to single spaces and source-edge whitespace trimmed; no Unicode normalization or spelling/nikud/punctuation edits.',
        'Instruction labels and the first document heading are editorial UI, separate from the source paragraphs.',
    ]
    document['unresolved'] = list(acquired['unresolved'])
    if identifier == 'edot_hamizrach':
        document['unresolved'].append('Yoshev Beseter remains abbreviated exactly as in the chosen source; no verses were borrowed to complete it.')
    return document


if __name__ == '__main__':
    for identifier in NUSCHAOT:
        document = prepare(identifier)
        (ROOT / 'content/nuschaot' / f'{identifier}.json').write_text(json.dumps(document, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print(identifier, len(document['sections']), 'source-mapped review sections')
