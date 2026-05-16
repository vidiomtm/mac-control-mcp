"""Unit tests for mac_control_mcp.ax.actions key maps."""

from __future__ import annotations

import pytest


@pytest.mark.unit
def test_key_codes_covers_alpha() -> None:
    from mac_control_mcp.ax.actions import _KEY_CODES

    for ch in "abcdefghijklmnopqrstuvwxyz":
        assert ch in _KEY_CODES, f"missing key: {ch!r}"


@pytest.mark.unit
def test_key_codes_covers_digits() -> None:
    from mac_control_mcp.ax.actions import _KEY_CODES

    for d in "0123456789":
        assert d in _KEY_CODES, f"missing digit: {d!r}"


@pytest.mark.unit
def test_key_codes_covers_function_keys() -> None:
    from mac_control_mcp.ax.actions import _KEY_CODES

    for i in range(1, 13):
        assert f"f{i}" in _KEY_CODES, f"missing key: f{i}"


@pytest.mark.unit
def test_key_codes_covers_special_keys() -> None:
    from mac_control_mcp.ax.actions import _KEY_CODES

    for key in ("return", "tab", "space", "escape", "delete", "up", "down", "left", "right"):
        assert key in _KEY_CODES, f"missing key: {key!r}"


@pytest.mark.unit
def test_modifier_flags_covers_synonyms() -> None:
    from mac_control_mcp.ax.actions import _MODIFIER_FLAGS

    for mod in ("cmd", "command", "shift", "alt", "option", "ctrl", "control"):
        assert mod in _MODIFIER_FLAGS, f"missing modifier: {mod!r}"


@pytest.mark.unit
def test_hotkey_raises_for_unknown_key(monkeypatch: pytest.MonkeyPatch) -> None:
    import mac_control_mcp.ax.actions as actions_mod

    monkeypatch.setattr(actions_mod, "_QUARTZ_AVAILABLE", True)

    # Patch CGEvent calls to no-ops
    monkeypatch.setattr(actions_mod, "CGEventCreateKeyboardEvent", lambda *a: object())
    monkeypatch.setattr(actions_mod, "CGEventSetFlags", lambda *a: None)
    monkeypatch.setattr(actions_mod, "CGEventPost", lambda *a: None)

    with pytest.raises(ValueError, match="Unknown key"):
        actions_mod.hotkey(["cmd", "totally_unknown_key_xyz"])


@pytest.mark.unit
def test_hotkey_skips_pure_modifier_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    """hotkey(['cmd']) with no non-modifier key does nothing (no KeyError)."""
    import mac_control_mcp.ax.actions as actions_mod

    monkeypatch.setattr(actions_mod, "_QUARTZ_AVAILABLE", True)
    monkeypatch.setattr(actions_mod, "CGEventCreateKeyboardEvent", lambda *a: object())
    monkeypatch.setattr(actions_mod, "CGEventSetFlags", lambda *a: None)
    monkeypatch.setattr(actions_mod, "CGEventPost", lambda *a: None)

    # Only modifiers — loop over non_mods is empty, no exception
    actions_mod.hotkey(["cmd", "shift"])
