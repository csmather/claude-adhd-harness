#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HARNESS_DIR="$HOME/.claude/adhd-harness"
SKILLS_DIR="$HOME/.claude/skills"
SETTINGS="$HOME/.claude/settings.json"

mkdir -p "$HARNESS_DIR/bin" "$HARNESS_DIR/hooks" "$HARNESS_DIR/anchors" "$SKILLS_DIR"

install -m 0755 "$REPO_DIR/bin/anchor.py"   "$HARNESS_DIR/bin/anchor.py"
install -m 0755 "$REPO_DIR/hooks/notice.py" "$HARNESS_DIR/hooks/notice.py"

for skill in anchor nudge; do
  mkdir -p "$SKILLS_DIR/$skill"
  install -m 0644 "$REPO_DIR/skills/$skill/SKILL.md" "$SKILLS_DIR/$skill/SKILL.md"
done

python3 - "$SETTINGS" "$HARNESS_DIR/hooks/notice.py" <<'PY'
import json, sys
from pathlib import Path

settings_path = Path(sys.argv[1])
hook_cmd = f"python3 {sys.argv[2]}"

settings = json.loads(settings_path.read_text()) if settings_path.exists() else {}
hooks = settings.setdefault("hooks", {})
ups   = hooks.setdefault("UserPromptSubmit", [])

found = False
for entry in ups:
    for h in entry.get("hooks", []):
        if "adhd-harness" in h.get("command", ""):
            h["command"] = hook_cmd
            found = True

if not found:
    ups.append({
        "matcher": "*",
        "hooks": [{"type": "command", "command": hook_cmd, "timeout": 3}],
    })

settings_path.write_text(json.dumps(settings, indent=2))
print(f"Hook registered: {hook_cmd}")
PY

echo
echo "claude-adhd-harness installed."
echo "  Set an anchor:  /anchor <what you're doing>"
echo "  View current:   /anchor"
echo "  Clear:          /anchor clear"
