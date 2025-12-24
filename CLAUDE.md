# Interface - Universal Project Context

## How Instruction Files Work (Read This First!)

**Claude Code automatically loads TWO instruction files for every agent:**

1. **CLAUDE.md (this file)** - Universal project context that ALL agents see
2. **Your agent-specific file** - Your unique role and responsibilities

### Agent Identity Map

**Check your agent-specific instruction file to determine who you are:**

| Nickname | Technical Role | Agent File Path | When You're Active |
|----------|---------------|-----------------|-------------------|
| **Arc** | Main Orchestrator | `.claude/agents/orchestrator.md` | Default (no agent specified in conversation) |
| **Sage** | Solution Architect | `.claude/agents/solution-architect.md` | When `subagent_type="Solution Architect"` |
| **Kai** | AI Engineer | `.claude/agents/ai-engineer.md` | When `subagent_type="AI Engineer"` |
| **Iris** | Frontend Engineer | `.claude/agents/frontend-engineer.md` | When `subagent_type="Frontend Engineer"` |
| **Devo** | DevOps Engineer | `.claude/agents/devops-engineer.md` | When `subagent_type="DevOps Engineer"` |
| **Vera** | QA Tester | `.claude/agents/qa-tester.md` | When `subagent_type="QA Tester"` |
| **Luna** | Frontend QA Specialist | `.claude/agents/frontend-qa-specialist.md` | When `subagent_type="Frontend QA Specialist"` |

**To identify yourself:**
- Your nickname and detailed instructions are in your agent-specific file
- If you don't see a nickname in your file, you are likely Arc (Main Orchestrator)

**Verified (2025-12-05)**: Both CLAUDE.md and agent-specific `.md` files load automatically when an agent is invoked.

---

## Universal Project Context (All Agents)

### Core Principles

#### Simplicity First
- Build exactly what's needed, nothing more
- Minimize code, maximize utility and readability
- Use managed services over custom solutions
- Start monolithic, scale only when necessary
- YAGNI (You Aren't Gonna Need It)

#### Technology Stack (Mandatory)
- **Backend**: Python 3.11+, FastAPI, PostgreSQL (Cloud SQL)
- **AI/Agents**: Google ADK, Vertex AI (Gemini models)
- **Cloud**: Google Cloud Platform (Cloud Run preferred)
  - **Region Preference**: Always use Europe regions (`europe-west1` or `europe-west3`)
  - All GCP resources (Cloud Run, Cloud SQL, GCS, etc.) must be in Europe
- **Frontend**: React + TypeScript (Vite, Tailwind CSS, TanStack Query)
- **Infrastructure**: Terraform, Cloud Build/GitHub Actions

See [PROJECT_GUIDELINES.md](PROJECT_GUIDELINES.md) for complete guidelines.

---

## 🚨 Mandatory Pre-Work Protocol: Skills-First Approach

**CRITICAL**: Before ANY investigation, debugging, or implementation, follow this protocol:

### Skills-First Checklist

**Step 1: Identify Technology**
- What technology/framework are we working with?
- Examples: Google ADK, FastAPI, GCS, React, PostgreSQL, Terraform

**Step 2: Check Relevant Skill File**
- Open `.claude/skills/[technology]-patterns.md`
- Common skill files:
  - `google-adk-patterns.md` - ADK agents, state, events, memory
  - `api-design.md` - FastAPI, REST patterns
  - `gcp-deployment.md` - GCS, Cloud Run, Terraform
  - `frontend-development.md` - React, Svelte, UI patterns
  - `testing-strategy.md` - pytest, E2E, state machine testing
  - `debugging-patterns.md` - Investigation approaches

**Step 3: Search for Pattern**
- Use Grep to search for relevant keywords
- Examples: "event persistence", "session reload", "state management", "authentication"

**Step 4: Execute Decision**
- ✅ **Pattern Found**: Use the documented approach (don't reinvent the wheel)
- ❌ **Not Found**: Proceed with investigation → After verification, document in skill file

### Why This Protocol Exists

**Time Investment**: 2 minutes to check skills
**Time Saved**: Hours (or days) of re-discovering known gotchas
**Quality**: Prevents repeating past mistakes

**Real Example**: Phase 2A bugs (event persistence, state reload) were documented in `google-adk-patterns.md` by end of phase. Checking skills first in Phase 2B would have prevented re-discovery.

### Enforcement

**Before ANY task**:
1. Explicitly state: "Checking skills for [technology]..."
2. Report findings: "Found pattern in [skill-file]" OR "No existing pattern, proceeding with investigation"
3. If investigating new territory: After verification, update skill file

**Only skip this protocol if**:
- Task is purely organizational (no technical implementation)
- You're 100% certain no skill file covers the technology (e.g., brand new tool)

**When in doubt**: Check anyway. 2 minutes is negligible vs. hours of re-work.

---

## Agent Memory & Continuous Learning

**CRITICAL**: All agents maintain memory files in `.claude/memory/` for persistent learning across sessions.

### Memory Philosophy: Contextualized Indexes

Memory files are **contextualized indexes**, not detailed documentation. They serve as:

1. **High-level context refresh** - Understand what's happened and why (1-2 pages max)
2. **Key rationale** - Brief summaries (1-2 lines) of decisions made
3. **Pointers to detailed docs** - Links to comprehensive specs in `docs/`
4. **Continuous learning scratchpad** - "Lessons" section updated after each session

**Three-Tier Knowledge System:**
- **Memory (.claude/memory/)**: Project-specific context + learnings (load every session)
- **Docs (docs/)**: Detailed implementation plans, ADRs, guides (load when implementing)
- **Skills (.claude/skills/)**: Latest technical patterns (invoke when implementing)

**See**: [SKILLS_AND_AGENTS_GUIDE.md](SKILLS_AND_AGENTS_GUIDE.md) for complete philosophy

### Your Memory File

**Location**: `.claude/memory/memory-[agent-name].md`
**Template**: `.claude/memory/MEMORY_TEMPLATE.md`
**Purpose**: Track project status, decisions (with brief rationale), lessons learned, and pointers to detailed docs

### Workflow

**At Start of Session:**
1. Read your memory file (high-level context refresh)
2. Memory file points to relevant docs for current work
3. Load specific docs for detailed context on task
4. Invoke skills for latest technical patterns if implementing

**During Work:**
1. Note important discoveries
2. Update "Lessons" section with new learnings
3. Track which docs are being created or updated

**At End of Session:**
1. Update memory with new context (status, decisions with brief rationale)
2. Add pointers to any new docs created
3. Ensure "Lessons" section captures new discoveries
4. Keep memory concise - detailed info stays in docs

### What to Record in Memory

**DO Record:**
- Project config (GCP project ID, regions, stack)
- Current phase and status
- Key decisions with 1-2 line rationale + link to full details in docs
- Critical file paths, commands, gotchas
- Lessons learned (project-specific discoveries)
- Pointers to all relevant docs with brief description of contents

**DON'T Record:**
- Full implementation details (those go in docs/)
- Complete step-by-step guides (those go in docs/)
- Duplicate information from docs (just point to them with brief context)
- General technical patterns (those go in skills/)

**Target Size**: 10-15k characters (2.5-3.75k tokens) per memory file

### STAR Format for Lessons

**For bugs, issues, and significant learnings**, use the STAR format for concise, actionable entries:

**Template**:
```markdown
### [Title] (Date)
**Situation**: [Context - what was the problem/scenario]
**Task**: [Goal - what needed to be accomplished]
**Action**: [Steps taken to resolve/implement]
**Result**: [Outcome and verification]
**Fix**: [File:line reference or specific change made]
**Pattern**: [Reusable lesson/gotcha for future work]
**Full details**: [Link to detailed doc in docs/ or docs/archive/]
```

**Example**:
```markdown
### Phase 2A Bug #2: Message History Empty (2025-12-03)
**Situation**: GET /sessions/{id}/messages returned 0 messages despite active conversations
**Task**: Fix chat history endpoint to show all messages
**Action**: Manually append user message + extend agent events to `runner_session.events` before save
**Result**: All 6 messages retrieved (3 user + 3 assistant), history working
**Fix**: `agent_service.py:209-215` - `events.append(user_msg)` + `events.extend(result)`
**Pattern**: ADK `run_async()` only RETURNS events, doesn't modify `session.events` (manual append required)
**Full details**: [docs/archive/handoffs/SESSION_HANDOFF_BUGFIX.md]
```

**Benefits**: 80% fewer characters, better structured, easy to scan, preserves all critical knowledge

---

## Resources

- **[PROJECT_GUIDELINES.md](PROJECT_GUIDELINES.md)** - Complete project guidelines
- **[README.md](README.md)** - Project overview and setup
- **[.claude/config.json](.claude/config.json)** - Agent and skill configuration
- **[.claude/memory/](.claude/memory/)** - Agent memory scratchpads (read/update each session)
- **Skills**: Reference `.claude/skills/` for best practices on specific topics
