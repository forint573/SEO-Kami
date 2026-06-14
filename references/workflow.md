# Workflow — end-to-end audit procedure

Evidence tiers: PROVEN (Google docs / direct measurement), CORRELATED (independent studies; not causation), CONSENSUS (practitioner agreement), SPECULATIVE (unproven/emerging). Every recommendation you emit MUST carry one.

## Contents
- [Scope question (ask once)](#scope-question-ask-once)
- [The 10-step order](#the-10-step-order)
- [Copyable checklist](#copyable-checklist)
- [Validate–fix–repeat loop](#validatefixrepeat-loop)
- [Escape hatches](#escape-hatches)
- [Script-to-step map](#script-to-step-map)

## Scope question (ask once)
Before crawling, ask one question and stop: **Quick or Full?**
- **Quick** — single URL or small set; indexability + CWV (field) + schema validity + top-of-page answer extraction. Minutes. Use for a landing page, a "why am I not ranking" gut-check, or a pre-publish pass.
- **Full** — whole site/section; all 10 steps including content/E-E-A-T, GEO/AEO, and entity/earned-media. Use for a quarterly audit, a traffic-loss investigation, or an AI-visibility push.

Ask once, then proceed. Do not re-prompt mid-audit. If the user names a single dimension up front (e.g. "just check my INP"), skip the question entirely — see [Escape hatches](#escape-hatches).

## The 10-step order
Rationale: **fix the foundation before the frontier.** Indexability and page-quality fundamentals gate everything downstream — including AI features, which use the same crawl and the same index (PROVEN). There is no separate AI ranking system to game on Google (PROVEN); GEO/AEO work that skips the foundation is wasted. Order is opinionated and deliberate; later steps assume earlier ones pass.

1. **Scope** — Quick vs Full (above). Sets crawl breadth and which steps run.
2. **Safe crawl** — fetch politely (respect robots, rate-limit, identify the agent), snapshot rendered + raw HTML. AI crawlers generally do NOT execute JS (PROVEN), so capture both; primary content must exist in crawled HTML.
3. **Indexability** — the gate. robots.txt, meta robots/X-Robots-Tag, canonicals, sitemap, status codes, render parity. If not indexed you can rank nor be cited (PROVEN). Nothing later matters until this passes.
4. **CWV (field first)** — pull CrUX/field data, not lab (PROVEN). Targets at 75th pct: LCP <=2.5s, INP <=200ms, CLS <=0.1. INP (replaced FID 2024-03-12; FID deprecated 2024-09-09) is the usual failure (~43% of sites miss 200ms; CORRELATED) — decompose into input delay + processing + presentation; fix via breaking long JS tasks, yielding to main thread, web workers, smaller DOM. Frame CWV honestly: the Page Experience system was retired in 2023; CWV is a quality input/tiebreaker and conversion lever, not a standalone ranking factor (PROVEN).
5. **Schema** — validate JSON-LD (not microdata). Earns rich results: Product, Review/AggregateRating, Article, Recipe, Video, Event, Organization, Person, LocalBusiness, Breadcrumb (PROVEN). Deprecated: FAQPage rich results removed ~2026-05-07 (markup valid, zero enhancement outside authoritative gov/health); HowTo earns no rich result anywhere (PROVEN). Removing deprecated schema causes no ranking drop; schema is not required for and is no shortcut to AI features (PROVEN).
6. **Content / E-E-A-T** — Experience, Expertise, Authoritativeness, Trust (Trust central) — a Quality-Rater concept Google's systems approximate, not one score (PROVEN). Operationalize: real bylines/credentials, first-hand experience, citations, current/accurate facts, off-site reputation (heightened for YMYL). The Helpful Content System folded into core ranking (March 2024 core update); recovery follows slow core-update cadence (PROVEN). Reward unique first-hand content with a POV; demote commodity/recycled/thin AI-spun pages. Watch spam policies: scaled content abuse, site-reputation abuse (parasite SEO), expired-domain abuse.
7. **GEO/AEO** — "AEO and GEO are still SEO" (PROVEN, Google 2026 guide). NOT needed: llms.txt/any AI text file, special schema, content chunking, rewriting "for AI", long-tail saturation (PROVEN). DOES help: foundational SEO + crawlability, unique people-first expert content, high-quality media, good page experience, and for commerce clean Merchant Center feeds + Google Business Profile (PROVEN). AEO (Google SERP answer features — featured snippets, PAA, Knowledge Panel, Sitelinks Searchbox) is distinct from GEO (generative answer engines). Extraction tactics that are just good SEO (PROVEN-leaning): a self-contained ~40–60 word answer near the top, headings mirroring real questions, verifiable specifics (numbers/dates/named sources), freshness. Engines differ (CONSENSUS): Google AI Overviews/AI Mode = your index + quality systems; Perplexity = live retrieval favoring fresh, well-sourced pages and DOES read llms.txt when handed one; ChatGPT search = own retrieval (historically Bing-influenced) + training, skews authoritative. llms.txt is SPECULATIVE as a ranking/citation lever — Google crawls it with no special treatment, near-zero evidence AI bots fetch it during live retrieval, no measured citation lift; low-cost to ship but expect none. Flag "llms.txt gets you cited" and "FAQ schema wins AI answers" as HYPE.
8. **Entity / earned-media** — the strongest GEO signal is off-site (CORRELATED): Ahrefs (75,000 brands, Aug 2025) found branded web mentions correlate ~0.664 with AI-Overview visibility vs ~0.218 for backlinks (~3:1); Dec 2025 follow-up put YouTube mentions at ~0.737. Muck Rack (1M+ AI citations): ~82% from earned media, ~94% non-paid. Mechanic (CONSENSUS): a backlink says WHERE to go, a mention says WHAT to trust — for citation, trust dominates. Make the brand/author an unambiguous ENTITY (CONSENSUS, durable): consistent NAP/name-description everywhere, authoritative About/author page, sameAs links, ideally Wikipedia/Wikidata, corroborating mentions. Prioritize digital PR, third-party quotes, Reddit/Wikipedia/industry presence over raw link-building.
9. **Verify** — re-run validators/field checks on each fix. Citation is probabilistic and query-dependent — never promise a guaranteed AI citation (HYPE). See loop below.
10. **Report** — every line carries an evidence tier and a fix. Report on impressions / visibility / AI-citation share / brand-mention growth, not sessions alone: ~58–68% of Google searches are zero-click (SparkToro: <1/3 send a click), ~83% for AI-Overview queries; Seer (53 brands, 5.47M queries) measured organic CTR ~37% lower on AIO-present queries (CORRELATED). Prioritize intents where a click still has value (transactional, deep, comparison/tool).

## Copyable checklist
```markdown
SEO-Kami audit — [site] — [date]
- [ ] 1. Scope confirmed (Quick / Full)
- [ ] 2. Safe crawl done (raw + rendered HTML snapshotted, robots respected)
- [ ] 3. Indexability: robots / meta / canonical / sitemap / status / render parity
- [ ] 4. CWV (FIELD): LCP <=2.5s | INP <=200ms | CLS <=0.1 (75th pct)
- [ ] 5. Schema: JSON-LD valid; deprecated FAQ/HowTo flagged, not blocking
- [ ] 6. Content/E-E-A-T: bylines, first-hand, citations, current facts, off-site rep
- [ ] 7. GEO/AEO: top ~40-60w answer; question headings; specifics; no AI-hype tactics
- [ ] 8. Entity/earned-media: consistent NAP, sameAs, About page, PR/mention plan
- [ ] 9. Verify: every fix re-validated (loop until clean)
- [ ] 10. Report: each finding tier-tagged; visibility metrics, not sessions alone
```

## Validate–fix–repeat loop
For each finding: **validate** (measure against the PROVEN target or run the validator) -> **fix** (smallest change that moves the metric) -> **re-validate** (same tool, same field source). Repeat until the check passes or you hit a hard dependency (e.g. CWV field data lags ~28 days — note the lag, don't re-test prematurely). Never mark a step done on lab/synthetic data when a field/CrUX source exists. A fix that touches an earlier step (e.g. a render change altering indexability) reopens that step.

## Escape hatches
If the user names a single dimension, skip Scope and run only that step plus its hard prerequisites:
- "Check my INP / speed" -> step 4 only (field data). Mention indexability only if the page is non-indexable.
- "Validate my schema" -> step 5 only; flag deprecated types without forcing removal.
- "Why aren't I cited in AI?" -> steps 7+8; state up front that citation is probabilistic and foundation-gated.
- "Am I indexed?" -> step 3 only.
Always still attach an evidence tier. Always still warn if a named single fix is blocked by a foundation failure (e.g. tuning INP on a noindexed page).

## Script-to-step map
| Step | Backing script (intended) |
|---|---|
| 2 Safe crawl | crawl/fetcher (polite, dual-snapshot) |
| 3 Indexability | indexability checker (robots/meta/canonical/sitemap/status/parity) |
| 4 CWV | field/CrUX puller (LCP/INP/CLS at 75th pct) |
| 5 Schema | JSON-LD validator (rich-result eligibility + deprecation flags) |
| 6 Content/E-E-A-T | content/author-signal auditor |
| 7 GEO/AEO | answer-extraction + SERP-feature checker |
| 8 Entity | entity/NAP/sameAs + mention-coverage checker |
| 9 Verify | re-runs the step's own validator |
| 10 Report | report assembler (tiers + visibility metrics) |

Steps 1 and 9 are procedural, not scripted. If a backing script is absent, run the step manually and say so in the report.
