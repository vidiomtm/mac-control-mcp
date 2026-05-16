"""System-level UI targets: Spotlight, menu bar, Control Center, Launchpad."""

from __future__ import annotations

import logging
import subprocess

log = logging.getLogger(__name__)


def open_spotlight() -> dict[str, str]:
    """Open Spotlight via cmd+space."""
    from mac_control_mcp.ax.actions import hotkey

    hotkey(["cmd", "space"])
    return {"status": "opened"}


def search_spotlight(query: str) -> dict[str, str]:
    """Open Spotlight and type query."""
    import time

    from mac_control_mcp.ax.actions import hotkey, type_text

    hotkey(["cmd", "space"])
    time.sleep(0.4)
    type_text(query)
    return {"status": "searching", "query": query}


def open_control_center() -> dict[str, str]:
    """Open Control Center (macOS 11+)."""
    # Control Center has no standard shortcut; use menu bar click via AX
    result = subprocess.run(
        [
            "osascript",
            "-e",
            'tell application "System Events" to key code 49 using {control down, option down}',
        ],
        capture_output=True,
        text=True,
        timeout=5,
    )
    return {"status": "opened", "stderr": result.stderr.strip()}


def open_launchpad() -> dict[str, str]:
    subprocess.run(
        ["osascript", "-e", 'tell application "Launchpad" to activate'],
        capture_output=True,
        text=True,
        timeout=5,
    )
    return {"status": "opened"}


def get_menu_bar_items(app_name: str) -> list[str]:
    """List top-level menu bar items for an app."""
    script = f'''
tell application "System Events"
    tell process "{app_name}"
        set menuNames to name of every menu bar item of menu bar 1
    end tell
end tell
return menuNames
'''
    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True,
        text=True,
        timeout=10,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())
    items = [i.strip() for i in result.stdout.strip().split(",") if i.strip()]
    return items


def click_menu_item(app_name: str, menu: str, item: str) -> dict[str, str]:
    """Click a specific menu item in an app."""
    script = f'''
tell application "System Events"
    tell process "{app_name}"
        click menu item "{item}" of menu "{menu}" of menu bar 1
    end tell
end tell
'''
    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True,
        text=True,
        timeout=10,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())
    return {"status": "clicked", "app": app_name, "menu": menu, "item": item}
