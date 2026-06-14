# Evidence tiers

SEO-Kami's core differentiator: every finding, recommendation, and claim it reports MUST carry exactly one evidence tier. A finding without a tier is incomplete and must not ship.

## Contents
- [The four tiers](#the-four-tiers)
- [Claim to tier quick table](#claim-to-tier-quick-table)
- [Myths and low-ROI moves](#myths-and-low-roi-moves)
- [Reporting rule](#reporting-rule)

## The four tiers

**PROVEN** — Google primary documentation or direct measurement. Verifiable, not opinion. Stable enough to act on without hedging.
- Core Web Vitals "good" thresholds: LCP <=2.5s, INP <=200ms, CLS <=0.1 (75th-percentile field data).
- INP replaced FID as the responsiveness vital on 2024-03-12; FID deprecated 2024-09-09.
- FAQPage rich results removed ~2026-05-07 (markup still valid, no enhancement except authoritative gov/health); HowTo earns no rich result on any surface.
- Google's 2026 AI-optimization guidance: "AEO and GEO are still SEO"; AI Overviews / AI Mode use the same index and core ranking systems — no separate AI ranking system, no AI text file needed.

**CORRELATED** — independent studies showing a statistical relationship. Correlation, NOT causation. Useful for direction, never stated as a guaranteed lever. Always name the source and sample.
- Ahrefs (75,000 brands, Aug 2025): branded web mentions correlate ~0.664 with AI-Overview visibility vs ~0.218 for backlinks (~3:1); Dec 2025 follow-up: YouTube mentions ~0.737.
- Muck Rack (1M+ AI citations): ~82% from earned media, ~94% from non-paid sources.
- Seer Interactive (53 brands, 5.47M queries): organic CTR ~37% lower on AIO-present queries; SparkToro: <1/3 of searches send a click.

**CONSENSUS** — broad practitioner agreement, no hard proof. Reasonable default practice; flag that it rests on judgment, not data.
- For AI citation, trust dominates: a backlink says WHERE to go, a brand mention says WHAT to trust — digital PR, third-party quotes, Reddit/Wikipedia/industry presence beat raw link-building.
- Entity optimization is durable: consistent NAP/name-description, authoritative About/author page, sameAs links, ideally Wikipedia/Wikidata.
- Engines differ: Google = index + quality systems; Perplexity = live retrieval favoring fresh, well-sourced pages; ChatGPT search = its own retrieval + training, skewing to authoritative sources.

**SPECULATIVE** — unproven or emerging. Low-cost experiments are fine, but never promise results. Default skepticism.
- llms.txt as a ranking/citation lever: proposed Sept 2024, published by Anthropic/Stripe/Vercel/Cloudflare, but Google gives it no special treatment and there is near-zero evidence AI crawlers fetch it during live retrieval. Ship if cheap; expect no lift.
- Any "rewrite content for AI" / "chunk for AI" tactic presented as a distinct discipline.

## Claim to tier quick table

| Claim | Tier |
|---|---|
| LCP <=2.5s / INP <=200ms / CLS <=0.1 are the "good" thresholds | PROVEN |
| INP is the hardest CWV to pass (~43% of sites fail) | PROVEN |
| CWV is a direct, standalone ranking factor | MYTH (Page Experience system retired 2023; it's a page-quality input/tiebreaker) |
| Indexability is the foundation for both classic search and AI features | PROVEN |
| AI crawlers generally don't execute JavaScript | PROVEN |
| FAQPage / HowTo schema earns rich results | MYTH (deprecated; FAQ removed ~2026-05-07) |
| Product / Review / Article / Recipe / Video / Event / LocalBusiness still earn rich results | PROVEN |
| Removing deprecated schema causes a ranking drop | MYTH (no drop) |
| E-E-A-T is a single score Google computes | MYTH (rater concept Google's systems approximate) |
| Helpful Content is now part of core ranking (since Mar 2024) | PROVEN |
| ~58-68% of searches are zero-click; ~83% on AIO queries | CORRELATED |
| Brand mentions correlate with AI-Overview visibility ~3:1 over backlinks | CORRELATED |
| ~82% of AI citations come from earned media | CORRELATED |
| A ~40-60 word self-contained answer near the top earns extraction | PROVEN-leaning (it's good SEO) |
| Entity consistency (NAP, sameAs, Wikidata) helps AI citation | CONSENSUS |
| llms.txt gets you cited or ranked | SPECULATIVE / HYPE |
| GEO/AEO is a new discipline that replaces SEO | MYTH ("still SEO") |
| Guaranteed AI citations are achievable | MYTH (probabilistic, query-dependent) |

## Myths and low-ROI moves

**"llms.txt is essential for AI visibility."** WRONG. Google crawls it with no special treatment; there is near-zero evidence ClaudeBot/PerplexityBot/GPTBot request it during live retrieval, and no measured citation lift. It only helps when a URL is pasted directly into a chat tool (and Perplexity reads it when handed one). DO INSTEAD: ship it if trivial, expect nothing; invest in earned mentions and indexable, people-first content.

**"FAQ schema wins AI answers."** WRONG. FAQPage rich results were removed ~2026-05-07 and structured data is not required for AI features or any AI shortcut. DO INSTEAD: write the answer in the visible HTML — a real question as an H2/H3 with an immediate 40-60 word answer that's quotable.

**"GEO/AEO replaces SEO."** OVERSTATED. Google's own guidance: AEO and GEO are still SEO; AI Overviews/AI Mode run on the same index and core quality systems with no separate ranking surface to game. DO INSTEAD: do foundational SEO well (crawlability, unique first-hand content, page experience) — that IS the AI optimization. Keep AEO (Google SERP answer features) distinct from GEO (generative answer engines).

**"More schema = better rankings."** WRONG. Schema unlocks specific rich results where eligible; it is not a ranking multiplier and adds nothing for deprecated types. DO INSTEAD: use valid JSON-LD only for types that still earn enhancements; don't pile on markup "for AI."

**"You can guarantee AI citations."** WRONG. Citation is probabilistic, query-dependent, and not directly controllable. DO INSTEAD: maximize the inputs that correlate (earned/PR mentions, entity clarity, verifiable specifics) and measure citation/mention SHARE over time, not a guaranteed placement.

**"Core Web Vitals are a direct ranking factor."** OVERSTATED. The Page Experience ranking system was retired in 2023; CWV is a page-quality input, a tiebreaker, and above all a conversion lever. DO INSTEAD: fix CWV from CrUX/field data (INP first: break up long JS tasks, yield to the main thread, use web workers, shrink the DOM) for users and conversion — not for an imagined ranking boost.

## Reporting rule

Tag every finding with one tier. Prefer PROVEN sources; when only CORRELATED evidence exists, name the study and sample and say "correlation, not causation." Never let SPECULATIVE claims wear PROVEN language. The tier is the honesty contract that separates SEO-Kami from hype-driven advice.
