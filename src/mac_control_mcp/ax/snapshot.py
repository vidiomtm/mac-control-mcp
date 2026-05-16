"""AX accessibility tree snapshot via pyobjc ApplicationServices."""

from __future__ import annotations

import logging
from typing import Any

log = logging.getLogger(__name__)

try:
    import AppKit
    from ApplicationServices import (
        AXUIElementCopyAttributeValue,
        AXUIElementCreateApplication,
        AXUIElementCreateSystemWide,
        kAXErrorSuccess,
    )

    _AX_AVAILABLE = True
except ImportError:
    _AX_AVAILABLE = False
    log.warning("pyobjc ApplicationServices not available; AX tools disabled")


def _ax_attr(element: Any, attr: str) -> Any:
    err, val = AXUIElementCopyAttributeValue(element, attr, None)
    if err == kAXErrorSuccess:
        return val
    return None


def _element_to_dict(element: Any, depth: int, max_depth: int) -> dict[str, Any]:
    node: dict[str, Any] = {}

    role = _ax_attr(element, "AXRole")
    if role:
        node["role"] = str(role)

    for attr, key in [
        ("AXTitle", "title"),
        ("AXValue", "value"),
        ("AXDescription", "description"),
        ("AXLabel", "label"),
        ("AXIdentifier", "identifier"),
        ("AXEnabled", "enabled"),
        ("AXFocused", "focused"),
    ]:
        val = _ax_attr(element, attr)
        if val is not None:
            import contextlib

            with contextlib.suppress(Exception):
                node[key] = str(val) if not isinstance(val, bool) else val

    frame = _ax_attr(element, "AXFrame")
    if frame is not None:
        import contextlib

        with contextlib.suppress(Exception):
            node["frame"] = {
                "x": round(frame.origin.x, 1),
                "y": round(frame.origin.y, 1),
                "w": round(frame.size.width, 1),
                "h": round(frame.size.height, 1),
            }

    if depth < max_depth:
        children = _ax_attr(element, "AXChildren")
        if children:
            child_nodes = []
            for child in children:
                try:
                    child_dict = _element_to_dict(child, depth + 1, max_depth)
                    if child_dict:
                        child_nodes.append(child_dict)
                except Exception:
                    pass
            if child_nodes:
                node["children"] = child_nodes
    else:
        children = _ax_attr(element, "AXChildren")
        if children:
            node["children_truncated"] = len(children)

    return node


def snapshot_app(app_name: str | None, max_depth: int = 8) -> dict[str, Any]:
    if not _AX_AVAILABLE:
        raise RuntimeError("pyobjc ApplicationServices not installed")

    if app_name:
        apps = AppKit.NSWorkspace.sharedWorkspace().runningApplications()
        pid = None
        for app in apps:
            if app.localizedName() and app_name.lower() in app.localizedName().lower():
                pid = app.processIdentifier()
                break
        if pid is None:
            raise ValueError(f"App not found: {app_name!r}")
        root = AXUIElementCreateApplication(pid)
    else:
        root = AXUIElementCreateSystemWide()

    return _element_to_dict(root, 0, max_depth)


def focused_element() -> dict[str, Any]:
    if not _AX_AVAILABLE:
        raise RuntimeError("pyobjc ApplicationServices not installed")
    system = AXUIElementCreateSystemWide()
    focused = _ax_attr(system, "AXFocusedUIElement")
    if focused is None:
        return {}
    return _element_to_dict(focused, 0, 2)
