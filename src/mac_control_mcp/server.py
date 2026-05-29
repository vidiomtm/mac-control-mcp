"""MCP server: registers all mac-control tools via FastMCP."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from mac_control_mcp.tools.apple_tools import register_apple_tools
from mac_control_mcp.tools.ax_tools import register_ax_tools
from mac_control_mcp.tools.osa_tools import register_osa_tools
from mac_control_mcp.tools.vision_tools import register_vision_tools


def create_server() -> FastMCP:
    mcp = FastMCP(
        "mac-control",
        instructions="Unified macOS automation: AX tree, vision/OCR, AppleScript/JXA, Apple apps",
    )

    register_ax_tools(mcp)
    register_vision_tools(mcp)
    register_osa_tools(mcp)
    register_apple_tools(mcp)

    return mcp
