#!/usr/bin/env python3
"""
PreToolUse Hook: Block dev servers launched outside tmux
Ensures log accessibility by requiring tmux sessions for long-running servers.
"""

import json
import re
import sys

data = json.load(sys.stdin)
cmd = data.get('tool_input', {}).get('command', '')

# Patterns that launch dev servers
dev_patterns = [
    r'\bnpm\s+run\s+dev\b',
    r'\bpnpm(?:\s+run)?\s+dev\b',
    r'\byarn\s+dev\b',
    r'\bbun\s+run\s+dev\b',
    r'\bnpm\s+start\b',
    r'\bpnpm\s+start\b',
    r'\byarn\s+start\b',
    r'\bbun\s+start\b',
]

# tmux launch commands are allowed
tmux_launcher = re.compile(r'^\s*tmux\s+(new|new-session|new-window|split-window)\b')


def split_shell_segments(command):
    """Split a shell command into segments by ;, &&, ||, &"""
    segments = []
    current = ''
    quote = None
    i = 0
    while i < len(command):
        ch = command[i]
        if quote:
            if ch == quote:
                quote = None
            current += ch
            i += 1
            continue
        if ch in ('"', "'"):
            quote = ch
            current += ch
            i += 1
            continue
        next_ch = command[i + 1] if i + 1 < len(command) else ''
        if ch == ';' or (ch in ('&', '|') and next_ch == ch):
            if current.strip():
                segments.append(current.strip())
            current = ''
            if ch in ('&', '|') and next_ch == ch:
                i += 1
        else:
            current += ch
        i += 1
    if current.strip():
        segments.append(current.strip())
    return segments


segments = split_shell_segments(cmd)
dev_re = re.compile('|'.join(dev_patterns))

for segment in segments:
    if dev_re.search(segment) and not tmux_launcher.match(segment):
        print('[Hook] BLOCKED: Dev server must run inside tmux for log access', file=sys.stderr)
        print('[Hook] Use: tmux new-session -d -s dev "npm run dev"', file=sys.stderr)
        print('[Hook] Then attach: tmux attach -t dev', file=sys.stderr)
        sys.exit(2)

sys.exit(0)
