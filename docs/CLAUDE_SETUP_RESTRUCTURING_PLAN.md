# Claude Code Setup Restructuring Plan

> Implementation plan for aligning `.claude/` setup with Claude Code best practices.

**Created**: 2024-12-24
**Reference**: [SKILLS_AND_AGENTS_GUIDE.md](SKILLS_AND_AGENTS_GUIDE.md), [claude-code-best-setup.md](claude-code-best-setup.md), [rules-reference.md](rules-reference.md), [skill-complexity-levels.md](skill-complexity-levels.md)

---

## Table of Contents

1. [Current State](#current-state)
2. [Gaps Identified](#gaps-identified)
3. [Phase 1: Skill Restructuring](#phase-1-skill-restructuring)
4. [Phase 2: Path-Scoped Rules](#phase-2-path-scoped-rules)
5. [Phase 3: Hook Enforcement](#phase-3-hook-enforcement)
6. [Phase 4: Agent Updates](#phase-4-agent-updates)
7. [Execution Order](#execution-order)
8. [Rollback Plan](#rollback-plan)
9. [Success Criteria](#success-criteria)

---

## Current State

### What Exists
- **8 Agents**: `.claude/agents/` with well-defined roles (Ezio, Scout, Sage, Kai, Iris, Devo, Vera, Luna)
- **35+ Skills**: Organized in single files and multi-file groups
  - Multi-file: `google-adk-patterns/`, `testing-strategy/`, `deployment/`, `frontend-patterns/`
  - Single-file: `api-design.md`, `database-design.md`, etc.
- **8 Memory Files**: `.claude/memory/` with STAR format lessons
- **Hook System**: `settings.json` with SessionStart, UserPromptSubmit, PostToolUse, Stop, SessionEnd hooks
- **Context Sharing**: `shared-context.json` for cross-agent communication

---

## Gaps Identified

| Gap | Current State | Target State |
|-----|---------------|--------------|
| **Skill entry point** | README.md | SKILL.md with frontmatter |
| **Skill frontmatter** | None | `name:`, `description:` for auto-discovery |
| **Path-scoped rules** | Not used | `.claude/rules/` with path triggers |
| **Memory enforcement** | Agent compliance | Hook-based enforcement |
| **Single-file skills** | Flat files | Directory with SKILL.md |

---

## Phase 1: Skill Restructuring

**Goal**: Enable skill auto-discovery by Claude Code

### 1.1 Rename README.md to SKILL.md

For each multi-file skill group:

```bash
# google-adk-patterns
mv .claude/skills/google-adk-patterns/README.md .claude/skills/google-adk-patterns/SKILL.md

# testing-strategy
mv .claude/skills/testing-strategy/README.md .claude/skills/testing-strategy/SKILL.md

# deployment
mv .claude/skills/deployment/README.md .claude/skills/deployment/SKILL.md

# frontend-patterns
mv .claude/skills/frontend-patterns/README.md .claude/skills/frontend-patterns/SKILL.md
```

### 1.2 Add Frontmatter to Each SKILL.md

**google-adk-patterns/SKILL.md:**
```yaml
---
name: google-adk-patterns
description: Build AI agents with Google ADK including agent setup, event persistence, state management, tools, FastAPI integration, and OAuth. Use when building agents, debugging persistence, or integrating with Vertex AI.
---
```

**testing-strategy/SKILL.md:**
```yaml
---
name: testing-strategy
description: Comprehensive testing patterns including unit, integration, E2E, accessibility, security, and AI/LLM testing. Use when writing tests, setting up test infrastructure, or debugging test failures.
---
```

**deployment/SKILL.md:**
```yaml
---
name: deployment
description: GCP deployment patterns for Cloud Run, Terraform, Cloud Build, and OAuth. Use when deploying to GCP, creating infrastructure, or setting up CI/CD.
---
```

**frontend-patterns/SKILL.md:**
```yaml
---
name: frontend-patterns
description: React/TypeScript frontend patterns including troubleshooting, OAuth, performance, TanStack Query, forms, routing, state management, and animations. Use when building UIs or debugging frontend issues.
---
```

### 1.3 Convert Single-File Skills to Directories

For each single-file skill:

```bash
# api-design
mkdir -p .claude/skills/api-design
mv .claude/skills/api-design.md .claude/skills/api-design/SKILL.md

# database-design
mkdir -p .claude/skills/database-design
mv .claude/skills/database-design.md .claude/skills/database-design/SKILL.md

# debugging-patterns
mkdir -p .claude/skills/debugging-patterns
mv .claude/skills/debugging-patterns.md .claude/skills/debugging-patterns/SKILL.md

# frontend-development
mkdir -p .claude/skills/frontend-development
mv .claude/skills/frontend-development.md .claude/skills/frontend-development/SKILL.md

# security-best-practices
mkdir -p .claude/skills/security-best-practices
mv .claude/skills/security-best-practices.md .claude/skills/security-best-practices/SKILL.md

# artifact-management
mkdir -p .claude/skills/artifact-management
mv .claude/skills/artifact-management.md .claude/skills/artifact-management/SKILL.md

# websocket-streaming
mkdir -p .claude/skills/websocket-streaming
mv .claude/skills/websocket-streaming.md .claude/skills/websocket-streaming/SKILL.md

# tdd-workflow
mkdir -p .claude/skills/tdd-workflow
mv .claude/skills/tdd-workflow.md .claude/skills/tdd-workflow/SKILL.md
```

Then add frontmatter to each SKILL.md.

### Files Modified (Phase 1)

| File | Action |
|------|--------|
| `.claude/skills/google-adk-patterns/README.md` | Rename to SKILL.md + add frontmatter |
| `.claude/skills/testing-strategy/README.md` | Rename to SKILL.md + add frontmatter |
| `.claude/skills/deployment/README.md` | Rename to SKILL.md + add frontmatter |
| `.claude/skills/frontend-patterns/README.md` | Rename to SKILL.md + add frontmatter |
| `.claude/skills/api-design.md` | Move to directory + add frontmatter |
| `.claude/skills/database-design.md` | Move to directory + add frontmatter |
| `.claude/skills/debugging-patterns.md` | Move to directory + add frontmatter |
| `.claude/skills/frontend-development.md` | Move to directory + add frontmatter |
| `.claude/skills/security-best-practices.md` | Move to directory + add frontmatter |
| `.claude/skills/artifact-management.md` | Move to directory + add frontmatter |
| `.claude/skills/websocket-streaming.md` | Move to directory + add frontmatter |
| `.claude/skills/tdd-workflow.md` | Move to directory + add frontmatter |

---

## Phase 2: Path-Scoped Rules

**Goal**: Add domain-specific rules that trigger when working on specific file paths

### 2.1 Create Directory Structure

```bash
mkdir -p .claude/rules/backend
mkdir -p .claude/rules/frontend
mkdir -p .claude/rules/infra
mkdir -p .claude/rules/testing
```

### 2.2 Create Universal Rules (Always Loaded)

**.claude/rules/code-style.md:**
```markdown
# Code Style Standards

## Python
- Type hints required for all function signatures
- Use `pathlib.Path` over `os.path`
- Use f-strings for string formatting
- Maximum function length: 50 lines
- Linting: `ruff check .`
- Formatting: `black .`

## TypeScript
- Strict mode enabled
- No `any` types - use `unknown` with type guards
- Prefer interfaces over type aliases for objects
- Use named exports over default exports
```

**.claude/rules/git-workflow.md:**
```markdown
# Git Workflow

## Commit Messages
- Use imperative mood: "Add feature" not "Added feature"
- Prefix with type: `feat:`, `fix:`, `refactor:`, `docs:`, `test:`, `chore:`
- Keep subject under 72 characters

## Branching
- Feature branches: `feature/{description}`
- Bug fixes: `fix/{description}`
- Always branch from `main`

## Pre-Commit Checklist
- Run tests
- Run linter
- Run type check
```

### 2.3 Create Path-Scoped Rules

**.claude/rules/backend/fastapi.md:**
```markdown
---
paths: backend/**/*.py, src/api/**/*.py, app/routers/**/*.py, app/endpoints/**/*.py
---

# FastAPI Development Rules

## Endpoint Structure
- All endpoints must have Pydantic models for request/response
- Use appropriate HTTP status codes:
  - 200: Success (GET, PUT, PATCH)
  - 201: Created (POST)
  - 204: No Content (DELETE)
  - 400: Bad Request
  - 404: Not Found
  - 422: Validation Error

## Request/Response Models
- Location: `app/schemas/`
- Naming: `{Resource}Create`, `{Resource}Update`, `{Resource}Response`
- Always include `model_config = {"from_attributes": True}` for ORM models

## Error Handling
- Always log before raising HTTPException
- Include meaningful error details
```

**.claude/rules/backend/adk-agents.md:**
```markdown
---
paths: **/agents/**/*.py, **/agent_*.py, **/*_agent.py
---

# Google ADK Agent Rules

## Critical Gotchas
- `run_async()` only RETURNS events, doesn't modify `session.events`
- Manual append required: `session.events.append(user_msg)` + `extend(result)`
- Use `model_dump(mode='json')` for serialization (bytes handling)
- State doesn't survive reload without explicit save/restore

## Required Patterns
- Always use `google-adk` package (not `google-genai`)
- Set `GOOGLE_GENAI_USE_VERTEXAI=TRUE` for Vertex AI
- Use `europe-west1` region (project mandate)
```

**.claude/rules/frontend/react.md:**
```markdown
---
paths: frontend/**/*.tsx, frontend/**/*.ts, src/components/**/*
---

# React/TypeScript Rules

## Component Structure
- Functional components only (no class components)
- Props interface: `{ComponentName}Props`
- One component per file

## State Management
- Local state: `useState`
- Global state: Zustand store in `stores/`
- Server state: `@tanstack/react-query`

## API Calls
- Use typed fetch functions in `api/`
- Always use react-query for data fetching
- Handle loading and error states

## Type Safety
- Never use `any`
- Use `unknown` and narrow with type guards
- Prefer `interface` for props, `type` for unions
```

**.claude/rules/infra/terraform.md:**
```markdown
---
paths: infra/**/*.tf, terraform/**/*.tf, modules/**/*.tf
---

# Terraform/GCP Rules

## Variables
- Always use variables for: `project_id`, `region`, `environment`
- Provide sensible defaults where appropriate
- Document all variables with `description`

## Resource Tagging
All resources must have labels:
```hcl
labels = {
  environment = var.environment
  managed_by  = "terraform"
  project     = var.project_name
}
```

## Region Mandate
- All GCP resources MUST be in Europe regions
- Default: `europe-west1`
```

**.claude/rules/testing/pytest.md:**
```markdown
---
paths: tests/**/*.py, **/test_*.py, **/*_test.py
---

# Pytest Rules

## Test Structure (AAA Pattern)
1. **Arrange** - Set up test data
2. **Act** - Execute the code
3. **Assert** - Verify the outcome

## Naming
- Test files: `test_{module}.py`
- Test functions: `test_{scenario}_{expected_result}`

## Fixtures
- Use fixtures for common setup
- Prefer `conftest.py` for shared fixtures
- Use `@pytest.fixture(scope="session")` for expensive setup

## Coverage
- Aim for 80%+ coverage on new code
- Run: `pytest --cov=src --cov-report=html`
```

### Files Created (Phase 2)

| File | Type |
|------|------|
| `.claude/rules/code-style.md` | Universal |
| `.claude/rules/git-workflow.md` | Universal |
| `.claude/rules/backend/fastapi.md` | Path-scoped |
| `.claude/rules/backend/adk-agents.md` | Path-scoped |
| `.claude/rules/frontend/react.md` | Path-scoped |
| `.claude/rules/infra/terraform.md` | Path-scoped |
| `.claude/rules/testing/pytest.md` | Path-scoped |

---

## Phase 3: Hook Enforcement

**Goal**: Guarantee memory updates and cross-agent sync happen

### 3.1 Add SubagentStop Hook

Update `.claude/settings.json`:

```json
{
  "hooks": {
    "SubagentStop": [
      {
        "hooks": [{
          "type": "command",
          "command": "python3 \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/agent_reflection.py"
        }]
      }
    ]
  }
}
```

### 3.2 Create agent_reflection.py

**.claude/hooks/agent_reflection.py:**
```python
#!/usr/bin/env python3
"""
Runs at agent session end via SubagentStop hook.
Outputs a prompt that forces memory update before ending.
"""

import os
from datetime import datetime

def main():
    agent_name = os.environ.get("CLAUDE_AGENT_NAME", "unknown")
    memory_path = f".claude/memory/memory-{agent_name.lower().replace(' ', '-')}.md"

    prompt = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AGENT SESSION REFLECTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Agent: {agent_name}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Update Memory File: {memory_path}

You MUST add an entry with:

### [{datetime.now().strftime('%Y-%m-%d')}] Session Summary

**Task**: What was accomplished
**What Worked**: Successful approaches
**What Didn't**: Failed attempts and why
**Pattern**: Any reusable pattern discovered
**Gotcha**: Any pitfall to avoid

You cannot end this session without updating the memory file.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    print(prompt)

if __name__ == "__main__":
    main()
```

### Files Modified/Created (Phase 3)

| File | Action |
|------|--------|
| `.claude/settings.json` | Add SubagentStop hook |
| `.claude/hooks/agent_reflection.py` | Create new file |

---

## Phase 4: Agent Updates

**Goal**: Remove incorrect `Skill(skill="name")` syntax, explain auto-discovery

### 4.1 Update Each Agent File

For each agent in `.claude/agents/`:

**Remove:**
```markdown
**How to invoke skills:**
- Skill(skill="google-adk-patterns")
- Skill(skill="vertex-ai-models")
```

**Replace with:**
```markdown
**How skills work:**
Skills are auto-discovered based on your task context. When working on AI agents,
the `google-adk-patterns` skill will be automatically available. Just reference
the skill content in your work.

**Available skills for your domain:**
- `google-adk-patterns` - ADK agent patterns (auto-loaded for agent work)
- `testing-strategy` - Test patterns (auto-loaded when writing tests)
```

### Files Modified (Phase 4)

| File | Changes |
|------|---------|
| `.claude/agents/ai-engineer.md` | Remove Skill() syntax, add auto-discovery explanation |
| `.claude/agents/frontend-engineer.md` | Remove Skill() syntax, add auto-discovery explanation |
| `.claude/agents/devops-engineer.md` | Remove Skill() syntax, add auto-discovery explanation |
| `.claude/agents/qa-tester.md` | Remove Skill() syntax, add auto-discovery explanation |
| `.claude/agents/frontend-qa-specialist.md` | Remove Skill() syntax, add auto-discovery explanation |
| `.claude/agents/solution-architect.md` | Remove Skill() syntax, add auto-discovery explanation |
| `.claude/agents/orchestrator.md` | Remove Skill() syntax, add auto-discovery explanation |

---

## Execution Order

| Phase | Description | Files | Risk |
|-------|-------------|-------|------|
| **1** | Skill restructuring | 12 skills | Medium - renames and moves |
| **2** | Rules creation | 7 new files | Low - additive only |
| **3** | Hook enforcement | 2 files | Low - additive only |
| **4** | Agent updates | 7 agents | Low - documentation only |

**Recommended sequence:**
1. Phase 2 (Rules) - No breaking changes
2. Phase 3 (Hooks) - No breaking changes
3. Phase 1 (Skills) - Requires careful renaming
4. Phase 4 (Agents) - Documentation cleanup

---

## Rollback Plan

If issues occur:

### Phase 1 (Skills)
```bash
# Restore from archive
cp -r .claude/skills/archive/* .claude/skills/

# Or revert from git
git checkout HEAD -- .claude/skills/
```

### Phase 2 (Rules)
```bash
# Simply delete
rm -rf .claude/rules/
```

### Phase 3 (Hooks)
```bash
# Revert settings.json
git checkout HEAD -- .claude/settings.json

# Delete hook script
rm .claude/hooks/agent_reflection.py
```

### Phase 4 (Agents)
```bash
# Revert from git
git checkout HEAD -- .claude/agents/
```

---

## Success Criteria

- [ ] All skills have `SKILL.md` with proper frontmatter (`name`, `description`)
- [ ] Skills are organized in directories (not flat files)
- [ ] Path-scoped rules load when working on domain-specific files
- [ ] `SubagentStop` hook enforces memory updates
- [ ] Agent files no longer reference `Skill(skill="name")` syntax
- [ ] `SKILLS_AND_AGENTS_GUIDE.md` accurately describes the new system

---

## Quick Reference

### Skill Frontmatter Template
```yaml
---
name: skill-name-here
description: What this skill does. Use when [trigger conditions].
allowed-tools: Read, Grep, Glob  # Optional
---
```

### Rule Frontmatter Template
```yaml
---
paths: path/to/files/**/*.ext, other/path/**/*
---
```

### Hook Configuration Template
```json
{
  "hooks": {
    "EventName": [{
      "matcher": "ToolName",
      "hooks": [{
        "type": "command",
        "command": "script.py"
      }]
    }]
  }
}
```
