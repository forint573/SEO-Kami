# Entity optimization & earned media

The differentiator most SEO skills miss: for AI citation, *who trusts you* outweighs *who links to you*. This file covers the link-vs-mention mechanic, the correlation data, entity optimization, a digital-PR playbook, and how `entity_check.py` supports it. Every claim is tagged by evidence tier.

## Contents
- [The core mechanic](#the-core-mechanic)
- [The correlation data](#the-correlation-data)
- [Entity optimization](#entity-optimization)
- [Earned-media / digital-PR playbook](#earned-media--digital-pr-playbook)
- [How entity_check.py supports this](#how-entity_checkpy-supports-this)
- [Hype to flag](#hype-to-flag)

## The core mechanic

(CONSENSUS) A backlink and a brand mention do different jobs:
- A **backlink** tells an engine WHERE to go — it's a navigational/authority edge in a link graph.
- A **brand mention** tells an engine WHAT to trust — it's corroboration that an entity exists, is named consistently, and is associated with a topic.

For classic ranking, links still carry weight. For AI citation (generative answer engines), trust dominates: the engine is deciding which sources to *quote*, not which page to *send a user to*. Unlinked mentions across many credible third-party sources build the entity association that makes a brand a likely citation. Digital PR, third-party quotes, and Reddit/Wikipedia/industry presence move AI citation more than classic link-building.

## The correlation data

All CORRELATED — independent studies, correlation NOT proven causation. The consistent direction across all of them: off-site brand presence and earned mentions track AI visibility better than backlinks.

- **Ahrefs, 75,000 brands (Aug 2025):** branded web MENTIONS correlate ~**0.664** with AI-Overview brand visibility, vs ~**0.218** for backlinks — roughly a 3:1 edge for mentions over links.
- **Ahrefs follow-up (Dec 2025):** YouTube mentions correlate ~**0.737** — the strongest single signal observed.
- **Muck Rack, 1M+ AI citations:** ~**82%** of citations come from earned media; ~**94%** come from non-paid sources. Paid placement is not the lever; earned coverage is.

Read these as "build off-site presence and earned/PR mentions," not "mentions cause citations." Citation remains probabilistic, query-dependent, and not directly controllable.

## Entity optimization

(CONSENSUS, durable) Make the brand/author/product an unambiguous ENTITY so engines can disambiguate it from look-alikes and attach the right topics. This is the most stable GEO lever because it's grounded in how knowledge graphs resolve entities, not in any one engine's ranking quirks.

- **Consistent NAP + name/description everywhere.** Same legal name, same one-line description, same address/contact across the site, profiles, directories, and citations. Inconsistency forces the engine to guess which entity it's seeing.
- **Authoritative About / author page.** Real identity, credentials, first-hand experience, links out to corroborating profiles. This anchors E-E-A-T (PROVEN/CONSENSUS) and the entity at once.
- **`sameAs` links** in `Organization`/`Person` JSON-LD pointing to the entity's other authoritative profiles (Wikipedia, Wikidata, Crunchbase, LinkedIn, official socials). This is the explicit "these are all the same entity" signal.
- **Wikipedia / Wikidata presence** where the entity genuinely meets notability — a strong corroboration node feeding knowledge graphs. Do not fabricate notability; failed/edited-out entries hurt.
- **Knowledge-graph disambiguation:** corroborating mentions that consistently pair the name with its topic, category, and people, so the engine resolves "Acme" to *your* Acme.

Note (PROVEN): structured data is NOT required for AI features and is not an AI shortcut. `sameAs`/`Organization` schema helps the *entity-resolution* job specifically (and earns a Knowledge Panel), not "AI ranking."

## Earned-media / digital-PR playbook

(PROVEN-leaning where noted, because these are also just good SEO)

- **Be quotable.** Put a self-contained ~40-60 word direct answer near the top; lead with verifiable specifics — numbers, dates, named sources — that a journalist or an engine can lift and attribute. Quotable specifics signal trust.
- **Get cited in third-party articles.** Original data, surveys, or a defensible POV give writers a reason to name you. Earned coverage in credible outlets is what the Muck Rack 82% reflects.
- **Reddit / industry / community presence.** Genuine participation where your audience already discusses the category builds the unlinked-mention corpus engines read.
- **Wikipedia presence** only where notability is real (see entity section).
- **Freshness + headings that mirror real questions** keep earned and owned content extractable.

Per-engine nuance (CONSENSUS):
- **Google AI Overviews / AI Mode** = your index + core quality systems; no special file, no separate AI ranking to game.
- **Perplexity** = live retrieval; favors fresh, well-structured, clearly-sourced pages; will read `llms.txt` when handed one.
- **ChatGPT search** = its own retrieval (historically Bing-influenced) + training; skews to authoritative, well-known sources — which is exactly where entity + earned-media work pays off.

## How `entity_check.py` supports this

`entity_check.py` audits the *mechanical* half of entity optimization — the part a script can verify — and surfaces gaps for the human/PR half:
- NAP / name / description **consistency** across the site and declared profiles (flags drift).
- Presence and validity of an **About/author page** with real bylines.
- `Organization`/`Person` JSON-LD with **`sameAs`** coverage; flags missing authoritative profiles.
- Wikipedia/Wikidata linkage status as a corroboration signal.

It cannot measure citation lift (probabilistic) or manufacture earned media — it tells you whether your *entity scaffolding* is consistent enough for engines to resolve you, then points at the digital-PR work that only humans do.

## Hype to flag

- "Add FAQ schema to win AI answers" — FAQPage rich results were removed ~2026-05-07; not a shortcut.
- "`llms.txt` gets you cited" — SPECULATIVE; near-zero evidence engines fetch it during live retrieval.
- "GEO/AEO replaces SEO" — it IS SEO; entity + earned media are durable SEO, not a new discipline.
- Any guaranteed-AI-citation promise — citation is probabilistic and query-dependent, not directly controllable.
- Treating the correlation numbers above as proof of causation — they are direction, not mechanism.
