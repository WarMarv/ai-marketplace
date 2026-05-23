#!/usr/bin/env python3
"""
Secret Scanner Hook
Detects hardcoded secrets before git commits
"""

import json
import sys
import re
import subprocess
import os

# Secret detection patterns with descriptions
SECRET_PATTERNS = [
    # AWS Keys
    (r'AKIA[0-9A-Z]{16}', 'AWS Access Key ID', 'high'),
    (r'(?i)aws[_\-\s]*secret[_\-\s]*access[_\-\s]*key[\'"\s]*[=:][\'"\s]*[A-Za-z0-9/+=]{40}', 'AWS Secret Access Key', 'high'),

    # Anthropic (Claude) API Keys
    (r'sk-ant-api\d{2}-[A-Za-z0-9\-_]{20,}', 'Anthropic API Key', 'high'),

    # OpenAI API Keys
    (r'sk-[a-zA-Z0-9]{48,}', 'OpenAI API Key', 'high'),
    (r'sk-proj-[a-zA-Z0-9\-_]{32,}', 'OpenAI Project API Key', 'high'),

    # Google API Keys & Service Accounts
    (r'AIza[0-9A-Za-z\-_]{35}', 'Google API Key', 'high'),
    (r'ya29\.[0-9A-Za-z\-_]+', 'Google OAuth Access Token', 'high'),

    # Stripe API Keys
    (r'sk_live_[0-9a-zA-Z]{24,}', 'Stripe Live Secret Key', 'critical'),
    (r'sk_test_[0-9a-zA-Z]{24,}', 'Stripe Test Secret Key', 'medium'),
    (r'rk_live_[0-9a-zA-Z]{24,}', 'Stripe Live Restricted Key', 'high'),
    (r'pk_live_[0-9a-zA-Z]{24,}', 'Stripe Live Publishable Key', 'medium'),

    # GitHub Tokens
    (r'ghp_[0-9a-zA-Z]{36}', 'GitHub Personal Access Token', 'high'),
    (r'gho_[0-9a-zA-Z]{36}', 'GitHub OAuth Token', 'high'),
    (r'ghs_[0-9a-zA-Z]{36}', 'GitHub App Secret', 'high'),
    (r'ghr_[0-9a-zA-Z]{36}', 'GitHub Refresh Token', 'high'),
    (r'github_pat_[0-9a-zA-Z_]{22,}', 'GitHub Fine-Grained PAT', 'high'),

    # GitLab Tokens
    (r'glpat-[0-9a-zA-Z\-_]{20,}', 'GitLab Personal Access Token', 'high'),

    # Vercel Tokens
    (r'vercel_[0-9a-zA-Z_\-]{24,}', 'Vercel Token', 'high'),

    # Supabase Keys
    (r'sbp_[0-9a-f]{40}', 'Supabase Service Key', 'high'),
    (r'sb_publishable_[A-Za-z0-9\-_]{20,}', 'Supabase Publishable Key', 'medium'),
    (r'sb_secret_[A-Za-z0-9\-_]{20,}', 'Supabase Secret Key', 'high'),

    # Hugging Face Tokens
    (r'hf_[a-zA-Z0-9]{34,}', 'Hugging Face Token', 'high'),

    # Replicate API Tokens
    (r'r8_[a-zA-Z0-9]{38,}', 'Replicate API Token', 'high'),

    # Groq API Keys
    (r'gsk_[a-zA-Z0-9]{48,}', 'Groq API Key', 'high'),

    # Databricks Personal Access Tokens
    (r'dapi[0-9a-f]{32}', 'Databricks Access Token', 'high'),

    # Azure Keys
    (r'(?i)azure[_\-\s]*(?:key|secret|token)[\'"\s]*[=:][\'"\s]*[A-Za-z0-9+/=]{32,}', 'Azure Key', 'high'),

    # DigitalOcean Tokens
    (r'dop_v1_[0-9a-f]{64}', 'DigitalOcean Personal Access Token', 'high'),
    (r'doo_v1_[0-9a-f]{64}', 'DigitalOcean OAuth Token', 'high'),

    # Linear API Keys
    (r'lin_api_[a-zA-Z0-9]{40,}', 'Linear API Key', 'high'),

    # Notion API Keys
    (r'ntn_[0-9a-zA-Z]{40,}', 'Notion Integration Token', 'high'),

    # Figma Access Tokens
    (r'figd_[0-9a-zA-Z\-_]{40,}', 'Figma Access Token', 'high'),

    # npm Tokens
    (r'npm_[0-9a-zA-Z]{36,}', 'npm Access Token', 'high'),

    # PyPI API Tokens
    (r'pypi-[A-Za-z0-9\-_]{16,}', 'PyPI API Token', 'high'),

    # Generic API Keys
    (r'(?i)(api[_\-\s]*key|apikey)[\'"\s]*[=:][\'"\s]*[\'"][0-9a-zA-Z\-_]{20,}[\'"]', 'Generic API Key', 'medium'),
    (r'(?i)(secret[_\-\s]*key|secretkey)[\'"\s]*[=:][\'"\s]*[\'"][0-9a-zA-Z\-_]{20,}[\'"]', 'Generic Secret Key', 'medium'),

    # Passwords
    (r'(?i)password[\'"\s]*[=:][\'"\s]*[\'"][^\'"\s]{8,}[\'"]', 'Hardcoded Password', 'high'),

    # Private Keys
    (r'-----BEGIN (RSA |DSA |EC )?PRIVATE KEY-----', 'Private Key', 'critical'),
    (r'-----BEGIN OPENSSH PRIVATE KEY-----', 'OpenSSH Private Key', 'critical'),

    # Database Connection Strings
    (r'(?i)(mysql|postgresql|postgres|mongodb)://[^\s\'"\)]+:[^\s\'"\)]+@', 'Database Connection String', 'high'),

    # JWT Tokens
    (r'eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}', 'JWT Token', 'medium'),

    # Slack Tokens
    (r'xox[baprs]-[0-9a-zA-Z\-]{10,}', 'Slack Token', 'high'),

    # Twilio API Keys
    (r'SK[0-9a-fA-F]{32}', 'Twilio API Key', 'high'),

    # SendGrid API Keys
    (r'SG\.[A-Za-z0-9_\-]{22}\.[A-Za-z0-9_\-]{43}', 'SendGrid API Key', 'high'),
]

# Files to exclude from scanning
EXCLUDED_FILES = [
    '.env.example', '.env.sample', '.env.template',
    'package-lock.json', 'yarn.lock', 'poetry.lock',
    'Pipfile.lock', 'Cargo.lock', 'go.sum', '.gitignore',
    # Hook scripts themselves contain pattern strings — not actual secrets
    'secret-scanner.py', 'conventional-commits.py',
    'dangerous-command-blocker.py', 'prevent-direct-push.py',
]

EXCLUDED_DIRS = [
    'node_modules/', 'vendor/', '.git/', 'dist/', 'build/',
    '__pycache__/', '.pytest_cache/', 'venv/', 'env/',
]

def should_skip_file(file_path):
    if not os.path.exists(file_path):
        return True
    if os.path.basename(file_path) in EXCLUDED_FILES:
        return True
    for excluded_dir in EXCLUDED_DIRS:
        if excluded_dir in file_path:
            return True
    try:
        with open(file_path, 'rb') as f:
            if b'\0' in f.read(1024):
                return True
    except:
        return True
    return False

def get_staged_files():
    try:
        result = subprocess.run(
            ['git', 'diff', '--cached', '--name-only', '--diff-filter=ACM'],
            capture_output=True, text=True, check=True
        )
        return [f.strip() for f in result.stdout.split('\n') if f.strip()]
    except subprocess.CalledProcessError:
        return []

def scan_file(file_path):
    findings = []
    if should_skip_file(file_path):
        return findings
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        for line_num, line in enumerate(content.split('\n'), 1):
            for pattern, description, severity in SECRET_PATTERNS:
                for match in re.finditer(pattern, line):
                    line_stripped = line.strip()
                    if line_stripped.startswith('#') or line_stripped.startswith('//'):
                        if 'example' in line_stripped.lower() or 'placeholder' in line_stripped.lower():
                            continue
                    findings.append({
                        'file': file_path, 'line': line_num,
                        'description': description, 'severity': severity,
                        'match': match.group(0)[:50] + '...' if len(match.group(0)) > 50 else match.group(0),
                    })
    except:
        pass
    return findings

def main():
    try:
        input_data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    command = input_data.get('tool_input', {}).get('command', '')
    if not re.search(r'git\s+commit', command):
        sys.exit(0)

    staged_files = get_staged_files()

    if not staged_files:
        commit_match = re.search(r'git\s+commit\s+(.+)', command)
        if commit_match and re.search(r'-\w*a', commit_match.group(1)):
            result = subprocess.run(['git', 'diff', '--name-only'], capture_output=True, text=True)
            for f in result.stdout.strip().split('\n'):
                if f.strip() and os.path.isfile(f.strip()):
                    staged_files.append(f.strip())

    if not staged_files:
        sys.exit(0)

    all_findings = []
    for file_path in staged_files:
        all_findings.extend(scan_file(file_path))

    if all_findings:
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        all_findings.sort(key=lambda x: severity_order.get(x['severity'], 4))

        print('', file=sys.stderr)
        print('🚨 SECRET SCANNER: Potential secrets detected!', file=sys.stderr)
        print('', file=sys.stderr)
        print(f'Found {len(all_findings)} potential secret(s):', file=sys.stderr)
        for f in all_findings:
            emoji = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🔵'}.get(f['severity'], '⚪')
            print(f'{emoji} {f["description"]} — {f["file"]}:{f["line"]}', file=sys.stderr)
            print(f'   Match: {f["match"]}', file=sys.stderr)
        print('', file=sys.stderr)
        print('❌ COMMIT BLOCKED: Move secrets to environment variables (.env)', file=sys.stderr)
        sys.exit(2)

    sys.exit(0)

if __name__ == '__main__':
    main()
