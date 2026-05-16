"""AX actions: click, type, scroll, hotkey via CGEvent."""

from __future__ import annotations

import logging
import time
from typing import Literal

log = logging.getLogger(__name__)

try:
    from Foundation import NSPoint
    from Quartz import (
        CGEventCreateKeyboardEvent,
        CGEventCreateMouseEvent,
        CGEventCreateScrollWheelEvent,
        CGEventPost,
        CGEventSetFlags,
        kCGEventFlagMaskAlternate,
        kCGEventFlagMaskCommand,
        kCGEventFlagMaskControl,
        kCGEventFlagMaskShift,
        kCGEventLeftMouseDown,
        kCGEventLeftMouseUp,
        kCGEventMouseMoved,
        kCGEventRightMouseDown,
        kCGEventRightMouseUp,
        kCGHIDEventTap,
        kCGMouseButtonLeft,
        kCGMouseButtonRight,
        kCGScrollEventUnitLine,
    )

    _QUARTZ_AVAILABLE = True
except ImportError:
    _QUARTZ_AVAILABLE = False
    log.warning("pyobjc Quartz not available; AX actions disabled")

_KEY_CODES: dict[str, int] = {
    "return": 36,
    "enter": 36,
    "tab": 48,
    "space": 49,
    "delete": 51,
    "backspace": 51,
    "escape": 53,
    "esc": 53,
    "cmd": 0,
    "command": 0,  # handled as modifier
    "up": 126,
    "down": 125,
    "left": 123,
    "right": 124,
    "home": 115,
    "end": 119,
    "pageup": 116,
    "pagedown": 121,
    "f1": 122,
    "f2": 120,
    "f3": 99,
    "f4": 118,
    "f5": 96,
    "f6": 97,
    "f7": 98,
    "f8": 100,
    "f9": 101,
    "f10": 109,
    "f11": 103,
    "f12": 111,
    "a": 0,
    "b": 11,
    "c": 8,
    "d": 2,
    "e": 14,
    "f": 3,
    "g": 5,
    "h": 4,
    "i": 34,
    "j": 38,
    "k": 40,
    "l": 37,
    "m": 46,
    "n": 45,
    "o": 31,
    "p": 35,
    "q": 12,
    "r": 15,
    "s": 1,
    "t": 17,
    "u": 32,
    "v": 9,
    "w": 13,
    "x": 7,
    "y": 16,
    "z": 6,
    "0": 29,
    "1": 18,
    "2": 19,
    "3": 20,
    "4": 21,
    "5": 23,
    "6": 22,
    "7": 26,
    "8": 28,
    "9": 25,
    "minus": 27,
    "equal": 24,
    "leftbracket": 33,
    "rightbracket": 30,
    "semicolon": 41,
    "quote": 39,
    "comma": 43,
    "period": 47,
    "slash": 44,
    "grave": 50,
    "backslash": 42,
}

_MODIFIER_FLAGS: dict[str, int] = {
    "cmd": kCGEventFlagMaskCommand if _QUARTZ_AVAILABLE else 0,
    "command": kCGEventFlagMaskCommand if _QUARTZ_AVAILABLE else 0,
    "shift": kCGEventFlagMaskShift if _QUARTZ_AVAILABLE else 0,
    "alt": kCGEventFlagMaskAlternate if _QUARTZ_AVAILABLE else 0,
    "option": kCGEventFlagMaskAlternate if _QUARTZ_AVAILABLE else 0,
    "ctrl": kCGEventFlagMaskControl if _QUARTZ_AVAILABLE else 0,
    "control": kCGEventFlagMaskControl if _QUARTZ_AVAILABLE else 0,
}


def _require_quartz() -> None:
    if not _QUARTZ_AVAILABLE:
        raise RuntimeError("pyobjc Quartz not installed")


def mouse_move(x: float, y: float) -> None:
    _require_quartz()
    pt = NSPoint(x, y)
    ev = CGEventCreateMouseEvent(None, kCGEventMouseMoved, pt, kCGMouseButtonLeft)
    CGEventPost(kCGHIDEventTap, ev)


def mouse_click(
    x: float,
    y: float,
    button: Literal["left", "right"] = "left",
    count: int = 1,
) -> None:
    _require_quartz()
    pt = NSPoint(x, y)
    if button == "right":
        down_type, up_type, btn = kCGEventRightMouseDown, kCGEventRightMouseUp, kCGMouseButtonRight
    else:
        down_type, up_type, btn = kCGEventLeftMouseDown, kCGEventLeftMouseUp, kCGMouseButtonLeft

    mouse_move(x, y)
    for _ in range(count):
        ev_down = CGEventCreateMouseEvent(None, down_type, pt, btn)
        ev_up = CGEventCreateMouseEvent(None, up_type, pt, btn)
        CGEventPost(kCGHIDEventTap, ev_down)
        CGEventPost(kCGHIDEventTap, ev_up)
        if count > 1:
            time.sleep(0.05)


def type_text(text: str, clear_first: bool = False) -> None:
    """Type text using clipboard paste for reliability (handles unicode)."""
    _require_quartz()
    if clear_first:
        hotkey(["cmd", "a"])
        time.sleep(0.05)

    import AppKit

    pb = AppKit.NSPasteboard.generalPasteboard()
    pb.clearContents()
    pb.setString_forType_(text, AppKit.NSPasteboardTypeString)
    hotkey(["cmd", "v"])


def scroll(x: float, y: float, dy: int, speed: int = 3) -> None:
    _require_quartz()
    mouse_move(x, y)
    ev = CGEventCreateScrollWheelEvent(None, kCGScrollEventUnitLine, 1, dy * speed)
    CGEventPost(kCGHIDEventTap, ev)


def hotkey(keys: list[str]) -> None:
    """Press modifier + key combo. E.g. ['cmd','c'] for copy."""
    _require_quartz()
    modifiers = [k.lower() for k in keys if k.lower() in _MODIFIER_FLAGS]
    non_mods = [k.lower() for k in keys if k.lower() not in _MODIFIER_FLAGS]

    flags = 0
    for mod in modifiers:
        flags |= _MODIFIER_FLAGS[mod]

    for key_name in non_mods:
        keycode = _KEY_CODES.get(key_name)
        if keycode is None:
            raise ValueError(f"Unknown key: {key_name!r}. Use _KEY_CODES keys.")
        ev_down = CGEventCreateKeyboardEvent(None, keycode, True)
        ev_up = CGEventCreateKeyboardEvent(None, keycode, False)
        if flags:
            CGEventSetFlags(ev_down, flags)
            CGEventSetFlags(ev_up, flags)
        CGEventPost(kCGHIDEventTap, ev_down)
        CGEventPost(kCGHIDEventTap, ev_up)
        time.sleep(0.02)
