#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="$HOME/.claude/auto-titler"
SETTINGS="$HOME/.claude/settings.json"

mkdir -p "$INSTALL_DIR/hooks"

install -m 0755 "$REPO_DIR/hooks/auto-title.py" "$INSTALL_DIR/hooks/auto-title.py"

python3 - "$SETTINGS" "$INSTALL_DIR/hooks/auto-title.py" <<'PY'
import json, sys
from pathlib import Path

settings_path = Path(sys.argv[1])
script = sys.argv[2]

settings = json.loads(settings_path.read_text()) if settings_path.exists() else {}
hooks = settings.setdefault("hooks", {})
ups   = hooks.setdefault("UserPromptSubmit", [])

hook_cmd = f"python3 {script}"
script_name = Path(script).name

found = False
for entry in ups:
    for h in entry.get("hooks", []):
        if script_name in h.get("command", ""):
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
echo "auto-title installed."
