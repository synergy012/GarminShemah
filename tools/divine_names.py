"""Auditable display-only substitutions; verbatim source documents stay intact."""
import copy
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / 'content/divine-name-policy.json'
IDS = ('ashkenaz', 'sefard', 'edot_hamizrach')
REPLACEMENT = 'ה׳'
CONVENTION = 'four-letter-only-v3'
TOKEN = re.compile(r'[\u05d0-\u05ea\u0591-\u05bd\u05bf\u05c1\u05c2\u05c4\u05c5\u05c7]+')
GRAPHEME = re.compile(r'[\u05d0-\u05ea][\u0591-\u05bd\u05bf\u05c1\u05c2\u05c4\u05c5\u05c7]*')
ROOTS = {'יהוה': 'tetragrammaton', 'אדני': 'adonai', 'אל': 'el', 'שדי': 'shaddai',
         'צבאות': 'tzevaot', 'אהיה': 'ehyeh', 'יה': 'yah'}
for _form in ('אלהים', 'אלוהים', 'אלהי', 'אלוהי', 'אלהינו', 'אלוהינו', 'אלהיך', 'אלוהיך',
              'אלהיכם', 'אלוהיכם', 'אלהיו', 'אלוהיו', 'אלוה'):
    ROOTS[_form] = 'elohim_forms'
PREFIXES = ('', 'ו', 'ל', 'ב', 'מ', 'ה', 'כ', 'ול', 'וב', 'ומ', 'וה', 'וכ', 'ש')


def letters(text):
    return ''.join(c for c in text if '\u05d0' <= c <= '\u05ea')


def document_digest(document):
    values = [[s['id'], s['heading_he'], s['paragraphs']] for s in document['sections']]
    return hashlib.sha256(json.dumps(values, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()


def display_name(name, kind):
    return REPLACEMENT if kind == 'tetragrammaton' else name


def name_spans(text):
    """Classify exact pointed words, not arbitrary substrings or divine epithets."""
    tokens = list(TOKEN.finditer(text))
    replacements, exceptions = [], []
    for index, token in enumerate(tokens):
        plain = letters(token[0])
        for prefix in PREFIXES:
            if not plain.startswith(prefix):
                continue
            stem = plain[len(prefix):]
            if stem not in ROOTS or (stem == 'יה' and prefix):
                continue
            clusters = list(GRAPHEME.finditer(token[0]))
            name_start = clusters[len(prefix)].start() if prefix else 0
            name = token[0][name_start:]
            reason = None
            if stem == 'אל' and '\u05b5' not in clusters[len(prefix)][0]:
                reason = 'preposition_or_negation_not_a_divine_name'
            if stem in ('אלהים', 'אלוהים') and index + 1 < len(tokens) and letters(tokens[index + 1][0]) == 'אחרים':
                reason = 'other_gods_not_a_name_of_Hashem'
            span = {'start': token.start() + name_start, 'end': token.end(), 'source': name, 'kind': ROOTS[stem]}
            if reason:
                span['reason'] = reason
                exceptions.append(span)
            else:
                span['display'] = display_name(name, ROOTS[stem])
                if span['display'] == name:
                    span['reason'] = 'preserved_by_requested_convention'
                    exceptions.append(span)
                    break
                replacements.append(span)
            break
    return replacements, exceptions


def make_policy(documents):
    result = {'replacement': REPLACEMENT, 'convention': CONVENTION, 'documents': {}}
    for document in documents:
        fields = []
        for section in document['sections']:
            for index, text in [(-1, section['heading_he']), *enumerate(section['paragraphs'])]:
                replacements, exceptions = name_spans(text)
                if replacements or exceptions:
                    fields.append({'section': section['id'], 'paragraph': index, 'replacements': replacements, 'exceptions': exceptions})
        result['documents'][document['id']] = {'text_sha256': document_digest(document), 'fields': fields}
    return result


def display_document(document):
    if document['id'] not in IDS:
        return document
    policy = json.loads(POLICY.read_text())
    entry = policy['documents'][document['id']]
    if policy['replacement'] != REPLACEMENT or policy.get('convention') != CONVENTION or entry['text_sha256'] != document_digest(document):
        raise ValueError('Divine-name policy needs review for changed source text')
    output = copy.deepcopy(document)
    sections = {s['id']: s for s in output['sections']}
    for field in entry['fields']:
        section = sections[field['section']]
        index = field['paragraph']
        text = section['heading_he'] if index == -1 else section['paragraphs'][index]
        expected, exceptions = name_spans(text)
        if expected != field['replacements'] or exceptions != field['exceptions']:
            raise ValueError('Divine-name span audit does not match the pinned policy')
        for span in reversed(field['replacements']):
            if text[span['start']:span['end']] != span['source']:
                raise ValueError('Divine-name source span changed')
            text = text[:span['start']] + span['display'] + text[span['end']:]
        if index == -1:
            section['heading_he'] = text
        else:
            section['paragraphs'][index] = text
    return output


def export_review():
    policy = json.loads(POLICY.read_text())
    report = ['# Divine-name display substitutions', '', 'Only the four-letter Name displays as **ה׳**. Every other Name remains exactly as it appears in the source, including its spelling, vowels, prefixes and endings. No kuf substitutions or added dashes are applied. Original acquired and reader-input JSON remains verbatim for provenance. Substitutions apply only at pinned four-letter Name spans. Attached prefixes remain unchanged; the four-letter Name itself becomes unpointed ה׳. All other source text is unchanged.', '', 'Ordinary prepositions/negations, angel/personal names, descriptive words and the Shema reference to other gods are not Divine Names and remain unchanged. This is a display convention, not a change to source certification.', '', '| Nusach | Replacements | By name family |', '| --- | ---: | --- |']
    folder = ROOT / 'content/review'
    folder.mkdir(exist_ok=True)
    for identifier in IDS:
        document = json.loads((ROOT / 'content/nuschaot' / f'{identifier}.json').read_text())
        displayed = display_document(document)
        counts = Counter(s['kind'] for f in policy['documents'][identifier]['fields'] for s in f['replacements'])
        report.append(f"| {identifier} | {sum(counts.values())} | {dict(sorted(counts.items()))} |")
        lines = [f"# {document['title_he']}", '', '**Source-review display text: only the four-letter Name uses ה׳. Other Names retain their source spelling.**', '', 'See [name substitution audit](../../docs/DIVINE-NAMES.md) and [source notices](../acquired/NOTICE.md).', '']
        for section in displayed['sections']:
            lines += [f"## {section['id']}", '']
            for kind, text in zip(section['paragraph_kinds'], section['paragraphs']):
                if kind in ('instruction', 'conditional'):
                    lines += [f'[{kind}]', '']
                lines += [text, '']
        (folder / f'{identifier}.md').write_text('\n'.join(lines))
    report += ['', 'The policy in `content/divine-name-policy.json` records each exact source span, replacement, exception and text digest. Preparation/generation rejects changed source text until the mapping is reviewed. Saved positions migrate by word anchor after this reflow. Prefixes and replacements keep the same word count.', '']
    (ROOT / 'docs/DIVINE-NAMES.md').write_text('\n'.join(report))


if __name__ == '__main__':
    export_review()
