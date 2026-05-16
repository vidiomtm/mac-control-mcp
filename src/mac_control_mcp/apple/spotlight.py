"""Spotlight / mdfind with structured predicates."""

from __future__ import annotations

import subprocess
from typing import Any


def spotlight_query(
    predicate: str,
    directory: str | None = None,
    limit: int = 50,
) -> dict[str, Any]:
    cmd = ["mdfind"]
    if directory:
        cmd += ["-onlyin", directory]
    cmd.append(predicate)

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    if result.returncode != 0:
        raise RuntimeError(f"mdfind error: {result.stderr.strip()}")

    paths = [p for p in result.stdout.strip().splitlines() if p][:limit]
    return {"paths": paths, "count": len(paths), "predicate": predicate}
