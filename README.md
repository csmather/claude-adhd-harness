# claude-adhd-harness

A tiny drift-catcher for Claude Code sessions. Set an anchor for what you're trying to do; if your next prompt reads as drift, Claude taps you on the shoulder and offers to branch, refocus, or update the anchor.

Not a deadline system. Not a scheduler. Just an external signal for when the internal compass is unreliable.

## Install

```bash
./install.sh
```

Copies skills into `~/.claude/skills/`, the hook into `~/.claude/adhd-harness/hooks/`, and registers the hook in `~/.claude/settings.json`. Idempotent — safe to re-run.

## Use

```
/anchor working on the drift hook for claude-adhd-harness
```

Then work normally. When a prompt drifts enough, you'll see a one-line check:

> Anchor check: "working on the drift hook for claude-adhd-harness" (set 12m ago). Branch, refocus, or update?

Pick one. That's the loop.

```
/anchor                # show current
/anchor clear          # remove
/anchor set <text>     # explicit set
```

Anchors are scoped to the current working directory — switching projects switches anchors automatically.

## How it works (three moves)

1. **Anchor** — plain text stored at `~/.claude/adhd-harness/anchors/<cwd-hash>.json`.
2. **Notice** — `UserPromptSubmit` hook tokenizes the anchor and the current prompt, checks word-overlap. Fires if overlap < 20% and the prompt is substantive (≥8 non-stopword tokens). 5-minute cooldown between nudges.
3. **Nudge** — `~/.claude/skills/nudge/SKILL.md` defines the response policy. Editing it changes the nudge behavior.

## Tuning

Thresholds live at the top of `hooks/notice.py`:

- `MIN_PROMPT_WORDS` — shorter prompts pass without checking.
- `OVERLAP_THRESHOLD` — below this ratio, a nudge fires.
- `NUDGE_COOLDOWN_SEC` — minimum gap between nudges per anchor.

Too noisy → raise the threshold or shorten the cooldown window. Too quiet → lower the threshold.

## Uninstall

- Remove the `adhd-harness` entry from `~/.claude/settings.json`'s `hooks.UserPromptSubmit`.
- `rm -rf ~/.claude/skills/anchor ~/.claude/skills/nudge ~/.claude/adhd-harness`.

## Known limits (v1)

- Word-overlap is dumb. Synonym drift slips through (anchor: "set up the hook", prompt: "wire the detector" → zero overlap, no nudge). Good enough for the common case.
- Short prompts always pass. "yeah do it" will never nudge. Acknowledged blind spot.
- No pattern-specific detectors yet (stacked questions, pre-execution reconsideration, tool-eval loops). Designed in, deliberately not in v1.
- No session-level rituals for completion-gap / session-start. Also deliberate — different mechanism, different project.
