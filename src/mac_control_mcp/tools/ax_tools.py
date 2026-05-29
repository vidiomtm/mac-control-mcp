"""AX (Accessibility) tool registration."""

from __future__ import annotations

import json
from typing import Literal

from mcp.server.fastmcp import FastMCP


def register_ax_tools(mcp: FastMCP) -> None:
    @mcp.tool()
    def ax_snapshot(
        app: str | None = None,
        max_depth: int = 8,
        budget_chars: int = 12000,
    ) -> str:
        """
        Snapshot the macOS accessibility tree for an app (or system-wide).
        Returns pruned JSON with element roles, labels, values, and screen coords.
        Works with non-vision models — coords can be passed directly to ax_click.
        """
        from mac_control_mcp.ax.snapshot import snapshot_app
        from mac_control_mcp.truncate import prune_tree, trim_to_budget

        raw = snapshot_app(app, max_depth=max_depth)
        pruned = prune_tree(raw, max_depth=max_depth, budget_chars=budget_chars) or {}
        trimmed = trim_to_budget(pruned, budget_chars=budget_chars)
        return json.dumps(trimmed, ensure_ascii=False)

    @mcp.tool()
    def ax_click(
        x: float,
        y: float,
        button: Literal["left", "right"] = "left",
        count: int = 1,
    ) -> str:
        """Click at screen coordinates. count=2 for double-click."""
        from mac_control_mcp.ax.actions import mouse_click

        mouse_click(x, y, button=button, count=count)
        return json.dumps({"status": "clicked", "x": x, "y": y, "button": button, "count": count})

    @mcp.tool()
    def ax_type(text: str, clear_first: bool = False) -> str:
        """Type text into the focused element. clear_first selects all before typing."""
        from mac_control_mcp.ax.actions import type_text

        type_text(text, clear_first=clear_first)
        return json.dumps({"status": "typed", "length": len(text)})

    @mcp.tool()
    def ax_scroll(x: float, y: float, dy: int, speed: int = 3) -> str:
        """Scroll at (x,y). dy positive = scroll down, negative = scroll up."""
        from mac_control_mcp.ax.actions import scroll

        scroll(x, y, dy, speed=speed)
        return json.dumps({"status": "scrolled", "dy": dy})

    @mcp.tool()
    def ax_hotkey(keys: list[str]) -> str:
        """
        Press a keyboard shortcut. Pass modifiers + key as a list.
        Examples: ["cmd","c"], ["cmd","shift","4"], ["escape"], ["cmd","tab"]
        """
        from mac_control_mcp.ax.actions import hotkey

        hotkey(keys)
        return json.dumps({"status": "sent", "keys": keys})

    @mcp.tool()
    def ax_system_ui(
        target: Literal["spotlight", "menubar_items", "control_center", "launchpad"],
        action: str = "open",
        app: str | None = None,
        menu: str | None = None,
        item: str | None = None,
        query: str | None = None,
    ) -> str:
        """
        Interact with system-level UI elements.
        target=spotlight: action=open|search (pass query for search)
        target=menubar_items: lists menu bar items for app=<name>
        target=control_center: action=open
        target=launchpad: action=open
        For clicking a menu item: target=menubar_items, action=click, app, menu, item
        """
        from mac_control_mcp.ax.system_ui import (
            click_menu_item,
            get_menu_bar_items,
            open_control_center,
            open_launchpad,
            open_spotlight,
            search_spotlight,
        )

        if target == "spotlight":
            if action == "search" and query:
                return json.dumps(search_spotlight(query))
            return json.dumps(open_spotlight())
        elif target == "menubar_items":
            if action == "click" and app and menu and item:
                return json.dumps(click_menu_item(app, menu, item))
            if app:
                return json.dumps({"items": get_menu_bar_items(app)})
            return json.dumps({"error": "app required for menubar_items"})
        elif target == "control_center":
            return json.dumps(open_control_center())
        elif target == "launchpad":
            return json.dumps(open_launchpad())
        return json.dumps({"error": f"unknown target: {target}"})
