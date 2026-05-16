"""Shared E2E helpers: MCP session management."""

from __future__ import annotations

import json
import sys
import time
from collections.abc import Generator
from contextlib import contextmanager
import subprocess


@contextmanager
def mcp_session(timeout: float = 15.0) -> Generator[tuple, None, None]:
    """Start server subprocess, yield (send, recv) helpers, shutdown on exit."""
    proc = subprocess.Popen(
        [sys.executable, "-m", "mac_control_mcp"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    def send(msg: dict) -> None:
        assert proc.stdin is not None
        line = json.dumps(msg) + "\n"
        proc.stdin.write(line.encode())
        proc.stdin.flush()

    def recv(req_id: int, deadline: float | None = None) -> dict:
        assert proc.stdout is not None
        if deadline is None:
            deadline = time.time() + timeout
        while time.time() < deadline:
            proc.stdout.flush()
            line = proc.stdout.readline()
            if not line:
                time.sleep(0.05)
                continue
            obj = json.loads(line.decode())
            if obj.get("id") == req_id:
                return obj
        raise TimeoutError(f"No response for id={req_id}")

    try:
        yield send, recv
    finally:
        try:
            assert proc.stdin is not None
            proc.stdin.close()
        except Exception:
            pass
        proc.wait(timeout=3)


def _initialize(send, recv) -> dict:
    send(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "pytest", "version": "0.0.1"},
            },
        }
    )
    return recv(1)


def _extract_text(content) -> str:
    """Extract text from MCP content block list."""
    return content[0]["text"]
