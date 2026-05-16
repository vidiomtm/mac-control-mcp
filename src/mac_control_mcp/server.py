"""MCP server: registers all mac-control tools via FastMCP."""

from __future__ import annotations

import json
import logging
from typing import Any, Literal

from mcp.server.fastmcp import FastMCP

log = logging.getLogger(__name__)


def create_server() -> FastMCP:
    mcp = FastMCP(
        "mac-control",
        instructions="Unified macOS automation: AX tree, vision/OCR, AppleScript/JXA, Apple apps",
    )

    # ─── AX: Accessibility tree ──────────────────────────────────────────────

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

    # ─── Vision: screenshot + OCR ────────────────────────────────────────────

    @mcp.tool()
    def screen_capture(
        display: int = 0,
        region: list[int] | None = None,
        window_id: int | None = None,
        scale: float = 1.0,
        format: str = "png",
    ) -> dict[str, Any]:
        """
        Capture screen as base64-encoded image.
        region: [x, y, width, height] for partial capture.
        scale: 0.5 halves resolution (reduces tokens for vision models).
        Returns: {data: base64, format, width, height, size_bytes}
        """
        from mac_control_mcp.vision.capture import capture_screen

        region_tuple = tuple(region) if region else None
        return capture_screen(
            display=display,
            region=region_tuple,
            window_id=window_id,
            scale=scale,
            format=format,
        )

    @mcp.tool()
    def screen_list_windows() -> str:
        """List visible windows with IDs, owners, and bounds for targeted capture."""
        from mac_control_mcp.vision.capture import list_windows

        return json.dumps(list_windows())

    @mcp.tool()
    def screen_ocr(
        region: list[int] | None = None,
        image_b64: str | None = None,
    ) -> str:
        """
        OCR text from screen region or provided base64 image.
        Returns: {text: full_text, observations: [{text, confidence, bbox}], count}
        Works as fallback for Electron/game apps where AX tree is unavailable.
        """
        from mac_control_mcp.vision.ocr import ocr_image_b64, ocr_screen_region

        if image_b64:
            result = ocr_image_b64(image_b64)
        else:
            region_tuple = tuple(region) if region else None
            result = ocr_screen_region(region=region_tuple)
        return json.dumps(result)

    @mcp.tool()
    def screen_wait_for_change(
        region: list[int] | None = None,
        timeout_s: float = 10.0,
        poll_interval: float = 0.5,
    ) -> str:
        """
        Poll screen region until a visual change is detected.
        Returns: {changed: bool, elapsed_s, screenshot: {data, format, ...}}
        Useful after triggering an action to wait for UI to update.
        """
        from mac_control_mcp.vision.diff import wait_for_change

        region_tuple = tuple(region) if region else None
        result = wait_for_change(
            region=region_tuple,
            timeout_s=timeout_s,
            poll_interval=poll_interval,
        )
        return json.dumps(result)

    # ─── OSA: AppleScript / JXA ──────────────────────────────────────────────

    @mcp.tool()
    def osa_search(
        query: str,
        app: str | None = None,
        top_k: int = 5,
    ) -> str:
        """
        Fuzzy search the AppleScript/JXA knowledge base.
        Returns ranked KB entries with IDs to pass to osa_run.
        Use this before osa_exec to avoid writing incorrect AppleScript from scratch.
        """
        from mac_control_mcp.osa.kb import search

        results = search(query, app=app, top_k=top_k)
        return json.dumps(results)

    @mcp.tool()
    def osa_run(
        kb_id: str,
        args: list[str] | None = None,
    ) -> str:
        """
        Execute an AppleScript/JXA script from the knowledge base by ID.
        Get IDs from osa_search. Pass args matching the entry's arg list.
        """
        from mac_control_mcp.osa.kb import run_by_id

        result = run_by_id(kb_id, args=args)
        return json.dumps(result)

    @mcp.tool()
    def osa_exec(
        script: str,
        lang: Literal["applescript", "jxa"] = "applescript",
        timeout_s: float = 15.0,
    ) -> str:
        """
        Execute raw AppleScript or JXA. Use osa_search + osa_run first.
        Forbidden: do shell script with rm -rf, sudo, dd if=
        """
        from mac_control_mcp.osa.runner import run_osa

        result = run_osa(script, lang=lang, timeout_s=timeout_s)
        return json.dumps(result)

    # ─── Apple apps ──────────────────────────────────────────────────────────

    @mcp.tool()
    def mail_search(
        query: str,
        since: str | None = None,
        until: str | None = None,
        limit: int = 20,
    ) -> str:
        """
        Search Mail messages. Thin paginated wrapper — never dumps full inbox.
        since/until: ISO date strings e.g. '2026-01-01'
        """
        from mac_control_mcp.osa.kb import run_by_id

        result = run_by_id("mail_search_subject", args=[query])
        return json.dumps(result)

    @mcp.tool()
    def mail_recent(limit: int = 20) -> str:
        """Get recent inbox messages (newest first, paginated)."""
        from mac_control_mcp.osa.kb import run_by_id

        result = run_by_id("mail_recent_messages", args=[str(limit)])
        return json.dumps(result)

    @mcp.tool()
    def mail_send(to: str, subject: str, body: str) -> str:
        """Send an email via Mail.app."""
        from mac_control_mcp.osa.kb import run_by_id

        result = run_by_id("mail_compose_send", args=[to, subject, body])
        return json.dumps(result)

    @mcp.tool()
    def calendar_events(
        start: str,
        end: str,
        limit: int = 50,
    ) -> str:
        """
        List calendar events between start and end (YYYY-MM-DD).
        Filtered at OS layer — no full calendar dumps.
        """
        from mac_control_mcp.osa.kb import run_by_id

        result = run_by_id("calendar_list_events_range", args=[start, end, str(limit)])
        return json.dumps(result)

    @mcp.tool()
    def calendar_create_event(
        title: str,
        start: str,
        end: str,
        calendar_name: str = "",
    ) -> str:
        """
        Create a calendar event.
        start/end: datetime strings e.g. '2026-05-20 14:00'
        """
        from mac_control_mcp.osa.kb import run_by_id

        result = run_by_id("calendar_create_event", args=[title, start, end, calendar_name])
        return json.dumps(result)

    @mcp.tool()
    def reminders_list(
        list_name: str = "",
        completed: bool = False,
        limit: int = 50,
    ) -> str:
        """List reminders. Filtered at OS layer."""
        from mac_control_mcp.osa.kb import run_by_id

        result = run_by_id("reminders_list", args=[list_name, str(completed).lower(), str(limit)])
        return json.dumps(result)

    @mcp.tool()
    def reminders_add(
        name: str,
        list_name: str = "",
        due_date: str = "",
        notes: str = "",
    ) -> str:
        """Add a reminder. due_date format: 'YYYY-MM-DD HH:MM' (optional)."""
        from mac_control_mcp.osa.kb import run_by_id

        result = run_by_id("reminders_add", args=[name, list_name, due_date, notes])
        return json.dumps(result)

    @mcp.tool()
    def notes_search(
        query: str,
        folder: str = "",
        limit: int = 20,
    ) -> str:
        """Search Notes by title or body. Returns previews, not full bodies."""
        from mac_control_mcp.osa.kb import run_by_id

        result = run_by_id("notes_search", args=[query, folder, str(limit)])
        return json.dumps(result)

    @mcp.tool()
    def notes_get(note_id: str) -> str:
        """Get full content of a note by ID (from notes_search results)."""
        from mac_control_mcp.osa.kb import run_by_id

        result = run_by_id("notes_get", args=[note_id])
        return json.dumps(result)

    @mcp.tool()
    def notes_create(title: str, body: str, folder: str = "") -> str:
        """Create a new note."""
        from mac_control_mcp.osa.kb import run_by_id

        result = run_by_id("notes_create", args=[title, body, folder])
        return json.dumps(result)

    @mcp.tool()
    def messages_recent(handle: str = "", limit: int = 20) -> str:
        """Get recent Messages conversations. handle filters by name/number."""
        from mac_control_mcp.osa.kb import run_by_id

        result = run_by_id("messages_recent", args=[handle, str(limit)])
        return json.dumps(result)

    @mcp.tool()
    def messages_send(handle: str, text: str) -> str:
        """Send an iMessage/SMS to a phone number or Apple ID."""
        from mac_control_mcp.osa.kb import run_by_id

        result = run_by_id("messages_send", args=[handle, text])
        return json.dumps(result)

    @mcp.tool()
    def contacts_search(query: str, limit: int = 20) -> str:
        """Search Contacts by name, email, or phone number."""
        from mac_control_mcp.osa.kb import run_by_id

        result = run_by_id("contacts_search", args=[query, str(limit)])
        return json.dumps(result)

    @mcp.tool()
    def spotlight_query(
        predicate: str,
        directory: str | None = None,
        limit: int = 50,
    ) -> str:
        """
        Search files via Spotlight mdfind predicates.
        Examples: 'kMDItemKind == "PDF document"'
                  'kMDItemTextContent = "*budget*"cdw'
                  'kind:image date:today'
        """
        from mac_control_mcp.apple.spotlight import spotlight_query as _sq

        return json.dumps(_sq(predicate, directory=directory, limit=limit))

    @mcp.tool()
    def finder_tags_get(path: str) -> str:
        """Get Finder color tags on a file or folder."""
        from mac_control_mcp.osa.kb import run_by_id

        result = run_by_id("finder_list_tags", args=[path])
        return json.dumps(result)

    @mcp.tool()
    def finder_tags_set(path: str, tags: list[str]) -> str:
        """Set Finder tags on a file or folder. Replaces existing tags."""
        from mac_control_mcp.osa.kb import run_by_id

        result = run_by_id("finder_set_tags", args=[path, ",".join(tags)])
        return json.dumps(result)

    @mcp.tool()
    def quicklook(path: str) -> str:
        """Open a file in Quick Look preview."""
        from mac_control_mcp.osa.kb import run_by_id

        result = run_by_id("quicklook_file", args=[path])
        return json.dumps(result)

    return mcp
