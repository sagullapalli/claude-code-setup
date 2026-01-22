# Claude Code Rules: Complete Reference Guide

> This document serves as the authoritative reference for understanding and implementing rules in Claude Code. Use this when restructuring your project setup.

---

## Table of Contents

1. [What Are Rules?](#what-are-rules)
2. [How Rules Are Loaded](#how-rules-are-loaded)
3. [Rules vs Other Features](#rules-vs-other-features)
4. [The Four Levels of Rules](#the-four-levels-of-rules)
5. [Level 1: Basic Static Rules](#level-1-basic-static-rules)
6. [Level 2: Path-Scoped Rules](#level-2-path-scoped-rules)
7. [Level 3: Agent-Integrated Rules](#level-3-agent-integrated-rules)
8. [Level 4: Hook-Enforced Rules](#level-4-hook-enforced-rules)
9. [Common Patterns](#common-patterns)
10. [Anti-Patterns to Avoid](#anti-patterns-to-avoid)

---

## What Are Rules?

Rules are **modular, topic-specific instructions** stored as markdown files in `.claude/rules/`. They allow you to organize project guidance into focused, maintainable pieces rather than one monolithic CLAUDE.md file.

### File Structure

```
.claude/
├── CLAUDE.md                    # High-level project context (always loaded)
├── settings.json                # Hooks, permissions, MCP config
├── rules/
│   ├── code-style.md            # Always loaded (no frontmatter)
│   ├── git-workflow.md          # Always loaded
│   ├── backend/
│   │   └── fastapi.md           # Path-scoped (loaded when matching files accessed)
│   ├── frontend/
│   │   └── react.md             # Path-scoped
│   └── ml/
│       └── training.md          # Path-scoped
├── agents/
│   ├── ai-engineer.md           # Agent definition (includes agent-specific rules)
│   └── frontend-engineer.md
└── skills/
    └── ...
```

---

## How Rules Are Loaded

### Loading Behavior

| Rule Type | When Loaded | Trigger |
|-----------|-------------|---------|
| **No frontmatter** | Session start | Always loaded with CLAUDE.md |
| **With `paths:` frontmatter** | On file access | When Claude reads/edits files matching the pattern |

### Path-Scoped Loading Mechanism

```markdown
---
paths: src/api/**/*.py
---

# API Rules
...
```

This rule loads **only when Claude accesses files matching `src/api/**/*.py`**.

**Important**: The trigger is file access, NOT:
- Which agent is running
- What task is being performed
- What the user asked for

### Glob Pattern Syntax

| Pattern | Matches |
|---------|---------|
| `*.py` | Python files in current directory only |
| `**/*.py` | Python files in any subdirectory |
| `src/**/*` | All files under src/ |
| `{src,lib}/**/*.ts` | TypeScript files in src/ or lib/ |
| `tests/**/*.test.py` | Test files with .test.py suffix |

### Memory Hierarchy (Priority Order)

```
1. Enterprise policy     (highest - system directories, IT managed)
2. Project CLAUDE.md     (./CLAUDE.md or ./.claude/CLAUDE.md)
3. Project rules         (./.claude/rules/*.md)
4. User CLAUDE.md        (~/.claude/CLAUDE.md)
5. Local CLAUDE.md       (./CLAUDE.local.md - not committed)
```

All levels are loaded; higher priority doesn't override, it takes precedence on conflicts.

---

## Rules vs Other Features

Understanding what each feature does prevents misuse:

| Feature | Nature | Execution | Use For |
|---------|--------|-----------|---------|
| **Rules** | Suggestions ("should do") | Claude decides to follow | Guidelines, patterns, standards |
| **Hooks** | Enforcement ("must do") | Shell runs automatically | Guaranteed actions, validation |
| **Skills** | Actionable tools | Claude invokes when needed | Multi-step reusable tasks |
| **Agent definitions** | Identity + capabilities | Defines what agent can do | Subagent specialization |
| **CLAUDE.md** | Background context | Always in context | Project overview, key commands |

### Key Insight: Rules Cannot Guarantee Behavior

Rules are instructions that Claude *should* follow, but may skip when:
- Focused on primary task
- Context window is crowded
- Judges the instruction as low priority

**If you need guaranteed behavior, use hooks.**

---

## The Four Levels of Rules

| Level | Complexity | Loading | Primary Use |
|-------|------------|---------|-------------|
| **1. Basic** | Simple | Always | Universal standards |
| **2. Path-Scoped** | Medium | On file match | Domain-specific guidelines |
| **3. Agent-Integrated** | High | Via agent definition | Subagent coordination |
| **4. Hook-Enforced** | Advanced | Rules + Hooks | Guaranteed behaviors |

---

## Level 1: Basic Static Rules

**Characteristics:**
- No frontmatter
- Loaded every session
- Universal guidelines that apply to all work

**When to use:**
- Code style standards
- Git workflow
- Project commands reference
- Universal patterns

### Example 1.1: Code Style

```markdown
# .claude/rules/code-style.md

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
- No `any` types—use `unknown` with type guards
- Prefer interfaces over type aliases for objects
- Use named exports over default exports
```

### Example 1.2: Git Workflow

```markdown
# .claude/rules/git-workflow.md

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
- Run tests: `pytest`
- Run linter: `ruff check .`
- Run type check: `pyright`
```

### Example 1.3: Project Commands

```markdown
# .claude/rules/commands.md

# Project Commands Reference

## Development
- `make dev` — Start development server
- `make test` — Run all tests
- `make lint` — Run linter and formatter

## Database
- `make db-migrate` — Run migrations
- `make db-reset` — Reset database (destructive)

## Deployment
- `make deploy-staging` — Deploy to staging
- `make deploy-prod` — Deploy to production (requires approval)

## Environment
- Python: 3.11+ required
- Node: 20+ required
- Copy `.env.example` to `.env` for local development
```

---

## Level 2: Path-Scoped Rules

**Characteristics:**
- Has `paths:` frontmatter
- Loaded only when matching files are accessed
- Reduces context noise for unrelated work

**When to use:**
- Language-specific patterns
- Domain-specific guidelines (API, ML, Infra)
- Framework conventions

### Example 2.1: FastAPI Backend

```markdown
# .claude/rules/backend/fastapi.md

---
paths: src/api/**/*.py, app/routers/**/*.py, app/endpoints/**/*.py
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
  - 422: Validation Error (automatic from Pydantic)

## Request/Response Models
- Location: `app/schemas/`
- Naming: `{Resource}Create`, `{Resource}Update`, `{Resource}Response`
- \lways include `Config` with `from_attributes = True` for ORM models

## Error Handling
|```python
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

# Always log before raising
logger.error(f"Resource not found: {resource_id}")
raise HTTPException(status_code=404, detail="Resource not found")
```|

## Dependencies
- Database sessions: `Depends(get_db)`
- Authentication: `Depends(get_current_user)`
- Keep dependency functions in `app/dependencies/`

## Documentation
- Add docstrings to all endpoints (becomes OpenAPI description)
- Include example request/response in docstrings
```

### Example 2.2: React/TypeScript Frontend

```markdown
# .claude/rules/frontend/react.md

---
paths: frontend/**/*.tsx, frontend/**/*.ts, src/components/**/*
---

# React/TypeScript Rules

## Component Structure
- Functional components only (no class components)
- Props interface: `{ComponentName}Props`
- One component per file

## File Organization
|```
components/
├── Button/
│   ├── Button.tsx        # Component
│   ├── Button.test.tsx   # Tests
│   └── index.ts          # Export
```|

## State Management
- Local state: `useState`
- Global state: Zustand store in `stores/`
- Server state: `@tanstack/react-query`

## API Calls
- Use typed fetch functions in `api/`
- Always use react-query for data fetching
- Handle loading and error states

## Styling
- Tailwind CSS for styling
- No inline styles except for dynamic values
- Component-specific styles in same directory

## Type Safety
- Never use `any`
- Use `unknown` and narrow with type guards
- Prefer `interface` for props, `type` for unions
```

### Example 2.3: Terraform/GCP Infrastructure

```markdown
# .claude/rules/infra/terraform.md

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
|```hcl
labels = {
  environment = var.environment
  managed_by  = "terraform"
  project     = var.project_name
}
```|

## State Management
- State bucket: `gs://${var.project_id}-tfstate`
- Use workspaces for environments: `dev`, `staging`, `prod`

## Modules
- Create modules for repeated patterns
- Module location: `modules/{module-name}/`
- Required files: `main.tf`, `variables.tf`, `outputs.tf`

## Secrets
- Never hardcode secrets
- Use Google Secret Manager
- Reference: `data.google_secret_manager_secret_version`

## Naming Conventions
- Resources: `{project}-{environment}-{resource-type}`
- Example: `myapp-prod-cloud-run`
```

### Example 2.4: ML/Training Code

```markdown
# .claude/rules/ml/training.md

---
paths: ml/**/*.py, training/**/*.py, models/**/*.py, notebooks/**/*.ipynb
---

# ML Training Rules

## Experiment Tracking
- Log all experiments to Weights & Biases
- Required logged items:
  - Hyperparameters
  - Training/validation metrics
  - Model artifacts
  - Git commit hash
  - Dataset version

## Reproducibility
- Set random seeds at start of training:
|```python
import random
import numpy as np
import torch

def set_seed(seed: int = 42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
```|

## Configuration
- Use Hydra or similar for config management
- Config files in `configs/`
- Override via command line, not code changes

## Data Pipeline
- Data loading in `data/` module
- Use `torch.utils.data.DataLoader` with `num_workers > 0`
- Cache preprocessed data when possible

## Model Artifacts
Save with metadata:
|```python
artifact = {
    "model_state_dict": model.state_dict(),
    "config": config,
    "metrics": metrics,
    "git_hash": get_git_hash(),
    "timestamp": datetime.now().isoformat(),
}
torch.save(artifact, path)
```|

```

### Example 2.5: Using Imports in Path-Scoped Rules

You can load additional context using `@` imports:

```markdown
# .claude/rules/ml/rag-context.md

---
paths: ml/retrieval/**/*.py, ml/embeddings/**/*.py
---

# RAG Development Context

Reference architecture: @docs/architecture/rag-patterns.md

## Our RAG Stack
- Vector store: Pinecone
- Embedding model: text-embedding-3-large
- Chunk size: 512 tokens
- Chunk overlap: 50 tokens

## Key Files
- Embedding pipeline: `ml/embeddings/pipeline.py`
- Retrieval logic: `ml/retrieval/search.py`
- Index management: `ml/retrieval/indexer.py`
```

When this rule loads, it also pulls in the referenced architecture doc.

---

## Level 3: Agent-Integrated Rules

**Key Understanding**: Rules don't know which agent is running. There is no `agent:` frontmatter.

**How to give agents their own rules:**
1. Embed rules directly in agent definition files
2. Have orchestrator instructions that reinforce agent behaviors
3. Use path-scoped rules for files agents typically work with

### How Subagents Get Context

When the orchestrator (main Claude) spawns a subagent via the Task tool:
1. The agent definition file is loaded (`.claude/agents/{name}.md`)
2. The agent's custom system prompt is applied
3. The agent works with whatever files/context it's given

**Agent-specific rules must be IN the agent definition.**

### Example 3.1: AI Engineer Agent Definition

```markdown
# .claude/agents/ai-engineer.md

---
name: AI Engineer
description: Handles ML pipelines, RAG systems, embeddings, and model training
tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
---

# AI Engineer

You are the AI Engineer agent, specializing in machine learning systems.

## Your Domains
- ML pipeline development
- RAG system implementation
- Embedding generation and management
- Model training and evaluation
- LLM integration (Google ADK, LangChain, etc.)

## Key Project Locations
- ML code: `ml/`
- Training scripts: `training/`
- Model configs: `configs/models/`
- Notebooks: `notebooks/`

## Standards You Must Follow
- Type hints on all functions
- Docstrings with Args/Returns sections
- Log experiments to W&B
- Set random seeds for reproducibility

## Memory Protocol

IMPORTANT: Before completing ANY task, you MUST:

1. **Update your memory file** at `.claude/agents/ai-engineer/memory.md`:
   |```markdown
   ## [YYYY-MM-DD] - Brief Task Summary

   **What worked**: Describe successful approaches
   **What didn't**: Describe failed attempts and why
   **Pattern**: Any reusable pattern discovered
   **Gotcha**: Any pitfall to avoid next time
   ```|

2. **Check for skill candidates**:
   - If you performed a multi-step process that could be reused, note it
   - Add to `.claude/skills/proposed/` if significant

3. **Update shared context** if your work affects other agents:
   - API changes → notify Frontend Engineer
   - New dependencies → notify DevOps Engineer

## Handoff Protocol

When receiving tasks from Solution Architect:
- Check `.claude/context/current-task/` for specs
- Clarify ambiguities BEFORE implementing
- Report blockers to orchestrator immediately

When handing off:
- Document any interface changes
- Update relevant memory files
- Ensure tests pass
```

### Example 3.2: Frontend Engineer Agent Definition

```markdown
# .claude/agents/frontend-engineer.md

---
name: Frontend Engineer
description: Handles React/TypeScript frontend development
tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
---

# Frontend Engineer

You are the Frontend Engineer agent, specializing in React/TypeScript development.

## Your Domains
- React components and hooks
- TypeScript types and interfaces
- State management (Zustand)
- API integration (react-query)
- Styling (Tailwind CSS)

## Key Project Locations
- Components: `frontend/src/components/`
- Pages: `frontend/src/pages/`
- API clients: `frontend/src/api/`
- Stores: `frontend/src/stores/`
- Types: `frontend/src/types/`

## Standards You Must Follow
- Functional components only
- Strict TypeScript (no `any`)
- Props interfaces named `{Component}Props`
- Tests for all components

## Memory Protocol

IMPORTANT: Before completing ANY task, you MUST:

1. **Update your memory file** at `.claude/agents/frontend-engineer/memory.md`

2. **Document component patterns** that could be reused

3. **Update shared context** if:
   - You need new API endpoints (notify AI Engineer or Backend)
   - You changed shared types (notify all agents)

## Coordination with Backend

- API contracts defined in `.claude/context/current-task/interfaces.md`
- If API doesn't exist yet, create mock in `frontend/src/mocks/`
- Report API mismatches immediately
```

### Example 3.3: Orchestrator Instructions (in CLAUDE.md)

The main CLAUDE.md should include how to coordinate agents:

```markdown
# .claude/CLAUDE.md (partial - agent coordination section)

## Agent Coordination

### Available Agents
- **AI Engineer**: ML, RAG, embeddings, training
- **Frontend Engineer**: React, TypeScript, UI components
- **Solution Architect**: System design, technical decisions
- **DevOps Engineer**: Infrastructure, CI/CD, deployment
- **QA Tester**: Testing, validation, quality assurance

### Delegation Protocol

When delegating to a subagent:

1. **Provide clear context**:
   - What needs to be done
   - Which files are relevant
   - Any constraints or requirements

2. **Remind about memory updates**:
   Include in delegation: "Remember to update your memory file when done."

3. **Collect results**:
   - Check that memory was updated
   - Verify shared context if cross-cutting changes

### Cross-Agent Communication

Agents communicate via:
- `.claude/context/shared-context.json` — Structured facts and decisions
- `.claude/context/current-task/` — Active task artifacts
- Agent memory files — Historical learnings

### Conflict Resolution

If agents have conflicting approaches:
1. Document both options
2. Escalate to human for decision
3. Do NOT proceed until resolved
```

### Example 3.4: Shared Context Structure

```json
// .claude/context/shared-context.json

{
  "decisions": [
    {
      "id": "dec-001",
      "date": "2025-12-20",
      "decision": "Use Pinecone for vector storage",
      "rationale": "Better performance for our scale, managed service reduces ops burden",
      "made_by": "Solution Architect",
      "affects_agents": ["AI Engineer", "DevOps Engineer"]
    }
  ],
  "active_interfaces": [
    {
      "name": "SearchAPI",
      "provider": "AI Engineer",
      "consumer": "Frontend Engineer",
      "endpoint": "POST /api/v1/search",
      "status": "implemented"
    }
  ],
  "blockers": [],
  "recent_learnings": [
    {
      "date": "2025-12-22",
      "agent": "AI Engineer",
      "learning": "Chunk overlap of 50 tokens works better than 100 for our use case",
      "reference": ".claude/agents/ai-engineer/memory.md"
    }
  ]
}
```

---

## Level 4: Hook-Enforced Rules

**Key Understanding**: Rules are suggestions. Hooks are enforcement.

**When to use Level 4:**
- Critical behaviors that must happen (memory updates, tests, linting)
- Validation before certain actions (commit, deploy)
- Forced reflection/learning at session end

### The Complementary Pattern

**Rule**: Tells Claude *what* to do and *how*
**Hook**: *Ensures* it actually happens

### Hook Types

| Hook Event | When It Fires | Use For |
|------------|---------------|---------|
| `PreToolUse` | Before Claude uses a tool | Validation, blocking, pre-checks |
| `PostToolUse` | After a tool completes | Logging, follow-up actions |
| `Stop` | When session ends | Forced reflection, cleanup |

### Example 4.1: Enforced Memory Updates

**The Rule** (what and how):

```markdown
# .claude/rules/memory-protocol.md

# Memory Update Protocol

## What to Capture

After completing significant tasks, update the relevant memory file with:

1. **Task summary**: What was accomplished
2. **What worked**: Successful approaches
3. **What didn't**: Failed attempts and lessons
4. **Patterns**: Reusable approaches discovered
5. **Gotchas**: Pitfalls to avoid

## Memory Locations

- Agent-specific: `.claude/agents/{agent-name}/memory.md`
- Shared context: `.claude/context/shared-context.json`
- Skill proposals: `.claude/skills/proposed/`

## Format

|```markdown
## [YYYY-MM-DD] - Task Title

**Summary**: Brief description of what was done

**What worked**:
- Point 1
- Point 2

**What didn't**:
- Failed approach and why

**Pattern**: Reusable pattern if any

**Gotcha**: Pitfall to remember
```|
```

**The Hook** (enforcement):

```json
// .claude/settings.json

{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python .claude/scripts/enforce-memory-update.py"
          }
        ]
      }
    ]
  }
}
```

**The Script**:

```python
#!/usr/bin/env python3
# .claude/scripts/enforce-memory-update.py

"""
Runs at session end via Stop hook.
Outputs a prompt that Claude must respond to.
"""

prompt = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MANDATORY END-OF-SESSION CHECKLIST
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Before this session ends, you MUST complete the following:

1. SUMMARIZE: What was the main task accomplished?

2. REFLECT: What new patterns or learnings emerged?

3. UPDATE MEMORY: Edit the relevant memory file NOW.
   - If you were a subagent: `.claude/agents/{your-name}/memory.md`
   - If orchestrator: `.claude/context/shared-context.json`

   Show me the actual edit you're making.

4. SKILL CHECK: Should any process become a reusable skill?
   - If yes: Create `.claude/skills/proposed/{name}/SKILL.md`
   - If no: Explain why not

You cannot end this session without completing the above.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

print(prompt)
```

### Example 4.2: Test-Gated Commits

**The Rule**:

```markdown
# .claude/rules/testing.md

---
paths: **/*.py
---

# Testing Requirements

## Coverage Requirements
- All new functions must have tests
- Test file location mirrors source: `src/api/users.py` → `tests/api/test_users.py`

## Required Test Cases
- Happy path
- Edge cases (empty input, None, boundaries)
- Error cases (invalid input, missing resources)

## Running Tests
- Quick check: `pytest tests/ -x` (stop on first failure)
- Full suite: `pytest tests/ -v`
- With coverage: `pytest tests/ --cov=src`

NOTE: Commits are blocked if tests don't pass.
```

**The Hook**:

```json
// .claude/settings.json (partial)

{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash(git commit*)",
        "hooks": [
          {
            "type": "command",
            "command": "pytest tests/ -x --tb=short || (echo '❌ Tests must pass before commit. Fix failing tests and try again.' && exit 1)"
          }
        ]
      }
    ]
  }
}
```

### Example 4.3: Lint on File Write

**The Hook** (no rule needed—purely enforcement):

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "python .claude/scripts/lint-changed-file.py"
          }
        ]
      }
    ]
  }
}
```

```python
#!/usr/bin/env python3
# .claude/scripts/lint-changed-file.py

import json
import subprocess
import sys

# Hook provides tool input via stdin
input_data = json.loads(sys.stdin.read())
file_path = input_data.get("file_path", "")

if file_path.endswith(".py"):
    result = subprocess.run(
        ["ruff", "check", file_path, "--fix"],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"⚠️  Linting issues in {file_path}:")
        print(result.stdout)
elif file_path.endswith((".ts", ".tsx")):
    subprocess.run(["npx", "prettier", "--write", file_path])
```

### Example 4.4: Skill Candidate Detection

**The Rule**:

```markdown
# .claude/rules/skill-evolution.md

# Skill Evolution

## What Makes a Skill Candidate

A repeated process should become a skill when:
- Performed 2+ times in similar contexts
- Takes 3+ steps to complete
- Would benefit future tasks

## Skill Proposal Format

Create `.claude/skills/proposed/{skill-name}/SKILL.md`:

```markdown
# {Skill Name}

## Trigger
When should this skill be invoked?

## Steps
1. Step one
2. Step two
3. ...

## Inputs
What information is needed?

## Outputs
What does this skill produce?
```
```

**The Hook**:

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python .claude/scripts/skill-candidate-prompt.py"
          }
        ]
      }
    ]
  }
}
```

```python
#!/usr/bin/env python3
# .claude/scripts/skill-candidate-prompt.py

prompt = """
SKILL CANDIDATE CHECK:

Review this session's work:
- Did you perform any multi-step process that could be reused?
- Did you solve a problem in a way that would help with similar future tasks?

If YES:
1. Create a skill proposal at `.claude/skills/proposed/{name}/SKILL.md`
2. Use the format from `.claude/rules/skill-evolution.md`

If NO:
- Briefly explain why no skill candidates emerged from this session
"""

print(prompt)
```

### Example 4.5: Combined Settings File

A complete `.claude/settings.json` with multiple hooks:

```json
{
  "permissions": {
    "allow": [
      "Bash(pytest *)",
      "Bash(ruff *)",
      "Bash(black *)",
      "Bash(make *)",
      "Bash(npm run *)",
      "Bash(git status)",
      "Bash(git diff *)",
      "Bash(git add *)",
      "Bash(git commit *)",
      "Bash(git log *)"
    ],
    "deny": [
      "Bash(rm -rf *)",
      "Bash(git push --force*)",
      "Read(.env)"
    ]
  },
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash(git commit*)",
        "hooks": [
          {
            "type": "command",
            "command": "pytest tests/ -x --tb=short || exit 1"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "python .claude/scripts/auto-lint.py"
          }
        ]
      },
      {
        "matcher": "Task",
        "hooks": [
          {
            "type": "command",
            "command": "python .claude/scripts/log-agent-completion.py"
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python .claude/scripts/enforce-memory-update.py"
          },
          {
            "type": "command",
            "command": "python .claude/scripts/skill-candidate-prompt.py"
          }
        ]
      }
    ]
  }
}
```

---

## Common Patterns

### Pattern 1: Rule Provides Instructions, Hook Enforces

```
Rule (what/how) + Hook (must happen) = Reliable behavior
```

### Pattern 2: Path-Scoped Rules with Imports

Load additional context only when relevant:

```markdown
---
paths: ml/rag/**/*.py
---

# RAG Context

Reference: @docs/architecture/rag-design.md

Additional guidelines...
```

### Pattern 3: Agent Rules in Agent Definitions

Don't try to use path-scoped rules for agents. Put agent-specific rules directly in the agent's markdown definition file.

### Pattern 4: Hierarchical Shared Context

```
.claude/context/
├── shared-context.json      # Cross-agent facts and decisions
├── current-task/            # Active task artifacts
│   ├── spec.md              # Current task specification
│   └── interfaces.md        # API contracts
└── history/                 # Past task summaries (optional)
```

---

## Anti-Patterns to Avoid

### ❌ Anti-Pattern 1: Rules Without Enforcement for Critical Behaviors

```markdown
# BAD: This is just a suggestion
IMPORTANT: Always update your memory file after tasks.
```

**Fix**: Add a Stop hook to enforce memory updates.

### ❌ Anti-Pattern 2: Path-Scoped Rules for Agents

```markdown
---
paths: .claude/agents/ai-engineer/**/*
---

# AI Engineer Rules
```

**Problem**: This only loads when files in that directory are accessed, not when the AI Engineer agent runs.

**Fix**: Put rules in the agent definition file itself.

### ❌ Anti-Pattern 3: Overly Large Rules Files

```markdown
# Everything about our project in one rule...
(500 lines of content)
```

**Fix**: Split into focused, topic-specific files.

### ❌ Anti-Pattern 4: Redundant Rule + Hook

```markdown
# .claude/rules/testing.md
Run tests before committing.
```

```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Bash(git commit*)",
      "hooks": [{
        "command": "echo 'Remember to run tests!'"
      }]
    }]
  }
}
```

**Problem**: The hook just reminds—it doesn't enforce.

**Fix**: Hook should actually run tests and block on failure:

```json
"command": "pytest -x || exit 1"
```

### ❌ Anti-Pattern 5: No Organization

```
.claude/rules/
├── rule1.md
├── rule2.md
├── stuff.md
├── more-stuff.md
```

**Fix**: Use subdirectories by domain:

```
.claude/rules/
├── backend/
├── frontend/
├── infra/
├── ml/
└── meta/
```

---

## Quick Reference

### File Locations

| Purpose | Location |
|---------|----------|
| Project context | `.claude/CLAUDE.md` |
| Universal rules | `.claude/rules/*.md` (no frontmatter) |
| Domain rules | `.claude/rules/{domain}/*.md` (with paths) |
| Agent definitions | `.claude/agents/{name}.md` |
| Agent memory | `.claude/agents/{name}/memory.md` |
| Skills | `.claude/skills/{name}/SKILL.md` |
| Hooks & settings | `.claude/settings.json` |
| Shared context | `.claude/context/shared-context.json` |

### When to Use What

| Scenario | Solution |
|----------|----------|
| Universal code style | Level 1 rule (no frontmatter) |
| FastAPI-specific patterns | Level 2 rule (paths: src/api/**) |
| Agent should update memory | Level 3 (in agent definition) + Level 4 (Stop hook) |
| Tests must pass before commit | Level 4 (PreToolUse hook) |
| Format files after editing | Level 4 (PostToolUse hook) |

---

## Next Steps

Use this reference to restructure your project. Recommended order:

1. **Audit existing setup**: What rules/instructions do you have now?
2. **Create Level 1 rules**: Universal standards
3. **Create Level 2 rules**: Domain-specific (backend, frontend, ML, infra)
4. **Update agent definitions**: Embed agent-specific rules (Level 3)
5. **Add enforcement hooks**: For critical behaviors (Level 4)
6. **Test the flow**: Run a task and verify memory updates happen
