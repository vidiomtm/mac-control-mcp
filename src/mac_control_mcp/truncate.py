"""AX tree pruning: visible-only, depth cap, token budget (BFS)."""

from __future__ import annotations

import json
from typing import Any

_ALLOWED_ROLES = {
    "AXButton",
    "AXTextField",
    "AXTextArea",
    "AXStaticText",
    "AXLink",
    "AXMenuItem",
    "AXMenu",
    "AXMenuBar",
    "AXMenuBarItem",
    "AXCheckBox",
    "AXRadioButton",
    "AXComboBox",
    "AXPopUpButton",
    "AXList",
    "AXCell",
    "AXRow",
    "AXColumn",
    "AXTable",
    "AXTabGroup",
    "AXTab",
    "AXSlider",
    "AXScrollBar",
    "AXWindow",
    "AXSheet",
    "AXDialog",
    "AXToolbar",
    "AXGroup",
    "AXSplitGroup",
    "AXScrollArea",
    "AXImage",
    "AXWebArea",
    "AXHeading",
}


def prune_tree(
    node: dict[str, Any],
    *,
    max_depth: int = 8,
    budget_chars: int = 12_000,
    _depth: int = 0,
) -> dict[str, Any] | None:
    """Return pruned copy of node or None if should be excluded."""
    role = node.get("role", "")
    if role not in _ALLOWED_ROLES:
        children = node.get("children", [])
        if not children:
            return None

    pruned: dict[str, Any] = {}
    for key in (
        "role",
        "title",
        "value",
        "label",
        "description",
        "enabled",
        "focused",
        "frame",
        "identifier",
    ):
        if key in node:
            pruned[key] = node[key]

    if _depth < max_depth:
        kept: list[dict[str, Any]] = []
        for child in node.get("children", []):
            c = prune_tree(child, max_depth=max_depth, budget_chars=budget_chars, _depth=_depth + 1)
            if c is not None:
                kept.append(c)
        if kept:
            pruned["children"] = kept
    else:
        n = len(node.get("children", []))
        if n:
            pruned["children_truncated"] = n

    return pruned or None


def trim_to_budget(tree: dict[str, Any], budget_chars: int = 12_000) -> dict[str, Any]:
    """BFS-trim: serialize, if oversized drop deepest children first."""
    serialized = json.dumps(tree)
    if len(serialized) <= budget_chars:
        return tree

    nodes_with_children: list[tuple[int, dict[str, Any]]] = []

    def collect(node: dict[str, Any], depth: int = 0) -> None:
        if "children" in node:
            nodes_with_children.append((depth, node))
            for c in node["children"]:
                collect(c, depth + 1)

    collect(tree)
    nodes_with_children.sort(key=lambda x: -x[0])

    for _, node in nodes_with_children:
        n = len(node["children"])
        node["children_truncated"] = n
        del node["children"]
        if len(json.dumps(tree)) <= budget_chars:
            break

    return tree
