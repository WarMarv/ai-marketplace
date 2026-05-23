# AI Marketplace — Design Spec

**Date:** 2026-05-23  
**Status:** Approved

---

## Problem & Goal

Build a public plugin marketplace for Claude Code (and Codex) that ships a multi-agent system: specialized roles (Orchestrator, Reviewer, Tester, Documenter), quality-gate hooks, and autonomous subagents. After `claude plugin install`, everything works immediately in any project — no manual configuration. The marketplace doubles as a public portfolio/showcase.

Source material: Hooks and agents from `ai-engineering-stack` are ported and packaged as distributable plugins.

---

## Architecture Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Distribution | Own marketplace (monorepo) | Full control, identical format to `anthropics/claude-plugins-official` |
| Platform | Claude Code + Codex | Dual manifests: `.claude-plugin/` + `.codex-plugin/` |
| First plugin | `multi-agent-swarm` | Bundles agents + skills + hooks |
| Visibility | Public GitHub repo | Showcase + marketing |

---

## Repo Structure

```
ai-marketplace/                          # GitHub: marvinwarnke/ai-marketplace
├── .claude-plugin/
│   └── marketplace.json                 # Marketplace registry
├── plugins/
│   └── multi-agent-swarm/
│       ├── .claude-plugin/
│       │   └── plugin.json              # Claude Code manifest
│       ├── .codex-plugin/
│       │   └── plugin.json              # Codex manifest
│       ├── skills/
│       │   ├── orchestrator/SKILL.md    # Trigger: coordinate agents, delegate tasks
│       │   ├── reviewer-role/SKILL.md   # Trigger: review code, PR review
│       │   ├── documenter-role/SKILL.md # Trigger: update docs, document changes
│       │   └── tester-role/SKILL.md     # Trigger: write tests, TDD
│       ├── hooks/
│       │   ├── hooks.json               # Hook registry using ${CLAUDE_PLUGIN_ROOT}
│       │   ├── conventional-commits.py
│       │   ├── secret-scanner.py
│       │   ├── dangerous-command-blocker.py
│       │   ├── prevent-direct-push.py
│       │   ├── dev-server-block.py
│       │   ├── post-edit-format.py
│       │   ├── post-edit-typecheck.py
│       │   └── post-edit-console-warn.py
│       ├── agents/
│       │   ├── reviewer.md
│       │   ├── documenter.md
│       │   ├── tester.md
│       │   └── implementer.md
│       └── README.md
└── README.md
```

---

## Key Technical Details

### Portability: `${CLAUDE_PLUGIN_ROOT}`

The critical difference between project-local hooks and plugin hooks is the path variable:

- **Project hooks (not portable):** `python3 "$CLAUDE_PROJECT_DIR/.claude/hooks/secret-scanner.py"`
- **Plugin hooks (portable):** `python3 "${CLAUDE_PLUGIN_ROOT}/hooks/secret-scanner.py"`

`${CLAUDE_PLUGIN_ROOT}` resolves to the plugin's installation path at runtime, making hooks work identically in every project after install.

### `hooks/hooks.json` format

```json
{
  "description": "Multi-Agent Swarm — quality-gate hooks",
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "python3 \"${CLAUDE_PLUGIN_ROOT}/hooks/dangerous-command-blocker.py\"", "timeout": 10 },
          { "type": "command", "command": "python3 \"${CLAUDE_PLUGIN_ROOT}/hooks/secret-scanner.py\"", "timeout": 15 },
          { "type": "command", "command": "python3 \"${CLAUDE_PLUGIN_ROOT}/hooks/conventional-commits.py\"", "timeout": 10 },
          { "type": "command", "command": "python3 \"${CLAUDE_PLUGIN_ROOT}/hooks/prevent-direct-push.py\"", "timeout": 10 },
          { "type": "command", "command": "python3 \"${CLAUDE_PLUGIN_ROOT}/hooks/dev-server-block.py\"", "timeout": 10 }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit",
        "hooks": [
          { "type": "command", "command": "python3 \"${CLAUDE_PLUGIN_ROOT}/hooks/post-edit-format.py\"", "timeout": 30 },
          { "type": "command", "command": "python3 \"${CLAUDE_PLUGIN_ROOT}/hooks/post-edit-typecheck.py\"", "timeout": 15 },
          { "type": "command", "command": "python3 \"${CLAUDE_PLUGIN_ROOT}/hooks/post-edit-console-warn.py\"", "timeout": 10 }
        ]
      }
    ]
  }
}
```

### Skill SKILL.md format

```markdown
---
name: orchestrator
description: Coordinate parallel agent tasks, delegate to Reviewer/Tester/Documenter subagents, manage task dependencies
version: 1.0.0
---
# Orchestrator Role
...workflow instructions...
```

The `description` field is the auto-trigger condition — Claude Code activates the skill when context matches.

### Marketplace manifest (`marketplace.json`) format

```json
{
  "$schema": "https://anthropic.com/claude-code/marketplace.schema.json",
  "name": "warmarv-marketplace",
  "description": "Production-ready multi-agent plugins for Claude Code",
  "owner": { "name": "Marvin Warnke", "email": "marvin.warnke11@gmail.com" },
  "plugins": [
    {
      "name": "multi-agent-swarm",
      "description": "Orchestrator, Reviewer, Tester, Documenter roles with quality-gate hooks",
      "author": { "name": "Marvin Warnke" },
      "category": "development",
      "source": "./plugins/multi-agent-swarm",
      "homepage": "https://github.com/marvinwarnke/ai-marketplace"
    }
  ]
}
```

---

## End-User Installation

```bash
# Register marketplace once
claude plugin marketplace add github:marvinwarnke/ai-marketplace

# Install plugin
claude plugin install multi-agent-swarm

# Active immediately after reload — no further configuration needed
```

---

## Verification

1. `claude plugin marketplace add github:marvinwarnke/ai-marketplace` — runs without error
2. `claude plugin install multi-agent-swarm` — plugin appears in `~/.claude/plugins/cache/`
3. Open a test project, start Claude Code — skills appear in `/help`, hooks fire
4. `git commit -m "bad format"` in test project — conventional-commits hook blocks it
5. "Let's review this code" → reviewer-role skill auto-activates

---

## Deferred Decisions

- Include `pre-commit-tester` and `pre-push-reviewer` hooks? (They call agents — needs agent path resolution inside plugin)
- SemVer tagging strategy for plugin updates
- `dev-quality-gates` as a separate hooks-only plugin (later)
