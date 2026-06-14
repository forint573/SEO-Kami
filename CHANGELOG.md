# Changelog

All notable changes to SEO-Kami are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/); this project adheres to [Semantic Versioning](https://semver.org/).

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

[1.0.0]: #100---2026-06-14--initial-release
