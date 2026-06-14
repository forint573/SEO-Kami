# Technical Foundations: Indexability & Crawl

Foundation for BOTH classic search and AI features. Google's generative AI surfaces (AI Overviews, AI Mode) use publicly accessible, crawlable content and the SAME index as classic ranking. If you are not indexed you cannot rank OR be cited. [PROVEN] Evidence tiers: PROVEN (Google docs / direct measurement), CONSENSUS (practitioner agreement), CORRELATED (studies). Dated facts current as of 2026-06.

## Table of contents
1. robots.txt
2. Meta robots / X-Robots-Tag
3. Canonicalization
4. XML sitemaps
5. Crawl budget
6. Pagination
7. JavaScript SEO
8. hreflang
9. URL structure
10. Mobile-first indexing

## 1. robots.txt
- Controls CRAWLING, not indexing. A `Disallow`ed URL can still be indexed (URL-only, no snippet) if linked externally. To keep a page OUT of the index, allow crawl and use `noindex` — never block a page you want deindexed. [PROVEN]
- Lives at the host root only (`https://example.com/robots.txt`); one file per origin (scheme+host+port). Subdomains and `http`/`https` are separate. [PROVEN]
- Directives: `User-agent`, `Disallow`, `Allow`, `Sitemap` (absolute URL). Google supports `$` (end-anchor) and `*` (wildcard). Longest/most-specific matching path wins; on equal length, the least restrictive (`Allow`) wins. [PROVEN]
- `Crawl-delay` is IGNORED by Googlebot (set rate in Search Console / by capacity signals instead). [PROVEN]
- Common mistakes: blocking CSS/JS needed to render (breaks rendering and mobile evaluation); using robots.txt to "noindex" (the `noindex` directive in robots.txt is unsupported and ignored); a 5xx on robots.txt → Google treats site as fully disallowed; a 404 → Google assumes full allow; case-sensitive paths; trailing-slash mismatches. [PROVEN]

## 2. Meta robots / X-Robots-Tag
- `<meta name="robots" content="noindex">` (HTML head) or `X-Robots-Tag: noindex` (HTTP header, works for PDFs/images/non-HTML). Header and meta are equivalent in effect. [PROVEN]
- Common values: `noindex`, `nofollow`, `noindex, nofollow`, `noarchive`, `nosnippet`, `max-snippet:[n]`, `max-image-preview:[setting]`, `none` (= noindex,nofollow). [PROVEN]
- The page must be CRAWLABLE for `noindex` to be seen — do not also `Disallow` it in robots.txt, or Google never reads the tag. [PROVEN]
- Per-bot targeting: `<meta name="googlebot" content="...">`; AI/training control via `Google-Extended` token (robots.txt). [PROVEN]

## 3. Canonicalization
- `<link rel="canonical" href="...">` (or `Link:` HTTP header) is a HINT, not a directive; Google may pick a different canonical. [PROVEN]
- Use SELF-REFERENCING canonicals on every indexable page (absolute URL, including protocol/host). [CONSENSUS, low-risk]
- Cross-domain canonicals are valid (syndication → point to the original). [PROVEN]
- Avoid conflicts: every variant in a duplicate cluster should canonicalize to the SAME target; mixed signals (canonical vs. sitemap vs. internal links vs. redirects pointing different ways) cause Google to ignore your hint and choose its own. [PROVEN]
- Canonical-to-noindex is contradictory and self-defeating: a canonical says "consolidate to this page," `noindex` says "drop this page." Pick one. Never canonicalize variants to a noindexed URL. [PROVEN]
- Canonical target must return 200 and be the preferred indexable version; do not canonical to a redirect or a blocked URL. [PROVEN]

## 4. XML sitemaps
- Limits: max 50,000 URLs AND max 50 MB uncompressed per sitemap file; split larger sets and reference them in a sitemap index file. [PROVEN]
- Include ONLY indexable, canonical, 200-status URLs. Exclude noindex, redirected, blocked, non-canonical, and 4xx/5xx URLs — a sitemap full of non-indexable URLs erodes trust in the file. [PROVEN]
- `<lastmod>` should be accurate (W3C datetime); Google uses it as a signal only if consistently truthful. `<priority>`/`<changefreq>` are effectively ignored by Google. [PROVEN]
- Reference the sitemap in robots.txt (`Sitemap:` line) AND submit in Search Console. [PROVEN]
- URLs must be absolute and from the same host the sitemap is hosted on (or cross-host if verified via robots.txt reference). [PROVEN]

## 5. Crawl budget
- Two components: crawl-rate LIMIT (host capacity/server health) and crawl DEMAND (popularity + staleness). Budget = how many URLs Google will fetch in a window. [PROVEN]
- A real concern only for LARGE sites (~10k+ URLs) or sites with heavy auto-generated/parameter URLs; most sites never hit a ceiling. [PROVEN]
- Wasters: faceted-navigation/parameter explosion, infinite spaces (calendars), soft 404s, long redirect chains, duplicate content, slow responses (5xx/timeouts shrink the rate limit). [PROVEN]
- Levers: fix server speed, prune/consolidate low-value URLs, block crawl traps in robots.txt, return clean 404/410, keep sitemaps accurate, strong internal linking to priority pages. [PROVEN/CONSENSUS]

## 6. Pagination
- `rel="next"`/`rel="prev"` is NO LONGER used by Google (dropped ~2019); do not rely on it for indexing. [PROVEN]
- Each paginated page should be a self-canonical, crawlable, indexable URL with unique on-page content; do NOT canonical page 2..N to page 1 (hides deeper items). [PROVEN]
- Ensure crawlable `<a href>` links to all pages (not JS-only/button-only) so Googlebot can discover deep content. [PROVEN]
- "View-all" pages are acceptable if they load fast. Avoid `?page=` URLs that are noindexed AND the only path to products. [CONSENSUS]

## 7. JavaScript SEO
- Google renders in two waves: crawl HTML, then queue for headless-Chromium rendering (may lag). Primary content/links should exist in the SERVER-RENDERED HTML to avoid delay and discovery gaps. [PROVEN]
- Server-render (SSR) or pre-render/hydrate so critical content and internal links are in the crawled HTML, not injected only after client-side JS. [PROVEN]
- AI crawlers generally DO NOT execute JavaScript (GPTBot, ClaudeBot, PerplexityBot, etc. fetch raw HTML). Client-side-only content is invisible to them. SSR is mandatory for AI visibility. [PROVEN]
- Avoid: content behind user interaction, links as `onclick`/JS-only navigation, lazy-loading that never triggers for a crawler, blocking JS/CSS in robots.txt. [PROVEN]

## 8. hreflang
- Declares language/region variants: `<link rel="alternate" hreflang="xx-YY" href="...">` (head), or sitemap/HTTP-header equivalent. Format: ISO 639-1 language, optional ISO 3166-1 Alpha-2 region. [PROVEN]
- RECIPROCITY is mandatory: every URL in a set must list ALL alternates INCLUDING ITSELF, and each must link BACK. A non-reciprocal (missing return) annotation is ignored. [PROVEN]
- Include `hreflang="x-default"` for the fallback/unmatched-locale page (e.g. a language selector or default-region page). [PROVEN]
- Use absolute, canonical, indexable URLs. hreflang annotations must agree with canonicals — pointing an alternate at a URL that canonicalizes elsewhere is a conflict and breaks the set. [PROVEN]
- Common errors (Search Console flags): no return tags; wrong/invalid language or region codes (e.g. `en-UK` — should be `en-GB`); lang-mismatch (declared language differs from actual page language); pointing to redirected/non-200 URLs. [PROVEN]
- hreflang influences WHICH variant ranks for a user; it does NOT consolidate ranking signals or boost rankings. [PROVEN]

## 9. URL structure
- Prefer short, readable, lowercase, hyphen-separated (not underscores) URLs with words over IDs; stable over time. [CONSENSUS]
- One canonical URL per resource: pick `www` vs. non-`www`, `http`→`https`, trailing-slash policy, and 301 all others to it. [PROVEN — duplication, CONSENSUS — choices]
- Minimize parameters; avoid session IDs and tracking params in indexable URLs. Logical, shallow path hierarchy aids both users and crawl. [CONSENSUS]
- URLs are a weak/cosmetic ranking factor at best; do not break working URLs purely for keywords. [CONSENSUS]

## 10. Mobile-first indexing
- COMPLETE: Google indexes and ranks using the MOBILE version of pages for effectively all sites. The desktop version is not the indexed version. [PROVEN]
- Mobile and desktop must serve the SAME primary content, headings, structured data, metadata, internal links, images (with alt), and lazy-loaded content — do not strip content from mobile. Hidden-behind-tabs/accordions content on mobile is fully indexed. [PROVEN]
- Requirements: responsive design preferred; ensure robots meta and `hreflang` match across viewports; same `rel=canonical`; let Googlebot crawl all resources. [PROVEN]
- A page Googlebot-Smartphone cannot render or that hides content on mobile loses that content from the index. Test with the mobile rendering / URL Inspection tools. [PROVEN]
- CWV are measured on mobile field data first; mobile page experience feeds the same quality inputs (see core-web-vitals reference). [PROVEN]
