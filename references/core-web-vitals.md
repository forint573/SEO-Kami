# Core Web Vitals (INP / LCP / CLS) — 2026

All claims here are **PROVEN** (Google primary docs / direct measurement) unless tagged otherwise.

## Contents
- [Thresholds](#thresholds)
- [INP replaced FID](#inp-replaced-fid)
- [What INP measures + its three sub-parts](#what-inp-measures--its-three-sub-parts)
- [Concrete fixes](#concrete-fixes)
- [Field (CrUX) vs lab](#field-crux-vs-lab)
- [Data sources: cwv_check.py / PSI / CrUX](#data-sources-cwv_checkpy--psi--crux)
- [The honest ranking framing](#the-honest-ranking-framing)

## Thresholds
"Good" is judged at the **75th percentile of field data** (real users, segmented by device). All three must pass; the 75th-percentile gate means tail users matter, not the median.

| Vital | Good | Needs improvement | Poor |
|---|---|---|---|
| LCP (Largest Contentful Paint) | <=2.5s | <=4.0s | >4.0s |
| INP (Interaction to Next Paint) | <=200ms | <=500ms | >500ms |
| CLS (Cumulative Layout Shift) | <=0.1 | <=0.25 | >0.25 |

## INP replaced FID
- INP became the official responsiveness Core Web Vital on **2024-03-12**.
- FID (First Input Delay) was **deprecated 2024-09-09** and is gone. Treat FID only as a historical/deprecated note; do not recommend or report it.
- INP is the **hardest vital to pass** — roughly **43% of sites fail** the 200ms bar (worst pass rate of the three).

## What INP measures + its three sub-parts
INP measures responsiveness across the **whole page lifecycle**, reporting (near) the worst interaction latency a user experienced on the visit. It counts **only clicks, taps, and keypresses** — NOT scrolling, hovering, or zooming. Each measured interaction decomposes into:
1. **Input delay** — time from the user action until the event handler can start (main thread busy with other work).
2. **Processing duration** — time the event handlers themselves take to run.
3. **Presentation delay** — time to recompute layout/style and paint the next frame after handlers finish.
Long JavaScript tasks blocking the main thread are the usual culprit across all three.

## Concrete fixes
**INP** — break up long JS tasks; **yield to the main thread** (e.g. `scheduler.yield()` / `setTimeout` chunking); move heavy compute to **web workers**; shrink the **DOM and style-recalc** cost (smaller DOM, simpler selectors); defer non-critical scripts; debounce handler work. Always diagnose from FIELD/CrUX, then reproduce slow interactions in lab.

**LCP** — identify the LCP element (usually hero image or H1 text); preload it; serve modern image formats + correct sizing; set `fetchpriority="high"`; cut server response time (TTFB) and render-blocking CSS/JS; avoid lazy-loading the LCP image.

**CLS** — set explicit `width`/`height` (or `aspect-ratio`) on images, video, ads, and embeds; reserve space for dynamically injected content; preload fonts and use `size-adjust` / `font-display` to limit swap shift; never insert content above existing content without reserved space.

## Field (CrUX) vs lab
- **Field data (CrUX)** = real Chrome users over a trailing 28-day window; this is what Google scores and what "Good/Needs improvement/Poor" reflects. INP and the official pass/fail can ONLY come from field data.
- **Lab data** (Lighthouse/PSI synthetic run) = one simulated load, no real interactions. It estimates LCP/CLS and a *proxy* for responsiveness (e.g. TBT), but cannot produce a real INP. Use lab to **debug and reproduce**, field to **judge**.
- A common failure: lab is green, field is red — because real users have slower devices, more interactions, and varied conditions the single lab run never exercises.

## Data sources: cwv_check.py / PSI / CrUX
- **CrUX** is the source of truth. Access it via the **CrUX API** (URL- or origin-level, 75th-percentile distributions) or the BigQuery dataset for trends.
- **PageSpeed Insights (PSI)** returns BOTH: field data from CrUX (when the URL/origin has enough traffic) and a fresh lab run (Lighthouse). Low-traffic URLs return no field data and fall back to origin-level or lab only.
- **cwv_check.py** (SEO-Kami's tool) pulls field metrics programmatically (PSI/CrUX API) so audits report the *real-user* LCP/INP/CLS at the 75th percentile, not a one-off lab score — and flags URLs with insufficient field data rather than passing off lab numbers as field truth.

## The honest ranking framing
The **"Page Experience" ranking SYSTEM was retired in 2023**. Core Web Vitals are **NOT a standalone or direct ranking factor**. Frame them honestly: CWV are a **page-quality input and a tiebreaker** between otherwise comparable results — and, more durably, a **conversion / UX / retention lever**. Optimize CWV because faster, more stable, more responsive pages convert and retain better and remove a quality liability — not because a millisecond buys a position. Avoid any "fix CWV to rank #1" promise.
