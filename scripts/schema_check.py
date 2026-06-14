#!/usr/bin/env python3
"""Structured-data (JSON-LD) audit: parse errors, required props, deprecated rich-result types."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import seo_common
from seo_common import Page, Finding, emit, arg_url
from lib import safe_http, sanitize

# Required properties per known @type (built-in, no external fetch).
# Hard-required properties (missing one forfeits rich-result eligibility).
# Kept in lockstep with references/schema-2026.md "Required properties".
REQUIRED = {
    "Organization": ["name", "url"],
    "Article": ["headline"],
    "Product": ["name", "image"],
    "Review": ["itemReviewed", "reviewRating", "author"],
    "AggregateRating": ["itemReviewed", "ratingValue"],
    "Recipe": ["name", "image"],
    "LocalBusiness": ["name", "address"],
    "Person": ["name"],
    "BreadcrumbList": ["itemListElement"],
    "VideoObject": ["name", "description", "thumbnailUrl", "uploadDate"],
    "Event": ["name", "startDate", "location"],
}

# Strongly-recommended properties (missing = weaker/richer result, not invalid).
RECOMMENDED = {
    "Article": ["image", "datePublished", "author"],
    "Product": ["offers"],
    "Organization": ["logo", "sameAs"],
    "Person": ["url", "sameAs"],
    "LocalBusiness": ["telephone"],
    "Recipe": ["recipeIngredient", "recipeInstructions"],
}

# Rich-result types removed/unsupported in 2026 (PROVEN). Markup stays valid; no enhancement.
DEPRECATED_RICH = {
    "FAQPage": "FAQPage rich results removed ~2026-05-07 (still shown only for authoritative gov/health).",
    "HowTo": "HowTo rich results discontinued on all surfaces.",
}


def _types(block):
    """Return a list of @type strings for a JSON-LD block (handles str or list)."""
    t = block.get("@type")
    if t is None:
        return []
    if isinstance(t, list):
        return [str(x) for x in t]
    return [str(t)]


def _short(obj, limit=160):
    try:
        s = json.dumps(obj, ensure_ascii=False)
    except Exception:
        s = str(obj)
    return s if len(s) <= limit else s[:limit] + "..."


def collect(url, page=None):
    page = page or Page.fetch(url)
    findings = []
    blocks = page.jsonld or []

    # No structured data at all.
    if not blocks:
        microdata = "itemscope" in (page.html or "").lower()
        evid = "No <script type=\"application/ld+json\"> blocks found in the HTML."
        if microdata:
            evid += " Microdata (itemscope) detected instead."
        findings.append(Finding(
            id="schema-none",
            title="No JSON-LD structured data on page",
            severity="medium",
            category="schema",
            evidence=evid,
            impact="Eligible rich results (Product, Article, Breadcrumb, Organization, etc.) cannot be earned without structured data, reducing SERP real estate and clarity for parsers.",
            fix="Add a JSON-LD block describing the primary entity on this page (e.g. Organization on the homepage, Article on posts, Product on product pages). Validate with Google's Rich Results Test.",
            confidence="confirmed",
            evidence_tier="proven",
            detail={"jsonld_blocks": 0, "microdata_detected": microdata},
        ))
        # Schema is not an AI-feature requirement — say so honestly.
        findings.append(Finding(
            id="schema-not-ai-requirement",
            title="Structured data is not required for AI features",
            severity="info",
            category="schema",
            evidence="Google's 2026 AI-optimization guidance states no special schema markup is needed for AI Overviews or AI Mode; they use the same index and quality systems as classic search.",
            impact="Adding schema 'for AI' yields no citation lift. Schema's value is classic SERP rich results, not generative-answer visibility.",
            fix="Add schema where it earns rich results; do not add it expecting AI-citation gains. Prioritize crawlable, people-first content for AI features.",
            confidence="confirmed",
            evidence_tier="proven",
            detail={},
        ))
        return findings

    # Parse + validate each block.
    seen_types = []
    for i, block in enumerate(blocks):
        if isinstance(block, dict) and block.get("_parse_error"):
            raw = block.get("_raw", "")
            findings.append(Finding(
                id=f"schema-parse-error-{i}",
                title="JSON-LD block failed to parse",
                severity="high",
                category="schema",
                evidence="Invalid JSON in block #%d: %s" % (i + 1, sanitize.wrap_untrusted(_short(raw), "jsonld")),
                impact="Malformed JSON-LD is ignored entirely by Google, so any rich-result eligibility it was meant to provide is lost.",
                fix="Fix the JSON syntax (trailing commas, unescaped quotes, missing braces) and re-validate with the Rich Results Test.",
                confidence="confirmed",
                evidence_tier="proven",
                detail={"block_index": i},
            ))
            continue
        if not isinstance(block, dict):
            continue

        types = _types(block)
        seen_types.extend(types)

        for t in types:
            # Required-property checks for known types.
            if t in REQUIRED:
                for prop in REQUIRED[t]:
                    if prop not in block or block.get(prop) in (None, "", []):
                        findings.append(Finding(
                            id="schema-missing-%s-%s-%d" % (t.lower(), prop.lower(), i),
                            title="%s missing required property '%s'" % (t, prop),
                            severity="medium",
                            category="schema",
                            evidence="Block #%d (@type=%s) lacks required property '%s'." % (i + 1, t, prop),
                            impact="Google may treat the %s markup as invalid or incomplete, disqualifying it from the corresponding rich result." % t,
                            fix="Add the '%s' property to the %s block with an accurate value." % (prop, t),
                            confidence="confirmed",
                            evidence_tier="proven",
                            detail={"type": t, "missing": prop, "block_index": i},
                        ))
            # Recommended-property checks (lower severity than required).
            if t in RECOMMENDED:
                for prop in RECOMMENDED[t]:
                    if prop not in block or block.get(prop) in (None, "", []):
                        findings.append(Finding(
                            id="schema-recommended-%s-%s-%d" % (t.lower(), prop.lower(), i),
                            title="%s missing recommended property '%s'" % (t, prop),
                            severity="low",
                            category="schema",
                            evidence="Block #%d (@type=%s) omits recommended property '%s'." % (i + 1, t, prop),
                            impact="The %s markup stays valid but yields a less complete/rich result than it could." % t,
                            fix="Add '%s' to the %s block to strengthen the rich result and entity signals." % (prop, t),
                            confidence="confirmed",
                            evidence_tier="proven",
                            detail={"type": t, "missing": prop, "block_index": i, "level": "recommended"},
                        ))
            # Deprecated rich-result types.
            if t in DEPRECATED_RICH:
                findings.append(Finding(
                    id="schema-deprecated-%s-%d" % (t.lower(), i),
                    title="%s markup earns no rich result in 2026" % t,
                    severity="low" if t == "HowTo" else "info",
                    category="schema",
                    evidence="%s found in block #%d. %s Valid markup, no rich result in 2026 — not an error, just no enhancement." % (t, i + 1, DEPRECATED_RICH[t]),
                    impact="This markup is harmless but yields zero SERP enhancement; keeping or removing it causes no ranking change.",
                    fix="Optional: remove the %s block to reduce page weight, or keep it (no penalty). Do not add it expecting rich results." % t,
                    confidence="confirmed",
                    evidence_tier="proven",
                    detail={"type": t, "block_index": i},
                ))

    # Recommend JSON-LD if the page also uses microdata.
    if "itemscope" in (page.html or "").lower():
        findings.append(Finding(
            id="schema-microdata-detected",
            title="Microdata detected — migrate to JSON-LD",
            severity="low",
            category="schema",
            evidence="Found 'itemscope' attribute(s) in the HTML, indicating inline microdata markup.",
            impact="Microdata is harder to maintain and more error-prone than JSON-LD; Google recommends JSON-LD as the preferred format.",
            fix="Re-express structured data as JSON-LD <script> blocks and remove inline itemscope/itemprop attributes.",
            confidence="confirmed",
            evidence_tier="proven",
            detail={"types_seen": sorted(set(seen_types))},
        ))

    return findings


if __name__ == "__main__":
    url = arg_url(sys.argv)
    try:
        emit(collect(url), meta={"url": url, "check": "schema_check"})
    except safe_http.UnsafeURLError as e:
        print(json.dumps({"error": "unsafe_url", "detail": str(e)}))
        sys.exit(2)
    except Exception as e:
        print(json.dumps({"error": "schema_check_failed", "detail": str(e)}))
        sys.exit(2)
