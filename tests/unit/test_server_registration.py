"""Unit tests for MCP server tool registration."""

from __future__ import annotations

import json
import re

import pytest

EXPECTED_TOOLS = {
    "ax_click",
    "ax_hotkey",
    "ax_scroll",
    "ax_snapshot",
    "ax_system_ui",
    "ax_type",
    "calendar_create_event",
    "calendar_events",
    "contacts_search",
    "finder_tags_get",
    "finder_tags_set",
    "mail_recent",
    "mail_search",
    "mail_send",
    "messages_recent",
    "messages_send",
    "notes_create",
    "notes_get",
    "notes_search",
    "osa_exec",
    "osa_run",
    "osa_search",
    "quicklook",
    "reminders_add",
    "reminders_list",
    "screen_capture",
    "screen_list_windows",
    "screen_ocr",
    "screen_wait_for_change",
    "spotlight_query",
}


@pytest.mark.unit
def test_server_creates_successfully(mcp_server) -> None:
    assert mcp_server is not None


@pytest.mark.unit
def test_tool_count(mcp_server) -> None:
    tools = mcp_server._tool_manager.list_tools()
    assert len(tools) == 30


@pytest.mark.unit
def test_all_expected_tools_registered(mcp_server) -> None:
    tools = mcp_server._tool_manager.list_tools()
    registered = {t.name for t in tools}
    missing = EXPECTED_TOOLS - registered
    assert not missing, f"Missing tools: {missing}"


@pytest.mark.unit
def test_no_extra_tools(mcp_server) -> None:
    tools = mcp_server._tool_manager.list_tools()
    registered = {t.name for t in tools}
    extra = registered - EXPECTED_TOOLS
    assert not extra, f"Unexpected extra tools: {extra}"


@pytest.mark.unit
def test_tool_names_match_pattern(mcp_server) -> None:
    tools = mcp_server._tool_manager.list_tools()
    pattern = re.compile(r"^[a-z][a-z0-9_]+$")
    bad = [t.name for t in tools if not pattern.match(t.name)]
    assert not bad, f"Non-conforming tool names: {bad}"


@pytest.mark.unit
def test_tools_have_descriptions(mcp_server) -> None:
    tools = mcp_server._tool_manager.list_tools()
    no_desc = [t.name for t in tools if not (t.description or "").strip()]
    assert not no_desc, f"Tools missing descriptions: {no_desc}"


@pytest.mark.unit
def test_tools_have_valid_input_schema(mcp_server) -> None:
    tools = mcp_server._tool_manager.list_tools()
    for tool in tools:
        schema = tool.parameters
        assert schema is not None, f"{tool.name}: parameters schema is None"
        dumped = json.dumps(schema)
        parsed = json.loads(dumped)
        assert parsed.get("type") == "object", f"{tool.name}: schema.type != 'object'"
