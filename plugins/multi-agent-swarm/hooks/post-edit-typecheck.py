#!/usr/bin/env python3
"""
PostToolUse Hook: TypeScript check after editing .ts/.tsx files
Walks up to find nearest tsconfig.json and runs tsc --noEmit.
Reports only errors relevant to the edited file.
"""

import json
import os
import re
import subprocess
import sys

data = json.load(sys.stdin)
file_path = data.get('tool_input', {}).get('file_path', '')

if not file_path or not re.search(r'\.(ts|tsx)$', file_path):
    sys.exit(0)

abs_path = os.path.abspath(file_path)
if not os.path.exists(abs_path):
    sys.exit(0)


def find_tsconfig(start_dir):
    d = start_dir
    depth = 0
    while depth < 20:
        if os.path.exists(os.path.join(d, 'tsconfig.json')):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent
        depth += 1
    return None


tsconfig_dir = find_tsconfig(os.path.dirname(abs_path))
if not tsconfig_dir:
    sys.exit(0)

try:
    result = subprocess.run(
        ['npx', 'tsc', '--noEmit', '--pretty', 'false'],
        cwd=tsconfig_dir,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0:
        output = result.stdout + result.stderr
        rel_path = os.path.relpath(abs_path, tsconfig_dir)
        candidates = {file_path, abs_path, rel_path}
        relevant = [
            line for line in output.splitlines()
            if any(c in line for c in candidates)
        ][:10]
        if relevant:
            print(f'[Hook] TypeScript errors in {os.path.basename(file_path)}:', file=sys.stderr)
            for line in relevant:
                print(line, file=sys.stderr)
except Exception:
    pass  # Non-blocking

sys.exit(0)
