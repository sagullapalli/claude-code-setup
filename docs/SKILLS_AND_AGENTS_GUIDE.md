# Skills, Agents, and Memory: How They Work Together

This guide explains the knowledge system in this project and how it aligns with Claude Code best practices.

---

## Table of Contents

1. [The Three-Tier Knowledge System](#the-three-tier-knowledge-system)
2. [Two-System Architecture](#two-system-architecture)
3. [Mandatory Rules](#mandatory-rules)
4. [What Are Skills?](#what-are-skills)
5. [Skill Complexity Levels](#skill-complexity-levels)
6. [Path-Scoped Rules](#path-scoped-rules)
7. [How Agents Use Skills](#how-agents-use-skills)
8. [Memory Files](#memory-files)
9. [Hook Enforcement](#hook-enforcement)
10. [How to Add a New Skill](#how-to-add-a-new-skill)
11. [How to Add a New Rule](#how-to-add-a-new-rule)
12. [Summary](#summary)

---

## The Three-Tier Knowledge System

### 1. Skills (.claude/skills/)
**Purpose**: Single source of truth for technical patterns
**Content**: Latest API syntax, model names, code examples, best practices
**Update frequency**: When technology changes (new versions, deprecations)
**Example**: `google-adk-patterns/SKILL.md`, `testing-strategy/SKILL.md`

### 2. Agent Files (.claude/agents/)
**Purpose**: Define agent roles and responsibilities
**Content**: Who the agent is, what they do, when to delegate to them
**Update frequency**: When roles/responsibilities change
**Example**: `ai-engineer.md`, `solution-architect.md`, `general-worker.md`

**Note**: The General Worker (Scout) is a versatile agent for research, exploration, and routine tasks. Scout gathers context and returns compressed summaries to help Ezio (Main Orchestrator) make informed decisions.

### 3. Memory Files (.claude/memory/)
**Purpose**: Project-specific context and continuous learning
**Content**: Project config, decisions made, lessons learned, pointers to detailed docs
**Update frequency**: After every session/milestone
**Example**: `memory-orchestrator.md`, `memory-ai-engineer.md`, `memory-general-worker.md`

### 4. Documentation (docs/)
**Purpose**: Detailed implementation plans, ADRs, guides
**Content**: Complete specifications, step-by-step plans, full rationale
**Update frequency**: During planning and implementation phases
**Example**: `docs/current/PHASE_2_PLAN.md`, `docs/reference/ARCHITECTURE_DECISION_SUMMARY.md`

---

## Two-System Architecture

The project uses a two-system orchestrator-worker pattern:

### System 1: Planning & Coordination (Ezio)
- Main Orchestrator who plans and delegates
- NEVER executes directly (no file reads, no code writing)
- Receives compressed summaries from agents
- Makes strategic decisions

### System 2: Execution (Agents)
| Agent | Nickname | Role |
|-------|----------|------|
| General Worker | Scout | Research, exploration, file ops, routine tasks |
| Solution Architect | Sage | Architecture, design decisions |
| AI Engineer | Kai | Backend, AI agents, APIs |
| Frontend Engineer | Iris | UI, React, accessibility |
| DevOps Engineer | Devo | Infrastructure, deployment |
| QA Tester | Vera | Testing strategy, automation |
| Frontend QA Specialist | Luna | Frontend tests, a11y |

### The Flow
1. User request → Ezio plans with TodoWrite
2. Ezio delegates to Scout for research/context
3. Scout returns compressed findings
4. Ezio delegates to specialists for implementation
5. Specialists return compressed summaries
6. Ezio synthesizes and reports to user

**Key Principle**: Scout handles exploration so Ezio's context stays clear for strategic thinking.

---

## Mandatory Rules

Rules in `.claude/rules/` auto-load and enforce project standards.

### Current Rules

| Rule | Purpose | Loading |
|------|---------|---------|
| `agent-delegation.md` | Delegation protocol for Ezio | Always |
| `compression-protocol.md` | Response format for all agents | Always |
| `memory-protocol.md` | Memory file standards | Always |
| `orchestrator-protocol.md` | Ezio's mandatory workflow | Always |
| `pre-work-protocol.md` | Skills-first checklist | Always |
| `quality-gates.md` | Code quality standards | Path-scoped* |

*Path-scoped: Loads when accessing `backend/**/*.py`, `frontend/**/*.tsx`, `**/*.tf`

### Rules vs Skills

| Aspect | Rules | Skills |
|--------|-------|--------|
| Purpose | "You MUST do X" | "Here's HOW to do X" |
| Loading | Auto (always or path-scoped) | Auto (by context) |
| Content | Standards, mandates | Templates, examples |

---

## What Are Skills?

**Skills** are modular capabilities that extend Claude's functionality. They're **auto-invoked** based on context - Claude discovers and uses them automatically based on their description.

### Skill Structure

Skills are **directories** with a `SKILL.md` entry point:

```
.claude/skills/
└── skill-name/
    ├── SKILL.md              # Required entry point with frontmatter
    ├── REFERENCE.md          # Optional detailed documentation
    ├── EXAMPLES.md           # Optional examples
    └── scripts/              # Optional automation scripts
        └── validate.py
```

### Skill Frontmatter

Every `SKILL.md` requires frontmatter for discovery:

```yaml
---
name: google-adk-patterns
description: Build AI agents with Google ADK. Use when creating agents,
             debugging persistence, or integrating with Vertex AI.
allowed-tools: Read, Grep, Glob  # Optional - restricts tool access
---
```

**Critical**: The `description` field is how Claude decides when to use this skill. Make it specific with trigger keywords like "Use when...", "For...", or mention specific technologies.

### Skill Discovery

Skills are **auto-discovered** based on:
1. **Location**: `.claude/skills/skill-name/` (project) or `~/.claude/skills/skill-name/` (personal)
2. **Frontmatter**: The `description` field determines when Claude activates the skill

**No registration in config.json required** - just place the skill directory with proper frontmatter.

### Current Skills in This Project

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| `google-adk-patterns/` | Google ADK agent patterns | Building AI agents |
| `testing-strategy/` | Test patterns (unit, E2E) | Writing tests |
| `deployment/` | GCP deployment (Cloud Run, Terraform) | Deploying to GCP |
| `frontend-patterns/` | React/TypeScript patterns | Building UIs |
| `api-design.md` | RESTful API best practices | Creating API endpoints |
| `database-design.md` | Database schema patterns | Designing data models |
| `security-best-practices.md` | Security guidelines | Implementing auth, validation |

---

## Skill Complexity Levels

Skills exist on a spectrum of complexity. Choose the right level based on your needs:

| Level | Structure | Use When |
|-------|-----------|----------|
| **1** | Single SKILL.md | Quick references, templates, patterns (<200 lines) |
| **2** | SKILL.md + multiple .md files | Complex domains, progressive disclosure |
| **3** | Level 2 + scripts/ | Workflows needing validation/automation |
| **4** | Level 3 + hooks | Self-evolving, learning systems |

### Level 1 Example: API Design

```
.claude/skills/api-design/
└── SKILL.md    # ~200 lines, quick reference
```

Best for: Templates, quick patterns, checklists

### Level 2 Example: Google ADK Patterns

```
.claude/skills/google-adk-patterns/
├── SKILL.md                    # Entry point with navigation
├── 01-agent-setup.md           # Detailed topic
├── 02-event-persistence.md     # Detailed topic
├── 03-state-management.md
└── ...
```

Best for: Complex domains where you need progressive disclosure to save tokens

### Level 3 Example: Database Migration

```
.claude/skills/database-migration/
├── SKILL.md
├── ROLLBACK.md
└── scripts/
    ├── validate_migration.py    # Pre-action validation
    └── check_breaking_changes.py
```

Best for: Workflows that need validation before execution

### Level 4 Example: Skill Evolution System

```
.claude/skills/skill-evolution/
├── SKILL.md
├── PATTERNS.md              # Detected patterns
├── ANTI_PATTERNS.md         # Things that don't work
├── scripts/
│   ├── detect_patterns.py   # Pattern detection
│   └── promote_pattern.py   # Promotion logic
└── (hooks in settings.json)
```

Best for: Systems that should improve over time based on experience

---

## Path-Scoped Rules

Rules are **modular, topic-specific instructions** in `.claude/rules/` that load automatically when Claude works on matching files.

### Rules vs Skills

| Feature | Rules | Skills |
|---------|-------|--------|
| **Loading** | Auto (on file access) | Auto (by description match) |
| **Purpose** | Guidelines, standards, conventions | Technical patterns, examples, code |
| **Enforcement** | Suggestions (use hooks to enforce) | Reference material |
| **Trigger** | File path pattern (`paths:` frontmatter) | Context/description match |

### Rule Structure

```
.claude/rules/
├── code-style.md           # No frontmatter = always loaded
├── git-workflow.md         # No frontmatter = always loaded
├── backend/
│   ├── fastapi.md          # paths: backend/**/*.py
│   └── adk-agents.md       # paths: **/agents/**/*.py
├── frontend/
│   └── react.md            # paths: frontend/**/*.tsx
└── infra/
    └── terraform.md        # paths: **/*.tf
```

### Path-Scoped Rule Example

```markdown
---
paths: backend/**/*.py, src/api/**/*.py, app/routers/**/*.py
---

# FastAPI Development Rules

## Endpoint Structure
- All endpoints must have Pydantic models for request/response
- Use appropriate HTTP status codes (200, 201, 204, 400, 404, 422)
- Include error handling with proper logging
- Document endpoints with docstrings

## Naming Conventions
- Router files: `{resource}.py`
- Schema files: `{resource}.py` in schemas/
- Use snake_case for endpoints
```

### Rule Loading Behavior

| Rule Type | When Loaded | Trigger |
|-----------|-------------|---------|
| **No frontmatter** | Session start | Always loaded with CLAUDE.md |
| **With `paths:` frontmatter** | On file access | When Claude reads/edits matching files |

---

## How Agents Use Skills

### Skill Auto-Discovery

Skills are **automatically discovered** by Claude based on:
1. The task context (what files are being worked on)
2. The skill's `description` field (keywords that match the task)

**No explicit invocation syntax needed** - Claude reads the skill content when relevant.

### Agent Workflow

When a sub-agent receives a task:

```
1. Task assigned: "Build an AI poem generator"
   ↓
2. Agent reads their instruction file (auto-loaded)
   ↓
3. Agent reads memory file (as instructed in delegation prompt)
   ↓
4. Claude discovers relevant skills based on task context
   ↓
5. Agent implements using skill patterns
   ↓
6. Agent updates memory file
   ↓
7. Returns working code to Main Orchestrator
```

### Example: Delegation with Skills

**Main Orchestrator delegates:**
```
Task(
  subagent_type="AI Engineer",
  prompt="""
Kai, I need you to build an AI poem generator.

BACKGROUND CONTEXT:
The user wants a simple API endpoint that generates poems using AI.

MEMORY & KNOWLEDGE:
1. Read your memory file (.claude/memory/memory-ai-engineer.md)
2. The google-adk-patterns skill contains the latest ADK patterns
3. Use europe-west1 region (from project config)

TASK:
Create a poem generator agent with FastAPI endpoint POST /api/poems

CONSTRAINTS:
- Use Google ADK (not raw Vertex AI)
- Follow existing project patterns
"""
)
```

**AI Engineer receives task and:**
1. Reads memory file (gets project context)
2. Claude auto-discovers `google-adk-patterns` skill (based on "ADK" in context)
3. Implements using patterns from skill
4. Updates memory with learnings

---

## Memory Files

### Philosophy

Memory files are **contextualized indexes**, not detailed documentation. They provide:

1. **High-level context** - Enough to understand what's happened and why
2. **Key rationale** - 1-2 line summaries of decisions
3. **Pointers to detailed docs** - Links to full specifications
4. **Continuous learning** - Lessons section updated after each session

**NOT in memory files:**
- Full implementation details (those go in docs/)
- Complete step-by-step guides (those go in docs/)
- Duplicate information from docs (just point to them)

### Memory File Structure

```markdown
# Agent Name - Role

Last updated: YYYY-MM-DD

## Project Config
- Quick reference facts (project ID, region, stack)

## Current Status
- What phase we're in
- What's complete, what's pending
- Pointer to detailed docs for each phase

## Key Decisions (for architects)
- Decision: [1-line what]
- Rationale: [1-2 lines why]
- Full details: [link to doc]

## Critical Files & Commands (for engineers)
- Commands that are used frequently
- File paths that are important
- Gotchas to remember

## Lessons (Use STAR Format)
### [Bug/Issue Title] (Date)
**Situation**: [Context]
**Task**: [Goal]
**Action**: [Steps taken]
**Result**: [Outcome]
**Fix**: [File:line reference]
**Pattern**: [Reusable lesson]

## Documentation Map
- Table linking topics to docs
```

### Why This Works

**Efficient Context Management:**
- Memory = 1-2 pages (loads quickly, doesn't bloat context)
- Docs = 5-20 pages (loaded only when needed for implementation)
- Skills = Technical reference (loaded only when implementing)

**Prevents Duplication:**
- Memory: "We decided X because Y. Details: [link]"
- Docs: Full ADR with alternatives, trade-offs, implementation steps

---

## Hook Enforcement

Rules are **suggestions** Claude may skip. For critical behaviors, use hooks.

### Available Hook Events

| Event | When It Fires | Use For |
|-------|---------------|---------|
| `PreToolUse` | Before any tool runs | Validation, blocking, pre-checks |
| `PostToolUse` | After tool execution | Auto-format, logging, follow-up |
| `Stop` | When session ends | Forced reflection, cleanup |
| `SubagentStop` | When subagent finishes | Agent-specific reflection |
| `SessionStart` | Session initialization | Environment setup |
| `SessionEnd` | Session termination | Analytics, cleanup |

### Example: Enforced Memory Updates

**.claude/settings.json:**
```json
{
  "hooks": {
    "SubagentStop": [{
      "hooks": [{
        "type": "command",
        "command": "python3 .claude/hooks/agent_reflection.py"
      }]
    }]
  }
}
```

**agent_reflection.py** outputs a prompt forcing the agent to update their memory file before the session ends.

### Pattern: Rule + Hook = Guaranteed Behavior

| Behavior | Rule (what/how) | Hook (must happen) |
|----------|-----------------|-------------------|
| Memory updates | memory-protocol.md | SubagentStop hook |
| Tests before commit | testing.md | PreToolUse(git commit) |
| Linting on save | code-style.md | PostToolUse(Write\|Edit) |

---

## How to Add a New Skill

### 1. Create Skill Directory

```bash
mkdir -p .claude/skills/my-new-skill
```

### 2. Create SKILL.md with Frontmatter

```markdown
---
name: my-new-skill
description: Short description. Use when [trigger conditions].
---

# My New Skill

## When to Use
- Condition 1
- Condition 2

## Quick Reference
[Main content - patterns, templates, examples]

## Checklist
- [ ] Step 1
- [ ] Step 2
```

### 3. Test Discovery

Ask Claude: "What skills do you have for [topic]?"
Claude should mention your new skill based on the description.

### 4. Upgrade to Level 2+ (If Needed)

If SKILL.md exceeds 200 lines, split into multiple files:

```
.claude/skills/my-new-skill/
├── SKILL.md              # Navigation + quick start
├── TOPIC_A.md            # Detailed reference
└── TOPIC_B.md            # Detailed reference
```

### Best Practices

1. **Keep skills focused** - One skill = one domain
2. **Use examples heavily** - Code examples > long explanations
3. **Keep current** - Update when new versions release
4. **Make descriptions specific** - Include trigger keywords
5. **Cross-reference** - Link related skills

---

## How to Add a New Rule

### 1. Choose Rule Type

- **Universal rule** (no frontmatter): Always loaded
- **Path-scoped rule** (with `paths:` frontmatter): Loaded when files match

### 2. Create Rule File

**Universal rule** (`.claude/rules/code-style.md`):
```markdown
# Code Style

- Use 2-space indentation
- TypeScript strict mode
- No `any` types
```

**Path-scoped rule** (`.claude/rules/backend/fastapi.md`):
```markdown
---
paths: backend/**/*.py, src/api/**/*.py
---

# FastAPI Rules

- All endpoints must have Pydantic models
- Use appropriate HTTP status codes
```

### 3. Organize by Domain

```
.claude/rules/
├── code-style.md           # Universal
├── git-workflow.md         # Universal
├── backend/                # Domain-specific
├── frontend/
└── infra/
```

---

## Summary

**The three-tier knowledge system solves:**

1. **Skills** - Centralizing technical knowledge, latest patterns (auto-discovered)
2. **Rules** - Domain-specific guidelines (auto-loaded by path)
3. **Memory** - Efficient context management, continuous learning
4. **Docs** - Detailed specifications without duplication
5. **Hooks** - Guaranteed enforcement of critical behaviors

**The workflow:**
```
User Task → Main Orchestrator → Crafts delegation with full context
                                      ↓
                                Task tool invoked with subagent_type
                                      ↓
                                Agent spawned (receives instruction file)
                                      ↓
                                Agent reads Memory (as instructed)
                                      ↓
                                Claude discovers relevant Skills (auto)
                                      ↓
                                Rules load when accessing matching files
                                      ↓
                                Agent implements correctly with full context
                                      ↓
                                Agent updates Memory (enforced by hooks)
                                      ↓
                                Returns to Main Orchestrator
```

**Key Insight:**
Agents start with a **clean slate** - they only see their instruction file automatically.
ALL other context (memory, docs, background) must be explicitly provided in the delegation prompt. Skills and rules are auto-discovered based on context and file paths.

**Result:**
- Agents always have **accurate context** without token bloat
- Skills provide **latest patterns** (auto-discovered)
- Rules enforce **domain standards** (auto-loaded)
- Hooks **guarantee** critical behaviors
- Easy to maintain: Update one file in the right tier
