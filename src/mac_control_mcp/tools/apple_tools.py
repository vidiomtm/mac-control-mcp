"""Apple apps tool registration."""

from __future__ import annotations

import json

from mcp.server.fastmcp import FastMCP


def register_apple_tools(mcp: FastMCP) -> None:
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
