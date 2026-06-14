# Keyword research with free signals (honestly)

How to do keyword research WITHOUT paid tools, and the hard limit you must disclose: there is no reliable free source for search VOLUME or DIFFICULTY. Every recommendation carries an evidence tier.

## Contents
- The honest limit (read first)
- Free demand signals
- Your own first-party data (highest value)
- Competitor on-page extraction
- Intent classification and page-type mapping
- When a paid API is the only honest answer

## The honest limit (read first)
- [PROVEN] No free tool gives accurate monthly search volume or a reliable difficulty score. Google's Keyword Planner shows bucketed ranges (e.g. "1K-10K") only, gates exact numbers behind active ad spend, lumps close variants together, and reports ad demand — not organic demand. Treat it as directional, never precise.
- [CONSENSUS] "Free volume" widgets (browser extensions, freemium SERP add-ons) typically re-sell or model the same gated Keyword Planner ranges or clickstream estimates with unknown error. Do not present these as ground truth.
- [CONSENSUS] What free signals CAN tell you reliably: which phrasings real people use, the shape of intent, the SERP features in play, and (from your own data) what already gets you impressions. They cannot tell you absolute demand or competitiveness. Say this plainly to the user.

## Free demand signals (phrasing + intent, not volume)
- [CONSENSUS] Google Autocomplete — reflects real, popular query prefixes. Mine systematically: seed + a/b/c..., seed + who/what/when/where/why/how/which, "seed for", "seed vs", "best seed", "seed near me". Reveals modifiers and long-tail variants, NOT their volume.
- [CONSENSUS] People Also Ask (PAA) — live question clusters Google associates with the topic; expands as you click. Maps the question space and sub-intents. Each PAA also signals an answer-feature opportunity (see AEO: question H2/H3 + a 40-60 word direct answer).
- [CONSENSUS] Related Searches (SERP footer) and "People also search for" — adjacent entities and lateral phrasings; good for topic-cluster discovery and entity coverage.
- [PROVEN] SERP-feature observation — read the live SERP itself as data: presence of featured snippet, PAA, image/video pack, shopping pack, local pack, or an AI Overview tells you both intent and click value. [CORRELATED] AI-Overview-present queries are ~83% zero-click and organic CTR runs ~37% below AIO-absent queries (Seer, 53 brands / 5.47M queries) — deprioritize pure-informational targets where AIO already answers; favor transactional, comparison, and tool intents where a click still has value.
- [CONSENSUS] Free aggregators (e.g. autocomplete-scraper UIs, forum/Reddit/Quora threads, Amazon/YouTube autocomplete, Wikipedia tables of contents) widen the phrasing and question set across surfaces. Still phrasing-only — no volume.

## Your own first-party data (highest value, genuinely free)
- [PROVEN] Google Search Console query export is the single best free keyword source you have: it reports YOUR actual impressions, clicks, CTR, and average position for queries Google already shows you for. This is measured demand for your specific pages, not a model.
  - Find "striking-distance" terms (position ~8-20, high impressions, low CTR) — your fastest realistic wins.
  - Find high-impression / zero-click queries — content gaps or intent mismatch to address.
  - Read CTR vs position to spot title/meta or SERP-feature cannibalization (e.g. an AIO eating your clicks).
  - Caveats: GSC samples/anonymizes low-volume queries, caps rows, and only covers terms you ALREADY surface for — it cannot find demand you have zero presence on.
- [CONSENSUS] Internal site-search logs — what visitors type into your own search box is unfiltered intent and vocabulary, including demand you don't yet have pages for. Pull from your site-search analytics or server logs. Small-N but unusually high-signal for commercial/transactional gaps.

## Competitor on-page extraction (free, manual)
- [CONSENSUS] Extract a competitor's actual on-page targeting: title tags, H1-H3 structure, URL slugs, meta descriptions, internal anchor text, and visible "related" or hub links. This reveals which phrasings they bet on and their topic-cluster architecture — not their traffic.
- [CONSENSUS] Cross-reference ranking competitors against the live SERP features to infer the intent the page must satisfy. This is qualitative; do not infer volume or their traffic from on-page alone.

## Intent classification and page-type mapping
- [CONSENSUS] Classify every keyword by dominant intent — and verify against the live SERP, which is the authority on intent:
  - Informational ("what is", "how to", "guide") -> article / explainer / tutorial. [PROVEN] Often AIO/snippet-heavy and zero-click; target only where a click retains value or for entity/topical authority.
  - Navigational (brand, product, login) -> homepage / brand / login / specific named page. Defend, don't chase.
  - Commercial investigation ("best", "vs", "review", "alternatives") -> comparison / review / listicle / tool. High click value even amid AIO.
  - Transactional ("buy", "price", "near me", "book", "free trial") -> product / pricing / category / local / signup page. Highest conversion value; prioritize.
- [CONSENSUS] Map one dominant intent to one page type; if the SERP mixes intents, the term may need separate pages or is too broad to target with a single URL.
- [CORRELATED] Because ~58-68% of all Google searches are zero-click (SparkToro: <1/3 send a click), prioritize intents where a click still has value and measure impressions / visibility / AI-citation share, not only sessions.

## When a paid API is the only honest answer
- [CONSENSUS] If the user needs absolute monthly search volume, trend lines, keyword difficulty, or competitor traffic estimates, tell them directly: no free source provides this reliably. The honest options are paid — DataForSEO (cheapest programmatic), Ahrefs, or Semrush. State that these are estimates/models too (clickstream-derived), not Google ground truth, just better-calibrated than anything free.
- [CONSENSUS] Recommend the paid step only when the decision actually depends on volume/difficulty (e.g. prioritizing a large keyword portfolio or sizing a market). For phrasing, intent, page-type mapping, and finding striking-distance wins, the free signals above are sufficient — do not upsell an API the user doesn't need.
