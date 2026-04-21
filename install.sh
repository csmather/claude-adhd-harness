#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HARNESS_DIR="$HOME/.claude/adhd-harness"
SKILLS_DIR="$HOME/.claude/skills"
SETTINGS="$HOME/.claude/settings.json"

mkdir -p "$HARNESS_DIR/bin" "$HARNESS_DIR/hooks" "$HARNESS_DIR/anchors" "$SKILLS_DIR"

install -m 0755 "$REPO_DIR/bin/anchor.py"       "$HARNESS_DIR/bin/anchor.py"
install -m 0755 "$REPO_DIR/hooks/notice.py"     "$HARNESS_DIR/hooks/notice.py"
install -m 0755 "$REPO_DIR/hooks/auto-title.py" "$HARNESS_DIR/hooks/auto-title.py"

for skill in anchor nudge; do
  mkdir -p "$SKILLS_DIR/$skill"
  install -m 0644 "$REPO_DIR/skills/$skill/SKILL.md" "$SKILLS_DIR/$skill/SKILL.md"
done

python3 - "$SETTINGS" "$HARNESS_DIR/hooks/notice.py" "$HARNESS_DIR/hooks/auto-title.py" <<'PY'
import json, sys
from pathlib import Path

settings_path = Path(sys.argv[1])
scripts = sys.argv[2:]

settings = json.loads(settings_path.read_text()) if settings_path.exists() else {}
hooks = settings.setdefault("hooks", {})
ups   = hooks.setdefault("UserPromptSubmit", [])

for script in scripts:
    hook_cmd = f"python3 {script}"
    script_name = Path(script).name
    found = False
    for entry in ups:
        for h in entry.get("hooks", []):
            cmd = h.get("command", "")
            if "adhd-harness" in cmd and script_name in cmd:
                h["command"] = hook_cmd
                found = True
    if not found:
        ups.append({
            "matcher": "*",
            "hooks": [{"type": "command", "command": hook_cmd, "timeout": 3}],
        })
    print(f"Hook registered: {hook_cmd}")

settings_path.write_text(json.dumps(settings, indent=2))
PY

echo
echo "claude-adhd-harness installed."
echo "  Set an anchor:  /anchor <what you're doing>"
echo "  View current:   /anchor"
echo "  Clear:          /anchor clear"
