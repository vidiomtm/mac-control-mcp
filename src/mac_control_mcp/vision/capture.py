"""Screenshot capture: full screen, window, or region."""

from __future__ import annotations

import base64
import logging
import os
import subprocess
import tempfile
from typing import Any

log = logging.getLogger(__name__)


def capture_screen(
    display: int = 0,
    region: tuple[int, ...] | None = None,
    window_id: int | None = None,
    scale: float = 1.0,
    format: str = "png",
) -> dict[str, Any]:
    """
    Capture screen to base64.
    region: (x, y, width, height)
    scale: downsample for token efficiency (0.5 = half size)
    """
    with tempfile.NamedTemporaryFile(suffix=f".{format}", delete=False) as f:
        tmp_path = f.name

    try:
        cmd = ["screencapture", "-x"]

        if window_id is not None:
            cmd += ["-l", str(window_id)]
        elif region is not None:
            x, y, w, h = region
            cmd += ["-R", f"{x},{y},{w},{h}"]
        else:
            cmd += ["-D", str(display + 1)]

        if format == "jpg":
            cmd += ["-t", "jpg"]

        cmd.append(tmp_path)
        result = subprocess.run(cmd, capture_output=True, timeout=10)
        if result.returncode != 0:
            raise RuntimeError(f"screencapture failed: {result.stderr.decode()}")

        if scale != 1.0:
            _scale_image(tmp_path, scale, format)

        with open(tmp_path, "rb") as f:
            data = f.read()

        import io

        from PIL import Image

        img = Image.open(io.BytesIO(data))
        width, height = img.size

    except ImportError:
        with open(tmp_path, "rb") as f:
            data = f.read()
        width, height = None, None
    finally:
        os.unlink(tmp_path)

    return {
        "data": base64.b64encode(data).decode(),
        "format": format,
        "width": width,
        "height": height,
        "size_bytes": len(data),
    }


def _scale_image(path: str, scale: float, fmt: str) -> None:
    try:
        from PIL import Image

        img = Image.open(path)
        new_w = int(img.width * scale)
        new_h = int(img.height * scale)
        img = img.resize((new_w, new_h), Image.LANCZOS)
        img.save(path)
    except ImportError:
        pass  # PIL optional; skip scaling


def list_windows() -> list[dict[str, Any]]:
    """List visible windows with IDs for targeted capture."""
    try:
        from Quartz import (
            CGWindowListCopyWindowInfo,
            kCGNullWindowID,
            kCGWindowListOptionOnScreenOnly,
        )

        windows = CGWindowListCopyWindowInfo(kCGWindowListOptionOnScreenOnly, kCGNullWindowID)
        result = []
        for w in windows:
            entry: dict[str, Any] = {
                "id": w.get("kCGWindowNumber"),
                "owner": w.get("kCGWindowOwnerName"),
                "name": w.get("kCGWindowName"),
                "layer": w.get("kCGWindowLayer"),
            }
            bounds = w.get("kCGWindowBounds")
            if bounds:
                entry["bounds"] = {
                    "x": bounds.get("X"),
                    "y": bounds.get("Y"),
                    "w": bounds.get("Width"),
                    "h": bounds.get("Height"),
                }
            result.append(entry)
        return [r for r in result if r.get("layer", 999) <= 0 or r.get("owner")]
    except ImportError:
        return []
