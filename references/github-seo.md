# GitHub-repository SEO

A SEO-Kami differentiator: ranking and surfacing GitHub repositories. Distinct
from web-page SEO because GitHub controls the on-page surface (README, metadata)
while two indexes matter at once: GitHub's own search and Google's web index.
Evidence tiers per claim: PROVEN / CORRELATED / CONSENSUS / SPECULATIVE.

## Contents
- Discovery channels
- 100-point README rubric
- Repo metadata checklist
- github_seo_audit.py checks
- GEO/AI angle

## Discovery channels (how repos get found)

- GitHub search ranks on repo name, description, topics, README text, stars,
  recency, and `in:` qualifiers. Topics are first-class facets — a repo with
  topics appears under `topic:<name>` pages and topic search. CONSENSUS.
- Google indexes the rendered README and the repo page (description + About box
  become the title/meta-equivalent). The README is the de-facto landing page; a
  keyword-rich first paragraph and H1 do the heavy lifting. CONSENSUS.
- Same-index principle: Google's AI Overviews/AI Mode use the same crawl/index
  as classic search, so an indexed, well-described repo is eligible for both
  organic results and AI citation. PROVEN.
- Stars/forks are social proof and a GitHub-search signal, not a Google ranking
  factor; do not conflate. CONSENSUS.
- Crawlability: README content is server-rendered HTML on github.com, so it is
  fully crawlable (no JS-SEO problem). AI crawlers that skip JS still get it. PROVEN.

## 100-point README rubric (CONSENSUS — practitioner weighting)

These are the seven elements `github_seo_audit.py` scores; the weights below are
exactly what the script awards, so a fixed item maps 1:1 to a point gain.

| # | Element | Pts | What earns the points |
|---|---------|-----|-----------------------|
| 1 | Title / H1 (repo name + keyword) | 20 | A single clear `#` H1; primary keyword present, not just the bare package name |
| 2 | One-line description / tagline | 15 | A prose line of >=4 words near the top (not a heading/badge/HTML); states what + who-for; matches the repo description |
| 3 | Install section | 20 | Copy-paste command(s) — `npm install`/`pip install`/`go get`/"Getting started" |
| 4 | Usage / examples | 20 | A usage/quick-start section or a fenced code block showing a minimal runnable example |
| 5 | Badges | 10 | Informative shields.io badges (build/CI, version, license) — not decorative spam |
| 6 | License | 10 | License stated in the README (and, separately, a LICENSE file) |
| 7 | Links | 5 | Working outbound/doc/homepage links |

Total = 100. The heaviest weights sit on title + install + usage (60 pts): the
content that converts a discovered repo into a used one and that AI engines
extract as a direct answer. A self-contained ~40-60 word "what is this" answer
near the top also earns featured-snippet / AI extraction. PROVEN-leaning (it is
just good SEO applied to a README).

A README scoring <60 is "discoverable but not convertible"; <40 typically lacks
both a clear description and a usable quick start. Beyond the scored seven,
strong READMEs also add screenshots/demo GIFs, a scannable features list, and a
CONTRIBUTING link — improve these manually even though the script does not score
them.

## Repo metadata checklist

- Description: <=350 chars, keyword-forward, mirrors the README tagline. Becomes
  the Google title/snippet basis and the GitHub-search summary. CONSENSUS.
- Topics: GitHub allows up to 20 topics; use the full budget with real, searched
  terms (lowercase, hyphenated). Each is a discovery facet. PROVEN (limit).
- Homepage URL: set it — drives a do-follow-style outbound link and an entity
  signal to the project's canonical site. CONSENSUS.
- Social-preview image (Open Graph): 1280x640 px recommended; controls the card
  shown when the repo URL is shared (X, Slack, LinkedIn) and in some SERP/AI
  surfaces. Missing image = auto-generated grey card, lower CTR. CONSENSUS.
- Releases: tagged releases with notes are separately indexable URLs, add
  freshness, and feed package managers. CONSENSUS.
- About section: description + website + topics in one box; the highest-leverage
  metadata GitHub exposes. Fill all three. CONSENSUS.
- Pinned repos (profile/org): curate up to 6; raises crawl priority and
  human-discovery of the flagship repo. CONSENSUS.

## How github_seo_audit.py checks these

Run it as `python3 scripts/github_seo_audit.py owner/repo` (set `GITHUB_TOKEN`
to raise the API rate limit). It uses the GitHub REST API only — no scraping.

- Fetches repo metadata (`/repos/{owner}/{repo}`), topics, and the README
  (`/repos/{owner}/{repo}/readme`, base64-decoded).
- README rubric: scores the seven elements above (H1, one-line description,
  install, usage/examples, badges, license mention, links) and emits the 0-100
  total plus a per-element breakdown so each deficit is actionable.
- Metadata findings: description missing or very short; 0 topics (medium) or
  <5 topics (low) against the 20-topic budget; homepage URL not set; no license;
  no tagged releases.
- Each finding carries its evidence tier so users see what is PROVEN (e.g. the
  topic limit) vs. CONSENSUS practitioner weighting (the rubric points).

Items in the metadata checklist above that the script does **not** yet score —
the social-preview/OG image, About-box completeness, and pinned repos — are
manual checks; the script focuses on what the REST API exposes cleanly.

## GEO / AI angle

GitHub READMEs are heavily cited by AI engines because they are authoritative,
well-structured, and freshly maintained. Quotable specifics (version numbers,
benchmark figures, dated changelog entries) and question-shaped headings raise
extraction odds. CORRELATED (citation studies). Do NOT add FAQ schema (rich
result deprecated ~2026-05-07, no AI shortcut) or an llms.txt expecting a
citation lift (SPECULATIVE / HYPE). The durable lever is being an unambiguous
entity: consistent name/description across README, About, homepage, and package
registries, plus earned mentions linking back. CONSENSUS.
