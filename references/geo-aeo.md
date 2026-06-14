# GEO / AEO Reference

The backbone for answer-engine and generative-engine optimization. Every tactic carries an evidence tier: **PROVEN** (Google primary docs / direct measurement), **CORRELATED** (independent studies, correlation not causation), **CONSENSUS** (practitioner agreement, no hard proof), **SPECULATIVE** (unproven/emerging).

## Table of contents
1. [Core position: GEO/AEO is SEO](#1-core-position-geoaeo-is-seo)
2. [What Google says does / does NOT help](#2-what-google-says-does--does-not-help)
3. [Engine-by-engine retrieval guidance](#3-engine-by-engine-retrieval-guidance)
4. [Citability tactics](#4-citability-tactics)
5. [Citation correlation data](#5-citation-correlation-data)
6. [Entity optimization](#6-entity-optimization)
7. [llms.txt honest status](#7-llmstxt-honest-status)
8. [AEO: Google SERP answer features (distinct from GEO)](#8-aeo-google-serp-answer-features-distinct-from-geo)
9. [Hype to flag](#9-hype-to-flag)

---

## 1. Core position: GEO/AEO is SEO

**(PROVEN)** Google's official 2026 AI-optimization guidance states plainly: "AEO and GEO are still SEO." AI Overviews and AI Mode are rooted in Google's core ranking and quality systems and draw from the **same index** as classic search. There is no separate AI ranking system to game on Google.

**(PROVEN)** Indexability is the shared foundation. Google's generative AI features use publicly accessible, crawlable content. If you are not indexed, you can neither rank nor be cited. AI crawlers generally do NOT execute JavaScript — server-render or hydrate so primary content lives in the crawled HTML.

Define the terms and keep them separate:
- **AEO (Answer Engine Optimization)** — Google SERP answer features (featured snippets, People Also Ask, voice, Knowledge Panel, Sitelinks Searchbox). See section 8.
- **GEO (Generative Engine Optimization)** — being cited inside generative answer engines (Google AI Overviews/AI Mode, Perplexity, ChatGPT search). See sections 3–6.

## 2. What Google says does / does NOT help

**(PROVEN) NOT needed for AI features** — these are not levers, do not "optimize for AI" via:
- llms.txt or any AI text file
- special / extra schema markup ("AI schema")
- manually chunking content
- rewriting content "for AI"
- long-tail keyword saturation

The only test Google offers: "Is this content my visitors would find satisfying?"

**(PROVEN) DOES help:**
- Foundational SEO plus crawlability/indexability
- Unique, people-first content with genuine expert/experienced takes (ties to E-E-A-T; the Helpful Content System was folded into core ranking with the March 2024 core update)
- High-quality media (images, video) — more surfaces to appear on
- Good page experience (a quality input/tiebreaker, not a standalone ranking factor; the Page Experience system was retired in 2023)
- For commerce: clean Merchant Center feeds plus a complete Google Business Profile

## 3. Engine-by-engine retrieval guidance

**(CONSENSUS)** Engines retrieve and favor differently:

| Engine | Retrieval | Favors |
|---|---|---|
| Google AI Overviews / AI Mode | Your existing index + core quality systems; no special file | Whatever ranks well in core search; people-first content, media surfaces |
| Perplexity | Live retrieval at query time | Fresh, well-structured, clearly-sourced pages; DOES read llms.txt when a URL is handed to it |
| ChatGPT search | Its own retrieval (historically Bing-influenced) + training data | Authoritative, well-known sources; established entities |

Takeaway: Google rewards good SEO; Perplexity rewards freshness + structure + clear sourcing; ChatGPT skews to recognized authority. None of these is gamed by an AI-specific file.

## 4. Citability tactics

**(PROVEN-leaning — they ARE good SEO):**
- A self-contained **~40–60 word direct answer near the top** of the page earns extraction.
- **Headings that mirror real questions** users ask (question-shaped H2/H3).
- **Verifiable specifics** — numbers, dates, named sources — that are quotable and signal trust.
- **Freshness** — keep dates and facts current; cite when last updated.
- **Earned mentions** off-site (the dominant GEO lever; see section 5).

Note: citation is probabilistic, query-dependent, and not directly controllable. These tactics raise the odds of extraction; none guarantees a citation.

## 5. Citation correlation data

**(CORRELATED — strongest GEO signal set; correlation, not proven causation):**
- **Ahrefs** (75,000 brands, Aug 2025): branded web **mentions** correlate ~**0.664** with AI-Overview brand visibility vs ~**0.218** for backlinks — roughly **3:1** in favor of mentions.
- **Ahrefs** Dec 2025 follow-up: YouTube mentions correlate ~**0.737**.
- **Muck Rack** (1M+ AI citations): ~**82%** come from earned media; ~**94%** from non-paid sources.

**(CONSENSUS) Mechanic:** a backlink tells an AI engine WHERE to go; a brand **mention** tells it WHAT to trust — and for citation, trust dominates. Digital PR, third-party quotes, Reddit/Wikipedia/industry presence, and consistent entity descriptions move AI citation more than classic link-building.

## 6. Entity optimization

**(CONSENSUS, durable)** Make your brand / author / product an unambiguous **entity**:
- Consistent NAP and name+description everywhere
- An authoritative About / author page with real identity and credentials
- `sameAs` links to corroborating profiles
- Ideally Wikipedia/Wikidata presence
- Corroborating third-party mentions

## 7. llms.txt honest status

**(SPECULATIVE as a ranking/citation lever.)** Proposed by Jeremy Howard in Sept 2024; published by Anthropic, Stripe, Vercel, Cloudflare. But:
- Google crawls it with **no special treatment**.
- Near-zero evidence that ClaudeBot / PerplexityBot / GPTBot request it during **live retrieval**.
- No measurable citation lift attributable to it.
- It DOES work when a URL is pasted directly into a chat tool (the tool fetches and reads it on demand).

Net: low-cost to ship, expect no ranking/citation lift. Flag "llms.txt is essential for AI visibility" as **HYPE**.

## 8. AEO: Google SERP answer features (distinct from GEO)

These are zero-click SERP features, not generative AI answers. Keep AEO (Google SERP) separate from GEO (generative engines).

- **Featured snippets** — concise ~40–60 word answers; lists and tables get extracted for list/table snippets.
- **People Also Ask (PAA)** — a question as H2/H3 followed by an immediate, direct answer.
- **Voice** — favors the concise, conversational direct-answer pattern.
- **Knowledge Panel** — driven by entity strength: Organization/Person with `sameAs`.
- **Sitelinks Searchbox** — `WebSite` + `SearchAction` schema (JSON-LD).

Context: ~58–68% of Google searches end with no click (SparkToro: under 1/3 send a click); AI-Overview queries run ~83% zero-click. Seer Interactive (53 brands, 5.47M queries): organic CTR on AIO-present queries is ~37% lower than AIO-absent. Implication: measure impressions, visibility, AI-citation share, and brand-mention growth — not only sessions — and prioritize intents where a click still has value (transactional, deep, comparison/tool).

## 9. Hype to flag

- "GEO/AEO is a brand-new discipline that replaces SEO." — It IS SEO.
- "Add FAQ schema to win AI answers." — FAQPage rich results were removed ~2026-05-07 (markup still valid but yields no enhancement outside authoritative gov/health). Not a shortcut.
- "llms.txt gets you cited." — See section 7.
- Any guaranteed-AI-citation promise. — Citation is probabilistic, query-dependent, and not directly controllable.
