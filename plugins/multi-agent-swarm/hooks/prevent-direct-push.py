#!/usr/bin/env python3
import json
import sys
import subprocess

try:
    input_data = json.load(sys.stdin)
except json.JSONDecodeError as e:
    print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
    sys.exit(1)

tool_name = input_data.get("tool_name", "")
tool_input = input_data.get("tool_input", {})
command = tool_input.get("command", "")

# Only validate git push commands
if tool_name != "Bash" or "git push" not in command:
    sys.exit(0)

# Get current branch
try:
    current_branch = subprocess.check_output(
        ["git", "branch", "--show-current"],
        stderr=subprocess.DEVNULL,
        text=True
    ).strip()
except:
    current_branch = ""

# Check if pushing to main or develop
push_cmd = command
is_force_push = "--force" in push_cmd or "-f" in push_cmd

# Parse the branch being pushed from the command.
# e.g. "git push origin main" → "main"
# e.g. "git push -u origin feat/foo" → "feat/foo"
# e.g. "git push" → fall back to current branch
def extract_push_branch(cmd):
    tokens = cmd.split()
    try:
        push_idx = next(i for i, t in enumerate(tokens) if t == "push")
    except StopIteration:
        return None
    # Skip flags after "push"
    args = [t for t in tokens[push_idx + 1:] if not t.startswith("-")]
    # args[0] is the remote (e.g. "origin"), args[1] is the branch (may include refspec colon)
    if len(args) >= 2:
        branch = args[1].split(":")[0]  # handle refspecs like HEAD:main
        return branch
    return None  # no explicit branch → use current branch

push_target = extract_push_branch(push_cmd)
effective_branch = push_target if push_target else current_branch

# Check if command targets protected branches
targets_protected = effective_branch in ["main", "develop"]

# Allow initial push when the remote has no branches yet (empty repo after gh repo create)
def remote_is_empty():
    try:
        result = subprocess.check_output(
            ["git", "ls-remote", "--heads", "origin"],
            stderr=subprocess.DEVNULL,
            text=True
        ).strip()
        return not bool(result)
    except Exception:
        return False

if targets_protected and remote_is_empty():
    sys.exit(0)  # Initial push to empty remote — allow main branch setup

# Block direct push to main/develop (unless force push which is already dangerous)
if targets_protected and not is_force_push:
    reason = f"""❌ Direct push to main/develop is not allowed!

Protected branches:
  - main (production)
  - develop (integration)

Workflow:
  1. Create a feature branch: git checkout -b feature/<name>
  2. Make your changes and commit
  3. Push feature branch: git push origin feature/<name>
  4. Create pull request: gh pr create
  5. Merge after approval

Current branch: {current_branch}
Push target:    {effective_branch}

💡 Use feature branches and pull requests instead of pushing directly to main/develop."""

    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason
        }
    }
    print(json.dumps(output))
    sys.exit(0)

# Allow the command
sys.exit(0)
