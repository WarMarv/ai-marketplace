#!/usr/bin/env python3
"""
PreToolUse Hook: Ask Claude to run the Reviewer agent before a git push.
Injects feedback into Claude's context instructing it to review the branch diff.
"""

import json
import subprocess
import sys

try:
    input_data = json.load(sys.stdin)
except json.JSONDecodeError as e:
    print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
    sys.exit(0)

tool_name = input_data.get("tool_name", "")
tool_input = input_data.get("tool_input", {})
command = tool_input.get("command", "")

# Only act on Bash calls that include a git push
if tool_name != "Bash" or "git push" not in command:
    sys.exit(0)

# Skip dry-run pushes
if "--dry-run" in command:
    sys.exit(0)

# Get branch diff stat vs main
try:
    diff_result = subprocess.run(
        ["git", "diff", "main...HEAD", "--shortstat"],
        capture_output=True,
        text=True,
        timeout=15,
    )
    diff_stat = diff_result.stdout.strip()
except Exception:
    diff_stat = "unavailable"

if diff_stat == "":
    sys.exit(0)

feedback = (
    "Code review needed before pushing\n\n"
    f"A git push is about to be made.\n"
    f"  Branch diff stat (vs main): {diff_stat}\n\n"
    "Please read `agents/reviewer.md` and follow the Reviewer agent instructions "
    "to review the branch diff before pushing. "
    "Resolve all BLOCKING findings first before proceeding with the push."
)

output = {
    "hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "feedback": feedback,
    }
}
print(json.dumps(output))

sys.exit(0)
