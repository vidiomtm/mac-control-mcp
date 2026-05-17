# SPEC: CLI & Server Interface

**Version:** 0.1.0
**Status:** Draft
**Date:** 2026-05-17

## Purpose

Define the CLI entry point and MCP server interface for mac-control-mcp.

## Interface

### Entry Point

```
mac-control-mcp
```

- No CLI flags currently
- Starts stdio MCP server
- All logging goes to stderr (JSON-RPC on stdout)
- Exits on stdin EOF

### Server Lifecycle

```
run() → FastMCP server → listen on stdin → JSON-RPC loop → EOF → exit
```

### Tool Registration

All tools registered in `server.py:create_server()` via `@mcp.tool()` decorators. 26 tools total across 4 categories:

1. **AX tools** (6): `ax_snapshot`, `ax_click`, `ax_type`, `ax_scroll`, `ax_hotkey`, `ax_system_ui`
2. **Vision tools** (4): `screen_capture`, `screen_list_windows`, `screen_ocr`, `screen_wait_for_change`
3. **OSA tools** (3): `osa_search`, `osa_run`, `osa_exec`
4. **Apple app tools** (14): mail, calendar, reminders, notes, messages, contacts, finder, spotlight, quicklook

### Error Handling

- Tools return JSON-serialized dicts with error info
- Runtime errors raised as Python exceptions → MCP error response
- Security violations raise `ValueError` with descriptive message
- All errors include context (which tool, what input)

### Implementation

```python
def create_server() -> FastMCP:
    mcp = FastMCP("mac-control", ...)
    # ... register 26 tools ...
    return mcp

def main() -> None:
    server = create_server()
    server.run(transport="stdio")
```
