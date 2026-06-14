# Changelog

All notable changes to SEO-Kami are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/); this project adheres to [Semantic Versioning](https://semver.org/).

## [1.3.0] - 2026-06-15 — Second hardening round

A second adversarial pass (run against redirect chains, SPAs, multilingual sites, IDNs, and error pages) plus fresh primary-source currency checks. More correct, less code, no value lost.

### Added / currency (primary-source verified)
- **Newly-removed rich-result types flagged.** `schema_check` + `references/schema-2026.md` now know the types Google retired in its "simplifying search results" effort (ClaimReview, SpecialAnnouncement, Vehicle Listing, Course Info, and the Jan-2026 batch) — markup stays valid, no enhancement, ranking unaffected.
- **LCP-2.0s rumor flagged as unconfirmed.** Several blogs claim Google lowered the "Good" LCP threshold to 2.0s; web.dev still says **2.5s**, so SEO-Kami keeps 2.5s as PROVEN and labels 2.0s SPECULATIVE (a "proven vs hype" note in `references/core-web-vitals.md`).
- **Thin-content / SPA detection.** A page with almost no server-rendered text (and a SPA root container) now gets a "content may be invisible to crawlers" finding — the most important check for a client-rendered app, previously missing.

### Fixed
- **Un-auditable pages report `N/A`, not a letter grade.** A gated 403/JSON page used to render a misleading "Score 75 / Grade B"; it now shows `score: null, grade: "N/A"`.
- **`<title>` no longer bleeds into body text** — fixed a false "concise top-of-page answer" on empty SPA shells (and de-inflated word counts everywhere).
- **hreflang `es-419` (and other UN M.49 numeric regions) no longer flagged malformed** — this fired on github.com.
- **sameAs gap no longer double-penalized.** `geo_aeo_scan` and `entity_check` both flagged it; entity ownership is now consolidated in `entity_check`, which also distinguishes "no entity schema" from "entity present but no sameAs."
- **`geo_no_question_headings` downgraded** to `low` (a homepage having no question headings is normal, not a medium defect).

### Simplified (no capability lost)
- **Removed the provably-inert contradiction-suppressor** (~70 lines): it never fired once because collectors emit an absence finding XOR a presence finding, never both. `finding_verifier` is now an honest dedupe + re-score.
- **One shared dedupe** (`seo_common.merge_findings`) replaces the two divergent copies in the orchestrator and verifier.
- Removed dead helpers and unused imports.

## [1.2.0] - 2026-06-15 — Simpler & sharper

A correctness + usability pass driven by an adversarial audit that ran the tool against real sites. No new scope — the existing checks are now trustworthy, and the default path is one command.

### Added
- **One-command audit → report.** `seo_kami.py <url> --report md|html --out report.md` fetches, runs every check, merges, scores, and renders the report in a single call (the old 3-command chain still works for debugging).

### Fixed (effectiveness — these made scores untrustworthy)
- **Error/non-HTML pages are no longer audited as real pages.** A bot-blocked 403 (or a JSON/PDF response) used to yield a confident 22-finding F-grade audit; it now stops with one honest "not auditable" finding (`meta.auditable: false`). Gates on HTTP status + content-type across every collector.
- **Removed constant, page-independent score penalties** that dragged every page to a mediocre grade: CWV-unavailable (missing API key) and the standing earned-media recommendation are now `info` (0 pts), not `medium`; the GEO "citable specifics" check no longer penalizes the near-universal absence of .gov/.edu outbound links. Well-built sites now score in the high-80s instead of a flat 67.
- **`_same_site` host comparison** used `lstrip("www.")`, which stripped a character set, not the prefix (so `web.com` vs `eb.com` matched). Fixed — corrects internal/external link classification used by three collectors.
- **Brand-name false positives.** The check now matches the brand against every title segment (brand-first titles like "Stripe | …" no longer misfire) and reads `og:site_name` correctly.
- **Phone-number false positives.** The NAP regex no longer matches stats/years (e.g. "99.999% uptime"); it requires real phone structure (+country, (area), or 0-led). NAP-incomplete is `medium` only when a LocalBusiness schema is present, else `low`.
- **GitHub README rubric** recognizes HTML/centered-logo titles and the repo `description` field — `sindresorhus/awesome` went from a false 25/100 to 96/100.
- **Title/meta length** wording reframed as approximate (Google truncates by pixel width, not character count).

## [1.1.0] - 2026-06-14 — Strategy & internationalization

Adds a plan-and-grow layer on top of the audit-and-optimize core, plus deterministic hreflang validation. The additions came from a file-level audit of the SearchFit SEO plugin: only the genuinely-missing, currency-clean ideas were re-authored in (SearchFit ships no LICENSE, so it was a design reference only — see [NOTICE.md](./NOTICE.md)). Deprecated/fabrication-prone material (FAQ/HowTo-as-rich-results, estimated-volume/difficulty columns, SaaS branding) was deliberately left out.

### Added
- **Multilingual / international SEO** (`references/multilingual-seo.md`) — translation-vs-localization, per-market keyword research, URL-strategy decision (subdir vs subdomain vs ccTLD), and the hreflang correctness contract (PROVEN).
- **hreflang validator** (`scripts/hreflang_check.py`) — deterministic checks for self-reference, x-default, malformed codes, and conflicting targets; opt-in `--reciprocal` return-tag verification across the set. Wired into the `seo_kami.py` orchestrator (single-page mode; silent when no hreflang is declared).
- **Content strategy** (`references/content-strategy.md`) — pillar→cluster→keyword topical-authority planning, keyword clustering (semantic/SERP-overlap/intent), funnel mapping, a quick-win/big-bet priority matrix, and a content calendar — all prioritized by free signals, never invented volume.
- **Content brief + competitor gap** (`references/content-brief.md`) — turns one target query into a writer-ready brief, plus a competitor topic-gap / blue-ocean analysis sourced deterministically from sitemaps.
- **AI-visibility prompt audit** — a fixed buyer-intent prompt set and per-engine observation schema folded into `references/measurement-zero-click.md`; single runs tagged SPECULATIVE, longitudinal trends CORRELATED (no second scoring number invented).

## [1.0.0] - 2026-06-14 — Initial release

First public release. SEO-Kami is a 2026-current SEO/GEO/AEO audit skill where every finding carries an evidence tier (PROVEN / CORRELATED / CONSENSUS / SPECULATIVE) so recommendations are honest about what is measured versus merely believed.

### Added
- **Technical & indexability audit** — crawlability, robots/sitemap, render path, and the JS-SEO checks that decide whether content reaches both classic search and AI surfaces.
- **Core Web Vitals via PageSpeed Insights** — field/CrUX-first LCP, INP, and CLS against the PROVEN "Good" thresholds; INP-focused diagnostics.
- **Schema validation, 2026 rules** — JSON-LD checks that flag deprecated rich-result types (FAQPage, HowTo) and confirm types that still earn enhancements.
- **GEO/AEO extractability scan** — direct-answer blocks, question-mirroring headings, and quotable specifics; treats "AEO/GEO is still SEO" as the baseline and flags llms.txt hype.
- **Entity & earned-media check** — name/description consistency, sameAs, About/author signals, and the off-site brand-mention presence that correlates with AI-citation visibility.
- **Links audit** — internal structure and outbound/inbound signals.
- **Finding verifier** — re-checks claims and attaches the supporting evidence tier before anything ships in a report.
- **Report builder** — assembles tiered, prioritized output.
- **GitHub-SEO audit** — repository-level discoverability checks.
- **Evidence-tier tagging** — the core differentiator; applied across every recommendation.

### Security
- **SSRF-safe fetch** — shared HTTP layer that blocks private/loopback/link-local targets and redirect-based bypasses before any URL is retrieved.
- **Prompt-injection sanitizer** — strips/neutralizes adversarial instructions in fetched page content so crawled text can't hijack the audit.

### Provenance
This release fuses four prior skills. SEO-Kami is original work — code and references were written from scratch, not copied. It draws on claude-seo (MIT), agentic-seo (MIT), and seo-audit-skill (MIT), and used seo-geo-aeo (no license) as a design reference only. Full attribution is in [NOTICE.md](./NOTICE.md). Licensed MIT (see [LICENSE](./LICENSE)).

[1.3.0]: #130---2026-06-15--second-hardening-round
[1.2.0]: #120---2026-06-15--simpler--sharper
[1.1.0]: #110---2026-06-14--strategy--internationalization
[1.0.0]: #100---2026-06-14--initial-release
