---
name: good-morning
description: Use when the user says good morning, asks for morning orientation, or wants to start the day from their local vault. Reads self/context, updates today's daily note, surfaces priorities, and chooses one concrete first action.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [daily-notes, morning, vault, planning, orientation]
    related_skills: [obsidian]
---

# Good Morning

## Overview

Run a short morning orientation against the user's local knowledge vault. The goal is not a long plan; it is to restore continuity, update today's daily note, and give the user one clear first action.

This skill is filesystem-first. If the Zenith plugin toolset is available, use its daily-note helpers for log/todo writes. If those tools are not exposed in the current session, use normal file tools (`read_file`, `write_file`, `patch`, `search_files`) against the resolved vault path.

## When to Use

Use when:
- The user says "good morning", "start my day", "morning check-in", or asks for daily orientation.
- The user wants the agent to reconcile goals, reminders, tasks, and today's note.
- A gateway or cron routine needs a concise morning briefing.

Do not use for:
- End-of-day carry-forward; use a good-night/evening-summary routine instead.
- Deep project planning; create a separate plan after the first action is chosen.

## Vault Resolution

Resolve the vault before reading or writing:

1. Prefer `HERMES_ZENITH_VAULT_DIR`.
2. Then `ZENITH_VAULT_DIR`.
3. Then `OBSIDIAN_VAULT_PATH` if it exists.
4. Then `~/claude-hub`.
5. Then ask only if none of those paths exist and the user did not provide a vault path.

Use concrete absolute paths with file tools. Do not pass `$VARS` directly to file tools.

## Morning Routine

1. Read orientation files:
   - `self/identity.md`
   - `self/goals.md`
   - `self/methodology.md`
   - `ops/reminders.md` if present
   - `ops/tasks.md` if present
   - `notes/YYYY-MM-DD.md` for today, creating it if missing

   Completion criterion: you have the current north star, active threads, reminders/tasks, and today's existing log in context.

2. Create today's daily note if it does not exist. Use this skeleton:

   ```markdown
   ---
   description: Daily chronological log for YYYY-MM-DD
   type: daily
   date: YYYY-MM-DD
   tags: [daily]
   axes_touched: []
   arenas_active: []
   ---

   # YYYY-MM-DD

   ## Morning Reflection

   ## Quote

   ## Log

   ## Notes Created

   ## Decisions

   ## Research

   ## Evening Reflection

   ---

   Areas:
   - [[index]]
   ```

   Completion criterion: the note exists and has a `## Log` section.

3. Ask for missing human state only if it was not already provided:
   - energy level
   - mood / nervous-system state
   - hard commitments today
   - any one thing that must not slip

   Keep the ask compact. If the user gave enough context, do not ask; proceed.

4. Update the daily note:
   - Add a Morning Reflection paragraph or bullets.
   - Add one `[action]` log row for running morning orientation.
   - If a time-bound reminder is surfaced, add it as `[action]` or `[question]` depending on whether it is actionable.

   Log row format:
   `- HH:MM [Arena] [tag] prose...`

   Completion criterion: today's note can reconstruct what was surfaced and what first action was chosen.

5. Return a concise briefing with exactly these headings:
   - `State` — energy/mood if known, otherwise "not supplied".
   - `Today’s load-bearing context` — 2-4 bullets from goals/tasks/reminders.
   - `First action` — one concrete next move, not a menu.
   - `Watchouts` — 0-3 risks, including neglected axis/arena only if relevant.

## Using the Zenith Plugin

If the `zenith` toolset is enabled, prefer:

- `zenith_daily_note_log` for appending log rows and Notes Created entries.
- `zenith_daily_todo` for adding artifact-linked checkboxes to the daily note.

Still read the relevant files yourself first; the plugin writes rows but does not replace orientation.

## Common Pitfalls

1. **Over-planning.** Morning orientation should end with one action, not a project plan.
2. **Skipping self/context.** Without `self/goals.md`, the recommendation is ungrounded.
3. **Burying action in prose.** The first action must be explicit and executable.
4. **Forgetting the daily note.** If the note is not updated, the session starts cold next time.
5. **Asking too much.** Ask only for state/context that changes today's first action.

## Verification Checklist

- [ ] Vault path resolved to a concrete absolute path.
- [ ] `self/identity.md`, `self/goals.md`, and `self/methodology.md` were read.
- [ ] Today's daily note exists.
- [ ] Today's daily note has a morning-orientation log entry.
- [ ] Final response gives one concrete first action.
