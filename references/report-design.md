# Report design — the SEO-Kami deliverable

How to turn a verified finding set into a client-facing report. The format is
tool-agnostic (Markdown first; HTML/DOCX optional) and fully parameterized —
**no hardcoded paths**. `scripts/report_build.py` renders this structure from an
audit JSON; this file is the spec it follows and the guide for doing it by hand.

## Contents
- [Inputs and invocation](#inputs)
- [Report structure](#structure)
- [Severity coding](#severity)
- [Priority matrix](#priority-matrix)
- [Evidence-tier legend](#tier-legend)
- [Principles](#principles)

## Inputs and invocation {#inputs}

`report_build.py` accepts either an `emit()` envelope (from any scanner or the
`seo_kami.py` orchestrator) or `finding_verifier.py` output. Always prefer the
**verified** set — report what survived adversarial review, not the raw dump.

```
# verify first, then render
python3 scripts/seo_kami.py https://example.com > audit.json
python3 scripts/finding_verifier.py audit.json > verified.json
python3 scripts/report_build.py verified.json --format md --out report.md
python3 scripts/report_build.py verified.json --format html --out report.html
```

Output path is always supplied by the caller via `--out` (default: stdout).
Date is supplied via `--date` or left as a clearly-marked `{{date}}` token — the
script never bakes in a machine-specific path or a stale session date.

## Report structure {#structure}

1. **Cover** — site/URL, report date, overall score + letter grade.
2. **Executive summary** — 2-4 sentences: the headline state, the single most
   important fix, and the one strongest opportunity. Plain language.
3. **Score by dimension** — a table of the audited dimensions (technical,
   schema, content/E-E-A-T, GEO/AEO, entity, links) with counts by severity.
4. **Prioritized findings** — grouped by severity (Critical → Info). Each finding
   renders its full contract: **Finding / Evidence / Impact / Fix / Confidence /
   Evidence tier** (see `output-contract.md`).
5. **Priority matrix** — the triage table below; the part clients act on.
6. **Evidence-tier legend** — so readers know what is proven vs. correlated.
7. **Appendix** — raw audit JSON reference / methodology note, including the
   honest limits (WebFetch is lossy; CWV/keyword/backlink data need their tools).

## Severity coding {#severity}

| Severity | Label | Meaning |
|---|---|---|
| critical | 🔴 Critical | Blocks indexing/ranking now (e.g. `noindex` on a money page) |
| high | 🟠 High | Material loss of visibility or eligibility |
| medium | 🟡 Medium | Real but non-urgent; schedule it |
| low | 🔵 Low | Minor polish / recommended-not-required |
| info | ⚪ Info | Confirmation or context, no action |

Use the same single 0-100 score everywhere (`seo_common.score`): 100 minus
capped severity penalties (critical −25, high −12, medium −5, low −2). Grades:
A ≥ 90, B ≥ 75, C ≥ 60, D ≥ 40, F < 40. One scoring contract — never a second.

## Priority matrix {#priority-matrix}

Map each finding to an action lane by severity and rough effort. This is what
turns a list into a plan.

| Lane | Includes | When |
|---|---|---|
| **Fix now** | Critical findings | This week — they cap everything above them |
| **This sprint** | High severity | Next 2 weeks |
| **Quick wins** | Low effort + high/medium impact (e.g. add a meta description, set repo topics) | Anytime — bank the easy points |
| **Backlog** | Medium/low, higher effort | Scheduled, after the above |

"Effort" is a judgment call — annotate it; do not fabricate engineering
estimates. A Quick Win is anything fixable in minutes with outsized payoff.

## Evidence-tier legend {#tier-legend}

Every report carries this legend so a reader knows how much to trust each line
(full definitions in `evidence-tiers.md`):

- **Proven** — Google primary docs or direct measurement.
- **Correlated** — independent study; correlation, not causation.
- **Consensus** — practitioner agreement, no hard proof.
- **Speculative** — emerging/unproven; act only if cheap.

## Principles {#principles}

- **Lead with the verified headline**, not a feature tour. The first thing the
  reader sees is the score and the one fix that matters most.
- **Every claim is tagged.** Never present a Speculative tactic with the
  confidence of a Proven one — that is the whole point of SEO-Kami.
- **No fabricated numbers.** If a metric needs CrUX/GSC/PageSpeed and you don't
  have it, the report says so and names the tool — it does not guess.
- **Parameterize everything.** Paths, dates, and site names come from inputs.
  A report that hardcodes a path is broken for the next user.
