"""Shared fixtures and skip logic for mac-control-mcp tests."""

from __future__ import annotations

import os
import sys

import pytest


def pytest_runtest_setup(item: pytest.Item) -> None:
    if "integration" not in [mark.name for mark in item.iter_markers()] and "e2e" not in [mark.name for mark in item.iter_markers()]:
        try:
            from pytest_socket import disable_socket
            disable_socket()
        except ImportError:
            pass


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    is_darwin = sys.platform == "darwin"
    live = os.environ.get("LIVE_TESTS", "1") != "0"

    for item in items:
        if item.get_closest_marker("integration") or item.get_closest_marker("e2e"):
            if not is_darwin:
                item.add_marker(pytest.mark.skip(reason="macOS only"))
            elif not live:
                item.add_marker(pytest.mark.skip(reason="LIVE_TESTS=0"))


@pytest.fixture
def mcp_server():
    from mac_control_mcp.server import create_server

    return create_server()
