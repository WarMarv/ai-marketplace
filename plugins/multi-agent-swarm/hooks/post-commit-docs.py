#!/usr/bin/env python3
"""
PostToolUse Hook: Trigger Documenter agent after a successful git commit.
Injects feedback into Claude's context instructing it to run the Documenter agent.
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

# Extract commit message
try:
    commit_msg_result = subprocess.run(
        ["git", "log", "-1", "--format=%B"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    commit_msg = commit_msg_result.stdout.strip()
except Exception:
    commit_msg = "(could not retrieve commit message)"

# Truncate commit message to 200 chars
commit_msg_truncated = commit_msg[:200] + ("..." if len(commit_msg) > 200 else "")

try:
    diff_result = subprocess.run(
        ["git", "diff", "HEAD~1", "HEAD", "--shortstat"],
        capture_output=True, text=True, timeout=15
    )
    diff_stat = diff_result.stdout.strip() or "no stat available"
except Exception:
    diff_stat = "unavailable"

feedback = (
    "Documentation update needed\n\n"
    f"A git commit was just made:\n"
    f"  Commit message: {commit_msg_truncated}\n"
    f"  Diff stat: {diff_stat}\n\n"
    "Please read `agents/documenter.md` and follow the Documenter agent instructions "
    "to update any relevant documentation based on the changes introduced by this commit."
)

output = {
    "hookSpecificOutput": {
        "hookEventName": "PostToolUse",
        "feedback": feedback,
    }
}
print(json.dumps(output))

sys.exit(0)
