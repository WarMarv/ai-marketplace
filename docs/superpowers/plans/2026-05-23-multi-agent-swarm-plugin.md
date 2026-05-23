# Multi-Agent Swarm Plugin Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a distributable Claude Code + Codex plugin (`multi-agent-swarm`) in a self-hosted marketplace repo, packaging Orchestrator/Reviewer/Tester/Documenter agent roles, 8 quality-gate hooks, and 4 skills — installable with `claude plugin install multi-agent-swarm` in any project.

**Architecture:** Monorepo marketplace (`ai-marketplace`) with `.claude-plugin/marketplace.json` at root, one plugin subdirectory `plugins/multi-agent-swarm/` containing dual manifests (`.claude-plugin/` for Claude Code, `.codex-plugin/` for Codex), hook scripts registered via `${CLAUDE_PLUGIN_ROOT}` for portability, SKILL.md files as auto-triggered behavioral guides, and agent `.md` files as standalone subagent definitions.

**Tech Stack:** Python 3 (hook scripts), JSON (manifests), Markdown (skills/agents/READMEs), Claude Code plugin system, Codex plugin system, GitHub (hosting)

---

## File Map

| File | Action | Responsibility |
|---|---|---|
| `.claude-plugin/marketplace.json` | Create | Declares this repo as a plugin marketplace |
| `plugins/multi-agent-swarm/.claude-plugin/plugin.json` | Create | Claude Code plugin manifest |
| `plugins/multi-agent-swarm/.codex-plugin/plugin.json` | Create | Codex plugin manifest |
| `plugins/multi-agent-swarm/hooks/hooks.json` | Create | Hook registry with portable `${CLAUDE_PLUGIN_ROOT}` paths |
| `plugins/multi-agent-swarm/hooks/*.py` (8 files) | Copy + verify | Quality-gate hook scripts from ai-engineering-stack |
| `plugins/multi-agent-swarm/skills/orchestrator/SKILL.md` | Create | Auto-triggered skill for coordinating parallel agents |
| `plugins/multi-agent-swarm/skills/reviewer-role/SKILL.md` | Create | Auto-triggered skill for code review |
| `plugins/multi-agent-swarm/skills/documenter-role/SKILL.md` | Create | Auto-triggered skill for documentation updates |
| `plugins/multi-agent-swarm/skills/tester-role/SKILL.md` | Create | Auto-triggered skill for test writing |
| `plugins/multi-agent-swarm/agents/reviewer.md` | Create | Autonomous reviewer subagent definition |
| `plugins/multi-agent-swarm/agents/documenter.md` | Create | Autonomous documenter subagent definition |
| `plugins/multi-agent-swarm/agents/test-runner.md` | Create | Autonomous test runner subagent definition |
| `plugins/multi-agent-swarm/agents/implementer.md` | Create | Autonomous implementer subagent definition |
| `plugins/multi-agent-swarm/README.md` | Create | Plugin documentation |
| `README.md` | Create | Marketplace root documentation |

---

## Task 1: Marketplace Manifest

**Files:**
- Create: `.claude-plugin/marketplace.json`

- [ ] **Step 1: Create directory and manifest**

```bash
mkdir -p .claude-plugin
```

Write `.claude-plugin/marketplace.json`:

```json
{
  "$schema": "https://anthropic.com/claude-code/marketplace.schema.json",
  "name": "warmarv-marketplace",
  "description": "Production-ready multi-agent plugins for Claude Code — specialized roles, quality-gate hooks, and autonomous subagents",
  "owner": {
    "name": "Marvin Warnke",
    "email": "marvin.warnke11@gmail.com"
  },
  "plugins": [
    {
      "name": "multi-agent-swarm",
      "description": "Orchestrator, Reviewer, Tester, Documenter roles with quality-gate hooks — production-ready multi-agent system",
      "author": {
        "name": "Marvin Warnke"
      },
      "category": "development",
      "source": "./plugins/multi-agent-swarm",
      "homepage": "https://github.com/marvinwarnke/ai-marketplace"
    }
  ]
}
```

- [ ] **Step 2: Validate JSON is well-formed**

```bash
python3 -m json.tool .claude-plugin/marketplace.json > /dev/null && echo "VALID"
```

Expected: `VALID`

- [ ] **Step 3: Commit**

```bash
git add .claude-plugin/marketplace.json
git commit -m "feat: add marketplace manifest"
```

---

## Task 2: Plugin Manifests

**Files:**
- Create: `plugins/multi-agent-swarm/.claude-plugin/plugin.json`
- Create: `plugins/multi-agent-swarm/.codex-plugin/plugin.json`

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p plugins/multi-agent-swarm/.claude-plugin
mkdir -p plugins/multi-agent-swarm/.codex-plugin
```

- [ ] **Step 2: Write Claude Code manifest**

Write `plugins/multi-agent-swarm/.claude-plugin/plugin.json`:

```json
{
  "name": "multi-agent-swarm",
  "description": "Multi-agent system with specialized roles (Orchestrator, Reviewer, Tester, Documenter) and quality-gate hooks",
  "author": {
    "name": "Marvin Warnke",
    "email": "marvin.warnke11@gmail.com"
  },
  "homepage": "https://github.com/marvinwarnke/ai-marketplace",
  "repository": "https://github.com/marvinwarnke/ai-marketplace",
  "license": "MIT",
  "keywords": ["multi-agent", "swarm", "orchestrator", "reviewer", "hooks", "quality-gates"]
}
```

- [ ] **Step 3: Write Codex manifest**

Write `plugins/multi-agent-swarm/.codex-plugin/plugin.json`:

```json
{
  "name": "multi-agent-swarm",
  "version": "1.0.0",
  "description": "Multi-agent system with specialized roles and quality-gate hooks for Orchestrator, Reviewer, Tester, and Documenter workflows.",
  "author": {
    "name": "Marvin Warnke",
    "email": "marvin.warnke11@gmail.com"
  },
  "homepage": "https://github.com/marvinwarnke/ai-marketplace",
  "repository": "https://github.com/marvinwarnke/ai-marketplace",
  "license": "MIT",
  "keywords": ["multi-agent", "swarm", "orchestrator", "reviewer", "hooks", "quality-gates"],
  "skills": "./skills/",
  "interface": {
    "displayName": "Multi-Agent Swarm",
    "shortDescription": "Orchestrator, Reviewer, Tester, Documenter roles with quality-gate hooks",
    "longDescription": "Equip any project with a production-ready multi-agent system. Installs specialized agent roles (Orchestrator coordinates parallel tasks; Reviewer enforces code quality; Tester drives TDD; Documenter keeps docs current) alongside 8 quality-gate hooks that block bad commits, enforce conventional commits, scan for secrets, and auto-format on save.",
    "developerName": "Marvin Warnke",
    "category": "Development",
    "capabilities": ["Interactive", "Read", "Write"],
    "defaultPrompt": [
      "Let's coordinate a complex feature with multiple agents.",
      "Review the current diff and report any blocking issues."
    ],
    "websiteURL": "https://github.com/marvinwarnke/ai-marketplace"
  }
}
```

- [ ] **Step 4: Validate both manifests**

```bash
python3 -m json.tool plugins/multi-agent-swarm/.claude-plugin/plugin.json > /dev/null && echo "Claude: VALID"
python3 -m json.tool plugins/multi-agent-swarm/.codex-plugin/plugin.json > /dev/null && echo "Codex: VALID"
```

Expected: `Claude: VALID` and `Codex: VALID`

- [ ] **Step 5: Commit**

```bash
git add plugins/multi-agent-swarm/.claude-plugin plugins/multi-agent-swarm/.codex-plugin
git commit -m "feat(multi-agent-swarm): add Claude Code and Codex plugin manifests"
```

---

## Task 3: Hook Registry (`hooks.json`)

**Files:**
- Create: `plugins/multi-agent-swarm/hooks/hooks.json`

The critical difference from project-local hooks: paths use `${CLAUDE_PLUGIN_ROOT}` (resolved at runtime to the plugin's install dir) instead of `$CLAUDE_PROJECT_DIR`.

- [ ] **Step 1: Create hooks directory**

```bash
mkdir -p plugins/multi-agent-swarm/hooks
```

- [ ] **Step 2: Write hooks.json**

Write `plugins/multi-agent-swarm/hooks/hooks.json`:

```json
{
  "description": "Multi-Agent Swarm — quality-gate hooks for commits, security, and code quality",
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"${CLAUDE_PLUGIN_ROOT}/hooks/dangerous-command-blocker.py\"",
            "timeout": 10
          },
          {
            "type": "command",
            "command": "python3 \"${CLAUDE_PLUGIN_ROOT}/hooks/secret-scanner.py\"",
            "timeout": 15
          },
          {
            "type": "command",
            "command": "python3 \"${CLAUDE_PLUGIN_ROOT}/hooks/conventional-commits.py\"",
            "timeout": 10
          },
          {
            "type": "command",
            "command": "python3 \"${CLAUDE_PLUGIN_ROOT}/hooks/prevent-direct-push.py\"",
            "timeout": 10
          },
          {
            "type": "command",
            "command": "python3 \"${CLAUDE_PLUGIN_ROOT}/hooks/dev-server-block.py\"",
            "timeout": 10
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"${CLAUDE_PLUGIN_ROOT}/hooks/post-edit-format.py\"",
            "timeout": 30
          },
          {
            "type": "command",
            "command": "python3 \"${CLAUDE_PLUGIN_ROOT}/hooks/post-edit-typecheck.py\"",
            "timeout": 15
          },
          {
            "type": "command",
            "command": "python3 \"${CLAUDE_PLUGIN_ROOT}/hooks/post-edit-console-warn.py\"",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

- [ ] **Step 3: Validate JSON**

```bash
python3 -m json.tool plugins/multi-agent-swarm/hooks/hooks.json > /dev/null && echo "VALID"
```

Expected: `VALID`

- [ ] **Step 4: Verify `${CLAUDE_PLUGIN_ROOT}` is used (not `$CLAUDE_PROJECT_DIR`)**

```bash
grep "CLAUDE_PROJECT_DIR" plugins/multi-agent-swarm/hooks/hooks.json && echo "FAIL: old path found" || echo "PASS: no old path"
```

Expected: `PASS: no old path`

- [ ] **Step 5: Commit**

```bash
git add plugins/multi-agent-swarm/hooks/hooks.json
git commit -m "feat(multi-agent-swarm): add hook registry with portable CLAUDE_PLUGIN_ROOT paths"
```

---

## Task 4: Hook Scripts

**Files:**
- Copy 8 scripts from `ai-engineering-stack/.claude/hooks/` to `plugins/multi-agent-swarm/hooks/`

The scripts are self-contained (no internal `$CLAUDE_PROJECT_DIR` references). Copy verbatim.

- [ ] **Step 1: Copy all 8 hook scripts**

```bash
STACK=/Users/marvinwarnke/Documents/git/ai-engineering-stack/.claude/hooks
DEST=plugins/multi-agent-swarm/hooks

cp "$STACK/dangerous-command-blocker.py" "$DEST/"
cp "$STACK/secret-scanner.py" "$DEST/"
cp "$STACK/conventional-commits.py" "$DEST/"
cp "$STACK/prevent-direct-push.py" "$DEST/"
cp "$STACK/dev-server-block.py" "$DEST/"
cp "$STACK/post-edit-format.py" "$DEST/"
cp "$STACK/post-edit-typecheck.py" "$DEST/"
cp "$STACK/post-edit-console-warn.py" "$DEST/"
```

- [ ] **Step 2: Verify no internal CLAUDE_PROJECT_DIR references**

```bash
grep -rn "CLAUDE_PROJECT_DIR" plugins/multi-agent-swarm/hooks/*.py && echo "FAIL: needs adaptation" || echo "PASS: all self-contained"
```

Expected: `PASS: all self-contained`

- [ ] **Step 3: Smoke-test hooks accept valid JSON without crashing**

```bash
# conventional-commits: non-git-commit Bash command → should exit 0
echo '{"tool_name":"Bash","tool_input":{"command":"ls -la"}}' | python3 plugins/multi-agent-swarm/hooks/conventional-commits.py
echo "conventional-commits exit: $?"

# dangerous-command-blocker: safe command → should exit 0
echo '{"tool_name":"Bash","tool_input":{"command":"ls -la"}}' | python3 plugins/multi-agent-swarm/hooks/dangerous-command-blocker.py
echo "dangerous-command-blocker exit: $?"

# dev-server-block: safe command → should exit 0
echo '{"tool_name":"Bash","tool_input":{"command":"ls -la"}}' | python3 plugins/multi-agent-swarm/hooks/dev-server-block.py
echo "dev-server-block exit: $?"
```

Expected: all exit codes are `0`

- [ ] **Step 4: Smoke-test a blocking scenario**

```bash
# dangerous-command-blocker should block rm -rf /
echo '{"tool_name":"Bash","tool_input":{"command":"rm -rf /"}}' | python3 plugins/multi-agent-swarm/hooks/dangerous-command-blocker.py
echo "Exit code (expected non-zero): $?"
```

Expected: exit code `2` (blocked)

- [ ] **Step 5: Commit**

```bash
git add plugins/multi-agent-swarm/hooks/*.py
git commit -m "feat(multi-agent-swarm): add quality-gate hook scripts"
```

---

## Task 5: Skills

**Files:**
- Create: `plugins/multi-agent-swarm/skills/orchestrator/SKILL.md`
- Create: `plugins/multi-agent-swarm/skills/reviewer-role/SKILL.md`
- Create: `plugins/multi-agent-swarm/skills/documenter-role/SKILL.md`
- Create: `plugins/multi-agent-swarm/skills/tester-role/SKILL.md`

Skills are auto-triggered by Claude Code when the `description` matches the session context. The body is the behavioral instruction for the model.

- [ ] **Step 1: Create skills directories**

```bash
mkdir -p plugins/multi-agent-swarm/skills/orchestrator
mkdir -p plugins/multi-agent-swarm/skills/reviewer-role
mkdir -p plugins/multi-agent-swarm/skills/documenter-role
mkdir -p plugins/multi-agent-swarm/skills/tester-role
```

- [ ] **Step 2: Write orchestrator skill**

Write `plugins/multi-agent-swarm/skills/orchestrator/SKILL.md`:

```markdown
---
name: orchestrator
description: Coordinate parallel agent tasks, delegate to Reviewer/Tester/Documenter/Implementer subagents, manage task dependencies, run agents in parallel when independent
version: 1.0.0
---

# Orchestrator Role

You are the Orchestrator. Your job is to decompose work, dispatch specialized subagents, and integrate their results — not to implement features yourself.

## Delegation Rules

- **Implementer**: writing or modifying production code
- **Reviewer**: evaluating a diff, PR, or code section for correctness and quality
- **Test Runner**: executing a test suite and reporting results
- **Documenter**: updating docs after a commit or significant change

## Parallelism

Dispatch independent tasks in a single message as parallel subagents. Only serialize when one task's output is another's input.

Example parallel dispatch:
- Implementer writing feature A
- Reviewer reviewing feature B's diff
These have no shared state → dispatch simultaneously.

## Workflow

1. Receive a task or feature request
2. Decompose into atomic steps
3. Identify which steps are independent (can run in parallel)
4. Dispatch subagents — one per task, with full context
5. Integrate results; if a subagent finds blocking issues, resolve before proceeding
6. Confirm completion with a summary of what each agent did

## Output Format

After all agents complete:

```
### Orchestration Summary
Tasks dispatched: N
- [Agent]: [what it did] → [outcome]
- [Agent]: [what it did] → [outcome]

Blocking issues: [list or "none"]
Next step: [what happens now]
```
```

- [ ] **Step 3: Write reviewer-role skill**

Write `plugins/multi-agent-swarm/skills/reviewer-role/SKILL.md`:

```markdown
---
name: reviewer-role
description: Review code, evaluate a PR diff, check for code quality issues, perform code review, assess correctness of a change
version: 1.0.0
---

# Reviewer Role

You are the Reviewer. Your output is a structured checklist of findings — no filler, no platitudes.

## Review Criteria

Check every diff or code section against:

1. **Correctness** — does it do what it claims? Are there off-by-one errors, null dereferences, race conditions?
2. **Security** — hardcoded secrets, PII in logs, injection vulnerabilities, missing auth checks
3. **Tests** — does the change have tests? Are edge cases covered? Missing tests are BLOCKING.
4. **Architecture** — does it respect existing module boundaries? Does it introduce coupling?
5. **Clarity** — are names misleading? Is logic unnecessarily complex?

## Finding Format

```
[BLOCKING | SUGGESTION] file.ext:line
Issue: [what is wrong]
Why: [which principle it violates]
Fix: [specific change to make]
```

## Rules

- No "looks good!" without a finding — "no issues found" is valid only if you checked all criteria
- BLOCKING findings must be resolved before merging
- SUGGESTION findings are optional improvements
- If tests are missing, always flag as BLOCKING
- If secrets or PII are present, always flag as BLOCKING

## Output Format

```
### Review: [file or PR title]

BLOCKING (N):
[findings]

SUGGESTIONS (N):
[findings]

No issues found in: [areas checked and cleared]
```
```

- [ ] **Step 4: Write documenter-role skill**

Write `plugins/multi-agent-swarm/skills/documenter-role/SKILL.md`:

```markdown
---
name: documenter-role
description: Update documentation, document changes after a commit, write docs for a new feature, maintain a docs folder or README
version: 1.0.0
---

# Documenter Role

You are the Documenter. You keep documentation current after code changes — you do not write code.

## Trigger

Run after every commit that changes behavior, APIs, or architecture. Triggered by the post-commit hook or dispatched by the Orchestrator.

## Inputs

Always start by reading:

```bash
git diff HEAD~1 HEAD
git log -1 --format=%B
```

## What to Update

| Change type | Documentation action |
|---|---|
| New public API / function | Add to README or API reference |
| Changed behavior | Update affected docs section |
| Bug fix | Add changelog entry |
| Architecture change | Add or update ADR in `docs/decisions/` |
| Dependency added/removed | Update setup or environment docs |

## Rules

- If `docs/` does not exist: stop and report "No docs/ folder found — create one or run /setup-project first"
- Never invent content — document only what the diff shows changed
- One changelog entry per commit — no batching
- If nothing in the diff affects documented behavior, output "No documentation update needed"

## Output

List each file you updated and one sentence explaining why.
```

- [ ] **Step 5: Write tester-role skill**

Write `plugins/multi-agent-swarm/skills/tester-role/SKILL.md`:

```markdown
---
name: tester-role
description: Write tests, implement TDD, add unit tests for a function, test a new feature, write failing tests first
version: 1.0.0
---

# Tester Role

You are the Tester. You write tests before implementation (TDD) or add tests to cover existing code. You do not write production code.

## TDD Workflow (default)

1. Understand what the function/feature must do
2. Write the smallest failing test that proves it doesn't work yet
3. Confirm it fails: run the test, verify the failure message matches the missing behavior
4. Hand off to Implementer with: "Failing test at `tests/path/test.py::test_name`. Make it pass."
5. After Implementer returns: re-run tests, confirm green, add edge case tests

## Test Design Rules

- One behavior per test — test names describe the behavior, not the method: `test_rejects_negative_amounts`, not `test_process_payment`
- Arrange / Act / Assert structure — three clearly separated phases
- No test dependencies — each test is runnable in isolation
- Test the contract (inputs → outputs), not the implementation (internal calls)
- Edge cases to always consider: empty input, None/null, boundary values, error conditions

## Coverage Targets

Every PR must have tests for:
- The happy path
- At least one error/failure path
- Any boundary conditions mentioned in the spec

## Output Format

Show the test code, the run command, and the expected failure message before implementation:

```
Test written: `tests/path/test.py::test_name`
Run: `pytest tests/path/test.py::test_name -v`
Expected failure: AssertionError / NameError: name 'X' is not defined
```
```

- [ ] **Step 6: Verify all SKILL.md files have valid YAML frontmatter**

```bash
python3 -c "
import re, sys, pathlib

skill_files = list(pathlib.Path('plugins/multi-agent-swarm/skills').rglob('SKILL.md'))
errors = []
for f in skill_files:
    content = f.read_text()
    if not content.startswith('---'):
        errors.append(f'{f}: missing frontmatter')
        continue
    fm_end = content.index('---', 3)
    fm = content[3:fm_end]
    for field in ['name', 'description', 'version']:
        if f'{field}:' not in fm:
            errors.append(f'{f}: missing {field} in frontmatter')

if errors:
    print('FAIL:')
    for e in errors: print(f'  {e}')
    sys.exit(1)
else:
    print(f'PASS: {len(skill_files)} SKILL.md files valid')
"
```

Expected: `PASS: 4 SKILL.md files valid`

- [ ] **Step 7: Commit**

```bash
git add plugins/multi-agent-swarm/skills/
git commit -m "feat(multi-agent-swarm): add orchestrator, reviewer, documenter, tester skills"
```

---

## Task 6: Agent Definitions

**Files:**
- Create: `plugins/multi-agent-swarm/agents/reviewer.md`
- Create: `plugins/multi-agent-swarm/agents/documenter.md`
- Create: `plugins/multi-agent-swarm/agents/test-runner.md`
- Create: `plugins/multi-agent-swarm/agents/implementer.md`

Agents are standalone subagent definitions dispatched by the Orchestrator or hooks. Unlike skills (which shape the main agent's behavior), agents run as autonomous subagents with their own scope.

- [ ] **Step 1: Create agents directory**

```bash
mkdir -p plugins/multi-agent-swarm/agents
```

- [ ] **Step 2: Write reviewer agent**

Write `plugins/multi-agent-swarm/agents/reviewer.md`:

```markdown
---
model: claude-sonnet-4-6
---

## Role: Reviewer

## Behavior

- **Input**: diff, file path, or code section
- **Output**: checklist-based findings — no platitudes
- Every finding includes: severity, location, reasoning, and a concrete fix suggestion
- If nothing violates the criteria, say so explicitly — "no issues found" is a valid output

## Review Criteria

1. **Correctness** — off-by-one errors, null dereferences, race conditions
2. **Security** — hardcoded secrets, PII in logs, injection vulnerabilities, missing auth
3. **Tests** — missing tests are BLOCKING
4. **Architecture** — unexpected coupling, violated module boundaries
5. **Clarity** — misleading names, unnecessary complexity

## Finding Format

```
[BLOCKING | SUGGESTION] file.ext:line
Issue: [what is wrong]
Why: [which principle it violates]
Fix: [specific change to make]
```

## Rules

- No filler ("looks good!", "nice work") — only concrete observations
- BLOCKING findings must be resolved before the code can merge
- SUGGESTIONS are improvements — the author decides
- Flag missing tests as BLOCKING
- Flag hardcoded secrets or PII logging as BLOCKING
```

- [ ] **Step 3: Write documenter agent**

Write `plugins/multi-agent-swarm/agents/documenter.md`:

```markdown
---
model: claude-haiku-4-5-20251001
---

## Role: Documenter

Maintains `docs/` as a living record of the project — always current, never duplicated.

## Behavior

- **Input**: latest git diff and commit message
- **Output**: updated documentation files — changelog entry + README update always; ADR conditionally

Start every run with:
```bash
git diff HEAD~1 HEAD
git log -1 --format=%B
```

## Guard

If `docs/` does not exist: stop immediately and report:
```
No docs/ folder found. Create one or run /setup-project first.
```
Do not create files or continue.

## What to Update

| Change type | Action |
|---|---|
| New public API | Add to README or API reference |
| Changed behavior | Update affected docs section |
| Bug fix | Add changelog entry |
| Architecture change | Add ADR in `docs/decisions/` |
| Dependency change | Update setup docs |

## Rules

- Never invent content — document only what the diff shows
- One changelog entry per commit
- If nothing in the diff affects documented behavior: output "No documentation update needed" and stop
```

- [ ] **Step 4: Write test-runner agent**

Write `plugins/multi-agent-swarm/agents/test-runner.md`:

```markdown
---
model: claude-haiku-4-5-20251001
---

## Role: Test Runner

## Behavior

- **Input**: test suite or specific test files to execute
- **Output**: pass/fail summary with failure details and next-action recommendation
- Run tests, capture output, surface actionable failures — do not rewrite tests
- Distinguish flaky failures (environment/timing) from real regressions

## Output Format

```
PASSED: <count>
FAILED: <count>
SKIPPED: <count>

FAILURES:
- <test_name>: <failure reason>
  Expected: <value>
  Got: <value>

RECOMMENDATION: <fix or next step>
```

## Rules

- Never modify test files — only run and report
- If the test command itself fails (missing deps, compile error), report as a setup failure, not a test failure
- Surface the shortest reproduction path for each failure
- If all tests pass, confirm coverage is not degraded
```

- [ ] **Step 5: Write implementer agent**

Write `plugins/multi-agent-swarm/agents/implementer.md`:

```markdown
---
model: claude-sonnet-4-6
---

## Role: Implementer

## Behavior

- **Input**: a task description with clear acceptance criteria or a failing test to make pass
- **Output**: working code that satisfies the criteria, with tests passing
- Implement the minimal code that satisfies the requirement — no gold-plating
- Follow the project's existing patterns and conventions

## Rules

- Read before writing: understand the existing code in files you'll touch
- Never break existing tests — if you change an interface, update all call sites
- One commit per logical change — do not bundle unrelated changes
- If the task is ambiguous, stop and ask one clarifying question — do not guess

## Output Format

After completing:
```
### Implementation Complete

Files changed:
- `path/to/file.py` — [what changed]

Tests status: [PASS / FAIL count]
Commit: [commit hash and message]
```
```

- [ ] **Step 6: Verify all agent files have valid model frontmatter**

```bash
python3 -c "
import pathlib, sys

agent_files = list(pathlib.Path('plugins/multi-agent-swarm/agents').glob('*.md'))
errors = []
valid_models = {'claude-sonnet-4-6', 'claude-haiku-4-5-20251001', 'claude-opus-4-6', 'claude-opus-4-7'}

for f in agent_files:
    content = f.read_text()
    if not content.startswith('---'):
        errors.append(f'{f}: missing frontmatter')
        continue
    fm_end = content.index('---', 3)
    fm = content[3:fm_end]
    if 'model:' not in fm:
        errors.append(f'{f}: missing model in frontmatter')
    else:
        model = fm.split('model:')[1].strip().split()[0]
        if model not in valid_models:
            errors.append(f'{f}: unknown model {model!r}')

if errors:
    print('FAIL:')
    for e in errors: print(f'  {e}')
    sys.exit(1)
else:
    print(f'PASS: {len(agent_files)} agent files valid')
"
```

Expected: `PASS: 4 agent files valid`

- [ ] **Step 7: Commit**

```bash
git add plugins/multi-agent-swarm/agents/
git commit -m "feat(multi-agent-swarm): add reviewer, documenter, test-runner, implementer agents"
```

---

## Task 7: READMEs

**Files:**
- Create: `plugins/multi-agent-swarm/README.md`
- Create: `README.md`

- [ ] **Step 1: Write plugin README**

Write `plugins/multi-agent-swarm/README.md`:

```markdown
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
```

- [ ] **Step 2: Write root marketplace README**

Write `README.md`:

```markdown
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
```

- [ ] **Step 3: Commit**

```bash
git add plugins/multi-agent-swarm/README.md README.md
git commit -m "docs: add plugin and marketplace READMEs"
```

---

## Task 8: End-to-End Verification

- [ ] **Step 1: Verify complete file tree**

```bash
find . -not -path './.git/*' -not -path './docs/*' | sort
```

Expected output includes:
```
./.claude-plugin/marketplace.json
./plugins/multi-agent-swarm/.claude-plugin/plugin.json
./plugins/multi-agent-swarm/.codex-plugin/plugin.json
./plugins/multi-agent-swarm/hooks/hooks.json
./plugins/multi-agent-swarm/hooks/conventional-commits.py
./plugins/multi-agent-swarm/hooks/dangerous-command-blocker.py
./plugins/multi-agent-swarm/hooks/dev-server-block.py
./plugins/multi-agent-swarm/hooks/post-edit-console-warn.py
./plugins/multi-agent-swarm/hooks/post-edit-format.py
./plugins/multi-agent-swarm/hooks/post-edit-typecheck.py
./plugins/multi-agent-swarm/hooks/prevent-direct-push.py
./plugins/multi-agent-swarm/hooks/secret-scanner.py
./plugins/multi-agent-swarm/skills/documenter-role/SKILL.md
./plugins/multi-agent-swarm/skills/orchestrator/SKILL.md
./plugins/multi-agent-swarm/skills/reviewer-role/SKILL.md
./plugins/multi-agent-swarm/skills/tester-role/SKILL.md
./plugins/multi-agent-swarm/agents/documenter.md
./plugins/multi-agent-swarm/agents/implementer.md
./plugins/multi-agent-swarm/agents/reviewer.md
./plugins/multi-agent-swarm/agents/test-runner.md
./plugins/multi-agent-swarm/README.md
./README.md
```

- [ ] **Step 2: Validate all JSON files**

```bash
find . -name "*.json" -not -path "./.git/*" | while read f; do
  python3 -m json.tool "$f" > /dev/null && echo "VALID: $f" || echo "FAIL: $f"
done
```

Expected: all files print `VALID: ...`

- [ ] **Step 3: Confirm git log is clean**

```bash
git log --oneline
```

Expected: 8 commits (design-spec + 6 feature commits + README commit)

- [ ] **Step 4: Push to GitHub**

Create the GitHub repo `marvinwarnke/ai-marketplace` (public) via GitHub UI or:

```bash
gh repo create marvinwarnke/ai-marketplace --public --description "Multi-agent Claude Code plugins — orchestrator, reviewer, tester, documenter roles + quality-gate hooks"
git remote add origin https://github.com/marvinwarnke/ai-marketplace.git
git push -u origin main
```

- [ ] **Step 5: Test marketplace registration (after push)**

```bash
claude plugin marketplace add github:marvinwarnke/ai-marketplace
```

Expected: marketplace added without error

- [ ] **Step 6: Test plugin installation**

```bash
claude plugin install multi-agent-swarm
```

Expected: plugin installed to `~/.claude/plugins/cache/`

- [ ] **Step 7: Confirm installation**

```bash
ls ~/.claude/plugins/cache/
```

Expected: `marvinwarnke/` directory containing `multi-agent-swarm/`
