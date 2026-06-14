# NOTICE — attribution & provenance

SEO-Kami is an original fusion skill. It re-implements and adapts ideas from
four prior open-source SEO skills. This file records what was borrowed and the
terms, so the provenance is honest and the licensing is clean.

## Adapted from (MIT — compatible, attribution preserved)

| Source | License | What SEO-Kami took (re-authored, not copied wholesale) |
|---|---|---|
| [AgricIDaniel/claude-seo](https://github.com/AgricIDaniel/claude-seo) | MIT (© 2026 agricidaniel) | The SSRF / per-redirect-revalidation pattern behind `scripts/lib/safe_http.py`; the "GEO is operationalized, defer to Google over hype" stance and citability framing in `references/geo-aeo.md`; the dated deprecation facts (FID→INP, FAQ/HowTo retired) reflected across the references; the content-quality scoring approach; the paid-API cost-guardrail concept. **Not taken:** the hard-coded community/marketing footer, release-blog/dual-repo machinery, or any commercial coupling. |
| [Bhanunamikaze/Agentic-SEO-Skill](https://github.com/Bhanunamikaze/Agentic-SEO-Skill) | MIT (© 2026 Bhanu Namikaze; © 2026 agricidaniel) | The finding-verification idea behind `scripts/finding_verifier.py`; the Finding/Evidence/Impact/Fix + confidence-label output contract behind `seo_common.py` and `references/output-contract.md`; the GitHub-repository-SEO vertical behind `scripts/github_seo_audit.py` and `references/github-seo.md`; the answer-block / citation-readiness DOM-signal approach; the bs4→stdlib graceful-fallback philosophy. |
| [seo-skills/seo-audit-skill](https://github.com/seo-skills/seo-audit-skill) | MIT (© 2024-present SEOmator) | The nonce-fenced-untrusted-block + invisible-character-stripping prompt-injection defense behind `scripts/lib/sanitize.py`; the spirit of a few standout deterministic checks (hreflang reciprocity, near-duplicate detection, YMYL signalling) — re-implemented in Python, the TypeScript engine itself was **not** ported. |

Per the MIT license, each project's copyright and permission notice is preserved
by reference here. No source files were copied verbatim from these projects;
shared techniques were re-authored for SEO-Kami's architecture.

## Studied but NOT used (license blocker)

| Source | License | Status |
|---|---|---|
| [SNLabat/SEO-GEO-AEO-Skill](https://github.com/SNLabat/SEO-GEO-AEO-Skill) | **None declared** (all rights reserved) | Used only as a **design reference**. Its report-design ideas and trigger-phrase craft informed SEO-Kami's *independently written* `references/report-design.md` and SKILL.md description. **No file or text was copied**, because the repository ships no license. |

## Knowledge sources

The 2026 SEO/GEO/AEO facts encoded in `references/` are grounded in primary and
independent sources (Google Search Central, web.dev, Anthropic Agent Skills
docs, and independent studies from Ahrefs, Muck Rack, SparkToro, and Seer
Interactive). Each reference file dates its volatile claims and cites where it
matters. See `references/evidence-tiers.md` for how claims are graded.
