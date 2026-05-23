#!/usr/bin/env python3
"""
PostToolUse Hook: Warn about console.log statements after edits
Flags console.log in edited JS/TS files with line numbers.
"""

import json
import os
import re
import sys

data = json.load(sys.stdin)
file_path = data.get('tool_input', {}).get('file_path', '')

if not file_path or not re.search(r'\.(ts|tsx|js|jsx)$', file_path):
    sys.exit(0)

if not os.path.exists(file_path):
    sys.exit(0)

try:
    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.readlines()

    matches = [
        f'{i + 1}: {line.rstrip()}'
        for i, line in enumerate(lines)
        if re.search(r'console\.log', line)
    ]

    if matches:
        print(f'[Hook] WARNING: console.log found in {file_path}', file=sys.stderr)
        for match in matches[:5]:
            print(match, file=sys.stderr)
        if len(matches) > 5:
            print(f'[Hook] ... and {len(matches) - 5} more', file=sys.stderr)
        print('[Hook] Remove console.log before committing', file=sys.stderr)
except Exception:
    pass  # Non-blocking

sys.exit(0)
