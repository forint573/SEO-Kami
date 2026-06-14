"""Safe HTTP layer for SEO-Kami.

A single, self-contained network helper that every URL-fetching script imports.
It exists because an SEO skill fetches *user-supplied* URLs and feeds the
response to a model — the two things an attacker most wants to abuse (SSRF to
reach cloud metadata / internal services, and oversized/slow responses).

Design (re-authored for SEO-Kami; the SSRF + per-redirect-revalidation pattern
is inspired by the MIT-licensed url_safety.py in AgricIDaniel/claude-seo and
safe_http.py in Bhanunamikaze/Agentic-SEO-Skill — see NOTICE.md):

  * scheme allowlist (http/https only)
  * resolve the host, reject private / loopback / link-local / reserved /
    multicast / CGNAT addresses and known cloud-metadata endpoints
  * reject IP-literal obfuscation (octal / hex / 32-bit integer hosts)
  * follow redirects MANUALLY, re-validating the destination of every hop
    (a public URL that 302s to http://169.254.169.254 is the classic bypass)
  * cap response size and total time so a hostile host cannot exhaust us
  * one honest, identifiable User-Agent

Works with `requests` if installed; falls back to the stdlib (urllib) so the
script runs in a minimal environment. No third-party dependency is mandatory.
"""

from __future__ import annotations

import ipaddress
import socket
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from typing import Optional
from urllib.parse import urlparse, urljoin

USER_AGENT = "SEO-Kami/1.0 (+https://github.com/forint573/SEO-Kami)"
DEFAULT_TIMEOUT = 20  # seconds per request
MAX_BYTES = 6 * 1024 * 1024  # 6 MB hard cap on a fetched body
MAX_REDIRECTS = 8

# Hostnames that must never be reached regardless of DNS.
BLOCKED_HOSTNAMES = {
    "metadata.google.internal",
    "metadata",
    "instance-data",
    "instance-data.ec2.internal",
}

# Cloud metadata / link-local addresses (covered by range checks too, listed
# explicitly for clarity and defence in depth).
BLOCKED_IPS = {
    "169.254.169.254",  # AWS / GCP / Azure / DO IMDS
    "fd00:ec2::254",    # AWS IMDS over IPv6
}

try:  # optional, preferred transport
    import requests  # type: ignore

    _HAVE_REQUESTS = True
except Exception:  # pragma: no cover - exercised only without requests
    requests = None  # type: ignore
    _HAVE_REQUESTS = False


class UnsafeURLError(ValueError):
    """Raised when a URL fails the SSRF / safety policy."""


@dataclass
class Response:
    url: str            # final URL after redirects
    status: int
    headers: dict = field(default_factory=dict)
    text: str = ""
    content: bytes = b""
    elapsed_ms: int = 0

    @property
    def ok(self) -> bool:
        return 200 <= self.status < 400


def _ip_is_safe(ip_str: str) -> bool:
    try:
        ip = ipaddress.ip_address(ip_str)
    except ValueError:
        return False
    if ip_str in BLOCKED_IPS:
        return False
    # Block the whole catalogue of non-public ranges.
    if (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
    ):
        return False
    # CGNAT 100.64.0.0/10 is "private-ish" and not a legitimate public target.
    if isinstance(ip, ipaddress.IPv4Address) and ip in ipaddress.ip_network("100.64.0.0/10"):
        return False
    return True


def _looks_like_obfuscated_ip(host: str) -> bool:
    """Reject hosts that are integer / hex / octal encodings of an IP.

    A plain dotted-quad or a real hostname passes; '0x7f000001', '2130706433',
    and '0177.0.0.1' are rejected outright.
    """
    h = host.strip().strip(".")
    if not h:
        return True
    # Pure integer host (e.g. 2130706433 == 127.0.0.1)
    if h.isdigit():
        return True
    # Hex host
    if h.lower().startswith("0x"):
        return True
    # Octal-looking dotted parts (leading zero on a numeric label)
    parts = h.split(".")
    if all(p.isdigit() for p in parts) and len(parts) == 4:
        if any(len(p) > 1 and p.startswith("0") for p in parts):
            return True
    return False


def validate_url(url: str) -> str:
    """Validate a URL against the SSRF policy. Returns the URL or raises.

    Does NOT mutate the URL beyond stripping whitespace. Resolves DNS and checks
    every resolved address, so a hostname that maps to a private IP is rejected.
    """
    if not url or not isinstance(url, str):
        raise UnsafeURLError("empty URL")
    url = url.strip()
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise UnsafeURLError(f"scheme not allowed: {parsed.scheme!r} (http/https only)")
    host = parsed.hostname
    if not host:
        raise UnsafeURLError("URL has no host")
    host_l = host.lower()
    if host_l in BLOCKED_HOSTNAMES:
        raise UnsafeURLError(f"blocked host: {host}")
    if _looks_like_obfuscated_ip(host):
        raise UnsafeURLError(f"obfuscated IP host rejected: {host}")

    # If the host is already an IP literal, validate it directly.
    try:
        ipaddress.ip_address(host)
        if not _ip_is_safe(host):
            raise UnsafeURLError(f"IP not allowed: {host}")
        return url
    except ValueError:
        pass  # it's a hostname — resolve it

    try:
        infos = socket.getaddrinfo(host, parsed.port or (443 if parsed.scheme == "https" else 80))
    except socket.gaierror as exc:
        raise UnsafeURLError(f"DNS resolution failed for {host}: {exc}")
    resolved = {info[4][0] for info in infos}
    if not resolved:
        raise UnsafeURLError(f"no addresses resolved for {host}")
    for ip in resolved:
        if not _ip_is_safe(ip):
            raise UnsafeURLError(f"{host} resolves to a blocked address: {ip}")
    return url


def _read_capped(raw, cap: int = MAX_BYTES) -> bytes:
    chunks = []
    total = 0
    for chunk in raw:
        if not chunk:
            continue
        total += len(chunk)
        if total > cap:
            chunks.append(chunk[: cap - (total - len(chunk))])
            break
        chunks.append(chunk)
    return b"".join(chunks)


def get(url: str, timeout: int = DEFAULT_TIMEOUT, headers: Optional[dict] = None,
        method: str = "GET") -> Response:
    """Fetch a URL safely, following redirects with per-hop re-validation."""
    import time

    hdrs = {"User-Agent": USER_AGENT, "Accept": "*/*"}
    if headers:
        hdrs.update(headers)

    current = validate_url(url)
    start = time.time()
    for _ in range(MAX_REDIRECTS + 1):
        if _HAVE_REQUESTS:
            resp = requests.request(
                method, current, headers=hdrs, timeout=timeout,
                allow_redirects=False, stream=True, verify=True,
            )
            status = resp.status_code
            rheaders = {k.lower(): v for k, v in resp.headers.items()}
            if status in (301, 302, 303, 307, 308) and "location" in rheaders:
                current = validate_url(urljoin(current, rheaders["location"]))
                resp.close()
                continue
            body = _read_capped(resp.iter_content(chunk_size=65536))
            resp.close()
        else:  # urllib fallback (stdlib-only path when requests is absent)
            import urllib.request
            import urllib.error

            req = urllib.request.Request(current, headers=hdrs, method=method)
            opener = urllib.request.build_opener(_NoRedirect)
            try:
                resp = opener.open(req, timeout=timeout)
                status = resp.getcode()
                rheaders = {k.lower(): v for k, v in resp.headers.items()}
                body = _read_capped(iter(lambda: resp.read(65536), b""))
            except urllib.error.HTTPError as e:
                status = e.code
                rheaders = {k.lower(): v for k, v in (e.headers or {}).items()}
                if status in (301, 302, 303, 307, 308) and "location" in rheaders:
                    current = validate_url(urljoin(current, rheaders["location"]))
                    continue
                try:
                    body = _read_capped(iter(lambda: e.read(65536), b""))
                except Exception:
                    body = b""

        elapsed = int((time.time() - start) * 1000)
        charset = "utf-8"
        ctype = rheaders.get("content-type", "")
        if "charset=" in ctype:
            charset = ctype.split("charset=")[-1].split(";")[0].strip() or "utf-8"
        try:
            text = body.decode(charset, errors="replace")
        except (LookupError, TypeError):
            text = body.decode("utf-8", errors="replace")
        return Response(url=current, status=status, headers=rheaders,
                        text=text, content=body, elapsed_ms=elapsed)

    raise UnsafeURLError(f"too many redirects (> {MAX_REDIRECTS})")


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """urllib handler that refuses to auto-follow 3xx so get() can re-validate
    each redirect target itself. It raises HTTPError on a redirect, which get()
    catches to read the Location header and continue the manual loop."""

    def http_error_301(self, req, fp, code, msg, headers):
        raise urllib.error.HTTPError(req.full_url, code, msg, headers, fp)

    http_error_302 = http_error_303 = http_error_307 = http_error_308 = http_error_301


def head(url: str, timeout: int = DEFAULT_TIMEOUT) -> Response:
    return get(url, timeout=timeout, method="HEAD")


if __name__ == "__main__":
    import sys
    import json as _json

    target = sys.argv[1] if len(sys.argv) > 1 else "https://example.com"
    try:
        r = get(target)
        print(_json.dumps({
            "final_url": r.url, "status": r.status, "ok": r.ok,
            "bytes": len(r.content), "elapsed_ms": r.elapsed_ms,
            "content_type": r.headers.get("content-type", ""),
        }, indent=2))
    except UnsafeURLError as e:
        print(_json.dumps({"error": "unsafe_url", "detail": str(e)}))
        sys.exit(2)
