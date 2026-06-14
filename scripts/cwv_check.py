#!/usr/bin/env python3
"""Core Web Vitals audit via PageSpeed Insights API (field/CrUX first, lab fallback)."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import seo_common
from seo_common import Page, Finding, emit, arg_url
from lib import safe_http, sanitize

try:
    from urllib.parse import quote
except Exception:  # pragma: no cover
    from urllib import quote

PSI_ENDPOINT = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"

# metric_key: (label, good_threshold, needs_improvement_threshold, unit, finding_id)
# CLS field score is delivered x100 by CrUX percentiles, so thresholds are x100 too.
METRICS = {
    "LARGEST_CONTENTFUL_PAINT_MS": ("LCP", 2500, 4000, "ms", "cwv_lcp"),
    "INTERACTION_TO_NEXT_PAINT": ("INP", 200, 500, "ms", "cwv_inp"),
    "CUMULATIVE_LAYOUT_SHIFT_SCORE": ("CLS", 10, 25, "score", "cwv_cls"),
}


def _rate(value, good, ni):
    if value <= good:
        return "good"
    if value <= ni:
        return "needs-improvement"
    return "poor"


def _severity(rating):
    return {"good": "info", "needs-improvement": "medium", "poor": "high"}[rating]


def _fmt_cls(field_value):
    # CrUX delivers CLS percentile multiplied by 100; show the real unitless score.
    return round(field_value / 100.0, 3)


def _hypothesis(reason):
    return Finding(
        id="cwv_psi_unavailable",
        title="Core Web Vitals could not be measured automatically",
        severity="info",  # an UNMEASURED metric is not a page defect — never penalize the score for a missing key/quota
        category="perf",
        evidence=sanitize.wrap_untrusted(reason, "psi_status"),
        impact="Without field (CrUX) data we cannot confirm whether the page passes the LCP/INP/CLS thresholds Google uses as a page-quality input and tiebreaker.",
        fix="Run PageSpeed Insights at https://pagespeed.web.dev for this URL (mobile strategy), or set PAGESPEED_API_KEY to raise the API quota, then re-run this check.",
        confidence="hypothesis",
        evidence_tier="proven",
        detail={"reason": reason},
    )


def _field_finding(metric_key, percentile):
    label, good, ni, unit, fid = METRICS[metric_key]
    if metric_key == "CUMULATIVE_LAYOUT_SHIFT_SCORE":
        display = _fmt_cls(percentile)
        ev = "{} (field/CrUX, 75th percentile): {} (good <= 0.10, needs-improvement <= 0.25)".format(label, display)
    else:
        display = percentile
        good_s = good / 1000.0 if unit == "ms" and label == "LCP" else good
        ev = "{} (field/CrUX, 75th percentile): {} {} (good <= {}, needs-improvement <= {})".format(
            label, display, unit, good, ni)
    rating = _rate(percentile, good, ni)
    sev = _severity(rating)
    fixes = {
        "LCP": "Optimize the largest element: serve a smaller/properly-sized hero image, preload it, cut render-blocking CSS/JS, and use a fast server/CDN response.",
        "INP": "Break up long JavaScript tasks, yield to the main thread, move work to web workers, and shrink DOM/style-recalc cost. INP measures only clicks/taps/keypresses.",
        "CLS": "Reserve space for images/ads/embeds with width/height attributes, avoid inserting content above existing content, and preload fonts to prevent layout shifts.",
    }
    impacts = {
        "good": "This metric already meets Google's 'good' threshold, supporting page experience and conversion.",
        "needs-improvement": "This metric is in the 'needs-improvement' band; it weakens page experience and can cost conversions.",
        "poor": "This metric is 'poor'; it degrades page experience (a quality input/tiebreaker) and is a direct conversion drag.",
    }
    return Finding(
        id=fid,
        title="{} is {} ({})".format(label, rating.replace("-", " "), "field data"),
        severity=sev,
        category="perf",
        evidence=ev,
        impact=impacts[rating],
        fix=fixes[label],
        confidence="confirmed",
        evidence_tier="proven",
        detail={"metric": label, "rating": rating, "percentile": percentile, "source": "field"},
    )


def _lab_finding(label, value_ms, good, ni, unit, fid, is_cls=False):
    if is_cls:
        display = round(value_ms, 3)
        scaled = value_ms * 100
        rating = _rate(scaled, good, ni)
        ev = "{} (LAB / Lighthouse): {} (good <= 0.10, needs-improvement <= 0.25). Lab != field.".format(label, display)
    else:
        rating = _rate(value_ms, good, ni)
        ev = "{} (LAB / Lighthouse): {} {} (good <= {}, needs-improvement <= {}). Lab != field.".format(
            label, round(value_ms, 1), unit, good, ni)
    sev = _severity(rating)
    fixes = {
        "LCP": "Optimize the largest element: smaller/preloaded hero image, cut render-blocking CSS/JS, fast server/CDN.",
        "CLS": "Reserve space for images/ads/embeds with width/height, avoid inserting content above existing content, preload fonts.",
    }
    return Finding(
        id=fid,
        title="{} is {} (lab estimate)".format(label, rating.replace("-", " ")),
        severity=sev,
        category="perf",
        evidence=ev,
        impact="Lab data is a simulated estimate, not real-user field data; treat it as directional only. Confirm with CrUX field data before prioritizing.",
        fix=fixes.get(label, "Improve the metric per Google's CWV guidance, then validate with field data."),
        confidence="likely",
        evidence_tier="proven",
        detail={"metric": label, "rating": rating, "value": value_ms, "source": "lab"},
    )


def collect(url, page=None):
    """cwv_check ignores the page object; CWV needs the PSI API, not page HTML."""
    if not url:
        return [_hypothesis("No URL was provided to measure.")]

    key = os.environ.get("PAGESPEED_API_KEY")
    api = "{}?url={}&strategy=mobile&category=performance".format(PSI_ENDPOINT, quote(url, safe=""))
    if key:
        api += "&key=" + quote(key, safe="")

    try:
        resp = safe_http.get(api)
    except safe_http.UnsafeURLError as e:
        return [_hypothesis("PageSpeed Insights request was blocked as unsafe: {}".format(e))]
    except Exception as e:
        return [_hypothesis("PageSpeed Insights request failed: {}".format(e))]

    if not getattr(resp, "ok", False):
        return [_hypothesis("PageSpeed Insights returned HTTP {}.".format(getattr(resp, "status", "?")))]

    try:
        data = json.loads(resp.text)
    except Exception as e:
        return [_hypothesis("Could not parse PageSpeed Insights response: {}".format(e))]

    if isinstance(data, dict) and data.get("error"):
        msg = data["error"].get("message", "unknown error")
        return [_hypothesis("PageSpeed Insights API error: {}".format(msg))]

    findings = []

    # --- Field / CrUX data (preferred) ---
    field_metrics = (data.get("loadingExperience") or {}).get("metrics") or {}
    for metric_key in METRICS:
        m = field_metrics.get(metric_key)
        if isinstance(m, dict) and isinstance(m.get("percentile"), (int, float)):
            findings.append(_field_finding(metric_key, m["percentile"]))

    if findings:
        return findings

    # --- Lab / Lighthouse fallback (confidence=likely) ---
    audits = ((data.get("lighthouseResult") or {}).get("audits")) or {}

    lcp = (audits.get("largest-contentful-paint") or {}).get("numericValue")
    if isinstance(lcp, (int, float)):
        findings.append(_lab_finding("LCP", lcp, 2500, 4000, "ms", "cwv_lcp"))

    cls = (audits.get("cumulative-layout-shift") or {}).get("numericValue")
    if isinstance(cls, (int, float)):
        findings.append(_lab_finding("CLS", cls, 10, 25, "score", "cwv_cls", is_cls=True))

    if findings:
        return findings

    return [_hypothesis("PageSpeed Insights returned no field (CrUX) or lab data for this URL.")]


if __name__ == "__main__":
    try:
        url = arg_url(sys.argv)
        emit(collect(url), meta={"url": url, "check": "cwv_check"})
    except Exception as e:
        print(json.dumps({"error": "cwv_check failed", "detail": str(e)}))
        sys.exit(2)
