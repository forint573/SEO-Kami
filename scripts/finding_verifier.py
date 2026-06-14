#!/usr/bin/env python3
"""Dedupe + contradiction-suppress findings across one or more emit() envelopes."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import seo_common
from seo_common import Page, Finding, emit, arg_url
from lib import safe_http, sanitize

# Strongest-first ordering used for merge decisions.
SEV_RANK = {s: i for i, s in enumerate(seo_common.SEVERITY_ORDER)}  # critical=0 strongest

# Finding fields we know how to rebuild from a plain dict.
_FINDING_FIELDS = ("id", "title", "severity", "category", "evidence",
                   "impact", "fix", "confidence", "evidence_tier", "detail")

# Contradiction rules: a finding that ASSERTS the absence of some concept is
# contradicted when another CONFIRMED finding demonstrates that concept present.
# Each concept maps to the substrings that, in a finding's id/title, indicate
# the thing IS present (a measured/confirmed positive).
_PRESENCE_HINTS = {
    "canonical": ("canonical-present", "canonical found", "has canonical", "canonical ok", "canonical set"),
    "title": ("title-present", "title found", "has title", "title ok"),
    "meta description": ("meta-description-present", "description found", "has meta description", "description ok"),
    "h1": ("h1-present", "h1 found", "has h1", "single h1", "h1 ok"),
    "schema": ("schema-present", "jsonld-present", "structured-data-present", "schema found", "valid schema"),
    "jsonld": ("jsonld-present", "schema-present", "json-ld found", "valid jsonld"),
    "structured data": ("structured-data-present", "schema-present", "schema found"),
    "robots": ("robots-present", "robots.txt found", "has robots"),
    "sitemap": ("sitemap-present", "sitemap found", "has sitemap"),
    "alt": ("alt-present", "alt text found", "images have alt", "all images alt"),
    "viewport": ("viewport-present", "viewport found", "has viewport", "viewport ok"),
    "hreflang": ("hreflang-present", "hreflang found", "has hreflang"),
    "lang": ("lang-present", "lang attribute found", "has lang"),
    "author": ("author-present", "byline found", "has author", "author found"),
    "og": ("og-present", "open-graph-present", "og tags found", "has open graph"),
}

# Tokens that, in an absence-claiming finding, introduce the missing concept.
_ABSENCE_TOKENS = ("missing", "no ", "absent", "not found", "lacks", "without",
                   "none ", "no-", "-missing", "missing-")


def _normalize_title(title):
    return "".join(ch for ch in (title or "").lower() if ch.isalnum())


def _key(d):
    return (str(d.get("id", "")).strip().lower()) + "|" + _normalize_title(d.get("title", ""))


def _union_detail(a, b):
    out = {}
    if isinstance(a, dict):
        out.update(a)
    if isinstance(b, dict):
        for k, v in b.items():
            if k not in out:
                out[k] = v
    return out


def _rebuild_finding(d):
    kw = {f: d[f] for f in _FINDING_FIELDS if f in d and d[f] is not None}
    kw.setdefault("id", str(d.get("id", "unknown")))
    kw.setdefault("title", str(d.get("title", "untitled")))
    kw.setdefault("severity", "medium")
    kw.setdefault("category", "technical")
    if not isinstance(kw.get("detail"), dict):
        kw["detail"] = {}
    return Finding(**kw)


def _load_envelopes(argv):
    """Yield finding-dict lists from argv files, or a single stdin envelope."""
    raw_blobs = []
    paths = [a for a in argv[1:] if not a.startswith("-")]
    if paths:
        for p in paths:
            try:
                with open(p, "r", encoding="utf-8") as fh:
                    raw_blobs.append((p, fh.read()))
            except Exception as e:
                raw_blobs.append((p, None))
                sys.stderr.write("warn: could not read %s: %s\n" % (p, e))
    else:
        data = sys.stdin.read() if not sys.stdin.isatty() else ""
        if data.strip():
            raw_blobs.append(("<stdin>", data))

    findings = []
    sources = 0
    meta = {}
    for label, blob in raw_blobs:
        if not blob:
            continue
        try:
            env = json.loads(blob)
        except Exception as e:
            sys.stderr.write("warn: malformed JSON in %s: %s\n" % (label, e))
            continue
        sources += 1
        if isinstance(env, dict):
            fs = env.get("findings")
            # Carry through the first envelope's meta (url/site) so a report
            # rendered from verifier output still knows what it audited.
            if not meta and isinstance(env.get("meta"), dict):
                meta = env["meta"]
        elif isinstance(env, list):
            fs = env
        else:
            fs = None
        if isinstance(fs, list):
            for f in fs:
                if isinstance(f, dict):
                    findings.append(f)
    return findings, sources, meta


def _dedupe(findings):
    """Merge by canonical key, keeping strongest severity and union of detail."""
    merged = {}
    for d in findings:
        k = _key(d)
        if k not in merged:
            merged[k] = dict(d)
            continue
        cur = merged[k]
        # Strongest severity wins; lower SEV_RANK index == stronger.
        if SEV_RANK.get(str(d.get("severity")), 99) < SEV_RANK.get(str(cur.get("severity")), 99):
            cur["severity"] = d.get("severity")
        cur["detail"] = _union_detail(cur.get("detail"), d.get("detail"))
        # Keep the richer evidence/impact/fix if the current one is empty.
        for fld in ("evidence", "impact", "fix"):
            if not str(cur.get(fld, "")).strip() and str(d.get(fld, "")).strip():
                cur[fld] = d[fld]
        merged[k] = cur
    return list(merged.values())


def _claims_absence(d):
    """Return the absence concept asserted by this finding, or None."""
    hay = (str(d.get("id", "")) + " " + str(d.get("title", ""))).lower()
    if not any(tok in hay for tok in _ABSENCE_TOKENS):
        return None
    for concept in _PRESENCE_HINTS:
        if concept in hay:
            return concept
    return None


def _shows_presence(d, concept):
    """True if this CONFIRMED finding demonstrates `concept` is present."""
    if str(d.get("confidence", "confirmed")).lower() != "confirmed":
        return False
    if _claims_absence(d):  # an absence-claim is not evidence of presence
        return False
    hay = (str(d.get("id", "")) + " " + str(d.get("title", "")) + " "
           + str(d.get("evidence", ""))).lower()
    for hint in _PRESENCE_HINTS.get(concept, ()):
        if hint in hay:
            return True
    return False


def _suppress_contradictions(findings):
    """Drop absence-claims contradicted by a confirmed presence finding."""
    survivors, suppressed = [], []
    for d in findings:
        concept = _claims_absence(d)
        if concept:
            contradictor = None
            for other in findings:
                if other is d:
                    continue
                if _shows_presence(other, concept):
                    contradictor = other
                    break
            if contradictor is not None:
                reason = ("Claims '%s' absent, but confirmed finding '%s' shows %s present."
                          % (concept, contradictor.get("id", "?"), concept))
                suppressed.append({"finding": d, "reason": reason})
                continue
        survivors.append(d)
    return survivors, suppressed


def verify(argv):
    findings, sources, meta = _load_envelopes(argv)
    deduped = _dedupe(findings)
    survivors, suppressed = _suppress_contradictions(deduped)

    objs = []
    for d in survivors:
        try:
            objs.append(_rebuild_finding(d))
        except Exception as e:
            sys.stderr.write("warn: skipped unrebuildable finding %s: %s\n" % (d.get("id"), e))

    s = seo_common.score(objs)
    return {
        "meta": meta,
        "verified_findings": [seo_common.asdict(o) for o in objs],
        "suppressed": suppressed,
        "score": s,
        "grade": seo_common.grade(s),
        "summary": {
            "input_sources": sources,
            "raw_findings": len(findings),
            "after_dedupe": len(deduped),
            "suppressed": len(suppressed),
            "verified": len(objs),
            "by_severity": {sev: sum(1 for o in objs if o.severity == sev)
                            for sev in seo_common.SEVERITY_ORDER},
        },
    }


if __name__ == "__main__":
    try:
        result = verify(sys.argv)
    except Exception as e:
        print(json.dumps({"error": "verification failed", "detail": str(e)}))
        sys.exit(2)
    print(json.dumps(result, indent=2, ensure_ascii=False))
