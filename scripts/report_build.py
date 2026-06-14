#!/usr/bin/env python3
"""Render a client-facing SEO-Kami report (Markdown/HTML) from an audit JSON envelope."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import seo_common
from seo_common import Finding, emit
from lib import sanitize

SEV_ORDER = ["critical", "high", "medium", "low", "info"]
SEV_LABEL = {
    "critical": "Critical",
    "high": "High",
    "medium": "Medium",
    "low": "Low",
    "info": "Info",
}
# Priority triage: severity -> (when to act, effort/impact note).
PRIORITY = {
    "critical": ("Fix now", "Blocks indexing/ranking — highest impact, do before anything else"),
    "high": ("This sprint", "Material ranking/UX loss — schedule into the current cycle"),
    "medium": ("Backlog", "Worth doing — queue once Critical/High are cleared"),
    "low": ("Backlog (low)", "Minor polish — batch with other low-effort work"),
    "info": ("Monitor", "No action required — context / watch item"),
}
# Quick-Win is a derived bucket (low effort, high impact) surfaced in the matrix.
TIER_LEGEND = {
    "proven": "Google primary docs or direct measurement (e.g. CWV thresholds, indexability, schema deprecations).",
    "correlated": "Independent studies — correlation, NOT proven causation (Ahrefs / Muck Rack / Seer / SparkToro).",
    "consensus": "Practitioner agreement, no hard proof.",
    "speculative": "Unproven / emerging (e.g. llms.txt as a ranking or citation lever).",
}
CONF_LABEL = {
    "confirmed": "Confirmed",
    "likely": "Likely",
    "hypothesis": "Hypothesis (needs a tool/data to confirm)",
}


def die(error, detail=""):
    print(json.dumps({"error": str(error), "detail": str(detail)}))
    sys.exit(2)


def load_json(path):
    if not path:
        die("missing input", "Usage: report_build.py <audit.json> [--out PATH] [--format md|html] [--date YYYY-MM-DD]")
    if not os.path.isfile(path):
        die("input not found", path)
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except json.JSONDecodeError as e:
        die("invalid JSON", str(e))
    except Exception as e:
        die("could not read input", str(e))


def normalize(data):
    """Accept an emit() envelope or finding_verifier output; return (meta, score, grade, findings:list[dict])."""
    if not isinstance(data, dict):
        die("unexpected JSON shape", "top level must be an object")
    findings = data.get("findings")
    if findings is None and isinstance(data.get("verified_findings"), list):
        findings = data["verified_findings"]  # finding_verifier output
    if not isinstance(findings, list):
        findings = []
    meta = data.get("meta") if isinstance(data.get("meta"), dict) else {}
    score = data.get("score", meta.get("score"))
    grade = data.get("grade", meta.get("grade"))
    return meta, score, grade, findings


def parse_args(argv):
    path = None
    out = None
    fmt = "md"
    date = None
    i = 1
    positional = []
    while i < len(argv):
        a = argv[i]
        if a == "--out" and i + 1 < len(argv):
            out = argv[i + 1]; i += 2; continue
        if a == "--format" and i + 1 < len(argv):
            fmt = argv[i + 1].lower(); i += 2; continue
        if a == "--date" and i + 1 < len(argv):
            date = argv[i + 1]; i += 2; continue
        if a.startswith("--"):
            i += 1; continue
        positional.append(a); i += 1
    if positional:
        path = positional[0]
    if fmt not in ("md", "html"):
        fmt = "md"
    return path, out, fmt, date


def get(f, key, default=""):
    v = f.get(key, default) if isinstance(f, dict) else default
    return v if v is not None else default


def clean(text):
    """Defang any untrusted text pulled from a page into the report."""
    if not text:
        return ""
    return sanitize.strip_invisible(str(text)).strip()


def group_by_sev(findings):
    buckets = {s: [] for s in SEV_ORDER}
    for f in findings:
        sev = get(f, "severity", "info")
        if sev not in buckets:
            buckets.setdefault(sev, [])
        buckets[sev].append(f)
    return buckets


def md_escape_cell(text):
    return clean(text).replace("|", "\\|").replace("\n", " ")


def build_markdown(meta, score, grade, findings, date):
    site = clean(meta.get("url") or meta.get("site") or meta.get("domain")) or "(site not specified)"
    check = clean(meta.get("check") or "")
    date_str = clean(date) or "{{date}}"
    buckets = group_by_sev(findings)
    counts = {s: len(buckets.get(s, [])) for s in SEV_ORDER}
    total = len(findings)

    L = []
    L.append("# SEO-Kami Audit Report — {}".format(site))
    sub = ["**Date:** {}".format(date_str)]
    if check:
        sub.append("**Audit:** {}".format(check))
    L.append("  \n".join(sub))
    L.append("")

    score_txt = score if score is not None else "N/A"
    grade_txt = grade if grade is not None else "N/A"
    L.append("## Overall")
    L.append("")
    L.append("- **Score:** {}".format(score_txt))
    L.append("- **Grade:** {}".format(grade_txt))
    L.append("- **Total findings:** {}".format(total))
    L.append("")

    # Summary table
    L.append("## Summary — findings by severity")
    L.append("")
    L.append("| Severity | Count |")
    L.append("| --- | ---: |")
    for s in SEV_ORDER:
        L.append("| {} | {} |".format(SEV_LABEL[s], counts[s]))
    L.append("| **Total** | **{}** |".format(total))
    L.append("")

    # Priority matrix
    L.append("## Priority matrix")
    L.append("")
    L.append("| Severity | When to act | Effort / impact triage |")
    L.append("| --- | --- | --- |")
    for s in SEV_ORDER:
        when, note = PRIORITY[s]
        L.append("| {} | {} | {} |".format(SEV_LABEL[s], when, md_escape_cell(note)))
    L.append("| Quick-Win | Pick off first | Low effort / high impact — promote any High or Medium fix that is cheap to ship |")
    L.append("")

    # Findings grouped by severity
    L.append("## Findings")
    L.append("")
    if total == 0:
        L.append("_No findings in this audit._")
        L.append("")
    for s in SEV_ORDER:
        items = buckets.get(s, [])
        if not items:
            continue
        L.append("### {} ({})".format(SEV_LABEL[s], len(items)))
        L.append("")
        for f in items:
            title = clean(get(f, "title")) or clean(get(f, "id")) or "(untitled finding)"
            fid = clean(get(f, "id"))
            cat = clean(get(f, "category"))
            conf = get(f, "confidence", "confirmed")
            tier = get(f, "evidence_tier", "proven")
            head = "#### {}".format(title)
            L.append(head)
            tags = []
            if fid:
                tags.append("`{}`".format(fid))
            if cat:
                tags.append("category: {}".format(cat))
            if tags:
                L.append("")
                L.append(" · ".join(tags))
            L.append("")
            ev = clean(get(f, "evidence"))
            im = clean(get(f, "impact"))
            fx = clean(get(f, "fix"))
            L.append("- **Evidence:** {}".format(ev or "_not provided_"))
            L.append("- **Impact:** {}".format(im or "_not provided_"))
            L.append("- **Fix:** {}".format(fx or "_not provided_"))
            L.append("- **Confidence:** {}".format(CONF_LABEL.get(conf, conf)))
            L.append("- **Evidence tier:** {}".format(str(tier).capitalize()))
            L.append("")

    # Evidence-tier legend
    L.append("## Evidence-tier legend")
    L.append("")
    L.append("| Tier | Meaning |")
    L.append("| --- | --- |")
    for tier in ["proven", "correlated", "consensus", "speculative"]:
        L.append("| {} | {} |".format(tier.capitalize(), md_escape_cell(TIER_LEGEND[tier])))
    L.append("")
    L.append("---")
    L.append("")
    L.append("_Generated by SEO-Kami. Every recommendation carries an evidence tier — verify Correlated/Consensus/Speculative claims before acting on them as fact._")
    L.append("")
    return "\n".join(L)


def md_to_html(markdown_text, title):
    """Minimal, dependency-free Markdown -> HTML for the subset we emit (headings, tables, lists, bold)."""
    import re

    def inline(s):
        s = (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
        s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
        s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
        s = re.sub(r"_(.+?)_", r"<em>\1</em>", s)
        return s

    lines = markdown_text.split("\n")
    html = []
    i = 0
    in_list = False

    def close_list():
        nonlocal in_list
        if in_list:
            html.append("</ul>")
            in_list = False

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        # Table block: a line starting with | followed by a separator row.
        if stripped.startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]):
            close_list()
            header = [c.strip() for c in stripped.strip("|").split("|")]
            html.append("<table><thead><tr>")
            for c in header:
                html.append("<th>{}</th>".format(inline(c)))
            html.append("</tr></thead><tbody>")
            i += 2
            while i < len(lines) and lines[i].strip().startswith("|"):
                row = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                html.append("<tr>" + "".join("<td>{}</td>".format(inline(c)) for c in row) + "</tr>")
                i += 1
            html.append("</tbody></table>")
            continue
        if stripped.startswith("#"):
            close_list()
            level = len(stripped) - len(stripped.lstrip("#"))
            level = min(max(level, 1), 6)
            text = stripped[level:].strip()
            html.append("<h{0}>{1}</h{0}>".format(level, inline(text)))
        elif stripped.startswith("- "):
            if not in_list:
                html.append("<ul>")
                in_list = True
            html.append("<li>{}</li>".format(inline(stripped[2:])))
        elif stripped == "---":
            close_list()
            html.append("<hr>")
        elif stripped == "":
            close_list()
        else:
            close_list()
            html.append("<p>{}</p>".format(inline(stripped)))
        i += 1
    close_list()

    css = (
        "body{font:16px/1.55 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;"
        "max-width:860px;margin:2rem auto;padding:0 1rem;color:#1a1a1a;}"
        "h1{font-size:1.9rem;border-bottom:2px solid #222;padding-bottom:.3rem;}"
        "h2{font-size:1.4rem;margin-top:2rem;border-bottom:1px solid #ddd;padding-bottom:.2rem;}"
        "h3{font-size:1.15rem;margin-top:1.5rem;}h4{font-size:1rem;margin:1rem 0 .3rem;}"
        "table{border-collapse:collapse;width:100%;margin:1rem 0;}"
        "th,td{border:1px solid #ccc;padding:.45rem .6rem;text-align:left;vertical-align:top;}"
        "th{background:#f4f4f4;}code{background:#f0f0f0;padding:.1rem .3rem;border-radius:3px;font-size:.9em;}"
        "hr{border:none;border-top:1px solid #ddd;margin:2rem 0;}"
        "ul{margin:.4rem 0 .8rem 1.2rem;}em{color:#666;}"
    )
    safe_title = (title.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
    return (
        "<!DOCTYPE html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
        "<title>{}</title><style>{}</style></head><body>\n{}\n</body></html>\n"
    ).format(safe_title, css, "\n".join(html))


def main():
    path, out, fmt, date = parse_args(sys.argv)
    data = load_json(path)
    meta, score, grade, findings = normalize(data)
    markdown_text = build_markdown(meta, score, grade, findings, date)

    if fmt == "html":
        site = clean(meta.get("url") or meta.get("site") or meta.get("domain")) or "SEO-Kami Report"
        output = md_to_html(markdown_text, "SEO-Kami Report — {}".format(site))
    else:
        output = markdown_text

    try:
        if out:
            with open(out, "w", encoding="utf-8") as fh:
                fh.write(output)
            print(json.dumps({"ok": True, "written": os.path.abspath(out), "format": fmt, "findings": len(findings)}))
        else:
            sys.stdout.write(output)
            if not output.endswith("\n"):
                sys.stdout.write("\n")
    except Exception as e:
        die("could not write output", str(e))


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:
        die("unexpected failure", str(e))
