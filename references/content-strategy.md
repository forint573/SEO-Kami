# Content Strategy: Topical Authority, Clustering, Funnel & Calendar

One reference for planning a content program: how to build a topical-authority architecture, cluster keywords without cannibalizing yourself, tag the funnel, prioritize honestly (no fabricated volume), close gaps, and sequence a calendar with an internal-linking plan. SEO-Kami produces the PLAN/BRIEF here; it never ghostwrites the article — drafting is handed to the user's separate humanizer + translation skills.

Evidence tiers on every substantive claim — see references/evidence-tiers.md. Dated facts current as of 2026-06-14.

## Table of contents
- [1. Topical authority: the Hub-Spoke-Leaf method](#1-topical-authority-the-hub-spoke-leaf-method)
- [2. Keyword clustering heuristics](#2-keyword-clustering-heuristics)
- [3. Avoiding cannibalization: one cluster, one page](#3-avoiding-cannibalization-one-cluster-one-page)
- [4. Funnel-stage tagging and the modifier map](#4-funnel-stage-tagging-and-the-modifier-map)
- [5. Intent → page-type mapping](#5-intent--page-type-mapping)
- [6. Prioritization matrix (no fabricated volume)](#6-prioritization-matrix-no-fabricated-volume)
- [7. Content gap analysis](#7-content-gap-analysis)
- [8. Calendar, publishing order, internal linking](#8-calendar-publishing-order-internal-linking)
- [9. Success metrics](#9-success-metrics)

## 1. Topical authority: the Hub-Spoke-Leaf method

The named SEO-Kami method is **Hub-Spoke-Leaf** — a three-level content hierarchy that signals breadth + depth on a topic to both classic ranking and AI surfaces (which share Google's index — see references/technical-foundations.md).

- **Hub (pillar page)** — one broad-topic page that frames the whole subject and links out to every spoke. Targets a head/short-tail concept and an unmistakable topic, not a single keyword. (CONSENSUS)
- **Spoke (cluster article)** — one page per subtopic, each covering a distinct facet the hub only names. Each spoke targets a single keyword cluster. (CONSENSUS)
- **Leaf (supporting / long-tail page)** — narrow, specific pages answering one long-tail question, a single comparison, or one transactional/location query. Leaves feed the spoke they sit under. (CONSENSUS)

Why it works: comprehensive, well-interlinked coverage of a topic is a durable quality signal, and entity/topic coverage correlates with AI-Overview inclusion better than raw link count (see references/measurement-zero-click.md, references/geo-aeo.md). (CORRELATED) There is no "topical authority score" inside Google — treat it as an architecture discipline, not a metric you can read. (CONSENSUS)

Design rule: a hub with no leaves is a brochure; leaves with no hub are orphans. Every node must link up and the hub must link down (see §8).

## 2. Keyword clustering heuristics

A cluster is a set of keywords ONE page can satisfy. Build clusters with these four signals, strongest first:

1. **Live-SERP overlap (strongest signal)** — would a single page plausibly rank for all of these? Pull the top ~10 results for each keyword from the live SERP; if results substantially overlap across two keywords, they belong on the same page. This is the only clustering signal grounded in Google's own behavior rather than your guess about meaning. Observe SERPs per references/keyword-free-signals.md. (CONSENSUS)
2. **Shared search intent** — same dominant intent (informational / commercial / transactional / navigational) AND the same underlying job. "wireless headphones" and "buy wireless headphones" share a topic but split on intent — different pages. (CONSENSUS)
3. **Semantic similarity** — near-synonyms, plurals, reorderings, and close paraphrases ("running shoes for flat feet" / "best shoes flat feet running") that any one page would naturally cover. Use as a candidate generator, then confirm with SERP overlap. (CONSENSUS)
4. **Modifier pattern** — shared modifier signals shared intent and content type (see §4). Group "best X", "top X", "X reviews" together; group "how to X" separately. (CONSENSUS)

**Cluster-size guidance:** aim for ~3-15 keywords per cluster. Fewer than ~3 → the cluster is probably a near-duplicate of a neighbor; **merge** it. More than ~15 → the page would sprawl across multiple intents; **split** into a parent (spoke) and children (leaves). (CONSENSUS) These are working heuristics, not thresholds Google publishes.

**Special clusters that must be isolated** (never fold these into a general cluster):
- **Branded** keywords (your brand, product names, "[brand] login") — own intent, own defensive page; do not chase, defend (see references/keyword-free-signals.md). (CONSENSUS)
- **"X vs Y" / comparison** keywords — each comparison is its own page; "A vs B" and "A vs C" are different pages, not one. (CONSENSUS)
- **Location** keywords ("X in [city]", "X near me") — one page per location-intent; mixing locations onto one page dilutes both. (CONSENSUS)

**Orphan bucket:** keep an explicit ORPHAN list for keywords that fit no cluster yet — too unique, too thin, or unclear intent. Do not force-fit them; revisit when more siblings appear or park them as future leaves. An honest orphan list beats a junk cluster. (CONSENSUS)

## 3. Avoiding cannibalization: one cluster, one page

**Rule: one cluster = one page = one primary intent.** (CONSENSUS) Two of your own pages targeting the same cluster compete with each other — keyword *cannibalization* — splitting link equity, confusing Google's canonical choice, and depressing both. (CORRELATED — observed pattern, magnitude varies; not a Google-stated penalty.)

- Detect existing cannibalization from your own data: in the Google Search Console query export, a single query whose impressions/clicks bounce between two URLs (or whose position flickers) is the signature. (PROVEN — GSC is measured first-party data; see references/keyword-free-signals.md.)
- Fix by **consolidating** (merge thin duplicates, 301 the weaker URL into the stronger) or **differentiating** (re-target one page to a genuinely distinct intent/cluster). Canonicalize consolidations correctly per references/technical-foundations.md.
- Prevent at planning time: before creating a page, check it against your existing cluster map — if the cluster is already owned, extend that page, do not spawn a rival.

## 4. Funnel-stage tagging and the modifier map

Tag every cluster with a funnel stage so the calendar balances reach against revenue.

- **ToFu (top)** — awareness; broad informational intent. Earns impressions and brand mentions; expect low direct conversion and, increasingly, zero-click (see §9, references/measurement-zero-click.md).
- **MoFu (middle)** — consideration; commercial-investigation intent. Comparisons, listicles, "best" — high click value even amid AI Overviews.
- **BoFu (bottom)** — decision; transactional/navigational intent. Pricing, product, signup, local — highest conversion value and most click-resilient (AI rarely completes a transaction).

**Modifier → content-type map** (use as a default; the live SERP overrides it):

| Modifier pattern | Content type | Typical funnel stage |
|---|---|---|
| "best" / "top" / "X reviews" | Listicle / ranked roundup | MoFu |
| "how to" / "how do I" | Tutorial / step-by-step guide | ToFu–MoFu |
| "vs" / "alternative" / "vs [competitor]" | Comparison page | MoFu–BoFu |
| "for [audience]" ("for beginners", "for small teams") | Audience-tailored page | MoFu |
| "what is" / "definition" / "meaning" | Definitional guide / explainer | ToFu |
| "buy" / "price" / "near me" / "book" / "free trial" | Product / pricing / category / local / signup | BoFu |

(CONSENSUS) Note: "how to" and "what is" pages should NOT lean on FAQ or HowTo structured data as a rich-result lever — FAQ rich results were removed ~2026-05-07 and HowTo earns no rich result on any surface. Route all schema decisions through references/schema-2026.md. (PROVEN)

## 5. Intent → page-type mapping

Reuse the four-intent model and page-type mapping defined in references/keyword-free-signals.md — do not redefine it here. The operating rule for the calendar:

- **Match the page format to the dominant intent, verified against the live SERP** — the SERP is the authority on what Google considers the right intent. (CONSENSUS)
- **Never write a blog post for a transactional query.** "buy X", "X price", "X near me" want a product / pricing / category / local page, not an article — an explainer ranked for a transactional term converts poorly and is usually out-competed by the correct page type. (CONSENSUS)
- If the live SERP for a term mixes page types, the cluster is too broad or mixed-intent — split it (§2) or pick the dominant type and target the rest as leaves.

## 6. Prioritization matrix (no fabricated volume)

**The honest limit, stated up front:** there is NO reliable FREE source of search volume or keyword difficulty (see references/keyword-free-signals.md). This reference therefore carries **no** "Est. Volume", "Difficulty", "Est. Traffic", or "Est. Pages" columns, and you must never add them. Prioritize on signals you can actually observe.

Score each cluster on four observable factors, then place it on the matrix:

- **SERP-feature click value** — read the live SERP. Where an AI Overview already answers (≈83% zero-click) and no click remains, deprioritize; where intent is transactional / comparison / tool and a click still converts, prioritize. (CORRELATED — see references/keyword-free-signals.md, references/measurement-zero-click.md.)
- **GSC striking-distance** — clusters where you already rank ~positions 5-20 with real impressions are your fastest realistic wins; small on-page/internal-link work can move them onto page one. (PROVEN — measured first-party data.)
- **Topical-authority fit** — does the cluster fill a spoke/leaf under a hub you are building (§1)? On-topic clusters compound; off-topic ones do not. (CONSENSUS)
- **First-party business value** — does ranking serve a real commercial job (product fit, lead, BoFu intent)? Traffic with no business fit is vanity. (CONSENSUS)

**Matrix (high/low on opportunity vs effort/fit):**

| | High business + authority fit | Low business + authority fit |
|---|---|---|
| **Low effort** (striking-distance, click value present) | **Quick win** — do first | **Fill-in** — batch when convenient |
| **High effort** (no presence, competitive, build-heavy) | **Big bet** — plan deliberately, sequence after quick wins | **Avoid** — skip or park in ORPHAN |

(CONSENSUS) Quick wins are dominated by GSC striking-distance terms; big bets are net-new hubs/spokes you must earn from zero. Because absolute volume/difficulty is unknowable for free, this matrix deliberately ranks by *observed position + click value + fit*, not by modeled demand — say so to the user when presenting it.

## 7. Content gap analysis

Compare what you cover against what the topic (and your competitors) demand.

- **Existing-coverage inventory** — map your live URLs onto the hub/spoke/leaf model. Find hubs with missing spokes, spokes with no supporting leaves, and orphaned pages with no hub. Pull your URL set from the sitemap (references/technical-foundations.md) and your surfacing queries from the GSC export (references/keyword-free-signals.md). (PROVEN for the GSC half — it is measured data.)
- **Demand gaps** — questions and phrasings real users surface that you have no page for: GSC high-impression/zero-click queries, internal site-search logs, Autocomplete, People Also Ask, Related Searches (all in references/keyword-free-signals.md). These reveal demand you are missing, not its volume. (CONSENSUS)
- **Competitor-topic gaps** — subtopics competitors cover that you lack. Do not re-derive this here; the competitor-gap analysis lives in references/content-brief.md — pull its competitor-gap section and convert each missing subtopic into a candidate spoke or leaf. (CONSENSUS)

Output a gap list ranked by §6, not a raw dump. A gap with no business/authority fit is not a priority just because a competitor filled it.

## 8. Calendar, publishing order, internal linking

**Publishing order — build the hub first or cluster up?** Two valid sequences; pick per goal:

- **Hub-first** — publish the pillar, then ship spokes/leaves underneath it. Best when entering a new topic from low authority: the hub gives every later spoke an internal link target and a coherent home, and AI surfaces a complete topic earlier. (CONSENSUS)
- **Cluster-up** — ship several high-value spokes/leaves first (often GSC quick wins), then publish the hub that ties them together. Best when you already have fragments ranking and want fast quick-win movement before the bigger hub build. (CONSENSUS)

Either way, **front-load quick wins** from the §6 matrix for early measurable movement, and interleave one big-bet hub build per cycle so authority compounds rather than stalling on long projects.

**Cadence — explicitly NOT "daily AI publishing."** Mass/recycled or AI-spun content at volume is demoted, not rewarded, since Helpful Content folded into core ranking in March 2024. (PROVEN — Google primary docs.) Plan a sustainable cadence of genuinely useful pages; do not equate publishing frequency with authority.

**Internal-linking plan** (cross-link references/technical-foundations.md for URL/crawl mechanics):
- Every spoke and leaf links UP to its hub with descriptive anchor text. (CONSENSUS)
- The hub links DOWN to every spoke. (CONSENSUS)
- Each spoke links laterally to **≥1-2 sibling spokes** in the same cluster, so the cluster is interconnected, not a star with a dead rim. (CONSENSUS)
- Anchor text describes the destination topic (not "click here"); keep links crawlable `<a href>` (see references/technical-foundations.md on JavaScript/crawl). (PROVEN for crawlability.)
- Re-run the internal-linking pass each time a new spoke/leaf publishes — add its up-link, its sibling links, and the hub's new down-link in the same change.

## 9. Success metrics

Measure this program with the zero-click metric set in references/measurement-zero-click.md, NOT raw organic-traffic growth (~58-68% of searches are zero-click). (CORRELATED)

- **Impressions / share-of-voice** across the hub's cluster set — is the topic surfacing more over time? Primary signal (references/measurement-zero-click.md). (PROVEN that impressions are first-party GSC data.)
- **AI-citation share** — how often the program's pages are named/cited in AI Overviews, AI Mode, and third-party AI answers for target queries. Directional, no first-party Google metric. (CONSENSUS)
- **Brand-mention growth** — earned/unlinked mentions; the strongest measured correlate of AI-Overview visibility (~0.664 vs ~0.218 for backlinks). (CORRELATED — see references/measurement-zero-click.md, references/entity-earned-media.md.)
- **Clicks** kept only as a secondary, intent-weighted measure — high stakes on BoFu/transactional and deep/comparison clusters, low stakes on simple-fact ToFu pages (pursue those for surfacing and brand exposure, not sessions).

A hub whose impressions and citations climb while ToFu click counts stay flat is succeeding, not failing — set that expectation when the plan ships.
