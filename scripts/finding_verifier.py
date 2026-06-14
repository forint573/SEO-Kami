#!/usr/bin/env python3
"""Dedupe + re-score findings across one or more emit() envelopes.

Merges the findings from any number of envelopes (or a single one on stdin) into
one deduplicated, re-scored set. Dedupe is the shared `seo_common.merge_findings`
(strongest severity wins; detail unioned; empty evidence/impact/fix back-filled),
so the orchestrator and this tool can never drift apart.

(A previous version also tried to "suppress" findings contradicted by a measured
one. That machinery was provably inert — collectors emit an absence finding XOR a
presence finding, never both, so there was never a contradiction to suppress —
and was removed. Collector-level consistency already prevents that bug class.)
"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import seo_common
from seo_common import Finding

_FINDING_FIELDS = ("id", "title", "severity", "category", "evidence",
                   "impact", "fix", "confidence", "evidence_tier", "detail")


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
    """Collect finding-dicts from argv files, or a single stdin envelope."""
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

    findings, sources, meta = [], 0, {}
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
            if not meta and isinstance(env.get("meta"), dict):
                meta = env["meta"]  # carry url/site through to a rendered report
        elif isinstance(env, list):
            fs = env
        else:
            fs = None
        if isinstance(fs, list):
            findings.extend([f for f in fs if isinstance(f, dict)])
    return findings, sources, meta


def verify(argv):
    findings, sources, meta = _load_envelopes(argv)
    objs = []
    for d in findings:
        try:
            objs.append(_rebuild_finding(d))
        except Exception as e:
            sys.stderr.write("warn: skipped unrebuildable finding %s: %s\n" % (d.get("id"), e))
    merged = seo_common.merge_findings(objs)
    s = seo_common.score(merged)
    return {
        "meta": meta,
        "verified_findings": [seo_common.asdict(o) for o in merged],
        "score": s,
        "grade": seo_common.grade(s),
        "summary": {
            "input_sources": sources,
            "raw_findings": len(findings),
            "verified": len(merged),
            "by_severity": {sev: sum(1 for o in merged if o.severity == sev)
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
