#!/usr/bin/env python3
"""auto-title.py — UserPromptSubmit hook. Sets a short session title from the first real prompt.

Standalone: stdlib only, no API calls, no external state. Runs a heuristic on the first
non-slash-command user prompt of a session and emits a `sessionTitle` via
hookSpecificOutput to rename the session (same effect as /rename).
"""
import json
import re
import sys
from pathlib import Path

STOPWORDS = set("""a an the and or but if then so of to in on at for with by from as is are was were be been being
do does did have has had i you he she it we they me my your our their this that these those what which who whom
whose when where why how can could will would should may might must shall not no yes just like about into out up
down over under again further more most some any all each every one two three ok okay yeah yep nope nah hey hi
please really actually basically literally kinda sorta maybe probably guess think thought need want trying help""".split())

ACTION_VERBS = r"implement|build|fix|add|create|write|refactor|debug|investigate|research|explore|design|review|test|update|check|setup|configure|make|run|deploy"

INTENT_PATTERNS = [
    re.compile(r"\b(?:i\s+want\s+to|i'd\s+like\s+to|id\s+like\s+to|i\s+need\s+to|trying\s+to|let's|lets)\s+(.+?)(?:[.!?,;]|\s+(?:before|after|so|because|and\s+then)\b|$)", re.I),
    re.compile(r"\b(?:help\s+me(?:\s+with)?|can\s+you|could\s+you|please)\s+(.+?)(?:[.!?,;]|\s+(?:before|after|so|because)\b|$)", re.I),
    re.compile(rf"\b({ACTION_VERBS})\s+(.+?)(?:[.!?,;]|\s+(?:before|after|so|because)\b|$)", re.I),
]

COMMAND_MARKERS = ("<command-name>", "<command-message>", "<local-command-")


def first_sentence(text: str) -> str:
    text = text.strip()
    m = re.search(r"[.!?\n]", text)
    return text[: m.start()] if m else text


def content_words(text: str) -> list:
    words = re.findall(r"[a-z][a-z0-9'-]*", text.lower())
    return [w.strip("-'") for w in words if w not in STOPWORDS and len(w.strip("-'")) > 1]


def kebab(words: list, max_words: int = 4, max_chars: int = 40) -> str:
    out, total = [], 0
    for w in words[:max_words]:
        w = re.sub(r"[^a-z0-9-]", "", w).strip("-")
        if not w:
            continue
        extra = len(w) + (1 if out else 0)
        if total + extra > max_chars:
            break
        out.append(w)
        total += extra
    return "-".join(out)


def generate_title(prompt: str) -> str:
    sentence = first_sentence(prompt)
    if not sentence:
        return ""
    for pat in INTENT_PATTERNS:
        m = pat.search(sentence)
        if m:
            obj = m.groups()[-1]
            title = kebab(content_words(obj))
            if title:
                return title
    return kebab(content_words(sentence))


def has_prior_user_prompt(transcript_path: str) -> bool:
    """True if the transcript already contains a real (non-meta, non-command, string-content) user prompt."""
    if not transcript_path:
        return False
    p = Path(transcript_path)
    if not p.exists():
        return False
    try:
        with p.open() as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except Exception:
                    continue
                if not isinstance(entry, dict):
                    continue
                if entry.get("type") != "user" or entry.get("isMeta"):
                    continue
                msg = entry.get("message") or {}
                content = msg.get("content")
                if not isinstance(content, str):
                    continue
                stripped = content.lstrip()
                if not stripped or stripped.startswith(COMMAND_MARKERS):
                    continue
                return True
    except Exception:
        return True  # unreadable transcript → skip safely
    return False


def main() -> None:
    try:
        data = json.loads(sys.stdin.read())
    except Exception:
        return
    if not isinstance(data, dict):
        return

    prompt = data.get("prompt", "")
    if not isinstance(prompt, str):
        return
    prompt = prompt.strip()
    if not prompt or prompt.startswith("/"):
        return

    if has_prior_user_prompt(data.get("transcript_path", "")):
        return

    title = generate_title(prompt)
    if not title:
        return

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "sessionTitle": title,
        }
    }))


if __name__ == "__main__":
    main()
