#!/usr/bin/env python3
import json
import sys
import re

try:
    input_data = json.load(sys.stdin)
except json.JSONDecodeError as e:
    print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
    sys.exit(1)

tool_name = input_data.get("tool_name", "")
tool_input = input_data.get("tool_input", {})
command = tool_input.get("command", "")

# Only validate gh issue create commands.
# Skip git commit commands that mention gh issue create in the message body.
if tool_name != "Bash" or "git commit" in command:
    sys.exit(0)

# Strip single-quoted strings first to avoid false positives (e.g. echo '...gh issue create...')
command_unquoted = re.sub(r"'[^']*'", "", command)
if "gh issue create" not in command_unquoted:
    sys.exit(0)

# Normalize escaped quotes so \"feature\" becomes "feature"
command_normalized = command_unquoted.replace('\\"', '"')

# Extract all label values: --label "..." or --label '...' or --label word
labels = []
for m in re.finditer(r'(?:--label|-l)\s+(?:"([^"]+)"|\'([^\']+)\'|(\S+))', command_normalized):
    value = m.group(1) or m.group(2) or m.group(3)
    labels.extend([l.strip() for l in value.split(",")])

TYPE_LABELS = {"feature", "bug"}
EFFORT_LABELS = {"effort: S", "effort: M", "effort: L"}

has_type = any(l in TYPE_LABELS for l in labels)
has_effort = any(l in EFFORT_LABELS for l in labels)

if has_type and has_effort:
    sys.exit(0)

missing = []
if not has_type:
    missing.append("Typ-Label (feature oder bug)")
if not has_effort:
    missing.append("Aufwand-Label (effort: S, effort: M oder effort: L)")

reason = (
    "Blocked: GitHub Issue ohne Pflicht-Labels\n\n"
    f"Fehlende Labels: {', '.join(missing)}\n\n"
    "Jedes Issue benoetigt:\n"
    "  - Ein Typ-Label:     feature | bug\n"
    "  - Ein Aufwand-Label: effort: S | effort: M | effort: L\n\n"
    "Beispiel:\n"
    '  gh issue create --title "..." --body "..." \\\n'
    '    --label "feature" --label "effort: S"\n\n'
    f"Erkannte Labels: {labels if labels else '(keine)'}"
)

output = {
    "hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": reason
    }
}
print(json.dumps(output))
sys.exit(0)
