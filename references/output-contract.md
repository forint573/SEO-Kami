# Output Contract

Every SEO-Kami finding ships in one fixed shape, carries a confidence and an evidence tier, and rolls up into a single 0-100 score. This file defines that shape, the anti-hallucination rules, and the scoring math. Scripts in this repo already emit findings in this structure.

## Table of contents
- [The finding format](#the-finding-format)
- [Confidence vs evidence tier](#confidence-vs-evidence-tier)
- [Two GOOD findings](#two-good-findings)
- [Two BAD findings (and why)](#two-bad-findings-and-why)
- [Anti-hallucination rules](#anti-hallucination-rules)
- [The single 0-100 score](#the-single-0-100-score)

## The finding format

Each finding has exactly these fields, in order:

- **Finding** — one declarative sentence naming the issue.
- **Evidence** — the observed fact that proves it: a crawled value, a header, a measured metric, a URL. No claim may exist without an Evidence line that an auditor could re-check.
- **Impact** — what it costs in ranking, indexability, AI-citation, or conversion terms. Frame honestly; do not inflate.
- **Fix** — the concrete change, specific enough to act on without a follow-up question.
- **Confidence** — `Confirmed` | `Likely` | `Hypothesis`.
- **Evidence tier** — `PROVEN` | `CORRELATED` | `CONSENSUS` | `SPECULATIVE`.

Confidence and tier are separate axes (see below). A finding may be `Confirmed` (we measured it) yet `CORRELATED` (the link to outcomes is correlational), e.g. a brand-mention gap.

## Confidence vs evidence tier

- **Confidence** = how sure we are the *site has this property*. `Confirmed` = directly observed in the crawl/measurement. `Likely` = strong indirect signal, one inference step. `Hypothesis` = plausible, not yet checked — must say so.
- **Evidence tier** = how sure the field is that *fixing it changes outcomes* [these tiers are SEO-Kami's core differentiator]:
  - **PROVEN** — Google primary docs or direct measurement (CWV thresholds, indexability, schema deprecations).
  - **CORRELATED** — independent studies; correlation, not causation (Ahrefs, Muck Rack, Seer, SparkToro).
  - **CONSENSUS** — practitioner agreement, no hard proof.
  - **SPECULATIVE** — unproven/emerging (e.g. llms.txt as a ranking/citation lever).

## Two GOOD findings

**Good #1 — measured, PROVEN**
- Finding: INP fails the "Good" threshold on the product template.
- Evidence: CrUX 75th-percentile field INP = 412ms on `/products/*` (threshold is <=200ms; [PROVEN] INP replaced FID 2024-03-12).
- Impact: Responsiveness is a page-quality input and a conversion lever; ~43% of sites fail 200ms, so this is a real differentiator, not a tiebreaker-only nicety.
- Fix: Break the long JS tasks in the add-to-cart handler, yield to the main thread, move the price-recalc work to a web worker; re-measure from CrUX, not lab.
- Confidence: Confirmed. Evidence tier: PROVEN.

Why it is good: starts from field data, cites the exact metric and threshold, names a mechanism, and frames CWV honestly (input + lever, not a direct ranking factor).

**Good #2 — observed gap, CORRELATED**
- Finding: Brand has almost no off-site earned mentions relative to its backlink profile.
- Evidence: Crawl + mention scan found 1,140 referring domains but only 9 unlinked brand mentions in editorial/news sources over 12 months.
- Impact: For AI-Overview visibility, branded web mentions correlate ~0.664 vs ~0.218 for backlinks ([CORRELATED] Ahrefs, 75,000 brands, Aug 2025 — ~3:1). A mention tells an engine *what to trust*; this site is link-rich, trust-signal-poor.
- Fix: Run digital PR for third-party quotes and named-source coverage; seek Reddit/Wikipedia/industry presence; keep one consistent entity description everywhere.
- Confidence: Confirmed. Evidence tier: CORRELATED.

Why it is good: the gap is measured (`Confirmed`), but the tier is honestly `CORRELATED` — the study is correlation, not proof, and the Evidence line says so.

## Two BAD findings (and why)

**Bad #1 — "missing" without a crawl**
- Finding: Site is missing FAQ schema, hurting AI visibility.
- Why it is bad: Two failures. (1) It asserts *missing* without a crawl confirming absence — forbidden. (2) FAQPage rich results were removed ~2026-05-07; "add FAQ schema to win AI answers" is hype, not a fix. Tagging this PROVEN would be a fabrication. A correct finding would only flag deprecated FAQ markup *if a crawl found it*, and frame removal as zero-loss.

**Bad #2 — vague + invented metric**
- Finding: Page speed is bad and is killing your rankings; fixing it will boost traffic ~30%.
- Why it is bad: "bad" has no Evidence value (no metric, no URL, no threshold). The "~30%" is an invented number with no source. It also overstates CWV as a direct ranking factor — the Page Experience ranking system was retired in 2023. No measurement, no tier that could honestly apply, a fabricated lift figure: three separate contract violations.

## Anti-hallucination rules

- **Never flag "missing" until a crawl confirms absence.** Absence is a measured state, not an assumption. No crawl evidence -> no missing-X finding.
- **Never invent metrics, lifts, or percentages.** Every number traces to a measurement or a cited study. If you cannot measure it, do not state it.
- **Every finding needs a checkable Evidence line.** If an auditor cannot reproduce the observation from the Evidence field, the finding is not shippable.
- **Tag the tier honestly.** PROVEN only for Google primary docs or direct measurement. Do not promote CORRELATED/CONSENSUS/SPECULATIVE claims to PROVEN to sound confident. llms.txt as a ranking/citation lever stays SPECULATIVE; "llms.txt is essential for AI visibility" is flagged as HYPE.
- **Don't overstate causation.** CWV, E-E-A-T, and AI-citation are inputs/approximations/probabilistic — never guaranteed levers. No guaranteed-AI-citation promises.
- **Hypotheses must label themselves.** If unverified, Confidence = `Hypothesis` and the Fix should include the check that would confirm it.

## The single 0-100 score

One score per audit. Start at **100**, subtract capped severity penalties:

| Severity | Penalty each |
|----------|--------------|
| Critical | 25 |
| High     | 12 |
| Medium   | 5  |
| Low      | 2  |

Penalties are summed and the score is floored at 0 (`score = max(0, 100 - sum(penalties))`). "Capped" means the per-finding penalty is the value above — a category cannot drain the score arbitrarily through many low findings beyond their listed weight. Grade bands:

| Grade | Score |
|-------|-------|
| A | >=90 |
| B | >=75 |
| C | >=60 |
| D | >=40 |
| F | <40  |

A single Critical (indexability blocked, no-indexed homepage) drops an otherwise-perfect site to 75 (B), which is intended: foundation failures dominate. The repo's scripts already emit findings and the rolled-up score in this exact shape.
