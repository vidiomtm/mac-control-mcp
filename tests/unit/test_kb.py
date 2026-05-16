"""Unit tests for mac_control_mcp.osa.kb knowledge base."""

from __future__ import annotations

import pytest

from mac_control_mcp.osa.kb import _load, get, search


@pytest.fixture(autouse=True)
def reset_kb():
    """Reset lazy-loaded KB between tests."""
    import mac_control_mcp.osa.kb as kb_mod

    kb_mod._KB = None
    yield
    kb_mod._KB = None


# ── load ──────────────────────────────────────────────────────────────────────


@pytest.mark.unit
def test_kb_loads() -> None:
    kb = _load()
    assert len(kb) >= 28


@pytest.mark.unit
def test_kb_all_entries_have_required_fields() -> None:
    kb = _load()
    for entry_id, entry in kb.items():
        assert "id" in entry, f"{entry_id}: missing 'id'"
        assert "app" in entry, f"{entry_id}: missing 'app'"
        assert "lang" in entry, f"{entry_id}: missing 'lang'"
        assert "summary" in entry, f"{entry_id}: missing 'summary'"
        assert "script" in entry, f"{entry_id}: missing 'script'"


@pytest.mark.unit
def test_kb_all_langs_valid() -> None:
    kb = _load()
    valid_langs = {"applescript", "jxa"}
    for entry_id, entry in kb.items():
        assert entry["lang"] in valid_langs, f"{entry_id}: invalid lang {entry['lang']!r}"


@pytest.mark.unit
def test_kb_ids_match_keys() -> None:
    kb = _load()
    for key, entry in kb.items():
        assert entry["id"] == key


# ── search ────────────────────────────────────────────────────────────────────


@pytest.mark.unit
def test_search_create_reminder_ranks_first() -> None:
    results = search("create reminder")
    assert results[0]["id"] == "reminders_add"


@pytest.mark.unit
def test_search_mail_compose_ranks_first() -> None:
    results = search("mail compose")
    assert results[0]["id"] == "mail_compose_send"


@pytest.mark.unit
def test_search_filters_by_app() -> None:
    results = search("search", app="Notes")
    assert all("notes" in r["id"].lower() or r["app"].lower() == "notes" for r in results)


@pytest.mark.unit
def test_search_returns_at_most_top_k() -> None:
    results = search("event calendar", top_k=3)
    assert len(results) <= 3


@pytest.mark.unit
def test_search_returns_summary_and_tags() -> None:
    results = search("reminders", top_k=1)
    assert "summary" in results[0]
    assert "tags" in results[0]
    assert "args" in results[0]


# ── get ───────────────────────────────────────────────────────────────────────


@pytest.mark.unit
def test_get_returns_entry() -> None:
    entry = get("reminders_add")
    assert entry["id"] == "reminders_add"
    assert len(entry["script"]) > 10


@pytest.mark.unit
def test_get_raises_key_error_for_missing() -> None:
    with pytest.raises(KeyError, match="nonexistent"):
        get("nonexistent")
