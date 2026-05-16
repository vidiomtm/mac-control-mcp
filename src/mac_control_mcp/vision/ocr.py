"""OCR via macOS Vision.framework (VNRecognizeTextRequest)."""

from __future__ import annotations

import base64
import logging
import os
import tempfile
from typing import Any

log = logging.getLogger(__name__)


def ocr_image_b64(image_b64: str) -> dict[str, Any]:
    data = base64.b64decode(image_b64)
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        f.write(data)
        tmp_path = f.name
    try:
        return _ocr_path(tmp_path)
    finally:
        os.unlink(tmp_path)


def ocr_screen_region(
    region: tuple[int, ...] | None = None,
) -> dict[str, Any]:
    from mac_control_mcp.vision.capture import capture_screen

    result = capture_screen(region=region)
    return ocr_image_b64(result["data"])


def _ocr_path(path: str) -> dict[str, Any]:
    try:
        import Cocoa
        import Vision

        url = Cocoa.NSURL.fileURLWithPath_(path)
        handler = Vision.VNImageRequestHandler.alloc().initWithURL_options_(url, {})

        request = Vision.VNRecognizeTextRequest.alloc().init()
        request.setRecognitionLevel_(1)  # VNRequestTextRecognitionLevelAccurate
        request.setUsesLanguageCorrection_(True)

        success, error = handler.performRequests_error_([request], None)
        if not success or error:
            raise RuntimeError(f"Vision OCR failed: {error}")

        observations = request.results() or []
        texts = []
        for obs in observations:
            candidate = obs.topCandidates_(1)
            if candidate:
                c = candidate[0]
                bb = obs.boundingBox()
                texts.append(
                    {
                        "text": str(c.string()),
                        "confidence": float(c.confidence()),
                        "bbox": {
                            "x": round(bb.origin.x, 4),
                            "y": round(bb.origin.y, 4),
                            "w": round(bb.size.width, 4),
                            "h": round(bb.size.height, 4),
                        },
                    }
                )

        full_text = " ".join(t["text"] for t in texts)
        return {"text": full_text, "observations": texts, "count": len(texts)}

    except ImportError:
        log.warning("Vision framework unavailable; falling back to subprocess")
        return _ocr_fallback(path)


def _ocr_fallback(path: str) -> dict[str, Any]:
    """AppleScript-based OCR fallback using Preview + accessibility."""
    import subprocess

    script = f'''
use framework "Vision"
use scripting additions

set imageURL to POSIX file "{path}" as alias
set vHandler to current application's VNImageRequestHandler's alloc()'s initWithURL:(imageURL as «class furl») options:(current application's NSDictionary's dictionary())
set vRequest to current application's VNRecognizeTextRequest's alloc()'s init()
vHandler's performRequests:{{vRequest}} |error|:(missing value)
set results to vRequest's results()
set output to ""
repeat with obs in results
    set output to output & ((obs's topCandidates:1)'s objectAtIndex:0)'s |string|() & linefeed
end repeat
return output
'''
    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True,
        text=True,
        timeout=30,
    )
    text = result.stdout.strip()
    return {"text": text, "observations": [], "count": 0}
