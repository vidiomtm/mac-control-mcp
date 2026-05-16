"""Integration tests for KB run_by_id (macOS-only)."""

from __future__ import annotations

import json

import pytest

from mac_control_mcp.osa.kb import run_by_id


@pytest.mark.integration
def test_system_get_frontmost_app() -> None:
    result = run_by_id("system_get_frontmost_app")
    output = result["output"].strip()
    assert output != ""
    assert not output.lower().startswith("error")


@pytest.mark.integration
def test_system_list_running_apps_returns_json() -> None:
    result = run_by_id("system_list_running_apps")
    apps = json.loads(result["output"])
    assert isinstance(apps, list)
    assert len(apps) > 0
    first = apps[0]
    assert "name" in first
    assert "pid" in first


@pytest.mark.integration
def test_system_get_volume_is_integer() -> None:
    result = run_by_id("system_get_volume")
    vol = int(result["output"].strip())
    assert 0 <= vol <= 100
