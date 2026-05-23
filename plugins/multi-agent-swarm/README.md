# multi-agent-swarm

A production-ready multi-agent system for Claude Code and Codex. Install once, get specialized agent roles and quality-gate hooks in every project.

## What You Get

### Agent Roles (Skills)

Four auto-triggered skills that activate based on context:

| Skill | Auto-triggers when... |
|---|---|
| **Orchestrator** | coordinating parallel tasks, delegating to subagents |
| **Reviewer** | reviewing code, evaluating a diff or PR |
| **Documenter** | updating docs, documenting a change |
| **Tester** | writing tests, implementing TDD |

### Quality-Gate Hooks

Eight hooks that fire automatically — no configuration needed:

**PreToolUse (Bash):**
- `dangerous-command-blocker` — blocks catastrophic commands (`rm -rf /`, fork bombs)
- `secret-scanner` — scans staged files for 30+ secret patterns before commits
- `conventional-commits` — enforces `type(scope): description` commit format
- `prevent-direct-push` — blocks pushes to `main`/`develop`, requires PRs
- `dev-server-block` — blocks dev servers launched outside tmux

**PostToolUse (Edit):**
- `post-edit-format` — auto-formats JS/TS files (Biome or Prettier, auto-detected)
- `post-edit-typecheck` — runs `tsc --noEmit` on edited `.ts`/`.tsx` files
- `post-edit-console-warn` — flags `console.log` statements in edited files

### Autonomous Subagents

Four agent definitions you can dispatch as subagents:

- **reviewer** — structured code review with BLOCKING/SUGGESTION findings
- **documenter** — keeps `docs/` current after commits
- **test-runner** — runs test suites and reports failures with recommendations
- **implementer** — implements features from task descriptions or failing tests

## Installation

```bash
# Register this marketplace (once per machine)
claude plugin marketplace add github:marvinwarnke/ai-marketplace

# Install the plugin
claude plugin install multi-agent-swarm
```

Reload Claude Code. Hooks are active immediately. Skills appear in `/help`.

## Usage

### Skills (auto-triggered)

The Orchestrator, Reviewer, Documenter, and Tester skills activate automatically when Claude Code detects relevant context. You can also invoke them explicitly via slash commands if listed in `/help`.

### Agents (manual dispatch)

Dispatch agents as subagents from the Orchestrator skill or directly:

```
Dispatch the reviewer agent to evaluate this diff: [paste diff]
```

## Requirements

- Claude Code (any recent version) or Codex
- Python 3 (for hooks)
- `npx` available if using `post-edit-format` or `post-edit-typecheck` hooks
