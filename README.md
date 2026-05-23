# warmarv-marketplace

A public Claude Code plugin marketplace — production-ready multi-agent plugins built on real engineering workflows.

## Available Plugins

| Plugin | Description |
|---|---|
| [multi-agent-swarm](./plugins/multi-agent-swarm/) | Orchestrator, Reviewer, Tester, Documenter roles + 8 quality-gate hooks |

## Add This Marketplace

```bash
claude plugin marketplace add github:marvinwarnke/ai-marketplace
```

Then install individual plugins:

```bash
claude plugin install multi-agent-swarm
```

## Architecture

This marketplace follows the same structure as [`anthropics/claude-plugins-official`](https://github.com/anthropics/claude-plugins-official):

- `.claude-plugin/marketplace.json` — plugin registry
- `plugins/<name>/` — one directory per plugin
- Each plugin has `.claude-plugin/` (Claude Code) and `.codex-plugin/` (Codex) manifests
- Hooks use `${CLAUDE_PLUGIN_ROOT}` for portable paths — no project-specific configuration needed

New plugins can be added by creating a new subdirectory under `plugins/` and registering it in `marketplace.json`.

## Built By

[Marvin Warnke](https://github.com/marvinwarnke) — AI engineering tooling for production workflows.
