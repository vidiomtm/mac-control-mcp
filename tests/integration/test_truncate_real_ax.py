"""Integration tests for AX snapshot + truncation with real accessibility API."""

from __future__ import annotations

import json

import pytest

from mac_control_mcp.ax.snapshot import _AX_AVAILABLE

pytestmark = pytest.mark.integration


def _has_ax_permission() -> bool:
    if not _AX_AVAILABLE:
        return False
    try:
        from ApplicationServices import AXIsProcessTrusted  # type: ignore[import]

        return bool(AXIsProcessTrusted())
    except Exception:
        return False


@pytest.mark.skipif(not _has_ax_permission(), reason="AX permission not granted")
def test_snapshot_finder_returns_ax_application() -> None:
    from mac_control_mcp.ax.snapshot import snapshot_app

    result = snapshot_app("Finder", max_depth=3)
    assert result.get("role") == "AXApplication"
    assert result.get("title") == "Finder"


@pytest.mark.skipif(not _has_ax_permission(), reason="AX permission not granted")
def test_snapshot_pruned_under_budget() -> None:
    from mac_control_mcp.ax.snapshot import snapshot_app
    from mac_control_mcp.truncate import prune_tree, trim_to_budget

    raw = snapshot_app("Finder", max_depth=4)
    pruned = prune_tree(raw, max_depth=4) or {}
    trimmed = trim_to_budget(pruned, budget_chars=8000)
    size = len(json.dumps(trimmed))
    assert size <= 8000, f"Trimmed tree still {size} chars"


@pytest.mark.skipif(not _has_ax_permission(), reason="AX permission not granted")
def test_snapshot_nonexistent_app_raises() -> None:
    from mac_control_mcp.ax.snapshot import snapshot_app

    with pytest.raises(ValueError, match="App not found"):
        snapshot_app("DefinitelyNotAnApp_XYZ_123")
