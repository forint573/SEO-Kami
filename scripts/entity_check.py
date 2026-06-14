#!/usr/bin/env python3
"""Entity + earned-media signals: sameAs, brand-name consistency, authoritative pages, NAP, digital PR."""
import sys, os, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import seo_common
from seo_common import Page, Finding, emit, arg_url
from lib import safe_http, sanitize

# A phone must START like one: + country code, a (area code), or a 0-led number.
# This rejects year+stat runs like "2025 99.999" and "99.999% uptime" that the
# old permissive pattern matched as fake phone "signals".
PHONE_RE = re.compile(
    r"(?<![\d.])"
    r"(?:\+\d{1,3}[\s.\-]+\(?\d{1,4}\)?|\(\d{2,4}\)|0\d{1,4})"
    r"(?:[\s.\-]+\d{2,4}){1,4}"
    r"(?![\d%])")
# Require a plausible phone: 9-15 digits (E.164) in the matched run.
ADDR_HINT_RE = re.compile(
    r"\b(\d{1,5})\s+[A-Za-zĂÂÎȘȚăâîșț\.\-]+\s+(?:street|st|road|rd|ave|avenue|blvd|boulevard|"
    r"lane|ln|drive|dr|str|strada|str\.|bd|bd\.|bulevardul|calea|șoseaua|soseaua|piața|piata)\b",
    re.IGNORECASE,
)


def _phone_candidates(text):
    out = []
    for m in PHONE_RE.finditer(text or ""):
        s = m.group(0).strip()
        if 9 <= sum(c.isdigit() for c in s) <= 15:
            out.append(s)
        if len(out) >= 3:
            break
    return out


def _orgs(page):
    """Return Organization/Person JSON-LD nodes (flattening @graph)."""
    nodes = []
    for block in (page.jsonld or []):
        if not isinstance(block, dict) or block.get("_parse_error"):
            continue
        items = block.get("@graph") if isinstance(block.get("@graph"), list) else [block]
        for it in items:
            if not isinstance(it, dict):
                continue
            t = it.get("@type")
            types = t if isinstance(t, list) else [t]
            types = {str(x).lower() for x in types if x}
            if types & {"organization", "person", "localbusiness"} or any(
                "organization" in x or "business" in x for x in types
            ):
                nodes.append(it)
    return nodes


def collect(url, page=None):
    findings = []
    # Let fetch errors propagate to the caller (the orchestrator catches them and
    # degrades to a skip-finding; __main__ handles them for standalone runs).
    # Never sys.exit() here — SystemExit is not an Exception and would abort the
    # whole audit run instead of skipping this one check.
    page = page or Page.fetch(url)
    _gate = seo_common.audit_gate(page)
    if _gate is not None:
        return [_gate]

    orgs = _orgs(page)

    # (1) sameAs profiles --------------------------------------------------
    same_as = []
    for node in orgs:
        sa = node.get("sameAs")
        if isinstance(sa, str):
            same_as.append(sa)
        elif isinstance(sa, list):
            same_as.extend([s for s in sa if isinstance(s, str)])
    same_as = list(dict.fromkeys([s.strip() for s in same_as if s and s.strip()]))

    if same_as:
        findings.append(Finding(
            id="entity.sameas.present",
            title=f"{len(same_as)} sameAs profile(s) declared on the entity",
            severity="info",
            category="entity",
            evidence="sameAs links: " + ", ".join(same_as[:8]) + ("…" if len(same_as) > 8 else ""),
            impact="sameAs disambiguates your brand/author as a Knowledge-Graph entity, helping AI engines map mentions to the right entity.",
            fix="Keep these profiles live and consistent; ensure each linked profile points back and uses the same name/description.",
            confidence="confirmed",
            evidence_tier="consensus",
            detail={"count": len(same_as), "profiles": same_as},
        ))
    else:
        findings.append(Finding(
            id="entity.sameas.missing",
            title="No sameAs links on Organization/Person JSON-LD",
            severity="medium",
            category="entity",
            evidence=f"Found {len(orgs)} Organization/Person/LocalBusiness JSON-LD node(s); none declared a sameAs array.",
            impact="Without sameAs, AI/search engines have weaker signals tying your social/Wikidata/Crunchbase profiles to your entity. Brand MENTIONS correlate ~0.664 with AI-Overview visibility vs ~0.218 for backlinks (~3:1) — entity presence drives citation more than links.",
            fix="Add a sameAs array to your Organization/Person JSON-LD linking authoritative profiles (LinkedIn, Wikipedia/Wikidata, Crunchbase, X, official socials).",
            confidence="likely",
            evidence_tier="correlated",
            detail={"orgs_found": len(orgs)},
        ))

    # (2) Brand-name consistency ------------------------------------------
    title = page.title or ""
    og_site = (page.og or {}).get("site_name")  # Page.og already strips the "og:" prefix
    org_name = None
    for node in orgs:
        n = node.get("name")
        if isinstance(n, str) and n.strip():
            org_name = n.strip()
            break

    def norm(s):
        return re.sub(r"\s+", " ", (s or "")).strip().lower()

    def _match(a, b):  # a appears in b or vice-versa (normalized)
        na, nb = norm(a), norm(b)
        return bool(na) and bool(nb) and (na in nb or nb in na)

    # Split the title into every brand-candidate segment, not only the last —
    # brand-first titles ("Stripe | Financial Infrastructure") are very common,
    # and matching only the last segment produced constant false mismatches.
    segs = [title]
    for sep in ("|", "–", "—", "-", "::", "·", "»", ":"):
        segs.extend(title.split(sep))
    segs = [s.strip() for s in segs if s.strip()]

    structured = {k: v for k, v in
                  (("og:site_name", og_site), ("Organization.name", org_name)) if v}
    if structured:
        # A structured brand is "in the title" if it matches the full title or ANY segment.
        not_in_title = {k: v for k, v in structured.items()
                        if not any(_match(v, s) for s in segs)}
        vals = list(structured.values())
        cross_ok = all(_match(a, b) for i, a in enumerate(vals) for b in vals[i + 1:])
        if not_in_title or not cross_ok:
            findings.append(Finding(
                id="entity.brandname.mismatch",
                title="Brand name is inconsistent across title / og:site_name / Organization.name",
                severity="low",
                category="entity",
                evidence="title=%r; %s" % (title, "; ".join("%s=%r" % (k, v) for k, v in structured.items())),
                impact="Inconsistent brand naming fragments your entity signal, making it harder for engines to consolidate mentions into one trusted entity.",
                fix="Use one canonical brand spelling identically in <title>, og:site_name, and Organization.name (and across the web); include the brand somewhere in the <title>.",
                confidence="likely",
                evidence_tier="consensus",
                detail={"not_in_title": list(not_in_title.keys()), "cross_consistent": cross_ok},
            ))
        else:
            findings.append(Finding(
                id="entity.brandname.consistent",
                title="Brand name is consistent across available signals",
                severity="info",
                category="entity",
                evidence="; ".join(["title contains the brand"] + ["%s=%r" % (k, v) for k, v in structured.items()]),
                impact="Consistent naming reinforces a single, unambiguous entity for search and AI engines.",
                fix="Maintain this consistency across off-site profiles and citations.",
                confidence="confirmed",
                evidence_tier="consensus",
                detail={"structured": structured},
            ))
    else:
        findings.append(Finding(
            id="entity.brandname.insufficient",
            title="No structured brand signal to corroborate the title",
            severity="info",
            category="entity",
            evidence="Found no og:site_name or Organization.name to check the <title> brand against.",
            impact="Missing og:site_name and Organization.name removes corroborating brand signals that strengthen entity recognition.",
            fix="Add og:site_name and an Organization JSON-LD with a name matching your <title> brand.",
            confidence="likely",
            evidence_tier="consensus",
            detail={"title": title},
        ))

    # (3) Authoritative pages ---------------------------------------------
    link_blob = " ".join((l.get("text") or "") + " " + (l.get("href") or "") for l in (page.links or []))
    blob_l = link_blob.lower()
    has_about = bool(re.search(r"\babout(?:[\s\-]?us)?\b|/about", blob_l))
    has_contact = bool(re.search(r"\bcontact\b|/contact", blob_l))
    has_team = bool(re.search(r"\bteam\b|/team|\bour\s+team\b", blob_l))
    has_author = bool(re.search(r"\bauthor\b|/author", blob_l))

    missing = [name for name, present_ in (("About", has_about), ("Contact", has_contact)) if not present_]
    found_auth = [name for name, p in (("About", has_about), ("Contact", has_contact),
                                       ("Team", has_team), ("Author", has_author)) if p]
    if missing:
        findings.append(Finding(
            id="entity.authoritative.missing",
            title=f"Missing authoritative navigation: {', '.join(missing)}",
            severity="low",
            category="eeat",
            evidence=f"Scanned {len(page.links or [])} links. Detected: {', '.join(found_auth) or 'none'}. Missing: {', '.join(missing)}.",
            impact="About/Contact pages establish who is behind the site — a core E-E-A-T trust signal that engines and quality raters look for (especially YMYL).",
            fix="Add a clear About (org/author identity, expertise) and a Contact page (real address/phone/email) linked from primary navigation.",
            confidence="likely",
            evidence_tier="consensus",
            detail={"found": found_auth, "missing": missing},
        ))
    else:
        findings.append(Finding(
            id="entity.authoritative.present",
            title="About and Contact pages are linked",
            severity="info",
            category="eeat",
            evidence=f"Detected authoritative links: {', '.join(found_auth)}.",
            impact="Visible About/Contact pages support E-E-A-T trust and entity verification.",
            fix="Ensure these pages carry real identity/credentials and accurate, current NAP details.",
            confidence="confirmed",
            evidence_tier="consensus",
            detail={"found": found_auth},
        ))

    # (4) NAP: telephone + postal address ---------------------------------
    phones = _phone_candidates(page.text or "")
    tel_links = [l["href"] for l in (page.links or []) if (l.get("href") or "").lower().startswith("tel:")]
    has_phone = bool(phones or tel_links)

    addr_in_jsonld = False
    addr_sample = None
    for node in orgs:
        a = node.get("address")
        if a:
            addr_in_jsonld = True
            if isinstance(a, dict):
                addr_sample = ", ".join(
                    str(a[k]) for k in ("streetAddress", "postalCode", "addressLocality", "addressCountry")
                    if a.get(k)
                ) or json.dumps(a, ensure_ascii=False)[:120]
            else:
                addr_sample = str(a)[:120]
            break
    addr_text_match = ADDR_HINT_RE.search(page.text or "")
    has_address = addr_in_jsonld or bool(addr_text_match)

    # Missing NAP only matters much for an actual local business; many valid sites
    # (SaaS, blogs, news) legitimately omit it. Penalize accordingly.
    def _is_localbiz(node):
        t = node.get("@type")
        types = t if isinstance(t, list) else [t]
        return any("localbusiness" in str(x).lower() for x in types if x)
    has_localbusiness = any(_is_localbiz(n) for n in orgs)

    if not (has_phone and has_address):
        miss = []
        if not has_phone:
            miss.append("telephone")
        if not has_address:
            miss.append("postal address")
        findings.append(Finding(
            id="entity.nap.incomplete",
            title=f"NAP incomplete: missing {', '.join(miss)}",
            severity="medium" if has_localbusiness else "low",
            category="entity",
            evidence=(f"phone={'yes' if has_phone else 'no'} "
                      f"({(phones[0] if phones else (tel_links[0] if tel_links else 'none'))}); "
                      f"address={'yes' if has_address else 'no'}"
                      + (f" ({addr_sample})" if addr_sample else "")),
            impact="For a local/business site, missing Name-Address-Phone weakens entity disambiguation and local trust; consistent NAP everywhere is durable entity-optimization consensus.",
            fix="Publish consistent NAP in LocalBusiness/Organization JSON-LD (telephone + PostalAddress) and in visible site footer; mirror it on Google Business Profile and directories.",
            confidence="hypothesis",
            evidence_tier="consensus",
            detail={"has_phone": has_phone, "has_address": has_address,
                    "phones": phones, "tel_links": tel_links,
                    "address_in_jsonld": addr_in_jsonld,
                    "note": "If this is not a local/business site, NAP may be intentionally absent — confirm against site type."},
        ))
    else:
        findings.append(Finding(
            id="entity.nap.present",
            title="NAP signals present (telephone + postal address)",
            severity="info",
            category="entity",
            evidence=(f"phone={(phones[0] if phones else tel_links[0])}; "
                      f"address={'JSON-LD' if addr_in_jsonld else 'text'}"
                      + (f" ({addr_sample})" if addr_sample else "")),
            impact="Detectable NAP strengthens local/business entity trust and consistency.",
            fix="Keep NAP identical across JSON-LD, footer, Google Business Profile, and directories.",
            confidence="likely",
            evidence_tier="consensus",
            detail={"phones": phones, "tel_links": tel_links, "address_in_jsonld": addr_in_jsonld},
        ))

    # (5) Earned media / digital PR recommendation ------------------------
    findings.append(Finding(
        id="entity.earned_media.recommend",
        title="Invest in earned media / digital PR to drive AI citation",
        severity="info",  # standing strategic guidance, not a per-page defect — must not penalize the score
        category="entity",
        evidence=("Ahrefs (75,000 brands, Aug 2025): branded web MENTIONS correlate ~0.664 with AI-Overview "
                  "brand visibility vs ~0.218 for backlinks (~3:1). Muck Rack (1M+ AI citations): ~82% from "
                  "earned media, ~94% non-paid."),
        impact=("A backlink tells an AI engine WHERE to go; a brand MENTION tells it WHAT to trust — for citation, "
                "trust dominates. Off-site brand presence is the strongest known lever for AI-answer inclusion."),
        fix=("Run digital PR for third-party quotes/mentions; seed consistent entity descriptions on "
             "Reddit/Wikipedia/Wikidata/industry sites; pursue YouTube mentions (correlate ~0.737, Dec 2025). "
             "Build mentions, not just links."),
        confidence="likely",
        evidence_tier="correlated",
        detail={"mention_corr": 0.664, "backlink_corr": 0.218,
                "mechanic": "backlink=where-to-go; mention=what-to-trust",
                "caveat": "Correlation, not proven causation; citation is probabilistic and query-dependent."},
    ))

    return findings


if __name__ == "__main__":
    url = arg_url(sys.argv)
    if not url:
        print(json.dumps({"error": "missing_url", "detail": "Usage: entity_check.py <url>"}))
        sys.exit(2)
    try:
        emit(collect(url), meta={"url": url, "check": "entity_check"})
    except safe_http.UnsafeURLError as e:
        print(json.dumps({"error": "unsafe_url", "detail": str(e)}))
        sys.exit(2)
    except Exception as e:
        print(json.dumps({"error": "fetch_failed", "detail": str(e)}))
        sys.exit(2)
