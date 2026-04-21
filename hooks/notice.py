#!/usr/bin/env python3
"""notice.py — UserPromptSubmit hook. Nudges when the prompt drifts from the anchor."""
import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path

ANCHOR_DIR = Path.home() / ".claude" / "adhd-harness" / "anchors"
NUDGE_SKILL = Path.home() / ".claude" / "skills" / "nudge" / "SKILL.md"

MIN_PROMPT_WORDS = 8
OVERLAP_THRESHOLD = 0.20
NUDGE_COOLDOWN_SEC = 5 * 60

STOPWORDS = set("""a an the and or but if then so of to in on at for with by from as is are was were be been being do
does did have has had i you he she it we they me my your our their this that these those what which who whom whose
when where why how can could will would should may might must shall not no yes just like about into out up down
over under again further more most some any all each every one two three ok okay yeah yep nope nah hey hi""".split())


def tokenize(text: str) -> set:
    words = re.findall(r"[a-z][a-z0-9_-]{2,}", text.lower())
    return {w for w in words if w not in STOPWORDS}


def anchor_path(cwd: str) -> Path:
    key = hashlib.sha1(cwd.encode()).hexdigest()[:16]
    return ANCHOR_DIR / f"{key}.json"


def read_anchor(cwd: str):
    p = anchor_path(cwd)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text())
    except Exception:
        return None


def write_anchor(cwd: str, data: dict) -> None:
    try:
        anchor_path(cwd).write_text(json.dumps(data, indent=2))
    except Exception:
        pass


def extract_prompt(blob: str) -> str:
    try:
        d = json.loads(blob)
    except Exception:
        return ""
    if not isinstance(d, dict):
        return ""
    p = d.get("prompt")
    if isinstance(p, str):
        return p
    msg = d.get("message") or {}
    c = msg.get("content") if isinstance(msg, dict) else None
    return c if isinstance(c, str) else ""


def main() -> None:
    raw = sys.stdin.read()
    prompt = extract_prompt(raw)
    if not prompt:
        return

    # Don't self-trigger on harness commands.
    if re.match(r"^\s*/?(anchor|nudge)\b", prompt, re.I):
        return

    cwd = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    anchor = read_anchor(cwd)
    if not anchor:
        return

    if time.time() - anchor.get("last_nudge_at", 0) < NUDGE_COOLDOWN_SEC:
        return

    prompt_words = tokenize(prompt)
    if len(prompt_words) < MIN_PROMPT_WORDS:
        return

    anchor_words = tokenize(anchor.get("text", ""))
    if not anchor_words:
        return

    overlap = len(prompt_words & anchor_words) / len(anchor_words)
    if overlap >= OVERLAP_THRESHOLD:
        return

    anchor["last_nudge_at"] = time.time()
    write_anchor(cwd, anchor)

    age_min = int((time.time() - anchor.get("set_at", time.time())) / 60)
    age = f"{age_min}m ago" if age_min < 60 else f"{age_min // 60}h ago"
    pct = int(overlap * 100)
    policy = NUDGE_SKILL.read_text() if NUDGE_SKILL.exists() else ""

    print(f"""<adhd-harness-nudge>
Active anchor (set {age}): "{anchor['text']}"
Word-overlap with this prompt: {pct}% (threshold {int(OVERLAP_THRESHOLD * 100)}%).

{policy}
</adhd-harness-nudge>""")


if __name__ == "__main__":
    main()
