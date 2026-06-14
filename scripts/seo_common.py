"""Shared parsing + finding model for SEO-Kami scripts.

Two jobs:

1. `Page` — parse HTML *once* into the handful of SEO-relevant accessors every
   script needs (title, meta, canonical, headings, links, images, JSON-LD,
   hreflang, visible text). Implemented on the stdlib `html.parser` so there is
   NO third-party parsing dependency and every script sees identical results.

2. The finding contract — `Finding`, the severity / confidence vocabularies, and
   `emit()` so every script prints the same JSON envelope. The Finding shape
   (evidence + impact + fix + confidence label) is SEO-Kami's output spine; see
   references/output-contract.md. The confidence vocabulary is adapted from the
   MIT-licensed llm-audit-rubric.md in Bhanunamikaze/Agentic-SEO-Skill.
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, asdict, field
from html.parser import HTMLParser
from typing import Optional
from urllib.parse import urljoin, urlparse

# ---------------------------------------------------------------------------
# Finding contract
# ---------------------------------------------------------------------------

SEVERITY_ORDER = ["critical", "high", "medium", "low", "info"]
SEVERITY_WEIGHT = {"critical": 25, "high": 12, "medium": 5, "low": 2, "info": 0}
CONFIDENCE = ["confirmed", "likely", "hypothesis"]
# Evidence strength tiers — see references/evidence-tiers.md.
EVIDENCE_TIERS = ["proven", "correlated", "consensus", "speculative"]


@dataclass
class Finding:
    id: str                         # stable slug, e.g. "indexability-noindex"
    title: str
    severity: str                   # one of SEVERITY_ORDER
    category: str                   # technical | content | schema | geo | aeo | eeat | entity | links | github | perf
    evidence: str = ""              # what was actually observed (a measurement / quote)
    impact: str = ""                # why it matters
    fix: str = ""                   # the concrete remediation
    confidence: str = "confirmed"   # confirmed | likely | hypothesis
    evidence_tier: str = "proven"   # proven | correlated | consensus | speculative
    detail: dict = field(default_factory=dict)

    def __post_init__(self):
        if self.severity not in SEVERITY_ORDER:
            self.severity = "medium"
        if self.confidence not in CONFIDENCE:
            self.confidence = "likely"
        if self.evidence_tier not in EVIDENCE_TIERS:
            self.evidence_tier = "consensus"


def score(findings: list) -> int:
    """A simple, transparent 0-100 health score: 100 minus capped penalties.

    ONE scoring contract for the whole skill (the donors shipped two that didn't
    reconcile). Deterministic and explained in the report, not a black box.
    """
    penalty = sum(SEVERITY_WEIGHT.get(f.severity, 0) for f in findings)
    return max(0, 100 - min(penalty, 100))


def grade(s: int) -> str:
    return ("A" if s >= 90 else "B" if s >= 75 else "C" if s >= 60
            else "D" if s >= 40 else "F")


def emit(findings: list, meta: Optional[dict] = None) -> None:
    """Print the standard JSON envelope to stdout."""
    findings = sorted(findings, key=lambda f: SEVERITY_ORDER.index(f.severity))
    s = score(findings)
    out = {
        "meta": meta or {},
        "score": s,
        "grade": grade(s),
        "summary": {sev: sum(1 for f in findings if f.severity == sev) for sev in SEVERITY_ORDER},
        "findings": [asdict(f) for f in findings],
    }
    print(json.dumps(out, indent=2, ensure_ascii=False))


# ---------------------------------------------------------------------------
# HTML parsing (stdlib only)
# ---------------------------------------------------------------------------

_VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
         "meta", "param", "source", "track", "wbr"}
_SKIP_TEXT = {"script", "style", "noscript", "template", "svg"}


class _Collector(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title_parts: list = []
        self._in_title = False
        self.metas: list = []          # list of attr dicts
        self.links: list = []          # <link> attr dicts
        self.html_lang: Optional[str] = None
        self.headings: list = []       # (level, text)
        self._heading_level = 0
        self._heading_parts: list = []
        self.anchors: list = []        # dict(href, rel, text)
        self._a_href = None
        self._a_rel = None
        self._a_parts: list = []
        self.images: list = []         # dict(src, alt)
        self.jsonld_raw: list = []
        self._in_jsonld = False
        self._jsonld_parts: list = []
        self._skip_depth = 0
        self.text_parts: list = []

    def handle_starttag(self, tag, attrs):
        a = {k.lower(): (v or "") for k, v in attrs}
        if tag == "html" and "lang" in a and not self.html_lang:
            self.html_lang = a["lang"]
        elif tag == "title":
            self._in_title = True
        elif tag == "meta":
            self.metas.append(a)
        elif tag == "link":
            self.links.append(a)
        elif tag == "img":
            self.images.append({"src": a.get("src", ""), "alt": a.get("alt"),
                                "loading": a.get("loading", "")})
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self._heading_level = int(tag[1])
            self._heading_parts = []
        elif tag == "a":
            self._a_href = a.get("href")
            self._a_rel = a.get("rel", "")
            self._a_parts = []
        elif tag == "script" and "ld+json" in a.get("type", "").lower():
            self._in_jsonld = True
            self._jsonld_parts = []
        if tag in _SKIP_TEXT:
            self._skip_depth += 1

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6") and self._heading_level:
            self.headings.append((self._heading_level, " ".join(self._heading_parts).strip()))
            self._heading_level = 0
        elif tag == "a" and self._a_href is not None:
            self.anchors.append({"href": self._a_href, "rel": self._a_rel,
                                 "text": " ".join(self._a_parts).strip()})
            self._a_href = None
        elif tag == "script" and self._in_jsonld:
            self.jsonld_raw.append("".join(self._jsonld_parts))
            self._in_jsonld = False
        if tag in _SKIP_TEXT and self._skip_depth:
            self._skip_depth -= 1

    def handle_data(self, data):
        if self._in_jsonld:
            self._jsonld_parts.append(data)
            return
        if self._in_title:
            self.title_parts.append(data)
        if self._heading_level:
            self._heading_parts.append(data)
        if self._a_href is not None:
            self._a_parts.append(data)
        if not self._skip_depth:
            stripped = data.strip()
            if stripped:
                self.text_parts.append(stripped)


class Page:
    """Parsed view of one HTML page."""

    def __init__(self, url: str, html: str, headers: Optional[dict] = None,
                 status: Optional[int] = None):
        self.url = url
        self.html = html or ""
        self.headers = {k.lower(): v for k, v in (headers or {}).items()}
        self.status = status
        c = _Collector()
        try:
            c.feed(self.html)
        except Exception:
            pass
        self._c = c

    @classmethod
    def fetch(cls, url: str):
        """Fetch via the safe HTTP layer and parse. Returns a Page."""
        from lib import safe_http
        r = safe_http.get(url)
        return cls(r.url, r.text, r.headers, r.status)

    @property
    def title(self) -> Optional[str]:
        t = " ".join(self._c.title_parts).strip()
        return t or None

    def _meta(self, key: str, attr: str = "name") -> Optional[str]:
        for m in self._c.metas:
            if m.get(attr, "").lower() == key.lower():
                return m.get("content")
        return None

    @property
    def meta_description(self) -> Optional[str]:
        return self._meta("description")

    @property
    def meta_robots(self) -> Optional[str]:
        return self._meta("robots")

    @property
    def viewport(self) -> Optional[str]:
        return self._meta("viewport")

    @property
    def lang(self) -> Optional[str]:
        return self._c.html_lang

    @property
    def canonical(self) -> Optional[str]:
        for l in self._c.links:
            if "canonical" in l.get("rel", "").lower():
                return urljoin(self.url, l.get("href", ""))
        return None

    @property
    def hreflang(self) -> list:
        out = []
        for l in self._c.links:
            if "alternate" in l.get("rel", "").lower() and l.get("hreflang"):
                out.append({"lang": l["hreflang"], "href": urljoin(self.url, l.get("href", ""))})
        return out

    @property
    def h1s(self) -> list:
        return [t for lvl, t in self._c.headings if lvl == 1 and t]

    @property
    def headings(self) -> list:
        return [{"level": lvl, "text": t} for lvl, t in self._c.headings]

    @property
    def links(self) -> list:
        out = []
        for a in self._c.anchors:
            href = a.get("href") or ""
            if not href or href.startswith(("#", "javascript:", "mailto:", "tel:")):
                continue
            absu = urljoin(self.url, href)
            out.append({"href": absu, "text": a.get("text", ""), "rel": a.get("rel", ""),
                        "internal": _same_site(self.url, absu)})
        return out

    @property
    def images(self) -> list:
        return list(self._c.images)

    @property
    def og(self) -> dict:
        return {m.get("property", "")[3:]: m.get("content", "")
                for m in self._c.metas if m.get("property", "").lower().startswith("og:")}

    @property
    def jsonld(self) -> list:
        out = []
        for raw in self._c.jsonld_raw:
            raw = raw.strip()
            if not raw:
                continue
            try:
                data = json.loads(raw)
                out.extend(data if isinstance(data, list) else [data])
            except (json.JSONDecodeError, ValueError):
                out.append({"_parse_error": True, "_raw": raw[:200]})
        return out

    @property
    def text(self) -> str:
        return re.sub(r"\s+", " ", " ".join(self._c.text_parts)).strip()

    @property
    def word_count(self) -> int:
        return len([w for w in re.split(r"\s+", self.text) if w])


def _strip_www(host: str) -> str:
    # NB: NOT host.lstrip("www.") — that strips any leading chars in {w,.},
    # so "web.com" -> "eb.com". Strip the exact prefix only.
    return host[4:] if host.startswith("www.") else host


def _same_site(base: str, other: str) -> bool:
    try:
        b = _strip_www(urlparse(base).netloc.lower().split(":")[0])
        o = _strip_www(urlparse(other).netloc.lower().split(":")[0])
        return bool(b) and b == o
    except Exception:
        return False


def audit_gate(page) -> Optional["Finding"]:
    """Return a blocking Finding if `page` is not a real, auditable HTML page.

    Auditing an error page (403/404/5xx) or a non-HTML response (JSON API, PDF)
    as if it were a normal page produces confident, fictional findings — the
    fastest way to lose trust in the tool. Collectors call this first and stop
    if it returns a Finding. Returns None when the page is fine to audit.
    """
    status = getattr(page, "status", None)
    if status is not None and not (200 <= status < 300):
        return Finding(
            id="page.not_auditable.status", title="Page did not return HTTP 200 — not auditable",
            severity="critical", category="technical",
            evidence="Fetched %s returned HTTP %s." % (getattr(page, "url", "?"), status),
            impact="The on-page audit was skipped: a non-200 response (block, redirect loop, error, or down page) is not the live page, so auditing it would produce fictional findings.",
            fix="Ensure the URL returns 200 to crawlers (check bot-blocking/WAF, auth walls, and the correct canonical URL), then re-run.",
            confidence="confirmed", evidence_tier="proven", detail={"status": status})
    ctype = (getattr(page, "headers", {}) or {}).get("content-type", "")
    if ctype and "html" not in ctype.lower() and "xml" not in ctype.lower():
        return Finding(
            id="page.not_auditable.content_type", title="Response is not HTML — not auditable as a page",
            severity="high", category="technical",
            evidence="Content-Type is %r, not text/html." % ctype.split(";")[0].strip(),
            impact="The on-page audit was skipped: this is a non-HTML resource (e.g. JSON API, PDF, image), so page-level SEO checks do not apply.",
            fix="Point the audit at an HTML page (the document URL), not an API endpoint or asset.",
            confidence="confirmed", evidence_tier="proven", detail={"content_type": ctype})
    return None


def arg_url(argv: list, default: Optional[str] = None) -> str:
    """Tiny shared CLI helper: first positional non-flag arg is the URL."""
    for a in argv[1:]:
        if not a.startswith("-"):
            return a
    if default:
        return default
    print(json.dumps({"error": "missing URL argument"}))
    sys.exit(2)
