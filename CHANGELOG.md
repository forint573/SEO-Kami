# Changelog

All notable changes to SEO-Kami are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/); this project adheres to [Semantic Versioning](https://semver.org/).

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

[1.1.0]: #110---2026-06-14--strategy--internationalization
[1.0.0]: #100---2026-06-14--initial-release
