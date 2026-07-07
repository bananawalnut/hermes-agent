"""Zenith local-vault plugin.

Provides two small filesystem helpers for daily-note continuity:

- ``zenith_daily_note_log`` appends one structured row to today's daily note
  and can also update ``## Notes Created`` with an Obsidian wikilink.
- ``zenith_daily_todo`` adds one artifact-linked checkbox to today's daily note.

The tools are registered under the ``zenith`` toolset. They are bundled so the
plugin is discoverable in packaged installs, but the tool schemas only enter a
conversation when the user enables/selects the ``zenith`` toolset.
"""

from __future__ import annotations

from plugins.zenith.schemas import ZENITH_DAILY_NOTE_LOG, ZENITH_DAILY_TODO
from plugins.zenith.tools import zenith_daily_note_log, zenith_daily_todo

_TOOLS = (
    ("zenith_daily_note_log", ZENITH_DAILY_NOTE_LOG, zenith_daily_note_log, "🌅"),
    ("zenith_daily_todo", ZENITH_DAILY_TODO, zenith_daily_todo, "✅"),
)


def register(ctx) -> None:
    """Register Zenith local-vault tools."""
    for name, schema, handler, emoji in _TOOLS:
        ctx.register_tool(
            name=name,
            toolset="zenith",
            schema=schema,
            handler=handler,
            emoji=emoji,
        )
