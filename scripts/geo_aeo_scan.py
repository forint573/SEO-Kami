#!/usr/bin/env python3
"""GEO/AEO extractability scan: question headings, direct answers, citable specifics, entity, lists/tables, llms.txt."""
import sys, os, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import seo_common
from seo_common import Page, Finding, emit, arg_url
from lib import safe_http, sanitize

_Q_STARTS = ("who", "what", "why", "how", "when", "where", "which", "can", "does", "do", "is", "are", "should", "will")
_TRUST_DOMAINS = (".gov", ".edu", "wikipedia.org", "who.int")
_ORG_PERSON = {"organization", "person", "localbusiness", "corporation", "newsmediaorganization"}


def _is_question(text):
    t = (text or "").strip()
    if not t:
        return False
    if t.endswith("?"):
        return True
    first = re.split(r"[\s,]+", t.lower(), 1)[0]
    return first in _Q_STARTS


def _origin(url):
    m = re.match(r"^(https?://[^/]+)", url or "")
    return m.group(1) if m else None


def _flatten_jsonld(node, out):
    if isinstance(node, dict):
        if "@graph" in node and isinstance(node["@graph"], list):
            for n in node["@graph"]:
                _flatten_jsonld(n, out)
        out.append(node)
        for v in node.values():
            if isinstance(v, (list, dict)):
                _flatten_jsonld(v, out)
    elif isinstance(node, list):
        for n in node:
            _flatten_jsonld(n, out)


def _types(obj):
    t = obj.get("@type")
    if isinstance(t, list):
        return {str(x).lower() for x in t}
    return {str(t).lower()} if t else set()


def collect(url, page=None):
    findings = []
    page = page or Page.fetch(url)
    text = page.text or ""
    html = page.html or ""
    headings = page.headings or []

    # (1) Answer-block: question-shaped headings
    q_headings = [h for h in headings if _is_question(h.get("text", ""))]
    has_body = bool(text.strip())
    if not q_headings:
        findings.append(Finding(
            id="geo_no_question_headings",
            title="No question-shaped headings found",
            severity="medium", category="aeo",
            evidence="Scanned %d headings; none start with an interrogative word or end with '?'." % len(headings),
            impact="Headings that mirror real user questions feed People Also Ask and AI answer extraction; without them the page is harder to lift into an answer.",
            fix="Reframe section headings as the exact questions users ask (e.g. 'How do I…', 'What is…'), then place a self-contained answer directly beneath each.",
            confidence="likely", evidence_tier="consensus",
            detail={"heading_count": len(headings)}))
    else:
        # Heuristic: question headings present but no body text to answer them.
        if not has_body:
            findings.append(Finding(
                id="geo_question_headings_no_answer",
                title="Question headings present but little/no answer text",
                severity="medium", category="aeo",
                evidence="Found %d question-shaped heading(s) but visible body text is empty/negligible (word_count=%d)." % (len(q_headings), page.word_count),
                impact="A question heading with no concise answer beneath it cannot be extracted as a featured snippet or AI answer.",
                fix="Follow each question heading with a ~40-70 word self-contained answer before expanding into detail.",
                confidence="likely", evidence_tier="consensus",
                detail={"question_headings": [sanitize.strip_invisible(h["text"])[:120] for h in q_headings[:8]]}))
        else:
            findings.append(Finding(
                id="geo_question_headings_ok",
                title="Question-shaped headings present",
                severity="info", category="aeo",
                evidence="Found %d question-shaped heading(s), e.g. %r." % (len(q_headings), sanitize.strip_invisible(q_headings[0]["text"])[:120]),
                impact="Question headings mirror real queries and feed PAA / AI answer extraction.",
                fix="Ensure each is followed by a concise ~40-70 word direct answer, then detail.",
                confidence="likely", evidence_tier="consensus",
                detail={"count": len(q_headings)}))

    # (2) Direct-answer-near-top: a <=60-word early paragraph
    early = text[:1200]
    early_words = early.split()
    first_chunk = re.split(r"(?<=[.!?])\s+", early.strip(), 1)
    lead = first_chunk[0] if first_chunk else ""
    lead_wc = len(lead.split())
    concise_lead = bool(lead) and lead_wc <= 60
    if not concise_lead:
        findings.append(Finding(
            id="geo_no_direct_answer_top",
            title="No concise direct answer near the top",
            severity="medium", category="geo",
            evidence="Leading sentence is %d words (need <=60) in the first ~%d words of body text." % (lead_wc, min(len(early_words), 200)),
            impact="A self-contained ~40-60 word answer near the top is the single most extractable GEO/AEO unit; without it engines must synthesize from scattered text.",
            fix="Open the page (or each section) with a 40-60 word answer that resolves the core question on its own, before context or caveats.",
            confidence="likely", evidence_tier="proven",
            detail={"lead_word_count": lead_wc, "lead_preview": sanitize.strip_invisible(lead)[:160]}))
    else:
        findings.append(Finding(
            id="geo_direct_answer_top_ok",
            title="Concise direct answer near the top",
            severity="info", category="geo",
            evidence="Leading sentence is %d words: %r" % (lead_wc, sanitize.strip_invisible(lead)[:160]),
            impact="A self-contained short answer near the top is the most extractable GEO/AEO unit.",
            fix="Keep it self-contained (resolves the question without surrounding context).",
            confidence="likely", evidence_tier="proven",
            detail={"lead_word_count": lead_wc}))

    # (3) Citable specifics: numbers, %, years/dates, trust-domain outbound links
    nums = re.findall(r"(?<![A-Za-z])\d[\d,\.]*", text)
    pcts = re.findall(r"\d+(?:\.\d+)?\s?%", text)
    years = re.findall(r"\b(?:19|20)\d{2}\b", text)
    dates = re.findall(r"\b\d{4}-\d{2}-\d{2}\b", text)
    trust_links = []
    for ln in (page.links or []):
        href = (ln.get("href") or "").lower()
        if href.startswith("http") and not ln.get("internal") and any(d in href for d in _TRUST_DOMAINS):
            trust_links.append(ln["href"])
    specific_count = len(nums) + len(pcts) + len(years) + len(dates)
    if specific_count < 5 or not trust_links:
        findings.append(Finding(
            id="geo_low_citable_specifics",
            title="Few citable specifics / high-trust citations",
            severity="medium", category="geo",
            evidence="numbers=%d, percentages=%d, years=%d, ISO-dates=%d; outbound high-trust links (.gov/.edu/wikipedia/who.int)=%d." % (
                len(nums), len(pcts), len(years), len(dates), len(trust_links)),
            impact="Verifiable specifics (numbers, dated facts, named/authoritative sources) are what AI engines preferentially quote; sparse specifics correlate with lower AI citation share.",
            fix="Add quotable specifics — exact figures, absolute dates (e.g. 2026-05-07), named studies — and cite high-trust sources (.gov/.edu/Wikipedia/WHO) where relevant.",
            confidence="likely", evidence_tier="correlated",
            detail={"numbers": len(nums), "percentages": len(pcts), "years": len(years),
                    "iso_dates": len(dates), "trust_links": trust_links[:8]}))
    else:
        findings.append(Finding(
            id="geo_citable_specifics_ok",
            title="Citable specifics present",
            severity="info", category="geo",
            evidence="numbers=%d, percentages=%d, years=%d, high-trust links=%d." % (len(nums), len(pcts), len(years), len(trust_links)),
            impact="Verifiable specifics are preferentially quoted by AI engines.",
            fix="Keep figures current and dated; attribute to named sources.",
            confidence="likely", evidence_tier="correlated",
            detail={"specific_count": specific_count, "trust_links": len(trust_links)}))

    # (4) Entity: Organization/Person JSON-LD with sameAs
    objs = []
    for block in (page.jsonld or []):
        if isinstance(block, dict) and block.get("_parse_error"):
            continue
        _flatten_jsonld(block, objs)
    entity_objs = [o for o in objs if isinstance(o, dict) and _types(o) & _ORG_PERSON]
    with_sameas = [o for o in entity_objs if o.get("sameAs")]
    if not entity_objs or not with_sameas:
        findings.append(Finding(
            id="geo_entity_sameas_missing",
            title="No Organization/Person entity with sameAs",
            severity="medium", category="entity",
            evidence="Organization/Person JSON-LD objects=%d; with sameAs=%d." % (len(entity_objs), len(with_sameas)),
            impact="sameAs links tie your brand/author to authoritative profiles (Wikipedia/Wikidata/socials), strengthening entity disambiguation that drives Knowledge Panels and AI trust.",
            fix="Add Organization (and Person for authors) JSON-LD with a sameAs array linking official profiles (Wikipedia/Wikidata/LinkedIn/Crunchbase).",
            confidence="likely", evidence_tier="correlated",
            detail={"entity_objects": len(entity_objs), "with_sameas": len(with_sameas)}))
    else:
        findings.append(Finding(
            id="geo_entity_sameas_ok",
            title="Organization/Person entity with sameAs present",
            severity="info", category="entity",
            evidence="%d entity object(s) carry a sameAs reference." % len(with_sameas),
            impact="sameAs aids entity disambiguation for Knowledge Panels and AI trust.",
            fix="Keep sameAs pointed at authoritative, consistent profiles.",
            confidence="confirmed", evidence_tier="correlated",
            detail={"with_sameas": len(with_sameas)}))

    # (5) Lists >=3 items and tables (approx from HTML)
    list_items = len(re.findall(r"<li\b", html, re.I))
    ul_ol = len(re.findall(r"<(?:ul|ol)\b", html, re.I))
    tables = len(re.findall(r"<table\b", html, re.I))
    big_lists = ul_ol > 0 and list_items >= 3
    if not big_lists and tables == 0:
        findings.append(Finding(
            id="aeo_no_lists_or_tables",
            title="No substantial lists or tables",
            severity="low", category="aeo",
            evidence="<ul>/<ol>=%d, <li>=%d, <table>=%d." % (ul_ol, list_items, tables),
            impact="List and table snippets are common zero-click SERP answer formats (steps, comparisons, specs); their absence forfeits those surfaces.",
            fix="Where content is enumerable or comparative, structure it as a 3+ item list or a comparison table so it can be lifted into list/table snippets.",
            confidence="likely", evidence_tier="consensus",
            detail={"lists": ul_ol, "list_items": list_items, "tables": tables}))
    else:
        findings.append(Finding(
            id="aeo_lists_tables_ok",
            title="Lists/tables present (AEO-friendly)",
            severity="info", category="aeo",
            evidence="<li>=%d, <table>=%d." % (list_items, tables),
            impact="Lists/tables feed list and table SERP snippets.",
            fix="Keep enumerable content well-structured for snippet extraction.",
            confidence="confirmed", evidence_tier="consensus",
            detail={"list_items": list_items, "tables": tables}))

    # (6) llms.txt (SPECULATIVE)
    origin = _origin(page.url or url)
    if origin:
        llms_url = origin + "/llms.txt"
        try:
            resp = safe_http.get(llms_url)
            present = bool(resp.ok and resp.status == 200 and (resp.text or "").strip())
        except safe_http.UnsafeURLError:
            present = None
        except Exception:
            present = None
        if present is False:
            findings.append(Finding(
                id="geo_llms_txt_absent",
                title="No llms.txt at site root",
                severity="info", category="geo",
                evidence="GET %s did not return a populated 200 response." % llms_url,
                impact="No proven ranking or citation lift. llms.txt only helps when a URL is pasted directly into a chat tool; Google crawls it with no special treatment and there is near-zero evidence live AI crawlers request it during retrieval.",
                fix="Optional and low-cost to add, but do not prioritize it. Spend effort on people-first content, earned mentions, and indexability instead.",
                confidence="hypothesis", evidence_tier="speculative",
                detail={"url": llms_url}))
        elif present is None:
            findings.append(Finding(
                id="geo_llms_txt_uncheckable",
                title="Could not verify llms.txt",
                severity="info", category="geo",
                evidence="Request to %s failed or was blocked; presence unknown." % llms_url,
                impact="No proven ranking or citation lift either way, so its presence/absence is not a priority.",
                fix="Manually request %s if you want to confirm. It is low-cost but optional — do not prioritize." % llms_url,
                confidence="hypothesis", evidence_tier="speculative",
                detail={"url": llms_url}))

    return findings


if __name__ == "__main__":
    try:
        url = arg_url(sys.argv)
        if not url:
            print(json.dumps({"error": "missing_url", "detail": "Provide a URL as the first argument."}))
            sys.exit(2)
        emit(collect(url), meta={"url": url, "check": "geo_aeo_scan"})
    except safe_http.UnsafeURLError as e:
        print(json.dumps({"error": "unsafe_url", "detail": str(e)}))
        sys.exit(2)
    except Exception as e:
        print(json.dumps({"error": "geo_aeo_scan_failed", "detail": str(e)}))
        sys.exit(2)
