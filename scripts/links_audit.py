#!/usr/bin/env python3
"""Audit internal/external link health: anchors, rel usage, orphan risk, broken-link sample."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import seo_common
from seo_common import Page, Finding, emit, arg_url
from lib import safe_http, sanitize

GENERIC_ANCHORS = {"click here", "read more", "here", "link", "this", "more",
                   "learn more", "click", "go", "this page", "read"}
HEAD_CAP = 12  # politeness cap on broken-link probes


def collect(url, page=None):
    page = page or Page.fetch(url)
    _gate = seo_common.audit_gate(page)
    if _gate is not None:
        return [_gate]
    findings = []
    links = page.links or []

    internal = [l for l in links if l.get("internal")]
    external = [l for l in links if not l.get("internal")]
    n_int, n_ext = len(internal), len(external)

    # --- Orphan risk: zero internal links ---
    if n_int == 0:
        findings.append(Finding(
            id="links.no_internal",
            title="No internal links on the page",
            severity="high",
            category="links",
            evidence=f"{n_int} internal links, {n_ext} external links found.",
            impact="Pages with no internal links are orphan-risk: crawlers and PageRank flow "
                   "cannot reach deeper pages, hurting indexability and discovery.",
            fix="Add contextual internal links to related pages, hubs, and navigation so this page "
                "participates in the site's link graph.",
            confidence="confirmed",
            evidence_tier="proven",
            detail={"internal": n_int, "external": n_ext},
        ))

    # --- Generic anchor text ---
    generic_hits = []
    for l in links:
        text = (l.get("text") or "").strip()
        if text.lower() in GENERIC_ANCHORS:
            generic_hits.append({"anchor": sanitize.strip_invisible(text), "href": l.get("href")})
    if generic_hits:
        sample = generic_hits[:10]
        anchors_preview = ", ".join(sorted({h["anchor"] for h in sample}))
        findings.append(Finding(
            id="links.generic_anchors",
            title=f"{len(generic_hits)} link(s) use generic anchor text",
            severity="low",
            category="links",
            evidence=sanitize.wrap_untrusted(
                f"Generic anchors found: {anchors_preview}", "page anchor text"),
            impact="Generic anchors ('click here', 'read more') give crawlers and users no topical "
                   "context about the destination, weakening relevance signals and accessibility.",
            fix="Rewrite anchors to describe the destination page (use the target's topic/keyword).",
            confidence="confirmed",
            evidence_tier="proven",
            detail={"count": len(generic_hits), "anchors": sample},
        ))

    # --- rel usage summary (info) ---
    rel_counts = {"nofollow": 0, "sponsored": 0, "ugc": 0, "noopener": 0, "noreferrer": 0}
    for l in links:
        rel = (l.get("rel") or "").lower()
        for token in rel.split():
            if token in rel_counts:
                rel_counts[token] += 1
    if any(rel_counts[k] for k in ("nofollow", "sponsored", "ugc")):
        findings.append(Finding(
            id="links.rel_usage",
            title="rel attribute usage summary",
            severity="info",
            category="links",
            evidence=f"nofollow={rel_counts['nofollow']}, sponsored={rel_counts['sponsored']}, "
                     f"ugc={rel_counts['ugc']} across {len(links)} links.",
            impact="rel=sponsored/ugc/nofollow communicate link relationships to Google; misuse can "
                   "leak or wrongly suppress link equity.",
            fix="Use rel=sponsored for paid links, rel=ugc for user-generated content, and nofollow "
                "sparingly. Verify each matches the actual link context.",
            confidence="confirmed",
            evidence_tier="proven",
            detail=dict(rel_counts),
        ))

    # --- external links missing rel (informational) ---
    ext_no_rel = [l for l in external if not (l.get("rel") or "").strip()]
    if ext_no_rel:
        findings.append(Finding(
            id="links.external_no_rel",
            title=f"{len(ext_no_rel)} external link(s) have no rel attribute",
            severity="info",
            category="links",
            evidence=f"{len(ext_no_rel)} of {n_ext} external links carry no rel attribute.",
            impact="On user-content surfaces (comments, forums, profiles), external links without "
                   "rel=ugc/nofollow can be exploited for spam and may pass unintended equity. On "
                   "editorial pages, plain external links are normal.",
            fix="If this page hosts user-generated content, add rel=ugc (or nofollow) to external "
                "links. On editorial content, no action is needed.",
            confidence="likely",
            evidence_tier="consensus",
            detail={"count": len(ext_no_rel),
                    "sample": [l.get("href") for l in ext_no_rel[:10]]},
        ))

    # --- Broken-link SAMPLE: up to HEAD_CAP unique links, prefer internal ---
    seen, sample = set(), []
    for l in internal + external:  # internal first
        href = l.get("href")
        if not href or not href.lower().startswith(("http://", "https://")):
            continue
        if href in seen:
            continue
        seen.add(href)
        sample.append(href)
        if len(sample) >= HEAD_CAP:
            break

    probed = 0
    for href in sample:
        probed += 1
        try:
            resp = safe_http.head(href)
            status = getattr(resp, "status", None)
            if isinstance(status, int) and 400 <= status < 600:
                findings.append(Finding(
                    id="links.broken",
                    title=f"Broken link returns HTTP {status}",
                    severity="medium",
                    category="links",
                    evidence=f"{href} -> HTTP {status}",
                    impact="Broken links waste crawl budget, frustrate users, and bleed link equity "
                           "into dead ends, weakening the page's perceived quality.",
                    fix="Fix the URL, restore the target, or remove/redirect the link to a live page.",
                    confidence="confirmed",
                    evidence_tier="proven",
                    detail={"url": href, "status": status},
                ))
        except safe_http.UnsafeURLError as e:
            findings.append(Finding(
                id="links.unsafe_url",
                title="Link points to an unsafe/blocked URL",
                severity="medium",
                category="links",
                evidence=f"{href} rejected: {e}",
                impact="The link resolves to a private/loopback/blocked address (SSRF risk) or an "
                       "otherwise unsafe target that real crawlers and users cannot follow.",
                fix="Remove or replace the link with a public, safe destination.",
                confidence="confirmed",
                evidence_tier="proven",
                detail={"url": href, "reason": str(e)},
            ))
        except Exception as e:
            # Network/timeout errors are not conclusive broken-link evidence; report as hypothesis.
            findings.append(Finding(
                id="links.probe_error",
                title="Link could not be verified",
                severity="info",
                category="links",
                evidence=f"{href}: {type(e).__name__}: {e}",
                impact="The link could not be reached during this probe (timeout/DNS/connection). "
                       "It may be broken or may simply block automated HEAD requests.",
                fix="Manually verify this URL in a browser; if dead, fix, redirect, or remove it.",
                confidence="hypothesis",
                evidence_tier="speculative",
                detail={"url": href, "error": f"{type(e).__name__}: {e}"},
            ))

    return findings


if __name__ == "__main__":
    try:
        url = arg_url(sys.argv)
        if not url:
            print(json.dumps({"error": "missing_url",
                              "detail": "Provide a URL to audit links_audit."}))
            sys.exit(2)
        emit(collect(url), meta={
            "url": url,
            "check": "links_audit",
            "head_cap": HEAD_CAP,
            "note": f"Broken-link probe capped at {HEAD_CAP} unique links (internal first) to stay polite.",
        })
    except safe_http.UnsafeURLError as e:
        print(json.dumps({"error": "unsafe_url", "detail": str(e)}))
        sys.exit(2)
    except Exception as e:
        print(json.dumps({"error": "links_audit_failed", "detail": f"{type(e).__name__}: {e}"}))
        sys.exit(2)
