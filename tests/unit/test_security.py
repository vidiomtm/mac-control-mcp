"""Unit tests for mac_control_mcp.security."""

from __future__ import annotations

import pytest

from mac_control_mcp.security import check_osa_script, check_ssrf

# ── SSRF: blocked ─────────────────────────────────────────────────────────────


@pytest.mark.unit
@pytest.mark.parametrize(
    "url",
    [
        "http://127.0.0.1/api",
        "http://localhost/test",
        "http://192.168.1.100/resource",
        "http://10.0.0.1/internal",
        "http://172.16.0.1/secret",
        "http://172.31.255.255/edge",
        "http://[::1]/ipv6",
    ],
)
def test_ssrf_blocks_private(url: str) -> None:
    with pytest.raises(ValueError, match="SSRF blocked"):
        check_ssrf(url)


# ── SSRF: allowed ─────────────────────────────────────────────────────────────


@pytest.mark.unit
@pytest.mark.parametrize(
    "url",
    [
        "https://api.example.com/v1",
        "https://8.8.8.8/dns",
        "http://1.2.3.4/public",
        "https://github.com/repo",
    ],
)
def test_ssrf_allows_public(url: str) -> None:
    check_ssrf(url)  # must not raise


@pytest.mark.unit
def test_ssrf_blocks_empty_hostname() -> None:
    with pytest.raises(ValueError, match="SSRF blocked"):
        check_ssrf("http:///path-with-empty-host")


# ── OSA: forbidden ────────────────────────────────────────────────────────────


@pytest.mark.unit
@pytest.mark.parametrize(
    "script",
    [
        'do shell script "rm -rf /tmp/foo"',
        'do shell script "rm -rf / --no-preserve-root"',
        'do shell script "sudo launchctl unload ..."',
        'do shell script "dd if=/dev/zero of=/dev/disk0"',
    ],
)
def test_osa_blocks_forbidden(script: str) -> None:
    with pytest.raises(ValueError, match="Forbidden OSA pattern"):
        check_osa_script(script)


# ── OSA: allowed ──────────────────────────────────────────────────────────────


@pytest.mark.unit
@pytest.mark.parametrize(
    "script",
    [
        'tell application "Notes" to make new note',
        'tell application "Calendar" to get name of every calendar',
        'return "hello"',
        "set x to 1 + 2\nreturn x",
    ],
)
def test_osa_allows_safe(script: str) -> None:
    check_osa_script(script)  # must not raise
