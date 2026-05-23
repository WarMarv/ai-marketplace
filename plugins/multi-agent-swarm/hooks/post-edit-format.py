#!/usr/bin/env python3
"""
PostToolUse Hook: Auto-format JS/TS files after edits
Auto-detects Biome or Prettier from project config and formats in place.
Fails silently if no formatter is found or installed.
"""

import json
import os
import re
import subprocess
import sys

data = json.load(sys.stdin)
file_path = data.get('tool_input', {}).get('file_path', '')

if not file_path or not re.search(r'\.(ts|tsx|js|jsx)$', file_path):
    sys.exit(0)


def find_project_root(start):
    d = os.path.abspath(start)
    while True:
        if os.path.exists(os.path.join(d, 'package.json')):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            return start
        d = parent


def detect_formatter(root):
    biome_configs = ['biome.json', 'biome.jsonc']
    for cfg in biome_configs:
        if os.path.exists(os.path.join(root, cfg)):
            return 'biome'
    prettier_configs = [
        '.prettierrc', '.prettierrc.json', '.prettierrc.js', '.prettierrc.cjs',
        '.prettierrc.mjs', '.prettierrc.yml', '.prettierrc.yaml', '.prettierrc.toml',
        'prettier.config.js', 'prettier.config.cjs', 'prettier.config.mjs',
    ]
    for cfg in prettier_configs:
        if os.path.exists(os.path.join(root, cfg)):
            return 'prettier'
    return None


abs_path = os.path.abspath(file_path)
if not os.path.exists(abs_path):
    sys.exit(0)

project_root = find_project_root(os.path.dirname(abs_path))
formatter = detect_formatter(project_root)

if formatter == 'biome':
    cmd = ['npx', '@biomejs/biome', 'format', '--write', abs_path]
elif formatter == 'prettier':
    cmd = ['npx', 'prettier', '--write', abs_path]
else:
    sys.exit(0)

try:
    subprocess.run(cmd, cwd=project_root, capture_output=True, timeout=15)
except Exception:
    pass  # Non-blocking: formatter not installed or failed

sys.exit(0)
