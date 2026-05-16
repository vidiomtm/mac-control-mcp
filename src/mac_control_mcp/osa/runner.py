"""OSA script execution via subprocess list-args (no shell injection)."""

from __future__ import annotations

import logging
import subprocess
from typing import Any

from mac_control_mcp.security import check_osa_script

log = logging.getLogger(__name__)


def run_osa(
    script: str,
    lang: str = "applescript",
    args: list[str] | None = None,
    timeout_s: float = 15.0,
) -> dict[str, Any]:
    """
    Execute AppleScript or JXA. Uses list-form subprocess (no shell).
    args: positional argv passed after -- (accessible as argv in JXA).
    """
    check_osa_script(script)

    cmd = ["osascript"]
    if lang.lower() in ("jxa", "javascript"):
        cmd += ["-l", "JavaScript"]
    cmd += ["-e", script]
    if args:
        cmd += ["--"] + [str(a) for a in args]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout_s,
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"OSA script timed out after {timeout_s}s") from None

    if result.returncode != 0:
        raise RuntimeError(f"OSA error: {result.stderr.strip()}")

    return {
        "output": result.stdout.strip(),
        "lang": lang,
    }
