# Hands-On Tutorial: Building a Feature with Multi-Agent Orchestration

> **Time**: ~30 minutes | **Level**: Beginner-friendly | **Goal**: Understand how agents work together

This tutorial walks you through building a real feature using the multi-agent system. You'll see how Ezio orchestrates work, how agents communicate, and how you can customize the setup.

---

## Table of Contents

1. [Before You Start](#before-you-start)
2. [Tutorial 1: Your First Task](#tutorial-1-your-first-task)
3. [Tutorial 2: Adding a Custom Agent](#tutorial-2-adding-a-custom-agent)
4. [Tutorial 3: Creating a Skill](#tutorial-3-creating-a-skill)
5. [What's Happening Behind the Scenes](#whats-happening-behind-the-scenes)
6. [Common Customizations](#common-customizations)

---

## Before You Start

### Prerequisites
- Claude Code CLI installed
- This repository cloned locally
- Basic familiarity with the command line

### Quick Orientation

When you open Claude Code in this project:

```
You (human)
    ↓
Ezio (orchestrator) ← CLAUDE.md + rules loaded automatically
    ↓
Delegates to specialists → Each has own context + instructions
    ↓
Results synthesized and returned to you
```

**Key concept**: You talk to Ezio. Ezio talks to specialists. You don't need to know which agent does what—just describe what you want.

---

## Tutorial 1: Your First Task

### Goal
Add a simple health check endpoint to the API.

### Step 1: Start Claude Code

```bash
cd /path/to/claude-interface
claude
```

### Step 2: Describe Your Task

Just type naturally:

```
Add a health check endpoint at /health that returns {"status": "ok"}
```

### Step 3: Watch the Orchestration

Ezio will:

1. **Plan** using TodoWrite:
   ```
   □ Research existing API structure
   □ Implement health check endpoint
   □ Add tests for the endpoint
   ```

2. **Delegate to Scout** for research:
   ```
   Scout explores the codebase...
   Returns: "API routes in backend/routers/, uses FastAPI patterns..."
   ```

3. **Delegate to Kai** for implementation:
   ```
   Kai creates the endpoint...
   Returns: "Added backend/routers/health.py, registered in main.py:34"
   ```

4. **Report back** to you:
   ```
   ✓ Health check endpoint added at /health
   Files changed:
   - backend/routers/health.py (new)
   - backend/main.py:34 (router registration)
   ```

### What You Learned

- You describe WHAT you want, not HOW to do it
- Ezio plans and coordinates automatically
- Specialists have domain expertise
- Results come back as compressed summaries

---

## Tutorial 2: Adding a Custom Agent

### Goal
Create a "Documentation Writer" agent that specializes in writing docs.

### Step 1: Copy the Template

```bash
cp .claude/templates/agent-template.md .claude/agents/doc-writer.md
```

### Step 2: Customize the Agent

Edit `.claude/agents/doc-writer.md`:

```markdown
---
name: Documentation Writer
description: Technical documentation, API docs, user guides
tags: [docs, documentation, readme, api-docs, guides]
---

# Docu - Documentation Writer

## Identity

You are Docu, the Documentation Writer for the Interface project.

**Your nickname**: Docu
**Your role**: Create clear, user-friendly documentation

## Responsibilities

- Write API documentation
- Create user guides and tutorials
- Maintain README files
- Document architectural decisions

## What You Do

### Core Tasks
- **API Docs**: Document endpoints, parameters, responses
- **User Guides**: Step-by-step tutorials for features
- **Technical Docs**: Architecture, design decisions

### You Should NOT
- Write code (delegate to specialists)
- Make architectural decisions (that's Sage's job)

## Protocols

### Writing Style
- Use plain language, avoid jargon
- Include examples for every concept
- Structure with clear headings
- Target audience: developers with varying experience

### Before Writing
1. Read existing docs to match style
2. Understand the feature fully (ask Scout if needed)
3. Check if similar docs exist

## Quality Standards

- Every API endpoint has request/response examples
- Complex concepts include diagrams or visual aids
- Docs are tested by following them yourself
```

### Step 3: Add to CLAUDE.md

Open `CLAUDE.md` and add to the Agent Identity Map:

```markdown
| **Docu** | Documentation Writer | `.claude/agents/doc-writer.md` |
```

### Step 4: Create Memory File

```bash
cp .claude/templates/memory-template.md .claude/memory/memory-doc-writer.md
```

Edit it with initial context:

```markdown
# Docu Memory

> Last updated: 2025-12-27

## Current Status

New agent - no prior context.

## Project Context

### Documentation Standards
- API docs use OpenAPI/Swagger format
- User guides in `docs/` directory
- README follows project conventions

## Quick References

### Existing Docs
- `docs/ONBOARDING.md`: User onboarding guide
- `docs/SKILLS_AND_AGENTS_GUIDE.md`: Knowledge system docs
```

### Step 5: Test Your Agent

Start a new Claude Code session:

```
Write API documentation for the health check endpoint
```

Ezio should now recognize Docu as an option and may delegate documentation tasks to them.

### What You Learned

- Agents are defined in `.claude/agents/`
- Each agent needs: YAML frontmatter, identity, responsibilities, protocols
- Memory files persist agent knowledge across sessions
- Agents are discovered by tags and description

---

## Tutorial 3: Creating a Skill

### Goal
Create a skill for "API Error Handling" patterns.

### Step 1: Choose Skill Level

| Level | When to Use |
|-------|-------------|
| Simple (single file) | One pattern, <100 lines |
| Complex (directory) | Multiple related patterns |

For this tutorial, we'll create a simple skill.

### Step 2: Create the Skill File

```bash
touch .claude/skills/api-error-handling.md
```

### Step 3: Write the Skill

Edit `.claude/skills/api-error-handling.md`:

```markdown
---
name: API Error Handling
description: Patterns for consistent error responses in FastAPI
tags: [error, exception, api, fastapi, http, response]
last_verified: 2025-12-27
---

# API Error Handling Patterns

## Overview

Consistent error handling patterns for FastAPI applications. Use these patterns when building API endpoints that need to return meaningful error responses.

## When to Use

- Building new API endpoints
- Refactoring error handling in existing endpoints
- Need consistent error response format

## Core Pattern: Exception Handlers

### Problem
Inconsistent error responses across endpoints make debugging difficult.

### Solution

```python
# backend/exceptions.py
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

class AppException(Exception):
    """Base exception for application errors"""
    def __init__(self, message: str, code: str, status_code: int = 400):
        self.message = message
        self.code = code
        self.status_code = status_code

# Exception handler
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message
            }
        }
    )

# Register in main.py
app.add_exception_handler(AppException, app_exception_handler)
```

### Usage in Endpoints

```python
from backend.exceptions import AppException

@router.get("/users/{user_id}")
async def get_user(user_id: int):
    user = await user_service.get(user_id)
    if not user:
        raise AppException(
            message=f"User {user_id} not found",
            code="USER_NOT_FOUND",
            status_code=404
        )
    return user
```

## Standard Error Codes

| Code | Status | When to Use |
|------|--------|-------------|
| `NOT_FOUND` | 404 | Resource doesn't exist |
| `VALIDATION_ERROR` | 422 | Invalid input data |
| `UNAUTHORIZED` | 401 | Missing or invalid auth |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `INTERNAL_ERROR` | 500 | Unexpected server error |

## Common Gotchas

- **Don't expose stack traces**: Never include internal error details in responses
- **Use specific codes**: `USER_NOT_FOUND` is better than generic `NOT_FOUND`
- **Log before responding**: Always log errors server-side before returning response

## Related Skills

- `api-design.md`: Overall API design patterns
- `testing-strategy/integration-testing.md`: Testing error responses
```

### Step 4: Test Skill Discovery

Start a new Claude Code session and mention the keywords:

```
I need to add error handling to the user endpoints
```

Claude should discover and apply patterns from your new skill.

### What You Learned

- Skills are discovered by tags and keywords
- Frontmatter (name, description, tags) enables discovery
- Skills contain patterns, not just documentation
- Include code examples that can be directly used

---

## What's Happening Behind the Scenes

### File Loading Order

```
Session Start
    ↓
1. CLAUDE.md loaded (universal context)
    ↓
2. .claude/rules/*.md loaded (mandatory protocols)
    ↓
3. Agent file loaded (if delegated to)
    ↓
4. Skills discovered by keywords (on-demand)
    ↓
5. Memory file read by agent
```

### Agent Delegation Flow

```
You: "Add user authentication"
         ↓
    ┌────────────────────────────────────────┐
    │            Ezio (Orchestrator)          │
    │  - Plans tasks with TodoWrite           │
    │  - Decides which agents to engage       │
    │  - Synthesizes results                  │
    └────────────────────────────────────────┘
         │
         │ 1. Research needed
         ↓
    ┌────────────────────────────────────────┐
    │            Scout (Research)             │
    │  - Explores codebase                    │
    │  - Returns compressed findings          │
    └────────────────────────────────────────┘
         │
         │ 2. Implementation
         ↓
    ┌────────────────────────────────────────┐
    │            Kai (AI Engineer)            │
    │  - Writes backend code                  │
    │  - Returns file:line references         │
    └────────────────────────────────────────┘
         │
         │ 3. Frontend (if needed)
         ↓
    ┌────────────────────────────────────────┐
    │            Iris (Frontend)              │
    │  - Builds UI components                 │
    │  - Returns compressed summary           │
    └────────────────────────────────────────┘
         │
         ↓
    Results synthesized → Reported to you
```

### Why Sequential Delegation?

Agents are delegated **one at a time** (not in parallel) because:

1. **Quality control**: Review results before next step
2. **Context flow**: Later agents build on earlier findings
3. **Error recovery**: Catch issues early, adjust plan

### Compression in Action

**Without compression** (bad):
```
Here's what I found in the codebase. Let me show you the full contents
of auth_service.py which is 500 lines...
[dumps entire file]
```

**With compression** (good):
```
## Summary
Auth uses JWT with 15-minute expiry, refresh tokens in Redis.

## Key Files
- `auth_service.py:45-67`: Token generation
- `auth_middleware.py:23-40`: Validation
- `auth_config.py:12`: Expiry settings

## Recommendation
Kai should extend token generation for the new requirement.
```

---

## Common Customizations

### Change Agent Behavior

Edit the agent file in `.claude/agents/`:

```markdown
## Protocols

### Your Custom Protocol
[Add your specific instructions here]
```

### Add Domain-Specific Skills

Create skills for your tech stack:

```bash
# For a Django project
touch .claude/skills/django-patterns.md

# For AWS instead of GCP
touch .claude/skills/aws-deployment.md
```

### Modify Rules

Edit or add rules in `.claude/rules/`:

```markdown
# my-custom-rule.md (Mandatory)

**Purpose**: [Why this rule matters for your project]

## Requirements
1. [Your custom requirement]
```

### Adjust Hook Automation

Edit `.claude/settings.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "your-custom-script.sh"
          }
        ]
      }
    ]
  }
}
```

---

## Next Steps

1. **Try it**: Run through Tutorial 1 with a real task
2. **Customize**: Add an agent or skill for your specific needs
3. **Explore**: Read agent files to understand their personalities
4. **Experiment**: Modify a rule and see how behavior changes

### Quick Reference

| I want to... | Create/Edit... |
|--------------|----------------|
| Add a specialist | `.claude/agents/new-agent.md` |
| Add technical patterns | `.claude/skills/new-skill.md` |
| Enforce a behavior | `.claude/rules/new-rule.md` |
| Persist agent knowledge | `.claude/memory/memory-agent.md` |
| Automate tasks | `.claude/settings.json` hooks |

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Agent not being used | Check tags in frontmatter; mention relevant keywords |
| Skill not discovered | Verify tags match keywords you're using |
| Rule not applying | Ensure file is in `.claude/rules/` with `.md` extension |
| Memory not persisting | Agent must read/write memory file explicitly |

For more details, see [ONBOARDING.md](ONBOARDING.md).
