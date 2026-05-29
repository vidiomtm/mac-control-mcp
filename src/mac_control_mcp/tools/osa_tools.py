"""OSA (AppleScript/JXA) tool registration."""

from __future__ import annotations

import json
from typing import Literal

from mcp.server.fastmcp import FastMCP


def register_osa_tools(mcp: FastMCP) -> None:
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
