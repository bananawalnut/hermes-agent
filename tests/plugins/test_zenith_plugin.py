"""Tests for the bundled Zenith local-vault plugin."""

from __future__ import annotations

import json

from plugins.zenith import register
from plugins.zenith.tools import zenith_daily_note_log, zenith_daily_todo
from toolsets import TOOLSETS


class _FakeContext:
    def __init__(self) -> None:
        self.tools = []

    def register_tool(self, **kwargs):
        self.tools.append(kwargs)


def test_zenith_plugin_registers_daily_tools():
    ctx = _FakeContext()

    register(ctx)

    names = {tool["name"] for tool in ctx.tools}
    assert names == {"zenith_daily_note_log", "zenith_daily_todo"}
    assert {tool["toolset"] for tool in ctx.tools} == {"zenith"}


def test_zenith_toolset_lists_daily_tools():
    assert TOOLSETS["zenith"]["tools"] == ["zenith_daily_note_log", "zenith_daily_todo"]


def test_zenith_daily_note_log_creates_daily_note_and_notes_created(tmp_path):
    vault = tmp_path / "vault"
    artifact = vault / "notes" / "morning orientation.md"
    artifact.parent.mkdir(parents=True)
    artifact.write_text("# Morning orientation\n", encoding="utf-8")

    result = json.loads(
        zenith_daily_note_log(
            {
                "vault_dir": str(vault),
                "note_path": "notes/morning orientation.md",
                "action": "create",
                "area": "Zenith",
                "summary": "Started the day from the local vault",
                "date": "2026-07-06",
                "time": "09:00",
            }
        )
    )

    assert result["ok"] is True
    assert result["wikilink"] == "[[morning orientation]]"
    daily = vault / "notes" / "2026-07-06.md"
    content = daily.read_text(encoding="utf-8")
    assert "- 09:00 [Zenith] [create] Started the day from the local vault ([[morning orientation]])." in content
    assert "- [[morning orientation]] — Started the day from the local vault" in content


def test_zenith_daily_todo_adds_artifact_linked_checkbox(tmp_path):
    vault = tmp_path / "vault"
    artifact = vault / "notes" / "first action.md"
    artifact.parent.mkdir(parents=True)
    artifact.write_text("# First action\n", encoding="utf-8")

    result = json.loads(
        zenith_daily_todo(
            {
                "vault_dir": str(vault),
                "artifact_path": "notes/first action.md",
                "task": "Do the first action",
                "date": "2026-07-06",
            }
        )
    )

    assert result["ok"] is True
    assert result["todo_added"] is True
    daily = vault / "notes" / "2026-07-06.md"
    content = daily.read_text(encoding="utf-8")
    assert "## To Do's" in content
    assert "- [ ] Do the first action — [[first action]]" in content


def test_zenith_daily_note_log_reports_missing_required_fields():
    result = json.loads(zenith_daily_note_log({"action": "create"}))

    assert result == {
        "ok": False,
        "error": "missing required fields: note_path, area, summary",
    }
