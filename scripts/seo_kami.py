#!/usr/bin/env python3
"""SEO-Kami orchestrator.

Fetches the page ONCE, runs every audit collector against it, merges and
de-duplicates the findings (keeping the strongest severity; via the shared
seo_common.merge_findings), scores, and prints a single combined envelope — or a
finished report with --report.

Usage:
    python3 seo_kami.py https://example.com [--report md|html] [--out FILE] [--no-cwv] [--no-links]

Each audit module follows the contract: a module-level
`collect(url, page=None) -> list[Finding]`. The page-based collectors share one
fetched Page so the site is hit once; cwv_check fetches its own field data.
"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import seo_common
from seo_common import Page, Finding, emit, arg_url
from lib import safe_http

# (module name, needs the shared Page object)
PAGE_COLLECTORS = [
    ("technical_audit", True),
    ("schema_check", True),
    ("geo_aeo_scan", True),
    ("entity_check", True),
    ("links_audit", True),
    ("hreflang_check", True),  # single-page mode; silent when no hreflang declared
]
NETWORK_COLLECTORS = [
    ("cwv_check", False),
]


def _run_collector(modname: str, url: str, page):
    """Import and run one collector, swallowing its failures into a finding."""
    try:
        mod = __import__(modname)
    except Exception as exc:  # a missing/broken module shouldn't kill the audit
        return [Finding(
            id=f"{modname}-unavailable", title=f"{modname} could not be loaded",
            severity="info", category="technical",
            evidence=f"import error: {exc}", impact="That check was skipped.",
            fix=f"Inspect scripts/{modname}.py", confidence="confirmed",
            evidence_tier="proven")]
    fn = getattr(mod, "collect", None)
    if not callable(fn):
        return []
    try:
        return list(fn(url, page) if page is not None else fn(url)) or []
    except TypeError:
        # collector that doesn't take a page (e.g. cwv_check)
        try:
            return list(fn(url)) or []
        except Exception as exc:
            return [_skip(modname, exc)]
    except safe_http.UnsafeURLError as exc:
        raise
    except Exception as exc:
        return [_skip(modname, exc)]


def _skip(modname: str, exc: Exception) -> Finding:
    return Finding(
        id=f"{modname}-error", title=f"{modname} did not complete",
        severity="info", category="technical", evidence=str(exc),
        impact="That dimension was skipped.", fix="Re-run the individual script to debug.",
        confidence="confirmed", evidence_tier="proven")


def collect_all(url, no_cwv=False, no_links=False):
    try:
        page = Page.fetch(url)
    except safe_http.UnsafeURLError as exc:
        print(json.dumps({"error": "unsafe_url", "detail": str(exc)}))
        sys.exit(2)
    except Exception as exc:
        print(json.dumps({"error": "fetch_failed", "detail": str(exc)}))
        sys.exit(2)

    # Gate: if the response isn't a real 200 HTML page, don't audit it — one
    # honest finding beats a page of fictional ones from a 403/JSON/PDF.
    gate = seo_common.audit_gate(page)
    if gate is not None:
        return page, [gate]

    findings = []
    for modname, _ in PAGE_COLLECTORS:
        if no_links and modname == "links_audit":
            continue
        findings.extend(_run_collector(modname, url, page))
    if not no_cwv:
        for modname, _ in NETWORK_COLLECTORS:
            findings.extend(_run_collector(modname, url, None))
    return page, seo_common.merge_findings(findings)


def _flag(argv, name):
    """--name VALUE -> 'VALUE'; bare --name -> True; absent -> None."""
    if name in argv:
        i = argv.index(name)
        if i + 1 < len(argv) and not argv[i + 1].startswith("-"):
            return argv[i + 1]
        return True
    return None


def main():
    url = arg_url(sys.argv)
    no_cwv = "--no-cwv" in sys.argv
    no_links = "--no-links" in sys.argv
    report_fmt = _flag(sys.argv, "--report")
    if report_fmt is True:
        report_fmt = "md"
    out_path = _flag(sys.argv, "--out")
    date = _flag(sys.argv, "--date") or "{{date}}"

    page, findings = collect_all(url, no_cwv=no_cwv, no_links=no_links)
    auditable = not (len(findings) == 1 and str(findings[0].id).startswith("page.not_auditable"))
    meta = {
        "url": url,
        "final_url": page.url,
        "status": page.status,
        "auditable": auditable,
        "tool": "seo-kami orchestrator",
        "checks": [m for m, _ in PAGE_COLLECTORS] + ([] if no_cwv else [m for m, _ in NETWORK_COLLECTORS]),
    }

    # One command to a finished report: collect_all already merges + dedupes, so
    # `--report` renders the deliverable directly — no separate verify/report step.
    # An un-auditable page (gated) has no meaningful score — report N/A, never a
    # letter grade that looks like a pass.
    s = seo_common.score(findings) if auditable else None
    g = seo_common.grade(s) if auditable else "N/A"
    if report_fmt:
        import report_build
        fdicts = [seo_common.asdict(f) for f in findings]
        md = report_build.build_markdown(meta, s, g, fdicts, date if isinstance(date, str) else "{{date}}")
        content = report_build.md_to_html(md, "SEO-Kami Audit") if str(report_fmt).lower() == "html" else md
        if isinstance(out_path, str):
            with open(out_path, "w", encoding="utf-8") as fh:
                fh.write(content)
            print(json.dumps({"ok": True, "written": out_path, "format": report_fmt,
                              "score": s, "grade": g, "findings": len(fdicts)}, ensure_ascii=False))
        else:
            print(content)
    else:
        emit(findings, meta=meta, scored=auditable)


if __name__ == "__main__":
    main()
