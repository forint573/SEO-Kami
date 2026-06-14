# Multilingual / International SEO — Technical Layer

This reference covers the **technical** plumbing of serving SEO content across languages and markets: URL structure, hreflang, canonicals, locale signals. It does NOT cover wording or translation quality — that is handed to the user's translation/humanizer skills. For evidence-tier definitions see references/evidence-tiers.md.

## Table of contents
- [Scope and handoff](#scope-and-handoff)
- [Translation vs localization](#translation-vs-localization)
- [Per-market keyword research (do not translate keywords)](#per-market-keyword-research-do-not-translate-keywords)
- [URL strategy decision checklist](#url-strategy-decision-checklist)
- [The hreflang correctness contract](#the-hreflang-correctness-contract)
- [Common failure modes](#common-failure-modes)
- [RTL languages](#rtl-languages)
- [Validation: scripts/hreflang_check.py](#validation-scriptshreflang_checkpy)

## Scope and handoff

SEO-Kami produces the technical PLAN and the per-market keyword/brief skeleton. It never ghostwrites translated copy. Actual rendering of meaning into a target language goes to your separate humanizer + translation skills — that is where currency phrasing, idiom, and tone are decided. This file makes sure the page is *discoverable and correctly attributed to a market* once that copy exists. Cross-link: references/technical-foundations.md (rendering, indexability), references/keyword-free-signals.md (research inputs).

## Translation vs localization

Translation swaps words. Localization adapts the page to a market's reality (CONSENSUS):

- **Currency and units** — RON vs EUR vs USD; metric vs imperial; date format (DD/MM vs MM/DD); thousands separators.
- **Examples and entities** — local brands, local regulations, local place names. A US-centric example reads as foreign and lowers trust signals.
- **Search intent** — the same nominal topic can carry different intent per market (informational in one, transactional in another). Intent is set during per-market research, not assumed from the source language.
- **Legal/compliance phrasing** — disclaimers, tax wording, consumer-rights language differ by jurisdiction.

A page that is translated but not localized often ranks worse than a thinner page written natively for the market, because intent mismatch and foreign examples depress engagement and topical fit. Localization decisions are inputs to the translation skill; this layer just ensures the localized variant gets its own URL + correct hreflang.

## Per-market keyword research (do not translate keywords)

**Never translate a keyword and assume it is the query that market uses (CONSENSUS).** The literal translation is frequently not the searched term: the market may use an English loanword, a regional synonym, a brand-as-category term, or a different grammatical form. Examples of the failure pattern: an English-loanword query winning over the "correct" native word; a regional spelling differing from the standard one; singular vs plural intent splitting.

Research each market independently using that **locale's** signals (set Google to the target country + language):

- Autocomplete in the target locale (real query stems, not your guesses).
- People Also Ask (PAA) in the target locale (question framings unique to that market).
- The live SERP for candidate terms (which feature set appears, who ranks, what intent Google infers).
- Google Search Console, filtered by country, once the market page exists — your own impressions/position by query and country are the strongest striking-distance signal.

Full method for each of these in references/keyword-free-signals.md.

**No free localized volume data exists (PROVEN constraint, not a tooling gap).** There is no reliable FREE source of per-country search volume or keyword difficulty — and translating a foreign keyword tool's English number is meaningless because the term itself may be wrong. Do NOT add "Local Search Volume", "Est. Volume", "Difficulty", or "Est. Traffic" columns to any per-market plan. Prioritize markets and terms by: SERP-feature click value (what the live local SERP actually shows), GSC striking-distance (your own country-filtered impressions/positions), first-party business fit (where you can fulfill/sell), and topical authority you can credibly build. See references/measurement-zero-click.md for how to read success once live.

## URL strategy decision checklist

Three structures, with the trade-offs that actually decide it:

| Structure | Example | Authority | Geo-targeting clarity | Cost / maintenance |
|---|---|---|---|---|
| Subdirectory | example.com/ro/ | Consolidated on one domain (strongest) | Language clear from path; country set via hreflang/GSC | Lowest — one host, one cert, one CMS |
| Subdomain | ro.example.com | Treated as separate host; authority can fragment | Clear-ish, but Google treats it more like a distinct site | Medium — separate host config, sometimes separate analytics |
| ccTLD | example.ro | Each domain earns authority independently from scratch | Strongest single geo signal (country-coded) | Highest — buy/renew each TLD, separate hosting, separate link-building |

**Deterministic checklist:**

1. Do you have, or can you sustainably build, separate authority + link-building per country? → If NO, do NOT use ccTLDs. Go to 2.
2. Is there a hard legal/brand reason to physically separate sites (data residency, regional ownership, brand split)? → If YES, ccTLD or subdomain may be justified despite the cost. If NO, go to 3.
3. **Default: subdirectories (example.com/ro/).** They consolidate all link authority onto one domain, are cheapest to run, and geo-target perfectly well via hreflang + a GSC country setting. (CONSENSUS)

**When to deviate from the subdirectory default:**
- **ccTLD** when a strong country signal is worth more than consolidated authority AND you can fund independent SEO per market (e.g. a brand whose primary trust comes from being "the local one"), or when the law requires a national domain.
- **Subdomain** rarely — usually only when platform/hosting constraints make a subdirectory impossible (different stack per region you cannot reverse-proxy under one host). Otherwise it gets the worst of both: weaker consolidation than a subdirectory, weaker geo signal than a ccTLD.

ccTLDs cannot be re-targeted in GSC (the country is fixed by the TLD); generic domains (subdirectory/subdomain) carry the country signal primarily through hreflang, so the hreflang contract below is non-negotiable for them.

## The hreflang correctness contract

hreflang tells Google which URL serves which language/region so it can swap in the right one per searcher. It is an annotation, not a ranking boost — but getting it wrong actively breaks international visibility. Rules below are **PROVEN** (Google primary docs):

1. **Reciprocal / return-tag (bidirectional).** If page A links to B with hreflang, B must link back to A. Non-reciprocal annotations are ignored.
2. **Self-reference required.** Every page in the set must include an hreflang entry pointing to itself, in addition to its siblings.
3. **x-default.** Include an `x-default` entry for the fallback page shown when no language/region matches the user (e.g. a language selector or your primary version).
4. **One value → one URL.** A given language(-region) value must map to exactly one URL across the set. Duplicate values pointing at different URLs invalidate the cluster.
5. **Valid codes.** Language = ISO 639-1 (`en`, `ro`, `de`). Optional region = ISO 3166-1 Alpha-2 (`en-GB`, `pt-BR`). Use the correct region code: it is `en-GB`, **not** `en-UK`. Region without language is invalid.
6. **Per-language self-referencing canonical.** Each language version's `rel="canonical"` must point to **itself** (the same-language URL). A canonical pointing to another language version cancels the hreflang for that page (see failure modes).
7. **`<html lang>` matches.** The document's `lang` attribute (and `dir` for RTL) should match the language the page actually serves and the hreflang value.

**Placement (any one, pick a single method):** hreflang can live in the `<head>` as `<link rel="alternate" hreflang="...">`, in the **HTTP `Link:` header** (useful for non-HTML files like PDFs), or in an **XML sitemap** via `xhtml:link` entries. The sitemap method scales best for large sets because the whole cluster lives in one file and is easy to audit.

Structured data is governed separately — route any schema questions through references/schema-2026.md (note: FAQ/HowTo earn no rich result as of ~2026-05-07 and are not a lever in any locale).

## Common failure modes

All PROVEN to break or neutralize hreflang:

- **Non-reciprocal links** — A→B without B→A. The unconfirmed annotation is dropped silently.
- **Missing x-default** — no defined fallback; users with an unmatched locale get an arbitrary version, and you lose control of the selector page's targeting.
- **Cross-language canonical** — the classic killer: `ro` page sets `canonical` to the `en` URL. This tells Google the pages are duplicates and the `en` one is primary, which **cancels the hreflang** and de-indexes the localized variant's identity. Canonicals must be per-language self-references (contract rule 6).
- **Mixing methods** — declaring hreflang in both `<head>` and the sitemap with inconsistent values, or partially in HTTP headers. Pick ONE method and keep it complete and consistent; conflicting declarations produce undefined behavior.
- **Wrong/region-only codes** — `en-UK`, a made-up region, or a region with no language; all invalidate the affected entries.

## RTL languages

For right-to-left scripts (Arabic, Hebrew, Persian, Urdu) (CONSENSUS):

- Set `dir="rtl"` on `<html>` (or the relevant container) alongside the matching `lang`.
- Use **logical CSS properties** (`margin-inline-start`, `padding-inline-end`, `inset-inline`, `text-align: start`) instead of hard left/right, so the same stylesheet mirrors correctly without an RTL-specific override sheet.
- This is a rendering/UX correctness concern that feeds technical-foundations.md (layout, INP under mirrored interaction); it does not change the hreflang contract — RTL pages follow the same rules above.

## Validation: scripts/hreflang_check.py

Use scripts/hreflang_check.py to audit the contract:

- **Default — single-page validation.** Given a URL (or local HTML), it checks self-reference, valid ISO 639-1 / 3166-1 codes (flags `en-UK` and friends), presence of `x-default`, one-value-one-URL within that page, and whether the per-page canonical is a same-language self-reference (catches the cross-language-canonical killer).
- **`--reciprocal` — return-tag check across the set.** Crawls the alternates a page declares and verifies each target links back (bidirectional rule 1) and that the cluster's value→URL mapping is consistent (rule 4). Run this before launching any new market.

Pair it with the indexability checks in references/technical-foundations.md (a perfectly annotated page still needs to be crawlable and rendered).
