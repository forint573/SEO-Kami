#!/usr/bin/env python3
"""On-page + indexability technical SEO audit (title, meta, headings, canonical, robots, mixed-content)."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import seo_common
from seo_common import Page, Finding, emit, arg_url
from lib import safe_http, sanitize

import re
from urllib.parse import urlparse, urljoin


def _q(s, n=120):
    """Safely quote a value from the page for use as evidence."""
    if s is None:
        return ""
    s = sanitize.strip_invisible(str(s)).strip()
    s = re.sub(r"\s+", " ", s)
    return s[:n] + ("..." if len(s) > n else "")


def collect(url, page=None):
    findings = []
    page = page or Page.fetch(url)
    is_https = urlparse(page.url or url or "").scheme == "https"

    # --- Title ---
    title = page.title
    if not title or not title.strip():
        findings.append(Finding(
            "title-missing", "Page has no <title>", "high", "technical",
            evidence="No non-empty <title> element found in the page <head>.",
            impact="Title is the primary clickable headline in SERPs and a strong relevance signal; without it Google may synthesize a weak title.",
            fix="Add a unique, descriptive <title> of roughly 10-60 characters reflecting the page's primary intent.",
            confidence="confirmed", evidence_tier="proven"))
    else:
        tl = len(title.strip())
        if tl > 60:
            findings.append(Finding(
                "title-too-long", "Title likely truncated in SERPs", "low", "technical",
                evidence=f"Title is {tl} characters: \"{_q(title)}\".",
                impact="Titles over ~60 characters are often truncated in desktop SERPs, hiding the end of the message.",
                fix="Tighten the title to about 50-60 characters and front-load the primary keyword/intent.",
                confidence="likely", evidence_tier="consensus"))
        elif tl < 10:
            findings.append(Finding(
                "title-too-short", "Title is very short", "low", "technical",
                evidence=f"Title is only {tl} characters: \"{_q(title)}\".",
                impact="Very short titles waste SERP real estate and rarely capture the page's full intent or modifiers.",
                fix="Expand the title to about 50-60 characters with the primary topic and a distinguishing qualifier.",
                confidence="likely", evidence_tier="consensus"))

    # --- Meta description ---
    md = page.meta_description
    if not md or not md.strip():
        findings.append(Finding(
            "meta-desc-missing", "Meta description is missing", "low", "technical",
            evidence="No <meta name=\"description\"> with content was found.",
            impact="Without a description, Google auto-generates the SERP snippet, reducing control over click-through messaging.",
            fix="Add a 120-160 character meta description summarizing the page intent with a clear value proposition.",
            confidence="confirmed", evidence_tier="proven"))
    else:
        dl = len(md.strip())
        if dl > 160:
            findings.append(Finding(
                "meta-desc-too-long", "Meta description likely truncated", "low", "technical",
                evidence=f"Meta description is {dl} characters: \"{_q(md)}\".",
                impact="Descriptions over ~160 characters get truncated, cutting off the call to action in the snippet.",
                fix="Trim the description to about 120-160 characters and lead with the key benefit.",
                confidence="likely", evidence_tier="consensus"))

    # --- H1 ---
    h1s = page.h1s or []
    if len(h1s) == 0:
        findings.append(Finding(
            "h1-missing", "Page has no H1", "medium", "technical",
            evidence="No <h1> element was found in the rendered HTML.",
            impact="The H1 is the main on-page heading signaling the page topic to users and search engines.",
            fix="Add exactly one <h1> that states the page's primary subject.",
            confidence="confirmed", evidence_tier="proven"))
    elif len(h1s) > 1:
        findings.append(Finding(
            "h1-multiple", "Multiple H1 headings", "medium", "technical",
            evidence=f"Found {len(h1s)} <h1> elements, e.g. \"{_q(h1s[0])}\" / \"{_q(h1s[1])}\".",
            impact="Multiple H1s dilute the primary topic signal and can confuse heading-based content parsing.",
            fix="Keep a single <h1> for the page topic; demote the others to <h2>/<h3>.",
            confidence="confirmed", evidence_tier="proven"))

    # --- Heading order sanity (no skipped levels = minor) ---
    headings = page.headings or []
    levels = [h.get("level") for h in headings if isinstance(h.get("level"), int)]
    skipped = None
    prev = 0
    for h in headings:
        lv = h.get("level")
        if not isinstance(lv, int):
            continue
        if prev and lv > prev + 1:
            skipped = (prev, lv, h.get("text", ""))
            break
        prev = lv
    if skipped:
        findings.append(Finding(
            "heading-skip", "Heading levels skipped", "low", "technical",
            evidence=f"Heading jumps from H{skipped[0]} to H{skipped[1]} at \"{_q(skipped[2], 60)}\".",
            impact="Skipped heading levels weaken the document outline used by assistive tech and content parsers.",
            fix="Use sequential heading levels (do not jump from H2 straight to H4); insert the missing level or adjust.",
            confidence="likely", evidence_tier="consensus"))

    # --- Canonical ---
    canon = page.canonical
    if not canon:
        findings.append(Finding(
            "canonical-missing", "No canonical tag", "low", "technical",
            evidence="No <link rel=\"canonical\"> was found.",
            impact="Without a canonical, Google must guess the preferred URL, risking duplicate-content dilution across parameter/variant URLs.",
            fix="Add a self-referencing <link rel=\"canonical\" href=\"...\"> with the absolute preferred URL.",
            confidence="confirmed", evidence_tier="proven"))
    else:
        def _norm(u):
            p = urlparse(u)
            return (p.scheme, p.netloc.lower(), p.path.rstrip("/") or "/")
        if _norm(canon) != _norm(page.url or url or ""):
            findings.append(Finding(
                "canonical-cross", "Canonical points to a different URL", "info", "technical",
                evidence=f"Page URL is {_q(page.url or url, 100)} but canonical is {_q(canon, 100)}.",
                impact="A cross-URL canonical tells Google to index the target instead of this page; intentional for duplicates, but a mistake silently de-indexes this URL.",
                fix="Confirm this is deliberate. If this page should rank, set the canonical to its own absolute URL.",
                confidence="confirmed", evidence_tier="proven"))

    # --- Meta robots (indexability) ---
    robots = (page.meta_robots or "").lower()
    if "noindex" in robots:
        findings.append(Finding(
            "robots-noindex", "Page is set to noindex", "critical", "technical",
            evidence=f"meta robots directive contains noindex: \"{_q(page.meta_robots)}\".",
            impact="A noindex page cannot rank in classic search and cannot be cited by Google's AI features, which draw from the same index. This blocks all organic visibility.",
            fix="If this page should be discoverable, remove the noindex directive from the meta robots tag (and any X-Robots-Tag header).",
            confidence="confirmed", evidence_tier="proven"))
    if "nofollow" in robots:
        findings.append(Finding(
            "robots-nofollow", "Page-level nofollow on meta robots", "high", "technical",
            evidence=f"meta robots directive contains nofollow: \"{_q(page.meta_robots)}\".",
            impact="A page-level nofollow stops crawlers from following any outgoing links, blocking discovery of linked pages and bleeding off internal link equity.",
            fix="Remove nofollow from the page-level meta robots unless you intentionally want no links on this page crawled.",
            confidence="confirmed", evidence_tier="proven"))

    # --- Viewport (mobile) ---
    if not page.viewport or not page.viewport.strip():
        findings.append(Finding(
            "viewport-missing", "No mobile viewport meta tag", "medium", "technical",
            evidence="No <meta name=\"viewport\"> was found.",
            impact="Without a viewport tag the page is not mobile-optimized; Google indexes with mobile-first crawling, so this degrades both UX and ranking eligibility.",
            fix="Add <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"> to the <head>.",
            confidence="confirmed", evidence_tier="proven"))

    # --- HTML lang ---
    if not page.lang or not page.lang.strip():
        findings.append(Finding(
            "lang-missing", "No html lang attribute", "low", "technical",
            evidence="The <html> element has no usable lang attribute.",
            impact="A missing lang attribute hurts accessibility (screen readers) and weakens language/locale targeting signals.",
            fix="Set the document language, e.g. <html lang=\"ro\"> for Romanian content.",
            confidence="confirmed", evidence_tier="proven"))

    # --- Mixed content (http:// resources on an https page) ---
    if is_https and page.html:
        mixed = re.findall(r'(?:src|href)\s*=\s*["\'](http://[^"\']+)["\']', page.html, re.IGNORECASE)
        mixed = [m for m in mixed if not m.lower().startswith("http://www.w3.org")]  # XML/SVG namespaces aren't fetched
        if mixed:
            sample = ", ".join(_q(m, 80) for m in mixed[:3])
            findings.append(Finding(
                "mixed-content", "Mixed content: http resources on an https page", "high", "technical",
                evidence=f"{len(mixed)} insecure http:// resource reference(s) found, e.g. {sample}.",
                impact="Browsers block or warn on active mixed content, breaking assets and eroding trust; it also flags the page as not fully secure.",
                fix="Update the referenced resources to https:// (or protocol-relative/relative URLs).",
                confidence="confirmed", evidence_tier="proven", detail={"count": len(mixed), "samples": mixed[:10]}))

    # --- Open Graph ---
    og = page.og or {}
    missing_og = [k for k in ("title", "description") if not og.get(k)]
    if missing_og:
        findings.append(Finding(
            "og-missing", "Open Graph title/description missing", "low", "technical",
            evidence=f"Missing Open Graph tag(s): {', '.join('og:' + k for k in missing_og)}.",
            impact="Without og:title/og:description, social and chat-app link previews fall back to guessed text, weakening share click-through.",
            fix="Add og:title and og:description meta tags mirroring the page's headline and summary.",
            confidence="confirmed", evidence_tier="consensus"))

    # --- robots.txt + sitemap.xml (separate fetches, wrapped) ---
    parsed = urlparse(page.url or url or "")
    if parsed.scheme and parsed.netloc:
        origin = f"{parsed.scheme}://{parsed.netloc}"
        robots_txt = None
        try:
            r = safe_http.get(urljoin(origin, "/robots.txt"))
            if r.ok and r.text and r.text.strip():
                robots_txt = r.text
            else:
                findings.append(Finding(
                    "robotstxt-missing", "robots.txt is missing or empty", "low", "technical",
                    evidence=f"GET {origin}/robots.txt returned status {getattr(r, 'status', '?')} with no usable body.",
                    impact="No robots.txt means crawlers get no crawl directives and cannot discover a declared Sitemap line, slowing crawl efficiency.",
                    fix="Publish a /robots.txt that allows crawling and includes a Sitemap: directive.",
                    confidence="confirmed", evidence_tier="proven"))
        except safe_http.UnsafeURLError as e:
            findings.append(Finding(
                "robotstxt-unfetchable", "Could not fetch robots.txt", "info", "technical",
                evidence=f"robots.txt fetch blocked as unsafe: {_q(str(e))}.",
                impact="Could not verify crawl directives for this origin.",
                fix="Confirm /robots.txt is publicly reachable over HTTPS.",
                confidence="hypothesis", evidence_tier="proven"))
        except Exception as e:
            findings.append(Finding(
                "robotstxt-unfetchable", "Could not fetch robots.txt", "info", "technical",
                evidence=f"robots.txt fetch failed: {_q(str(e))}.",
                impact="Could not verify whether robots.txt exists or references a sitemap.",
                fix="Manually verify /robots.txt is reachable and inspect it; re-run when the host responds.",
                confidence="hypothesis", evidence_tier="proven"))

        # sitemap.xml
        try:
            s = safe_http.get(urljoin(origin, "/sitemap.xml"))
            sitemap_ok = bool(s.ok and s.text and "<" in s.text)
        except safe_http.UnsafeURLError:
            sitemap_ok = None
        except Exception:
            sitemap_ok = None

        referenced = bool(robots_txt and re.search(r"(?im)^\s*sitemap\s*:", robots_txt))
        if sitemap_ok is False:
            findings.append(Finding(
                "sitemap-missing", "No sitemap at /sitemap.xml", "low", "technical",
                evidence=f"GET {origin}/sitemap.xml did not return XML sitemap content.",
                impact="A missing XML sitemap makes it harder for Google to discover all URLs, especially deep or new pages.",
                fix="Generate an XML sitemap (or sitemap index) and reference it from robots.txt and Search Console.",
                confidence="confirmed", evidence_tier="proven"))
        elif sitemap_ok and robots_txt is not None and not referenced:
            findings.append(Finding(
                "sitemap-unreferenced", "Sitemap not referenced in robots.txt", "low", "technical",
                evidence=f"A sitemap exists at {origin}/sitemap.xml but robots.txt has no Sitemap: directive.",
                impact="Crawlers may not auto-discover the sitemap as quickly without the robots.txt pointer.",
                fix="Add a 'Sitemap: " + origin + "/sitemap.xml' line to robots.txt.",
                confidence="confirmed", evidence_tier="proven"))

    return findings


if __name__ == "__main__":
    try:
        url = arg_url(sys.argv)
        if not url:
            print(json.dumps({"error": "missing_url", "detail": "Usage: technical_audit.py <url>"}))
            sys.exit(2)
        emit(collect(url), meta={"url": url, "check": "technical_audit"})
    except safe_http.UnsafeURLError as e:
        print(json.dumps({"error": "unsafe_url", "detail": str(e)}))
        sys.exit(2)
    except Exception as e:
        print(json.dumps({"error": "audit_failed", "detail": str(e)}))
        sys.exit(2)
