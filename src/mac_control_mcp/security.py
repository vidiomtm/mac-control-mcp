"""Minimal security baseline: stderr logging, SSRF guard, forbidden OSA patterns."""

import logging
import re
from ipaddress import ip_address, ip_network
from urllib.parse import urlparse

log = logging.getLogger("mac_control_mcp.security")

_PRIVATE_NETS = [
    ip_network("10.0.0.0/8"),
    ip_network("172.16.0.0/12"),
    ip_network("192.168.0.0/16"),
    ip_network("127.0.0.0/8"),
    ip_network("::1/128"),
    ip_network("fc00::/7"),
]

_FORBIDDEN_OSA = re.compile(
    r"(do\s+shell\s+script\s+.*?(rm\s+-[rf]+\s+/|sudo|dd\s+if=))",
    re.IGNORECASE | re.DOTALL,
)


def check_ssrf(url: str) -> None:
    parsed = urlparse(url)
    host = parsed.hostname or ""
    if not host:
        raise ValueError(f"SSRF blocked: empty or missing hostname in {url!r}")
    if host.lower() in ("localhost", "127.0.0.1", "::1"):
        raise ValueError(f"SSRF blocked: private host {host!r}")
    try:
        addr = ip_address(host)
        for net in _PRIVATE_NETS:
            if addr in net:
                raise ValueError(f"SSRF blocked: private address {host!r}")
    except ValueError as exc:
        if "SSRF" in str(exc):
            raise
        # hostname — skip numeric check


def check_osa_script(script: str) -> None:
    m = _FORBIDDEN_OSA.search(script)
    if m:
        raise ValueError(f"Forbidden OSA pattern: {m.group()!r}")
