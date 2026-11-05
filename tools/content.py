"""Content validation and exact comparison; never infer liturgical equivalence."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NUSCHAOT = ("ashkenaz", "sefard", "edot_hamizrach")
ALLOWED_LICENSES = {"CC0-1.0", "Public Domain", "CC-BY-4.0", "CC-BY-SA-4.0"}


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate(document, release=False):
    errors = []
    if document.get("schema_version") != 1:
        errors.append("Unsupported content schema")
    sections = document.get("sections", [])
    if not sections:
        errors.append("No sections: complete text has not been acquired")
    sources = {s["id"]: s for s in document.get("sources", [])}
    ids = set()
    for section in sections:
        sid = section.get("id")
        if not sid or sid in ids:
            errors.append(f"Missing or duplicate section id: {sid}")
        ids.add(sid)
        if not isinstance(section.get("optional"), bool):
            errors.append(f"{sid}: optional must be explicit")
        if section.get("source_id") not in sources:
            errors.append(f"{sid}: missing source attribution")
        if not section.get("paragraphs"):
            errors.append(f"{sid}: no paragraphs")
        for text in [section.get("heading_he", ""), *section.get("paragraphs", [])]:
            if not isinstance(text, str) or not text.strip():
                errors.append(f"{sid}: empty or invalid text")
                continue
            if any(c in text for c in "<>\u202a\u202b\u202c\u202d\u202e\u2066\u2067\u2068\u2069"):
                errors.append(f"{sid}: markup or bidi controls require editorial review")
    if release:
        if document.get("id") not in NUSCHAOT or document.get("status") != "verified":
            errors.append("Not a verified nusach")
        review = document.get("review", {})
        if not all(review.get(k) for k in ("text_verified", "order_verified", "reviewer")):
            errors.append("Text and order need recorded human verification")
        if document.get("unresolved"):
            errors.append("Unresolved textual or licensing issues")
        for source in sources.values():
            if source.get("license") not in ALLOWED_LICENSES or not source.get("license_verified"):
                errors.append(f"{source['id']}: reuse permission is unverified")
            for key in ("url", "version_title", "license_url", "retrieved_on", "sha256"):
                if not source.get(key):
                    errors.append(f"{source['id']}: missing {key}")
    return errors


def fingerprint(section):
    # Exact characters and paragraph boundaries, including nikud and punctuation.
    raw = json.dumps(section["paragraphs"], ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


def report(root=ROOT):
    documents = [read_json(root / "content/nuschaot" / f"{n}.json") for n in NUSCHAOT]
    ready = all(not validate(doc, release=True) for doc in documents)
    status = "Status: VERIFIED — recorded text and license review passed for all three nuschaos." if ready else "Status: BLOCKED — no complete verified prayer texts incorporated."
    lines = ["# Text verification report", "", status, "",
             "Edition candidates are recorded in `content/source-candidates.json`. Index presence is not permission to redistribute.", ""]
    for doc in documents:
        lines += [f"## {doc['id']}", "", f"Status: {doc['status']}", "", "Section order:"]
        lines += [f"{i + 1}. {s['id']} — {s['heading_he']} (optional: {s['optional']})" for i, s in enumerate(doc['sections'])] or ["Not established; no sections acquired."]
        lines += ["", "Sources:"] + [f"- {s['url']} — {s.get('version_title', 'version unrecorded')}; license {s.get('license', 'unknown')} (verified: {s.get('license_verified', False)})" for s in doc['sources']] if doc['sources'] else ["", "Sources: none incorporated."]
        lines += ["", "Unresolved:"] + [f"- {e}" for e in doc.get('unresolved', [])] + [""]
    grouped = {}
    for doc in documents:
        for s in doc['sections']:
            grouped.setdefault(fingerprint(s), []).append((doc['id'], s['id']))
    lines += ["## Exact textual comparison", ""]
    if not grouped:
        lines += ["No comparison is possible yet. Shared passages, nusach-specific wording, complete order and optional customs remain unresolved."]
    for digest, occurrences in sorted(grouped.items()):
        lines += [f"- {digest}: {occurrences}"]
    lines += ["", "Equal hashes establish exact paragraph content only, not identical liturgical role, optionality, or prayer order.",
              "The typography fixture is original test prose, dedicated to CC0. It is not tefillah and is never used as a nusach fallback.", ""]
    return "\n".join(lines)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--release", action="store_true")
    parser.add_argument("--check", action="store_true", help="Check report freshness without changing tracked files")
    args = parser.parse_args()
    report_path = ROOT / "docs/TEXT-VERIFICATION.md"
    if args.check:
        if not report_path.exists() or report_path.read_text(encoding="utf-8") != report():
            parser.exit(1, "Text verification report is stale; regenerate and review it.\n")
    else:
        report_path.write_text(report(), encoding="utf-8")
    if args.release:
        failures = {n: validate(read_json(ROOT / "content/nuschaot" / f"{n}.json"), True) for n in NUSCHAOT}
        if any(failures.values()):
            print(json.dumps(failures, ensure_ascii=False, indent=2))
            raise SystemExit(1)
