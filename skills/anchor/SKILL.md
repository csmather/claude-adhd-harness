---
name: anchor
description: Set, view, or clear the drift anchor — what you're trying to focus on in this working directory. Triggered by /anchor.
---

# /anchor

Manages the current drift anchor for the claude-adhd-harness.

## Usage

When the user invokes `/anchor`, parse their input and run the matching Bash command. Report the command's stdout back concisely — no embellishment.

| User input | Run |
|---|---|
| `/anchor <text>` | `python3 ~/.claude/adhd-harness/bin/anchor.py set "<text>"` |
| `/anchor set <text>` | `python3 ~/.claude/adhd-harness/bin/anchor.py set "<text>"` |
| `/anchor` (no args) | `python3 ~/.claude/adhd-harness/bin/anchor.py get` |
| `/anchor get` | `python3 ~/.claude/adhd-harness/bin/anchor.py get` |
| `/anchor clear` | `python3 ~/.claude/adhd-harness/bin/anchor.py clear` |

## What this does

The anchor is plain text — "what I'm trying to do right now" — scoped to the current working directory. A `UserPromptSubmit` hook compares each of the user's prompts against the anchor; if word-overlap is low, it injects a nudge. See `~/.claude/skills/nudge/SKILL.md` for the response policy.
