# Pre-Work Protocol (Mandatory)

**CRITICAL**: Before ANY investigation, debugging, or implementation, follow this protocol.

## Skills-First Checklist

### Step 1: Identify Technology
- What technology/framework are we working with?
- Examples: Google ADK, FastAPI, GCS, React, PostgreSQL, Terraform

### Step 2: Check Relevant Skill
- Search `.claude/skills/` for matching patterns
- Common skills:
  - `google-adk-patterns/` - ADK agents, state, events, memory
  - `api-design.md` - FastAPI, REST patterns
  - `gcp-deployment/` - GCS, Cloud Run, Terraform
  - `frontend-patterns/` - React, UI patterns
  - `testing-strategy/` - pytest, E2E testing

### Step 3: Search for Pattern
- Use Grep to search for relevant keywords in skills
- Examples: "event persistence", "session reload", "state management"

### Step 4: Execute Decision
- **Pattern Found**: Use the documented approach (don't reinvent)
- **Not Found**: Proceed with investigation -> Document findings in skill file after

## Enforcement

**Before ANY task**, explicitly state:
1. "Checking skills for [technology]..."
2. "Found pattern in [skill-file]" OR "No existing pattern, proceeding with investigation"

**After investigating new territory**: Update the relevant skill file

## Skip Only If
- Task is purely organizational (no technical implementation)
- You're 100% certain no skill file covers the technology

**When in doubt**: Check anyway. 2 minutes is negligible vs. hours of re-work.
