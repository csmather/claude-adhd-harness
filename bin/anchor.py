#!/usr/bin/env python3
"""anchor.py — get/set/clear the drift anchor scoped to the current cwd."""
import hashlib
import json
import os
import sys
import time
from pathlib import Path

ANCHOR_DIR = Path.home() / ".claude" / "adhd-harness" / "anchors"


def anchor_path(cwd: str) -> Path:
    key = hashlib.sha1(cwd.encode()).hexdigest()[:16]
    return ANCHOR_DIR / f"{key}.json"


def cmd_set(text: str) -> None:
    cwd = os.getcwd()
    ANCHOR_DIR.mkdir(parents=True, exist_ok=True)
    data = {"text": text, "cwd": cwd, "set_at": time.time()}
    anchor_path(cwd).write_text(json.dumps(data, indent=2))
    print(f'Anchor set: "{text}"')


def cmd_get() -> None:
    p = anchor_path(os.getcwd())
    if not p.exists():
        print("No anchor set for this directory.")
        return
    data = json.loads(p.read_text())
    age_min = int((time.time() - data["set_at"]) / 60)
    age = f"{age_min}m ago" if age_min < 60 else f"{age_min // 60}h ago"
    print(f'Anchor: "{data["text"]}" (set {age})')


def cmd_clear() -> None:
    p = anchor_path(os.getcwd())
    if p.exists():
        p.unlink()
        print("Anchor cleared.")
    else:
        print("No anchor to clear.")


def main() -> None:
    argv = sys.argv[1:]
    if not argv:
        cmd_get()
        return
    head = argv[0].lower()
    if head == "set" and len(argv) > 1:
        cmd_set(" ".join(argv[1:]))
    elif head in ("clear", "unset", "rm"):
        cmd_clear()
    elif head == "get":
        cmd_get()
    else:
        cmd_set(" ".join(argv))


if __name__ == "__main__":
    main()
