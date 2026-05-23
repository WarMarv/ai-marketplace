#!/usr/bin/env python3
"""
PreToolUse Hook: Ask Claude to verify test coverage before a git commit.
Injects feedback into Claude's context instructing it to run the Tester agent.
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

# Only act on Bash calls that include a git commit
if tool_name != "Bash" or "git commit" not in command:
    sys.exit(0)

# Skip amend and dry-run commits
if "--amend" in command or "--dry-run" in command:
    sys.exit(0)

# Get staged diff stat
try:
    diff_result = subprocess.run(
        ["git", "diff", "--staged", "--shortstat"],
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
    "Test coverage check needed before committing\n\n"
    f"A git commit is about to be made.\n"
    f"  Staged diff stat: {diff_stat}\n\n"
    "Please read `agents/tester.md` and follow the Tester agent instructions "
    "to verify that adequate test coverage exists for the staged changes. "
    "Run any relevant tests and confirm they pass before proceeding with the commit."
)

output = {
    "hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "feedback": feedback,
    }
}
print(json.dumps(output))

sys.exit(0)
