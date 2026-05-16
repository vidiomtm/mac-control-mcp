"""E2E test: full osa_search → osa_run path via JSON-RPC stdio."""

from __future__ import annotations

import json

import pytest

from tests.e2e.helpers import _extract_text, _initialize, mcp_session


@pytest.mark.e2e
def test_get_volume_full_path() -> None:
    """osa_search finds system_get_volume → osa_run returns integer 0-100."""
    with mcp_session() as (send, recv):
        _initialize(send, recv)

        # Step 1: search
        send(
            {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "osa_search",
                    "arguments": {"query": "get volume audio", "top_k": 5},
                },
            }
        )
        search_resp = recv(2)
        results = json.loads(_extract_text(search_resp["result"]["content"]))
        ids = [r["id"] for r in results]
        assert "system_get_volume" in ids, f"Expected system_get_volume in {ids}"

        # Step 2: run
        send(
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {"name": "osa_run", "arguments": {"kb_id": "system_get_volume"}},
            }
        )
        run_resp = recv(3)
        result = json.loads(_extract_text(run_resp["result"]["content"]))
        vol = int(result["output"].strip())
        assert 0 <= vol <= 100, f"Volume out of range: {vol}"
