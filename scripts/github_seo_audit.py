#!/usr/bin/env python3
"""GitHub repository discoverability audit: description, topics, README rubric, releases."""
import sys, os, json, base64
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import seo_common
from seo_common import Page, Finding, emit, arg_url
from lib import safe_http, sanitize

API = "https://api.github.com"
GH_ACCEPT = "application/vnd.github+json"


def _headers():
    h = {"Accept": GH_ACCEPT, "X-GitHub-Api-Version": "2022-11-28"}
    tok = os.environ.get("GITHUB_TOKEN")
    if tok:
        h["Authorization"] = "Bearer " + tok
    return h


def _is_rate_limited(resp):
    """A 403/429 with the documented rate-limit headers means the quota is spent."""
    if resp.status not in (403, 429):
        return False
    remaining = resp.headers.get("x-ratelimit-remaining")
    return remaining == "0" or "rate limit" in (resp.text or "").lower()


def _get(path):
    return safe_http.get(API + path, headers=_headers())


def _readme_text(owner, repo):
    """Fetch and base64-decode the default README. Returns text or None."""
    try:
        r = _get(f"/repos/{owner}/{repo}/readme")
    except Exception:
        return None
    if not r.ok:
        return None
    try:
        data = json.loads(r.text)
    except (json.JSONDecodeError, ValueError):
        return None
    if data.get("encoding") == "base64" and data.get("content"):
        try:
            raw = base64.b64decode(data["content"])
            return raw.decode("utf-8", errors="replace")
        except Exception:
            return None
    # Fallback: some responses inline plain content.
    return data.get("content") if isinstance(data.get("content"), str) else None


def _rubric(readme, repo_description=""):
    """100-point README rubric. Returns (score, list of (label, points, passed))."""
    text = readme or ""
    lines = [l.rstrip() for l in text.splitlines()]
    low = text.lower()
    top = low[:800]  # the "above the fold" region where a title/logo lives
    checks = []

    # Title can be a markdown '# ', an HTML <h1>, or a centered logo whose <img
    # carries alt text (a very common high-quality pattern, e.g. awesome lists).
    has_h1 = (any(l.lstrip().startswith("# ") for l in lines)
              or "<h1" in low
              or ("<img" in top and "alt=" in top))
    checks.append(("title/H1", 20, has_h1))

    # A one-line description: a non-heading, non-badge prose line early in the
    # file — or, failing that, the repo's own GitHub `description` field.
    one_liner = bool((repo_description or "").strip())
    for l in lines[:25]:
        s = l.strip()
        if not s or s.startswith(("#", "!", "[!", "<", "---", "===", "```")):
            continue
        if len(s.split()) >= 4:
            one_liner = True
            break
    checks.append(("one-line description", 15, one_liner))

    has_install = any(k in low for k in (
        "## install", "# install", "installation", "npm install", "pip install",
        "yarn add", "go get", "cargo add", "getting started"))
    checks.append(("install section", 20, has_install))

    has_usage = any(k in low for k in (
        "## usage", "# usage", "## example", "examples", "quick start", "quickstart")) \
        or "```" in text
    checks.append(("usage/examples", 20, has_usage))

    has_badges = ("![" in text and "shields.io" in low) or "img.shields.io" in low \
        or low.count("![") >= 1 and ("badge" in low or "shields" in low)
    checks.append(("badges", 10, has_badges))

    has_license = "license" in low
    checks.append(("license mention", 10, has_license))

    has_links = "](http" in low or "<a " in low or "https://" in low
    checks.append(("links", 5, has_links))

    total = sum(pts for _, pts, ok in checks if ok)
    return total, checks


def collect(owner, repo):
    findings = []

    # --- core repo object ---
    repo_resp = _get(f"/repos/{owner}/{repo}")
    if _is_rate_limited(repo_resp):
        reset = repo_resp.headers.get("x-ratelimit-reset", "unknown")
        findings.append(Finding(
            id="github-rate-limited",
            title="GitHub API rate limit hit — set GITHUB_TOKEN to audit fully",
            severity="info", category="github",
            evidence=f"GitHub returned HTTP {repo_resp.status} with x-ratelimit-remaining=0 "
                     f"(reset epoch {reset}). Unauthenticated requests are capped at 60/hour.",
            impact="The audit could not read the repository metadata, so discoverability "
                   "findings below may be incomplete.",
            fix="Export a GitHub personal access token as GITHUB_TOKEN (5000 requests/hour) "
                "and re-run this audit.",
            confidence="hypothesis", evidence_tier="proven",
            detail={"status": repo_resp.status, "ratelimit_reset": reset}))
        return findings
    if repo_resp.status == 404:
        raise _NotFound(f"{owner}/{repo}")
    if not repo_resp.ok:
        raise RuntimeError(f"GitHub API returned HTTP {repo_resp.status} for /repos/{owner}/{repo}")
    try:
        meta = json.loads(repo_resp.text)
    except (json.JSONDecodeError, ValueError):
        raise RuntimeError("GitHub API returned non-JSON for the repository object")

    # --- description ---
    desc = (meta.get("description") or "").strip()
    if not desc:
        findings.append(Finding(
            id="github-description-missing",
            title="Repository has no description",
            severity="medium", category="github",
            evidence="The repo `description` field is empty.",
            impact="The description is the snippet GitHub search and the repo card show, and "
                   "it is the single strongest in-repo relevance signal for GitHub's search ranking. "
                   "An empty description suppresses the repo across keyword searches.",
            fix="Add a concise 1-sentence description (~120 chars) with the primary keyword a "
                "user would search, e.g. what it is + what it does.",
            confidence="confirmed", evidence_tier="consensus"))
    elif len(desc) < 40:
        findings.append(Finding(
            id="github-description-short",
            title="Repository description is very short",
            severity="medium", category="github",
            evidence=f"Description is {len(desc)} chars: "
                     + sanitize.wrap_untrusted(desc, "repo-description"),
            impact="A thin description carries few of the keywords GitHub search matches on and "
                   "gives humans little reason to click from the results list.",
            fix="Expand to ~80-120 chars: state what it is, the stack/language, and the core use case.",
            confidence="confirmed", evidence_tier="consensus",
            detail={"length": len(desc)}))

    # --- topics ---
    topics = []
    try:
        tr = _get(f"/repos/{owner}/{repo}/topics")
        if tr.ok:
            topics = (json.loads(tr.text) or {}).get("names", []) or []
    except Exception:
        topics = meta.get("topics", []) or []
    if not topics:
        findings.append(Finding(
            id="github-topics-none",
            title="Repository has no topics",
            severity="medium", category="github",
            evidence="The topics list is empty (0 topics).",
            impact="Topics are GitHub's tag taxonomy: they power topic pages (github.com/topics/<x>), "
                   "filtered search, and 'related repositories'. With zero topics the repo is invisible "
                   "to every topic-based discovery path.",
            fix="Add 5-12 relevant topics (lowercase, hyphenated) covering the language, domain, and "
                "use case, e.g. `python`, `seo`, `cli`, `static-site`.",
            confidence="confirmed", evidence_tier="consensus"))
    elif len(topics) < 5:
        findings.append(Finding(
            id="github-topics-few",
            title=f"Only {len(topics)} topic(s) set",
            severity="low", category="github",
            evidence="Topics: " + ", ".join(topics),
            impact="Fewer topics means fewer topic pages and filtered searches the repo appears on, "
                   "narrowing discovery.",
            fix="Add more relevant topics (aim for 5-12) spanning language, domain, and use case.",
            confidence="confirmed", evidence_tier="consensus",
            detail={"topics": topics, "count": len(topics)}))

    # --- homepage URL ---
    if not (meta.get("homepage") or "").strip():
        findings.append(Finding(
            id="github-homepage-missing",
            title="No homepage URL set",
            severity="low", category="github",
            evidence="The repo `homepage` field is empty.",
            impact="The homepage link appears in the repo's About box and sends visitors to docs or a "
                   "live demo — a missed conversion and trust signal.",
            fix="Set the homepage to the docs site, live demo, or product page in repo Settings.",
            confidence="confirmed", evidence_tier="consensus"))

    # --- license ---
    if not meta.get("license"):
        findings.append(Finding(
            id="github-license-missing",
            title="No license detected",
            severity="low", category="github",
            evidence="The repo `license` field is null (no recognised LICENSE file).",
            impact="Without a license GitHub shows no license badge and many users (and some "
                   "search/listing filters) skip repos they can't legally reuse, reducing adoption.",
            fix="Add a LICENSE file via GitHub's 'Add file > Create new file > LICENSE' template "
                "(e.g. MIT, Apache-2.0) so the license is detected and displayed.",
            confidence="confirmed", evidence_tier="consensus"))

    # --- releases ---
    has_releases = None
    try:
        rel = _get(f"/repos/{owner}/{repo}/releases?per_page=1")
        if rel.ok:
            has_releases = bool(json.loads(rel.text))
    except Exception:
        has_releases = None
    if has_releases is False:
        findings.append(Finding(
            id="github-no-releases",
            title="No published releases",
            severity="info", category="github",
            evidence="The /releases endpoint returned an empty list.",
            impact="Releases create versioned, indexable pages and signal an actively maintained, "
                   "consumable project — a minor discoverability and trust signal.",
            fix="Tag and publish releases with changelog notes when you ship versions.",
            confidence="confirmed", evidence_tier="consensus"))

    # --- README rubric ---
    readme = _readme_text(owner, repo)
    if readme is None:
        findings.append(Finding(
            id="github-readme-missing",
            title="No README found",
            severity="medium", category="github",
            evidence="The /readme endpoint returned no default README for the repository.",
            impact="The README is the page GitHub renders on the repo home and is the primary content "
                   "both humans and search crawlers read. Without one the repo has almost no on-page "
                   "context to rank or convert on.",
            fix="Add a README.md with a title, one-line description, install and usage sections, "
                "badges, and a license note.",
            confidence="confirmed", evidence_tier="consensus"))
    else:
        rub_score, checks = _rubric(readme, desc)
        missing = [(label, pts) for label, pts, ok in checks if not ok]
        evidence_summary = "README rubric score {}/100. ".format(rub_score) + \
            "Present: " + (", ".join(l for l, _, ok in checks if ok) or "none") + ". " + \
            "Missing: " + (", ".join(l for l, _ in missing) or "none") + "."
        if missing:
            # Severity scales with how deficient the README is.
            sev = "medium" if rub_score < 60 else "low"
            findings.append(Finding(
                id="github-readme-rubric",
                title=f"README is missing {len(missing)} discoverability element(s) "
                      f"(score {rub_score}/100)",
                severity=sev, category="github",
                evidence=evidence_summary,
                impact="A README that lacks a clear title, one-line pitch, install/usage steps, "
                       "badges or a license is harder for a visitor to evaluate at a glance and "
                       "gives search fewer signals about what the project is and how to use it.",
                fix="Add the missing sections: " + ", ".join(l for l, _ in missing) +
                    ". Lead with an H1 title and a single-sentence description, then install "
                    "and usage with a runnable example.",
                confidence="confirmed", evidence_tier="consensus",
                detail={"rubric_score": rub_score,
                        "missing": [l for l, _ in missing],
                        "checks": [{"check": l, "points": p, "passed": ok}
                                   for l, p, ok in checks]}))

    return findings


class _NotFound(Exception):
    pass


def _parse_slug(argv):
    """First non-flag arg is owner/repo (or a github.com URL). Returns (owner, repo)."""
    raw = None
    for a in argv[1:]:
        if not a.startswith("-"):
            raw = a
            break
    if not raw:
        print(json.dumps({"error": "missing argument", "detail": "pass owner/repo"}))
        sys.exit(2)
    raw = raw.strip()
    if "github.com/" in raw:
        raw = raw.split("github.com/", 1)[1]
    raw = raw.strip("/")
    if raw.endswith(".git"):
        raw = raw[:-4]
    parts = [p for p in raw.split("/") if p]
    if len(parts) < 2:
        print(json.dumps({"error": "bad argument",
                          "detail": f"expected owner/repo, got {raw!r}"}))
        sys.exit(2)
    return parts[0], parts[1]


if __name__ == "__main__":
    owner, repo = _parse_slug(sys.argv)
    try:
        findings = collect(owner, repo)
    except _NotFound:
        print(json.dumps({"error": "not_found",
                          "detail": f"GitHub repository {owner}/{repo} not found (HTTP 404)"}))
        sys.exit(2)
    except safe_http.UnsafeURLError as e:
        print(json.dumps({"error": "unsafe_url", "detail": str(e)}))
        sys.exit(2)
    except Exception as e:
        print(json.dumps({"error": "audit_failed", "detail": str(e)}))
        sys.exit(2)
    emit(findings, meta={"repo": f"{owner}/{repo}", "check": "github_seo_audit",
                         "authenticated": bool(os.environ.get("GITHUB_TOKEN"))})
