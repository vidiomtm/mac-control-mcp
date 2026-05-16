"""Integration tests for OSA runner (macOS-only, real osascript)."""

from __future__ import annotations

import json

import pytest

from mac_control_mcp.osa.runner import run_osa


@pytest.mark.integration
def test_applescript_hello() -> None:
    result = run_osa('return "hello"')
    assert result["output"] == "hello"
    assert result["lang"] == "applescript"


@pytest.mark.integration
def test_applescript_arithmetic() -> None:
    result = run_osa("return 2 + 2")
    assert result["output"] == "4"


@pytest.mark.integration
def test_jxa_json_output() -> None:
    result = run_osa('JSON.stringify({a: 1, b: "two"})', lang="jxa")
    parsed = json.loads(result["output"])
    assert parsed == {"a": 1, "b": "two"}


@pytest.mark.integration
def test_timeout_raises() -> None:
    with pytest.raises(RuntimeError, match="timed out"):
        run_osa("delay 5", timeout_s=0.5)


@pytest.mark.integration
def test_forbidden_script_rejected_before_spawn() -> None:
    """Security check fires before subprocess is spawned."""
    with pytest.raises(ValueError, match="Forbidden OSA pattern"):
        run_osa('do shell script "rm -rf /tmp/definitely_does_not_exist_xyz"')


@pytest.mark.integration
def test_invalid_applescript_raises() -> None:
    with pytest.raises(RuntimeError, match="OSA error"):
        run_osa("this is not valid applescript $$$$")
