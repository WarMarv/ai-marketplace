#!/usr/bin/env python3
"""
Stop Hook: Track token and cost metrics per session
Appends a JSONL record to ~/.claude/metrics/costs.jsonl after each response.
"""

import json
import os
import sys
from datetime import datetime, timezone

try:
    raw = sys.stdin.read()
    data = json.loads(raw) if raw.strip() else {}
except Exception:
    sys.exit(0)

usage = data.get('usage') or data.get('token_usage') or {}
input_tokens = int(usage.get('input_tokens') or usage.get('prompt_tokens') or 0)
output_tokens = int(usage.get('output_tokens') or usage.get('completion_tokens') or 0)

model = str(
    data.get('model') or
    os.environ.get('CLAUDE_MODEL', 'unknown')
).lower()

session_id = os.environ.get('CLAUDE_SESSION_ID', 'default')

# Approximate per-1M-token rates
RATES = {
    'haiku':  {'in': 0.80,  'out': 4.0},
    'sonnet': {'in': 3.00,  'out': 15.0},
    'opus':   {'in': 15.00, 'out': 75.0},
}
rates = RATES['sonnet']
if 'haiku' in model:
    rates = RATES['haiku']
elif 'opus' in model:
    rates = RATES['opus']

estimated_cost = round(
    (input_tokens / 1_000_000) * rates['in'] +
    (output_tokens / 1_000_000) * rates['out'],
    6,
)

metrics_dir = os.path.join(os.path.expanduser('~'), '.claude', 'metrics')
os.makedirs(metrics_dir, exist_ok=True)

row = {
    'timestamp': datetime.now(timezone.utc).isoformat(),
    'session_id': session_id,
    'model': model,
    'input_tokens': input_tokens,
    'output_tokens': output_tokens,
    'estimated_cost_usd': estimated_cost,
}

try:
    with open(os.path.join(metrics_dir, 'costs.jsonl'), 'a', encoding='utf-8') as f:
        f.write(json.dumps(row) + '\n')
except Exception:
    pass  # Non-blocking

sys.exit(0)
