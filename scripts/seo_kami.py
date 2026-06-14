#!/usr/bin/env python3
"""SEO-Kami orchestrator.

Fetches the page ONCE, runs every audit collector against it, merges and
de-duplicates the findings (keeping the strongest severity and suppressing a
claim contradicted by a measured one), and prints a single combined envelope.

Usage:
    python3 seo_kami.py https://example.com [--no-cwv] [--no-links]

Each audit module follows the contract: a module-level
`collect(url, page=None) -> list[Finding]`. The page-based collectors share one
fetched Page so the site is hit once; cwv_check fetches its own field data.
"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import seo_common
from seo_common import Page, Finding, emit, arg_url, SEVERITY_ORDER
from lib import safe_http

# (module name, needs the shared Page object)
PAGE_COLLECTORS = [
    ("technical_audit", True),
    ("schema_check", True),
    ("geo_aeo_scan", True),
    ("entity_check", True),
    ("links_audit", True),
]
NETWORK_COLLECTORS = [
    ("cwv_check", False),
]


def _normalize(title: str) -> str:
    return "".join(ch for ch in (title or "").lower() if ch.isalnum())


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


def merge(findings):
    """Dedupe by (id, normalized title); keep the strongest severity."""
    best = {}
    for f in findings:
        key = f"{f.id}|{_normalize(f.title)}"
        cur = best.get(key)
        if cur is None or SEVERITY_ORDER.index(f.severity) < SEVERITY_ORDER.index(cur.severity):
            best[key] = f
    return list(best.values())


def collect_all(url, no_cwv=False, no_links=False):
    try:
        page = Page.fetch(url)
    except safe_http.UnsafeURLError as exc:
        print(json.dumps({"error": "unsafe_url", "detail": str(exc)}))
        sys.exit(2)
    except Exception as exc:
        print(json.dumps({"error": "fetch_failed", "detail": str(exc)}))
        sys.exit(2)

    findings = []
    for modname, _ in PAGE_COLLECTORS:
        if no_links and modname == "links_audit":
            continue
        findings.extend(_run_collector(modname, url, page))
    if not no_cwv:
        for modname, _ in NETWORK_COLLECTORS:
            findings.extend(_run_collector(modname, url, None))
    return page, merge(findings)


def main():
    url = arg_url(sys.argv)
    no_cwv = "--no-cwv" in sys.argv
    no_links = "--no-links" in sys.argv
    page, findings = collect_all(url, no_cwv=no_cwv, no_links=no_links)
    emit(findings, meta={
        "url": url,
        "final_url": page.url,
        "status": page.status,
        "tool": "seo-kami orchestrator",
        "checks": [m for m, _ in PAGE_COLLECTORS] + ([] if no_cwv else [m for m, _ in NETWORK_COLLECTORS]),
    })


if __name__ == "__main__":
    main()
