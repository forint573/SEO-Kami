#!/usr/bin/env python3
"""Deterministic hreflang / international-SEO validator.

Single-page mode (default, no extra network): validates the page's own
hreflang set — self-reference, x-default, malformed language codes, and
duplicate/conflicting entries. Emits nothing when a page declares no hreflang
(correct for single-language sites), so it is safe inside the orchestrator.

Reciprocity mode (`--reciprocal`, opt-in): fetches each alternate URL (capped,
SSRF-guarded) and checks it points BACK to this page — the "return tag" rule
Google requires. Network failures degrade to hypothesis findings, never crashes.

The hreflang correctness rules are Google's documented spec (PROVEN); the
re-implementation as a deterministic check is SEO-Kami's, anticipated in
NOTICE.md (hreflang reciprocity, re-authored from seo-audit-skill's i18n rules;
the multilingual workflow idea was also informed by SearchFit — design ref only).
"""
import sys
import os
import re
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import seo_common
from seo_common import Page, Finding, emit, arg_url
from lib import safe_http, sanitize

RECIPROCAL_CAP = 12  # max alternate pages fetched in reciprocity mode
# valid: "x-default", or ll / ll-RR — ISO 639-1 lang + optional region that is
# either an ISO 3166-1 alpha-2 code (en-GB) or a UN M.49 numeric code (es-419).
# Google supports both; it does NOT use script subtags (zh-Hant) in hreflang.
LANG_RE = re.compile(r"^[a-z]{2,3}(-(?:[A-Za-z]{2}|[0-9]{3}))?$")


def _norm(u):
    return (u or "").split("#")[0].rstrip("/").lower()


def _self_refs(page):
    """URLs that count as 'this page' for self-reference purposes."""
    s = {_norm(page.url)}
    if page.canonical:
        s.add(_norm(page.canonical))
    return {x for x in s if x}


def collect(url, page=None, reciprocal=False):
    page = page or Page.fetch(url)
    _gate = seo_common.audit_gate(page)
    if _gate is not None:
        return [_gate]
    entries = page.hreflang or []
    findings = []

    # No hreflang at all -> nothing to validate. (Correct for monolingual sites.)
    if not entries:
        return findings

    selves = _self_refs(page)
    langs = [e.get("lang", "") for e in entries]
    hrefs = [e.get("href", "") for e in entries]

    # (1) self-reference -------------------------------------------------
    has_self = any(_norm(h) in selves for h in hrefs)
    if not has_self:
        findings.append(Finding(
            id="hreflang.no_self_reference",
            title="hreflang set is missing a self-referencing entry",
            severity="medium", category="technical",
            evidence="Page declares %d hreflang alternate(s) but none point back to this page (%s)."
                     % (len(entries), page.canonical or page.url),
            impact="Google requires every page in an hreflang group to include a self-referential hreflang. Without it the cluster can be ignored, collapsing your localized variants in search.",
            fix="Add a <link rel=\"alternate\" hreflang=\"<this page's lang>\" href=\"<this canonical URL>\"> entry to the set.",
            confidence="confirmed", evidence_tier="proven",
            detail={"alternates": len(entries)}))

    # (2) x-default ------------------------------------------------------
    if not any((l or "").lower() == "x-default" for l in langs):
        findings.append(Finding(
            id="hreflang.no_x_default",
            title="hreflang set has no x-default",
            severity="low", category="technical",
            evidence="No hreflang=\"x-default\" entry among %d alternate(s)." % len(entries),
            impact="x-default tells engines which page to serve users whose language/region you do not explicitly target; without it those users may get a mismatched localized page.",
            fix="Add <link rel=\"alternate\" hreflang=\"x-default\" href=\"<your default/selector page>\">.",
            confidence="confirmed", evidence_tier="proven",
            detail={}))

    # (3) malformed language codes --------------------------------------
    bad = [l for l in langs if (l or "").lower() != "x-default" and not LANG_RE.match(l or "")]
    if bad:
        findings.append(Finding(
            id="hreflang.malformed_codes",
            title="Malformed hreflang language code(s)",
            severity="medium", category="technical",
            evidence="Invalid value(s): " + ", ".join(repr(b) for b in bad[:8])
                     + (" …" if len(bad) > 8 else "") + ". Expected ISO 639-1 lang or lang-REGION (e.g. en, ro, en-GB) or x-default.",
            impact="Engines ignore hreflang entries with unparseable codes, breaking the affected localized links.",
            fix="Use a valid language (ISO 639-1) optionally with an ISO 3166-1 region: en, ro, pt-BR, en-GB, x-default. Do not invent codes like 'en-UK' (use en-GB).",
            confidence="confirmed", evidence_tier="proven",
            detail={"invalid": bad}))

    # (4) duplicate lang pointing to different URLs ----------------------
    by_lang = {}
    for e in entries:
        by_lang.setdefault((e.get("lang") or "").lower(), set()).add(_norm(e.get("href")))
    conflicts = {l: sorted(u) for l, u in by_lang.items() if len(u) > 1}
    if conflicts:
        findings.append(Finding(
            id="hreflang.conflicting_targets",
            title="Same hreflang value points to multiple URLs",
            severity="medium", category="technical",
            evidence="Conflicting: " + "; ".join("%s -> %d URLs" % (l, len(u)) for l, u in conflicts.items()),
            impact="When one hreflang value maps to several URLs, Google cannot resolve the cluster and may drop it entirely.",
            fix="Ensure each hreflang value maps to exactly one URL across the whole set.",
            confidence="confirmed", evidence_tier="proven",
            detail={"conflicts": conflicts}))

    # (5) reciprocity (opt-in; needs network) ----------------------------
    if reciprocal:
        findings.extend(_check_reciprocity(page, entries, selves))

    return findings


def _check_reciprocity(page, entries, selves):
    findings = []
    targets = []
    seen = set()
    for e in entries:
        lang = (e.get("lang") or "").lower()
        href = e.get("href") or ""
        if lang == "x-default":
            continue
        n = _norm(href)
        if not n or n in selves or n in seen:
            continue
        seen.add(n)
        targets.append(href)
    if not targets:
        return findings

    capped = targets[:RECIPROCAL_CAP]
    non_reciprocal, unreachable = [], []
    for t in capped:
        try:
            alt = Page.fetch(t)
            back = {_norm(h.get("href")) for h in (alt.hreflang or [])}
            if not (selves & back):
                non_reciprocal.append(t)
        except safe_http.UnsafeURLError as ex:
            unreachable.append((t, "blocked: %s" % ex))
        except Exception as ex:
            unreachable.append((t, str(ex)[:80]))

    if non_reciprocal:
        findings.append(Finding(
            id="hreflang.non_reciprocal",
            title="hreflang link(s) are not reciprocated (missing return tag)",
            severity="high", category="technical",
            evidence="%d alternate(s) do not link back to this page: %s"
                     % (len(non_reciprocal), ", ".join(non_reciprocal[:6]) + (" …" if len(non_reciprocal) > 6 else "")),
            impact="hreflang is bidirectional: if page A points to B but B does not point back to A, Google discards the annotation. Non-reciprocal links silently break localization.",
            fix="On each alternate page, add a return hreflang entry pointing back to this page's canonical URL.",
            confidence="confirmed", evidence_tier="proven",
            detail={"non_reciprocal": non_reciprocal,
                    "checked": len(capped), "total_targets": len(targets)}))
    if unreachable:
        findings.append(Finding(
            id="hreflang.reciprocity_uncheckable",
            title="Some hreflang alternates could not be fetched to verify reciprocity",
            severity="info", category="technical",
            evidence="; ".join("%s (%s)" % (u, why) for u, why in unreachable[:6]),
            impact="Reciprocity could not be confirmed for these alternates.",
            fix="Re-run with network access, or verify the return tags manually.",
            confidence="hypothesis", evidence_tier="proven",
            detail={"unreachable": [u for u, _ in unreachable]}))
    if len(targets) > RECIPROCAL_CAP:
        findings.append(Finding(
            id="hreflang.reciprocity_capped",
            title="Reciprocity check sampled a subset of alternates",
            severity="info", category="technical",
            evidence="Checked %d of %d alternate URLs (cap=%d)." % (RECIPROCAL_CAP, len(targets), RECIPROCAL_CAP),
            impact="Some alternates beyond the cap were not verified.",
            fix="Run hreflang_check.py per language group, or raise RECIPROCAL_CAP.",
            confidence="confirmed", evidence_tier="proven", detail={}))
    return findings


if __name__ == "__main__":
    url = arg_url(sys.argv)
    recip = "--reciprocal" in sys.argv
    try:
        emit(collect(url, reciprocal=recip),
             meta={"url": url, "check": "hreflang_check", "reciprocal": recip})
    except safe_http.UnsafeURLError as e:
        print(json.dumps({"error": "unsafe_url", "detail": str(e)}))
        sys.exit(2)
    except Exception as e:
        print(json.dumps({"error": "hreflang_check_failed", "detail": str(e)}))
        sys.exit(2)
