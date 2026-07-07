"""Filesystem helpers for the bundled Zenith local-vault plugin."""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any


def _json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True)


def _required(args: dict[str, Any], *keys: str) -> str | None:
    missing = [key for key in keys if not str(args.get(key, "")).strip()]
    return ", ".join(missing) if missing else None


def _local_now_parts() -> tuple[str, str]:
    now = datetime.now().astimezone()
    return now.strftime("%Y-%m-%d"), now.strftime("%H:%M %Z")


def _default_vault() -> Path:
    for var in ("HERMES_ZENITH_VAULT_DIR", "ZENITH_VAULT_DIR", "OBSIDIAN_VAULT_PATH"):
        raw = os.getenv(var)
        if raw:
            path = Path(raw).expanduser()
            if path.exists():
                return path
    return Path.home() / "claude-hub"


def _resolve_vault_path(vault_dir: str | None, note_path: str) -> tuple[Path, Path]:
    vault = Path(vault_dir).expanduser() if vault_dir else _default_vault().expanduser()
    vault = vault.resolve()
    raw = Path(note_path).expanduser()
    path = raw if raw.is_absolute() else vault / raw
    return vault, path.resolve()


def _vault_wikilink(vault: Path, path: Path) -> str:
    try:
        rel = path.relative_to(vault)
    except ValueError:
        return f"[[{path}|{path.stem}]]"
    stem = rel.with_suffix("").as_posix()
    if rel.parts and rel.parts[0] == "notes" and len(rel.parts) == 2:
        return f"[[{Path(stem).name}]]"
    return f"[[../{stem}|{Path(stem).name}]]"


def _daily_skeleton(day: str, *, include_todos: bool = False) -> str:
    todo_section = "\n## To Do's\n" if include_todos else ""
    return (
        f"---\n"
        f"description: Daily chronological log for {day}\n"
        f"type: daily\n"
        f"date: {day}\n"
        f"tags: [daily]\n"
        f"axes_touched: []\n"
        f"arenas_active: []\n"
        f"---\n\n"
        f"# {day}\n"
        f"{todo_section}\n"
        f"## Log\n\n"
        f"## Notes Created\n\n"
        f"## Decisions\n\n"
        f"## Research\n\n"
        f"## Evening Reflection\n\n"
        f"---\n\n"
        f"Areas:\n"
        f"- [[index]]\n"
    )


def _append_under_heading(content: str, heading: str, line: str) -> tuple[str, bool]:
    if line in content:
        return content, False
    marker = f"\n## {heading}\n"
    if marker not in content:
        suffix = "" if content.endswith("\n") else "\n"
        return f"{content}{suffix}\n## {heading}\n\n{line}\n", True
    start = content.index(marker) + len(marker)
    nxt = content.find("\n## ", start)
    if nxt == -1:
        section = content[start:].rstrip()
        return content[:start] + section + ("\n" if section else "") + line + "\n", True
    section = content[start:nxt].rstrip()
    return content[:start] + section + ("\n" if section else "") + line + "\n" + content[nxt:], True


def _insert_after_heading(content: str, heading: str, line: str) -> tuple[str, bool]:
    if line in content:
        return content, False
    marker = f"\n## {heading}\n"
    if marker not in content:
        suffix = "" if content.endswith("\n") else "\n"
        return f"{content}{suffix}\n## {heading}\n\n{line}\n", True
    idx = content.index(marker) + len(marker)
    if content[idx : idx + 1] == "\n":
        idx += 1
    return content[:idx] + line + "\n" + content[idx:], True


def _ensure_heading_before(content: str, heading: str, before_heading: str) -> tuple[str, bool]:
    if f"\n## {heading}\n" in content:
        return content, False
    before = f"\n## {before_heading}\n"
    if before not in content:
        suffix = "" if content.endswith("\n") else "\n"
        return f"{content}{suffix}\n## {heading}\n\n", True
    idx = content.index(before)
    return content[:idx].rstrip() + "\n" + f"\n## {heading}\n" + content[idx:], True


def zenith_daily_note_log(args: dict[str, Any], **_: Any) -> str:
    """Append one daily log row and optional Notes Created entry."""
    try:
        missing = _required(args, "note_path", "action", "area", "summary")
        if missing:
            return _json({"ok": False, "error": f"missing required fields: {missing}"})
        vault, note = _resolve_vault_path(args.get("vault_dir"), str(args["note_path"]))
        today, now = _local_now_parts()
        day = str(args.get("date") or today)
        daily = vault / "notes" / f"{day}.md"
        link = _vault_wikilink(vault, note)
        log_line = (
            f"- {str(args.get('time') or now)} "
            f"[{str(args['area']).strip()}] "
            f"[{str(args['action']).strip()}] "
            f"{str(args['summary']).strip()} ({link})."
        )
        content = daily.read_text(encoding="utf-8") if daily.exists() else _daily_skeleton(day)
        content, log_added = _append_under_heading(content, "Log", log_line)
        notes_added = False
        if args.get("add_notes_created", True):
            notes_line = f"- {link} — {str(args.get('notes_created_summary') or args['summary']).strip()}"
            content, notes_added = _insert_after_heading(content, "Notes Created", notes_line)
        daily.parent.mkdir(parents=True, exist_ok=True)
        daily.write_text(content, encoding="utf-8")
        return _json(
            {
                "ok": True,
                "daily_note": str(daily),
                "note_path": str(note),
                "wikilink": link,
                "log_added": log_added,
                "notes_created_added": notes_added,
            }
        )
    except Exception as exc:
        return _json({"ok": False, "error": str(exc)})


def zenith_daily_todo(args: dict[str, Any], **_: Any) -> str:
    """Add one artifact-linked checkbox to a daily note."""
    try:
        missing = _required(args, "artifact_path", "task")
        if missing:
            return _json({"ok": False, "error": f"missing required fields: {missing}"})
        vault, artifact = _resolve_vault_path(args.get("vault_dir"), str(args["artifact_path"]))
        today, _ = _local_now_parts()
        day = str(args.get("date") or today)
        daily = vault / "notes" / f"{day}.md"
        link = _vault_wikilink(vault, artifact)
        checkbox = "x" if bool(args.get("completed")) else " "
        todo_line = f"- [{checkbox}] {str(args['task']).strip()} — {link}"
        content = daily.read_text(encoding="utf-8") if daily.exists() else _daily_skeleton(day, include_todos=True)
        content, heading_added = _ensure_heading_before(content, "To Do's", "Log")
        content, todo_added = _append_under_heading(content, "To Do's", todo_line)
        daily.parent.mkdir(parents=True, exist_ok=True)
        daily.write_text(content, encoding="utf-8")
        return _json(
            {
                "ok": True,
                "daily_note": str(daily),
                "artifact_path": str(artifact),
                "wikilink": link,
                "todo_line": todo_line,
                "heading_added": heading_added,
                "todo_added": todo_added,
            }
        )
    except Exception as exc:
        return _json({"ok": False, "error": str(exc)})
