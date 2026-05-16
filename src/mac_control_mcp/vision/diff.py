"""Screen change detection via perceptual hashing."""

from __future__ import annotations

import base64
import logging
import time
from typing import Any

log = logging.getLogger(__name__)


def _hash_image_b64(b64: str) -> int:
    """Simple mean-hash for change detection (no PIL dependency)."""
    import hashlib

    return int(hashlib.md5(base64.b64decode(b64)).hexdigest(), 16)


def wait_for_change(
    region: tuple[int, ...] | None = None,
    timeout_s: float = 10.0,
    poll_interval: float = 0.5,
    threshold: float = 0.02,
) -> dict[str, Any]:
    """
    Poll region until screen changes. Returns elapsed time and final screenshot.
    threshold unused with MD5 strategy (any pixel change detected).
    """
    from mac_control_mcp.vision.capture import capture_screen

    baseline = capture_screen(region=region, scale=0.25)
    baseline_hash = _hash_image_b64(baseline["data"])

    start = time.time()
    while time.time() - start < timeout_s:
        time.sleep(poll_interval)
        current = capture_screen(region=region, scale=0.25)
        current_hash = _hash_image_b64(current["data"])
        if current_hash != baseline_hash:
            elapsed = time.time() - start
            full = capture_screen(region=region)
            return {
                "changed": True,
                "elapsed_s": round(elapsed, 2),
                "screenshot": full,
            }

    return {
        "changed": False,
        "elapsed_s": round(timeout_s, 2),
        "screenshot": capture_screen(region=region),
    }
