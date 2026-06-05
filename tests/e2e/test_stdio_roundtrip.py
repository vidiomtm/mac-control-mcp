"""E2E tests: full JSON-RPC stdio roundtrip via subprocess."""

from __future__ import annotations

import json
import re
import subprocess
import sys

import pytest

from tests.e2e.helpers import _extract_text, _initialize, mcp_session


@pytest.mark.e2e
def test_initialize_response() -> None:
    with mcp_session() as (send, recv):
        resp = _initialize(send, recv)
    assert resp["jsonrpc"] == "2.0"
    assert "result" in resp
    assert resp["result"]["protocolVersion"] == "2024-11-05"
    assert resp["result"]["serverInfo"]["name"] == "mac-control"


@pytest.mark.e2e
def test_tools_list_returns_30() -> None:
    with mcp_session() as (send, recv):
        _initialize(send, recv)
        send({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
        resp = recv(2)
    tools = resp["result"]["tools"]
    assert len(tools) == 30


@pytest.mark.e2e
def test_tool_names_snake_case() -> None:
    pattern = re.compile(r"^[a-z][a-z0-9_]+$")
    with mcp_session() as (send, recv):
        _initialize(send, recv)
        send({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
        resp = recv(2)
    for tool in resp["result"]["tools"]:
        assert pattern.match(tool["name"]), f"Bad name: {tool['name']!r}"


@pytest.mark.e2e
def test_osa_search_call() -> None:
    with mcp_session() as (send, recv):
        _initialize(send, recv)
        send(
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "osa_search",
                    "arguments": {"query": "create reminder", "top_k": 3},
                },
            }
        )
        resp = recv(3)
    assert "result" in resp, f"Error: {resp.get('error')}"
    results = json.loads(_extract_text(resp["result"]["content"]))
    assert results[0]["id"] == "reminders_add"


@pytest.mark.e2e
def test_screen_list_windows_call() -> None:
    with mcp_session() as (send, recv):
        _initialize(send, recv)
        send(
            {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {"name": "screen_list_windows", "arguments": {}},
            }
        )
        resp = recv(4)
    assert "result" in resp, f"Error: {resp.get('error')}"
    windows = json.loads(_extract_text(resp["result"]["content"]))
    assert isinstance(windows, list) and len(windows) > 0 and "id" in windows[0]


@pytest.mark.e2e
def test_unknown_tool_returns_error() -> None:
    with mcp_session() as (send, recv):
        _initialize(send, recv)
        send(
            {
                "jsonrpc": "2.0",
                "id": 5,
                "method": "tools/call",
                "params": {"name": "this_tool_does_not_exist", "arguments": {}},
            }
        )
        resp = recv(5)
    assert "error" in resp or ("result" in resp and resp["result"].get("isError"))


@pytest.mark.e2e
@pytest.mark.xfail(reason="Flaky: subprocess.run pipe may close before second response flushes")
def test_stdout_contains_only_jsonrpc() -> None:
    """Every stdout line must be a valid JSON-RPC frame — no bare print() pollution."""
    requests = (
        json.dumps(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "pytest", "version": "0.0.1"},
                },
            }
        )
        + "\n"
        + json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
        + "\n"
    )

    result = subprocess.run(
        [sys.executable, "-m", "mac_control_mcp"],
        input=requests.encode(),
        capture_output=True,
        timeout=15,
    )

    lines = [ln for ln in result.stdout.decode().splitlines() if ln.strip()]
    assert len(lines) >= 2, f"Expected ≥2 JSON-RPC responses, got: {lines}"
    for line in lines:
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as exc:
            pytest.fail(f"Non-JSON stdout line (stdout pollution): {line!r} — {exc}")
        assert "jsonrpc" in obj, f"Line missing 'jsonrpc' key (not a JSON-RPC frame): {line!r}"
