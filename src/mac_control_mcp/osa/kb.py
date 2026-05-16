"""Knowledge base: lazy-loaded YAML scripts with fuzzy search."""

from __future__ import annotations

import logging
import os
from typing import Any

log = logging.getLogger(__name__)

_KB: dict[str, dict[str, Any]] | None = None
_KB_DIR = os.path.join(os.path.dirname(__file__), "knowledge")


def _load() -> dict[str, dict[str, Any]]:
    global _KB
    if _KB is not None:
        return _KB
    import yaml

    kb: dict[str, dict[str, Any]] = {}
    for fname in os.listdir(_KB_DIR):
        if not fname.endswith(".yaml"):
            continue
        with open(os.path.join(_KB_DIR, fname)) as f:
            entries = yaml.safe_load(f)
        if isinstance(entries, list):
            for entry in entries:
                kb[entry["id"]] = entry
        elif isinstance(entries, dict):
            kb[entries["id"]] = entries
    _KB = kb
    return _KB


def search(query: str, app: str | None = None, top_k: int = 5) -> list[dict[str, Any]]:
    from rapidfuzz import fuzz

    kb = _load()
    candidates = list(kb.values())
    if app:
        candidates = [
            c for c in candidates if app.lower() in c.get("app", "").lower()
        ] or candidates

    def score_entry(entry: dict[str, Any]) -> float:
        haystack = " ".join(
            [
                entry.get("id", ""),
                entry.get("summary", ""),
                " ".join(entry.get("tags", [])),
                entry.get("app", ""),
            ]
        )
        return fuzz.WRatio(query, haystack)

    scored = sorted(candidates, key=score_entry, reverse=True)
    return [
        {
            "id": e["id"],
            "summary": e.get("summary", ""),
            "app": e.get("app", ""),
            "lang": e.get("lang", "applescript"),
            "tags": e.get("tags", []),
            "args": e.get("args", []),
        }
        for e in scored[:top_k]
    ]


def get(kb_id: str) -> dict[str, Any]:
    kb = _load()
    if kb_id not in kb:
        raise KeyError(f"KB entry not found: {kb_id!r}")
    return kb[kb_id]


def run_by_id(kb_id: str, args: list[str] | None = None) -> dict[str, Any]:
    from mac_control_mcp.osa.runner import run_osa

    entry = get(kb_id)
    return run_osa(entry["script"], lang=entry.get("lang", "applescript"), args=args)
