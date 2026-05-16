"""Unit tests for mac_control_mcp.truncate."""

from __future__ import annotations

import json

import pytest

from mac_control_mcp.truncate import prune_tree, trim_to_budget

# ── helpers ──────────────────────────────────────────────────────────────────


def button(title: str = "OK", x: float = 10, y: float = 10) -> dict:
    return {"role": "AXButton", "title": title, "frame": {"x": x, "y": y, "w": 80, "h": 30}}


def text_field(value: str = "hello") -> dict:
    return {"role": "AXTextField", "value": value, "frame": {"x": 10, "y": 50, "w": 200, "h": 30}}


def window(*children) -> dict:
    node = {"role": "AXWindow", "title": "Win", "frame": {"x": 0, "y": 0, "w": 800, "h": 600}}
    if children:
        node["children"] = list(children)
    return node


# ── allowed / disallowed roles ────────────────────────────────────────────────


@pytest.mark.unit
def test_prune_keeps_allowed_role():
    result = prune_tree(button())
    assert result is not None
    assert result["role"] == "AXButton"


@pytest.mark.unit
def test_prune_drops_unknown_role():
    node = {"role": "AXUnknownWidget", "title": "Hidden"}
    assert prune_tree(node) is None


@pytest.mark.unit
def test_prune_keeps_children_with_allowed_roles():
    tree = window(button("OK"), {"role": "AXSomeNonsense"}, text_field())
    result = prune_tree(tree)
    assert result is not None
    roles = [c["role"] for c in result.get("children", [])]
    assert "AXButton" in roles
    assert "AXTextField" in roles
    assert "AXSomeNonsense" not in roles


@pytest.mark.unit
def test_prune_drops_node_with_no_children_and_unknown_role():
    node = {"role": "AXSomething", "title": "X"}
    assert prune_tree(node) is None


@pytest.mark.unit
def test_prune_unknown_role_with_allowed_children_is_kept():
    """Unknown-role parent survives if it has allowed children."""
    node = {"role": "AXContainer", "children": [button()]}
    result = prune_tree(node)
    assert result is not None
    assert len(result["children"]) == 1


# ── depth cap ────────────────────────────────────────────────────────────────


@pytest.mark.unit
def test_prune_respects_max_depth():
    deep = button("leaf")
    mid = {"role": "AXGroup", "children": [deep]}
    root = window(mid)
    result = prune_tree(root, max_depth=1)
    assert result is not None
    # at depth 0 window children processed; mid at depth 1 => no further recursion
    child = result["children"][0]
    assert child["role"] == "AXGroup"
    assert "children" not in child
    assert child.get("children_truncated", 0) == 1


@pytest.mark.unit
def test_prune_children_truncated_count_is_correct():
    root = window(button("a"), button("b"), button("c"))
    result = prune_tree(root, max_depth=0)
    assert result is not None
    assert "children" not in result
    assert result.get("children_truncated") == 3


# ── field preservation ────────────────────────────────────────────────────────


@pytest.mark.unit
def test_prune_preserves_frame():
    node = button("X", x=100, y=200)
    result = prune_tree(node)
    assert result is not None
    assert result["frame"]["x"] == 100
    assert result["frame"]["y"] == 200


@pytest.mark.unit
def test_prune_preserves_value_and_identifier():
    node = {"role": "AXTextField", "value": "typed", "identifier": "search", "enabled": True}
    result = prune_tree(node)
    assert result is not None
    assert result["value"] == "typed"
    assert result["identifier"] == "search"
    assert result["enabled"] is True


TINY_BUDGET = 200


# ── prune edge cases ──────────────────────────────────────────────────────────


@pytest.mark.unit
def test_prune_empty_dict_returns_none():
    assert prune_tree({}) is None


@pytest.mark.unit
def test_prune_minimal_allowed_node():
    node = {"role": "AXButton"}
    result = prune_tree(node)
    assert result is not None
    assert result["role"] == "AXButton"


# ── trim_to_budget ────────────────────────────────────────────────────────────


@pytest.mark.unit
def test_trim_no_op_when_under_budget():
    tree = window(button())
    original = json.dumps(tree)
    trimmed = trim_to_budget(tree, budget_chars=len(original) + 100)
    assert json.dumps(trimmed) == original


@pytest.mark.unit
def test_trim_reduces_size():
    children = [button(f"btn{i}") for i in range(50)]
    tree: dict = {"role": "AXWindow", "children": children}
    serialized = json.dumps(tree)
    assert len(serialized) > TINY_BUDGET

    trimmed = trim_to_budget(tree, budget_chars=TINY_BUDGET)
    assert len(json.dumps(trimmed)) <= TINY_BUDGET


@pytest.mark.unit
def test_trim_adds_children_truncated():
    children = [button(f"b{i}") for i in range(30)]
    tree: dict = {"role": "AXWindow", "children": children}
    trimmed = trim_to_budget(tree, budget_chars=100)
    assert "children_truncated" in trimmed
    assert trimmed["children_truncated"] == 30
