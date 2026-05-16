"""Integration tests for Spotlight mdfind (macOS-only)."""

from __future__ import annotations

import pytest

from mac_control_mcp.apple.spotlight import spotlight_query


@pytest.mark.integration
def test_spotlight_finds_apps() -> None:
    result = spotlight_query(
        'kMDItemContentType == "com.apple.application-bundle"',
        directory="/Applications",
        limit=5,
    )
    assert result["count"] >= 1
    for path in result["paths"]:
        assert path.startswith("/")


@pytest.mark.integration
def test_spotlight_no_results_for_impossible_query() -> None:
    result = spotlight_query("kMDItemFSName == 'definitely_not_a_real_file_xyz_abc.txt'")
    assert result["count"] == 0
    assert result["paths"] == []


@pytest.mark.integration
def test_spotlight_respects_limit() -> None:
    result = spotlight_query(
        'kMDItemContentType == "com.apple.application-bundle"',
        directory="/Applications",
        limit=2,
    )
    assert len(result["paths"]) <= 2


@pytest.mark.integration
def test_spotlight_returns_predicate() -> None:
    predicate = 'kMDItemFSName == "Finder.app"'
    result = spotlight_query(predicate, directory="/System/Library/CoreServices")
    assert result["predicate"] == predicate
    assert result["count"] >= 1
