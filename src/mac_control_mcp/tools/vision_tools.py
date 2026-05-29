"""Vision (screenshot + OCR) tool registration."""

from __future__ import annotations

import json
from typing import Any

from mcp.server.fastmcp import FastMCP


def register_vision_tools(mcp: FastMCP) -> None:
    @mcp.tool()
    def screen_capture(
        display: int = 0,
        region: list[int] | None = None,
        window_id: int | None = None,
        scale: float = 1.0,
        format: str = "png",
    ) -> dict[str, Any]:
        """
        Capture screen as base64-encoded image.
        region: [x, y, width, height] for partial capture.
        scale: 0.5 halves resolution (reduces tokens for vision models).
        Returns: {data: base64, format, width, height, size_bytes}
        """
        from mac_control_mcp.vision.capture import capture_screen

        region_tuple = tuple(region) if region else None
        return capture_screen(
            display=display,
            region=region_tuple,
            window_id=window_id,
            scale=scale,
            format=format,
        )

    @mcp.tool()
    def screen_list_windows() -> str:
        """List visible windows with IDs, owners, and bounds for targeted capture."""
        from mac_control_mcp.vision.capture import list_windows

        return json.dumps(list_windows())

    @mcp.tool()
    def screen_ocr(
        region: list[int] | None = None,
        image_b64: str | None = None,
    ) -> str:
        """
        OCR text from screen region or provided base64 image.
        Returns: {text: full_text, observations: [{text, confidence, bbox}], count}
        Works as fallback for Electron/game apps where AX tree is unavailable.
        """
        from mac_control_mcp.vision.ocr import ocr_image_b64, ocr_screen_region

        if image_b64:
            result = ocr_image_b64(image_b64)
        else:
            region_tuple = tuple(region) if region else None
            result = ocr_screen_region(region=region_tuple)
        return json.dumps(result)

    @mcp.tool()
    def screen_wait_for_change(
        region: list[int] | None = None,
        timeout_s: float = 10.0,
        poll_interval: float = 0.5,
    ) -> str:
        """
        Poll screen region until a visual change is detected.
        Returns: {changed: bool, elapsed_s, screenshot: {data, format, ...}}
        Useful after triggering an action to wait for UI to update.
        """
        from mac_control_mcp.vision.diff import wait_for_change

        region_tuple = tuple(region) if region else None
        result = wait_for_change(
            region=region_tuple,
            timeout_s=timeout_s,
            poll_interval=poll_interval,
        )
        return json.dumps(result)
