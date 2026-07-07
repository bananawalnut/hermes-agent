"""Tool schemas for the bundled Zenith local-vault plugin."""

ZENITH_DAILY_NOTE_LOG = {
    "name": "zenith_daily_note_log",
    "description": "Append one Zenith/local-vault daily-note Log row and optional Notes Created entry.",
    "parameters": {
        "type": "object",
        "properties": {
            "vault_dir": {
                "type": "string",
                "description": "Absolute vault path. Defaults to HERMES_ZENITH_VAULT_DIR, ZENITH_VAULT_DIR, OBSIDIAN_VAULT_PATH, or ~/claude-hub.",
            },
            "note_path": {"type": "string", "description": "Artifact/note path to link from the daily note."},
            "action": {"type": "string", "description": "Log action tag, e.g. create, action, decision, learn."},
            "area": {"type": "string", "description": "Arena/area label for the log row."},
            "summary": {"type": "string", "description": "Human-readable log prose."},
            "notes_created_summary": {"type": "string", "description": "Optional prose for the Notes Created entry."},
            "date": {"type": "string", "description": "YYYY-MM-DD. Defaults to local today."},
            "time": {"type": "string", "description": "HH:MM or HH:MM TZ. Defaults to local current time."},
            "add_notes_created": {"type": "boolean", "description": "Whether to add a Notes Created entry. Defaults true."},
        },
        "required": ["note_path", "action", "area", "summary"],
    },
}

ZENITH_DAILY_TODO = {
    "name": "zenith_daily_todo",
    "description": "Add one artifact-linked checkbox To Do to a Zenith/local-vault daily note.",
    "parameters": {
        "type": "object",
        "properties": {
            "vault_dir": {
                "type": "string",
                "description": "Absolute vault path. Defaults to HERMES_ZENITH_VAULT_DIR, ZENITH_VAULT_DIR, OBSIDIAN_VAULT_PATH, or ~/claude-hub.",
            },
            "artifact_path": {"type": "string", "description": "Artifact or note path to wikilink from the todo."},
            "task": {"type": "string", "description": "Checkbox task text."},
            "date": {"type": "string", "description": "YYYY-MM-DD. Defaults to local today."},
            "completed": {"type": "boolean", "description": "Whether the checkbox should be marked done."},
        },
        "required": ["artifact_path", "task"],
    },
}
