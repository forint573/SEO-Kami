# SEO-Kami

SEO-Kami is a current (2026), evidence-tagged SEO/GEO/AEO Agent Skill. It audits a URL and returns recommendations where every claim carries an evidence tier — PROVEN (Google primary docs or direct measurement), CORRELATED (independent studies, correlation not causation), CONSENSUS (practitioner agreement), or SPECULATIVE (unproven/emerging). It fuses the working parts of four open-source SEO skills and fixes their shared blind spot: they conflate proven fundamentals with hype, and they underweight what actually moves AI-engine citation — brand entity strength and earned media, not backlinks. SEO-Kami separates proven from hype on every line, and weights mentions over links the way the 2025 data does (Ahrefs: branded mentions correlate ~0.664 with AI-Overview visibility vs ~0.218 for backlinks).

## Why it exists / the fusion

SEO-Kami is a synthesis, not a fork. It reuses ideas and structure from prior open-source skills, rewrites all content as original prose, and updates every volatile fact to 2026. Full attribution lives in [NOTICE.md](NOTICE.md).

| Source | License | What SEO-Kami took from it |
| --- | --- | --- |
| claude-seo | MIT | The router/skill shape and the idea of script-backed checks invoked from a single SKILL.md entry point. |
| agentic-seo | MIT | The audit-as-orchestrated-pipeline pattern — discrete checks (technical, schema, links) feeding one report. |
| seo-audit-skill | MIT | Concrete technical-audit checks and report structure for a crawl-and-grade pass. |
| seo-geo-aeo | no license | Design reference only. Used to shape the GEO/AEO topic coverage. No code or text was copied, because it carries no license; treated as inspiration, not source. |

The shared blind spot across all four: they present tactics without distinguishing Google-confirmed facts from practitioner folklore, and their GEO/AEO advice leans on backlinks and structured-data tricks instead of entity and earned-media signals. SEO-Kami's evidence tiers and entity/mention weighting are the fix.

## What makes it different

- **Evidence tiers on every recommendation.** Nothing ships without a tier. CWV thresholds and schema deprecations are PROVEN; citation-correlation numbers are CORRELATED (correlation, not proven causation); `llms.txt` as a ranking/citation lever is SPECULATIVE and flagged as hype where claimed otherwise.
- **Entity and earned-media weighting.** GEO scoring follows the 2025 evidence: branded web mentions correlate ~0.664 with AI-Overview brand visibility vs ~0.218 for backlinks (~3:1); Muck Rack found ~82% of AI citations come from earned media. The skill scores brand-entity consistency and off-site presence, not just link counts.
- **Zero-click measurement.** It frames success as impressions / visibility / AI-citation share / brand-mention growth rather than sessions alone, because ~58-68% of Google searches end without a click and AI-Overview queries run ~83% zero-click.
- **Built-in finding verification.** `finding_verifier.py` re-checks claims before they reach the report, so findings are grounded in what was actually observed rather than asserted.
- **Optional GitHub-SEO.** `github_seo_audit.py` audits a repo's discoverability (README, topics, metadata) when you point it at a GitHub project.
- **Zero mandatory paid APIs.** Standard-library-first Python. Everything core runs with no keys. Optional keys (`PAGESPEED_API_KEY`, `GITHUB_TOKEN`) unlock field-data and higher-rate-limit paths but are never required.

## Install

SEO-Kami is an Agent Skill (agentskills.io spec). Install it by copying the skill folder into your skills directory.

- **Claude Code:** copy this folder to `~/.claude/skills/seo-kami`.
- **Claude.ai / Cursor / Codex:** copy it into that tool's skills directory.

```
cp -R SEO-Kami ~/.claude/skills/seo-kami
```

Then invoke it by asking your agent to audit a URL, for example: "Audit https://example.com with SEO-Kami." The agent reads `SKILL.md`, routes to the relevant references and scripts, and runs the checks.

## Quickstart

One command does the whole audit — fetch, run every check, merge, score, and write the report:

```
python3 scripts/seo_kami.py https://example.com --report md --out report.md
```

Without `--report` it prints the JSON envelope; add `--no-cwv`/`--no-links` to skip the slower network checks. Any single check also runs standalone:

```
python3 scripts/seo_kami.py https://example.com            # JSON findings
python3 scripts/schema_check.py <url>                      # one dimension
python3 scripts/hreflang_check.py <url> --reciprocal       # i18n, with return-tag check
```

If a URL returns non-200 or non-HTML, the audit stops with one honest "not auditable" finding rather than inventing results from an error page.

## Layout

```
SEO-Kami/
  SKILL.md                  # router / entry point the agent reads first
  README.md
  LICENSE                   # MIT
  NOTICE.md                 # attribution to the source skills
  references/               # 16 evidence-tagged docs (CWV, schema, GEO/AEO, E-E-A-T,
                            #   multilingual, content-strategy, content-brief, ...)
  scripts/
    seo_kami.py             # orchestrator
    technical_audit.py
    schema_check.py
    cwv_check.py
    geo_aeo_scan.py
    entity_check.py
    links_audit.py
    hreflang_check.py       # deterministic hreflang / i18n validator
    finding_verifier.py
    report_build.py
    github_seo_audit.py
    seo_common.py
    lib/
      safe_http.py          # SSRF-guarded fetch + per-redirect re-validation
      sanitize.py           # prompt-injection sanitiser for crawled content
  agents/
    seo-verifier.md         # adversarial subagent: verify findings before reporting
  assets/
    schema-templates.json   # JSON-LD templates for types that still earn rich results
  tests/
    test_smoke.py           # offline smoke tests for the scripts
```

## Requirements

- Python 3.8+ (standard-library-first; no install step for core checks).
- `requests` is optional — scripts fall back to the standard library when it is absent.
- No API keys required. Optional environment variables:
  - `PAGESPEED_API_KEY` — enables PageSpeed Insights / CrUX field-data lookups for Core Web Vitals.
  - `GITHUB_TOKEN` — raises GitHub API rate limits for `github_seo_audit.py`.

## License

MIT. See [LICENSE](LICENSE) and the attribution in [NOTICE.md](NOTICE.md).
