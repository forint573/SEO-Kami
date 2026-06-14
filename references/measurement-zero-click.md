# Measurement in a Zero-Click World

How to reframe success metrics when most searches never produce a click. This is a positioning differentiator: SEO-Kami counsels measuring visibility and citation, not just sessions.

## Contents
- [The zero-click reality](#the-zero-click-reality)
- [What to measure now](#what-to-measure-now)
- [Tracking AI visibility: the prompt audit](#tracking-ai-visibility-the-prompt-audit)
- [Using Google Search Console](#using-google-search-console)
- [Prioritize intents where clicks still convert](#prioritize-intents-where-clicks-still-convert)
- [The reframe, stated plainly](#the-reframe-stated-plainly)

## The zero-click reality

The click is no longer the default outcome of a search. Plan for impressions without sessions.

- ~58-68% of Google searches end with no click (CORRELATED, SparkToro: fewer than 1 in 3 searches sends a click to the open web).
- On queries that trigger an AI Overview, ~83% end with no click (CORRELATED).
- Seer Interactive (53 brands, 5.47M queries): organic CTR on AIO-present queries runs ~37% below AIO-absent queries (CORRELATED — correlation, not proven causation; magnitude varies by query and position).

Implication: a page can grow in reach and influence while its click count flatlines or falls. Measuring only sessions will read that as failure when it may be success. The answer surface (AI Overview, featured snippet, knowledge panel) is consuming the click, not the demand.

## What to measure now

Track these alongside (declining) clicks — not instead of, since clicks still matter for transactional intents.

- Impressions — how often you surface, independent of click. The clearest signal that visibility holds even as CTR erodes.
- Visibility / share-of-voice — your presence across a tracked keyword/intent set relative to competitors. Position and impression share are the proxies; rank-tracking tools approximate it.
- AI-citation share — how often you are named/cited in AI Overviews, AI Mode, Perplexity, ChatGPT search answers for your target queries. There is no first-party Google metric for this (CONSENSUS); measure via third-party AI-visibility trackers and manual prompt audits. Treat as directional — citation is probabilistic and query-dependent, not directly controllable.
- Brand-mention growth — earned/unlinked mentions across the web (digital PR, Reddit, industry sites, YouTube). This is the strongest correlate of AI-Overview brand visibility: Ahrefs (75,000 brands, Aug 2025) found branded web mentions correlate ~0.664 with AIO visibility vs ~0.218 for backlinks (~3:1); Dec 2025 follow-up put YouTube mentions at ~0.737 (CORRELATED). Muck Rack (1M+ AI citations): ~82% from earned media, ~94% from non-paid sources (CORRELATED). Mentions are now a measurable input, not just a vanity number.

Why this set: a brand mention tells an AI engine WHAT to trust, a backlink tells it WHERE to go — for citation, trust dominates (CONSENSUS). So the scoreboard shifts from "did they land?" to "did we surface, get cited, and get talked about?"

## Tracking AI visibility: the prompt audit

AI-citation share has no first-party metric, so measure it directly: ask the AI engines the questions your buyers ask and record whether you show up. This is the demand side of GEO — `scripts/geo_aeo_scan.py` measures whether your *page* is extractable (the supply side); this audit measures whether engines actually *cite* you. Run both.

**The fixed prompt set** (buyer-intent, kept stable run-to-run so results are comparable). Fill in your category/brand/competitor:

- "What is the best [category] tool/service?"
- "[Your brand] vs [competitor]"
- "What are alternatives to [competitor]?"
- "[Your brand] review — is it any good?"
- "Recommend a [product type] for [specific use case]"
- "How do I [problem your product solves]?"

Run each prompt across the engines that matter for your market — ChatGPT search, Claude, Gemini / Google AI Mode, Perplexity — since they retrieve differently (see references/geo-aeo.md).

**Per-prompt observation schema** (record one row per prompt × engine):

| Field | Capture |
|---|---|
| Mentioned | Yes / No |
| Position | 1st / 2nd / nth recommendation, or absent |
| Accuracy | Is what it says about you correct? note errors |
| Sentiment | Positive / neutral / negative |
| Cited source | Which URL/page (if any) the engine attributed |
| Competitors named instead | Who showed up in your place |

**How to read it — and the honest evidence framing.** A SINGLE run is **SPECULATIVE**: LLM answers are non-deterministic, personalized, and shift as models and indexes update, so one snapshot proves little. Value comes from a **longitudinal series** — re-run the same prompt set on a cadence (monthly, or after a digital-PR push) and track the *trend*; a sustained rise in mention-rate/position is **CORRELATED** directional evidence. Do **not** collapse this into a single averaged "score": SEO-Kami keeps ONE 0-100 scoring contract for the deterministic audit only, and inventing a second number for a qualitative, drifting signal would overstate it. Keep a competitor column so "are we gaining or losing share?" is answerable.

**Acting on it.** Poor AI visibility is fixed by the levers in references/entity-earned-media.md, not by on-page tricks: comparison/"vs" pages, getting named in authoritative third-party reviews and roundups, a consistent entity description everywhere, and Wikipedia/Wikidata presence if notable. Inaccurate descriptions are usually a signal that the web's corroborating content about you is thin or stale — fix the sources, not the prompt.

## Using Google Search Console

GSC is the one first-party, free source of truth in this stack. Read it for trends, not vanity totals.

- Impressions and average position trends — the primary zero-click metric. Rising impressions with falling clicks usually means you are surfacing inside an answer feature, not losing relevance. Segment by query and page; watch position bands (1-3 vs 4-10) since AIO and snippets compress the value of classic position 1.
- CTR by query intent — split queries by intent. Falling CTR on informational queries is expected (the answer is shown in-SERP). Falling CTR on transactional/comparison queries is a real problem worth fixing.
- Query intent classification — bucket Performance-report queries into informational / navigational / transactional / commercial-investigation, then judge CTR against the right baseline per bucket rather than one site-wide number.
- Caveats: GSC reports Google-search impressions/clicks; it does NOT report AI-Overview citations or off-Google AI engines. Use it for the search half of the picture and layer external AI-visibility data on top. Always read field/trend data, not single-day snapshots.

## Prioritize intents where clicks still convert

If the click is scarce, spend effort where a click still carries value. Zero-click pressure is uneven across intent.

- Transactional ("buy", "price", "near me", branded purchase) — the user must reach a destination to convert; AI answers rarely complete the transaction. Click value stays high.
- Deep / research intent — questions whose full answer cannot fit a 40-60 word extraction; the snippet teases, the page delivers. Click value stays meaningful.
- Comparison / tool intent ("X vs Y", calculators, configurators, checkers) — interactive or multi-factor needs that an answer box cannot satisfy. Click value stays high.

Conversely, simple-fact informational intent ("what is", "definition", single-number lookups) is where zero-click is structural and likely permanent — pursue it for surfacing/citation and brand exposure, not for traffic. Set expectations accordingly per page.

## The reframe, stated plainly

This is an explicit redefinition of success. SEO-Kami says so out loud rather than letting clients keep an obsolete scoreboard:

- Old KPI: organic sessions as the headline number.
- New KPI set: impressions + share-of-voice + AI-citation share + brand-mention growth, WITH clicks kept as a secondary, intent-weighted measure — high stakes on transactional/deep/comparison intent, low stakes on simple-fact intent.

Stating this up front is the differentiator: a flat or declining click line is no longer prima-facie failure, and a strategy optimized only for sessions is mis-specified for the answer-surface era.
