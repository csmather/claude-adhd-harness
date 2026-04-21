# auto-titler

A tiny `UserPromptSubmit` hook that sets a short, kebab-case Claude Code session title from your first prompt — same effect as `/rename` with no args, but automatic. Makes `/resume` pickers and session UIs readable without manual effort.

No LLM, no API key, no dependencies beyond Python stdlib.

## Install

```bash
./install.sh
```

Copies the hook into `~/.claude/auto-titler/hooks/` and registers it in `~/.claude/settings.json` as a `UserPromptSubmit` hook. Idempotent — safe to re-run.

## How it works

On every `UserPromptSubmit` event, the hook:

1. Skips empty prompts and slash commands.
2. Reads the session transcript (`transcript_path` from the hook input). If any prior real user prompt exists, bails out — not the first prompt.
3. Otherwise, runs a heuristic on the prompt: looks for intent patterns (`i want to ...`, `help me ...`, action verbs like `fix`/`build`/`refactor`), strips stopwords, keeps the first few content words.
4. Emits `{"hookSpecificOutput": {"sessionTitle": "<kebab-label>"}}` — Claude Code applies it the same way `/rename` does.

First-prompt detection is stateless — no seen-sessions cache, no side files. Just reads the transcript JSONL and short-circuits on the first prior real user entry (slash-command wrappers and meta entries filtered out). Resumed sessions are handled correctly as a freebie: their transcript already contains prior prompts, so the hook skips them.

## Example titles

| first prompt                                                                   | title                              |
| ------------------------------------------------------------------------------ | ---------------------------------- |
| `i want to implement the auto-titling feature before refining the nudge skill` | `implement-auto-titling-feature`   |
| `fix the login bug`                                                            | `login-bug`                        |
| `trying to debug this flaky test in the CI pipeline`                           | `debug-flaky-test-ci`              |
| `lets refactor the auth middleware`                                            | `refactor-auth-middleware`         |
| `hey check the build`                                                          | `build`                            |
| `hi`                                                                           | (silently skipped — not enough)    |

## Tuning

Constants at the top of `hooks/auto-title.py`:

- `STOPWORDS` — words ignored when extracting content.
- `INTENT_PATTERNS` — regexes for common "statement of intent" prefixes.
- `kebab(max_words, max_chars)` — controls label length.

## Uninstall

- Remove the `auto-title` entry from `hooks.UserPromptSubmit` in `~/.claude/settings.json`.
- `rm -rf ~/.claude/auto-titler`.

## Known limits

- Heuristic, not LLM. Complex or unusual first prompts produce mediocre titles compared to `/rename` no-args (which uses Claude's own generation with full context).
- First-prompt detection depends on Claude Code's transcript JSONL schema; a schema change could break it.
- Fires on every prompt but short-circuits fast (single-line read) once the transcript has any prior real user entry.

## History

Started as a drift-catching ADHD harness (anchor + nudge hook). The auto-titler turned out to be the durable, standalone-useful piece; the anchor/nudge work lives on the `anchor` branch for future revisiting.
