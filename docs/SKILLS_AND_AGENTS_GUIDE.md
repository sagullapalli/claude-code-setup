# Skills, Agents, and Memory: How They Work Together

This guide explains the three-tier knowledge system in this project:
1. **Skills** - Latest technical patterns (how to build)
2. **Agents** - Role definitions and responsibilities (who does what)
3. **Memory** - Project-specific context and learnings (what we've done and learned)

---

## The Three-Tier Knowledge System

### 1. Skills (.claude/skills/)
**Purpose**: Single source of truth for technical patterns
**Content**: Latest API syntax, model names, code examples, best practices
**Update frequency**: When technology changes (new versions, deprecations)
**Example**: `google-adk-patterns.md`, `vertex-ai-models.md`

### 2. Agent Files (.claude/agents/)
**Purpose**: Define agent roles and responsibilities
**Content**: Who the agent is, what they do, when to delegate to them
**Update frequency**: When roles/responsibilities change
**Example**: `ai-engineer.md`, `solution-architect.md`

### 3. Memory Files (.claude/memory/)
**Purpose**: Project-specific context and continuous learning
**Content**: Project config, decisions made, lessons learned, pointers to detailed docs
**Update frequency**: After every session/milestone
**Example**: `memory-orchestrator.md`, `memory-solution-architect.md`

### 4. Documentation (docs/)
**Purpose**: Detailed implementation plans, ADRs, guides
**Content**: Complete specifications, step-by-step plans, full rationale
**Update frequency**: During planning and implementation phases
**Example**: `docs/current/PHASE_2_PLAN.md`, `docs/reference/ARCHITECTURE_DECISION_SUMMARY.md`

---

## The Problem We Solved

### Before This System
- ❌ Sub-agents had **outdated examples** in their markdown files (e.g., Gemini 1.5 instead of 2.0)
- ❌ Agents used **wrong patterns** (raw Vertex AI instead of Google ADK)
- ❌ Examples got **stale** as technology evolved
- ❌ Updating required editing **multiple agent files**
- ❌ Memory files became **bloated** with duplicate information from docs
- ❌ Agents loaded unnecessary context, hitting token limits

### After This System
- ✅ Skills contain **latest patterns and models** (single source of truth)
- ✅ Agents **invoke skills** to get current technical information
- ✅ Memory files are **contextualized indexes** with key rationale + pointers to docs
- ✅ Docs contain **detailed specifications** without duplication
- ✅ Efficient context management: Memory → Docs → Skills as needed
- ✅ Easy to update **one file** instead of many

---

## What Are Skills?

**Skills** are specialized knowledge modules that agents can invoke during their work.

### Skill Structure

```
.claude/skills/
├── google-adk-patterns.md     # Latest Google ADK agent patterns
├── vertex-ai-models.md         # Latest Gemini 2.0 models
├── database-design.md          # Database design patterns
├── api-design.md               # API best practices
├── testing-strategy.md         # Testing approaches
├── gcp-deployment.md           # GCP deployment patterns
├── security-best-practices.md  # Security guidelines
└── frontend-development.md     # Frontend patterns
```

### Configuration

Skills are registered in [.claude/config.json](.claude/config.json):

```json
{
  "skills": {
    "google-adk-patterns": {
      "name": "Google ADK Patterns",
      "description": "Latest Google ADK patterns and examples for building AI agents (2024-2025)",
      "file": "skills/google-adk-patterns.md"
    },
    "vertex-ai-models": {
      "name": "Vertex AI Models",
      "description": "Latest Vertex AI models including Gemini 2.0 and usage best practices",
      "file": "skills/vertex-ai-models.md"
    }
  }
}
```

---

## How Agents Use Skills

### Agent Instructions

Each agent (e.g., [AI Engineer](.claude/agents/ai-engineer.md)) has instructions to **invoke skills before implementation**:

```markdown
## ⚠️ CRITICAL: Use Skills Before Implementation

**BEFORE implementing ANY AI agent or Vertex AI integration, you MUST:**

1. **Invoke the `google-adk-patterns` skill** to get latest Google ADK examples
2. **Invoke the `vertex-ai-models` skill** to get latest Gemini 2.0 models

**How to invoke skills:**
- Skill(skill="google-adk-patterns")
- Skill(skill="vertex-ai-models")
```

### Agent Workflow

When a sub-agent receives a task:

```
1. Task assigned: "Build an AI poem generator"
   ↓
2. Agent reads instruction: "Use skills before implementation"
   ↓
3. Agent invokes: Skill(skill="google-adk-patterns")
   ↓
4. Skill loads → Agent receives latest Google ADK patterns
   ↓
5. Agent invokes: Skill(skill="vertex-ai-models")
   ↓
6. Skill loads → Agent receives latest Gemini 2.0 model names
   ↓
7. Agent implements using correct patterns and models
   ↓
8. Returns working code with:
   - ✅ Google ADK (not raw Vertex AI)
   - ✅ Gemini 2.0 Flash (not 1.5)
   - ✅ Proper tool integration
```

---

## Example: Real Collaboration with Skills

### Scenario: Build AI Poem Generator

**Main Orchestrator (you) delegates with full context:**
```
Task(
  subagent_type="AI Engineer",
  prompt="""
Kai, I need you to build an AI poem generator.

BACKGROUND CONTEXT:
The user wants a simple API endpoint that generates poems using AI. This will be
added to the existing FastAPI backend. We're using Google ADK for all agent work.

MEMORY & KNOWLEDGE:
1. Read your memory file (.claude/memory/memory-ai-engineer.md) for project setup
2. Load docs/reference/ARCHITECTURE_DECISION_SUMMARY.md for tech stack context
3. Invoke these skills:
   - google-adk-patterns: Latest Google ADK agent patterns
   - vertex-ai-models: Latest Gemini 2.0 model selection

TASK:
Create a poem generator agent:
1. Create agent using Google ADK and latest Gemini model
2. Add FastAPI endpoint POST /api/poems
3. Accept topic in request body
4. Return generated poem

DELIVERABLES:
- Working code in backend/app/agents/poem_generator.py
- API endpoint in backend/app/main.py
- Simple test showing it works

CONSTRAINTS:
- Use Google ADK (not raw Vertex AI)
- Use europe-west1 region
- Follow existing project patterns
"""
)
```

**AI Engineer agent receives task:**

1. **Sees only their instruction file automatically** (can't see conversation history)

2. **Reads memory file** (as instructed in delegation prompt):
   - Gets project context (GCP project ID, region, existing patterns)

3. **Loads docs** (as instructed):
   - Understands tech stack decisions

4. **Invokes skills** (as instructed + from agent instructions):
   ```
   Skill(skill="google-adk-patterns")
   # Receives: Latest Google ADK syntax, examples, best practices

   Skill(skill="vertex-ai-models")
   # Receives: Gemini 2.0 model names, capabilities, pricing
   ```

5. **Implements using skill knowledge:**
   ```python
   # Correct implementation (from skills)
   from google import genai

   client = genai.Client(
       vertexai=True,
       project="genai-advertisment",  # From memory file
       location="europe-west1"         # From delegation context
   )

   agent = client.agentic.Agent(
       model="gemini-2.0-flash-exp",  # From vertex-ai-models skill
       system_instruction="You are a poem generator."
   )

   response = agent.generate_content("Write a poem about AI")
   ```

6. **Updates memory file** (as requested in delegation)

7. **Returns implementation to Main Orchestrator**

---

## Benefits of This Approach

### 1. **Always Current**
- Update one skill file → all agents use latest patterns
- No stale examples in agent markdown files

### 2. **Single Source of Truth**
- Skills are the authoritative source for technical patterns
- Agents don't have conflicting examples

### 3. **Easy Maintenance**
- New Gemini model? Update `vertex-ai-models.md`
- New ADK pattern? Update `google-adk-patterns.md`
- No need to update 5 different agent files

### 4. **Enforced Best Practices**
- Agent instructions **require** skill invocation
- Can't implement without checking latest patterns
- Quality gates built into the workflow

### 5. **Scalable**
- Add new skills as needed (e.g., `terraform-patterns.md`)
- Agents can invoke multiple skills
- Cross-functional knowledge sharing

---

## Key Skills in This Project

### 1. **google-adk-patterns.md**

**Purpose:** Latest Google ADK agent development patterns

**Contents:**
- Google ADK installation and setup
- Agent creation with tools
- Function calling patterns
- FastAPI integration
- Multi-agent orchestration
- RAG patterns
- Migration from raw Vertex AI

**When to use:** Building any AI agent

### 2. **vertex-ai-models.md**

**Purpose:** Latest Vertex AI models and usage

**Contents:**
- Gemini 2.0 model names (`gemini-2.0-flash-exp`, `gemini-2.0-pro-exp`)
- Model capabilities (multimodal, context window, pricing)
- Model selection guide (which model for what use case)
- Configuration options (temperature, top-p, max tokens)
- Performance optimization
- Cost optimization

**When to use:** Choosing or using any Vertex AI model

### 3. **Other Skills**

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| `database-design.md` | Database schema patterns | Designing data models |
| `api-design.md` | RESTful API best practices | Creating API endpoints |
| `testing-strategy.md` | Test patterns (unit, E2E) | Writing tests |
| `gcp-deployment.md` | GCP deployment patterns (Cloud Run, Terraform) | Deploying to GCP |
| `security-best-practices.md` | Security guidelines | Implementing auth, validation |
| `frontend-development.md` | React/Svelte patterns | Building UIs |

---

## How to Add a New Skill

### 1. Create the Skill File

```bash
# Create new skill file
touch .claude/skills/my-new-skill.md
```

### 2. Write the Skill Content

```markdown
# My New Skill

This skill helps with [purpose].

## Usage

Use this skill when you need to:
- [Use case 1]
- [Use case 2]

## Patterns

### Pattern 1: [Name]

```[language]
[code example]
```

## Best Practices

- [Practice 1]
- [Practice 2]
```

### 3. Register in config.json

Edit `.claude/config.json`:

```json
{
  "skills": {
    "my-new-skill": {
      "name": "My New Skill",
      "description": "Short description of what this skill provides",
      "file": "skills/my-new-skill.md"
    }
  }
}
```

### 4. Update Agent Instructions (if needed)

Edit relevant agent markdown file (e.g., `.claude/agents/ai-engineer.md`):

```markdown
**BEFORE implementing [specific task], you MUST:**

1. Invoke `Skill(skill="my-new-skill")` to get latest patterns
```

---

## Testing Skills

### Test 1: Verify Skill Registration

```bash
# Skills should be listed in config
cat .claude/config.json | grep -A 3 "my-new-skill"
```

### Test 2: Agent Invocation (Simulated)

When the Main Orchestrator delegates a task, the agent should:
1. See skill invocation instructions in agent markdown
2. Invoke `Skill(skill="skill-name")`
3. Receive skill content
4. Use patterns from skill in implementation

---

## Best Practices for Skills

### 1. **Keep Skills Focused**
- One skill = one domain (e.g., Google ADK, not "all of GCP")
- Clear, specific purpose

### 2. **Use Examples Heavily**
- Code examples > long explanations
- Show good vs. bad patterns
- Include complete working examples

### 3. **Keep Current**
- Update when new versions release
- Add deprecation warnings for old patterns
- Date-stamp major updates

### 4. **Make Them Searchable**
- Clear headings
- Table of contents
- Quick reference section at bottom

### 5. **Cross-Reference**
- Link related skills
- "See also: `other-skill.md`"

---

## Skills vs. Agent Markdown Files

### Agent Files (`.claude/agents/`)
- **Who** the agent is
- **What** they're responsible for
- **When** to delegate to them
- **How** they should work (high-level)
- **Instruction** to use skills

### Skills (`.claude/skills/`)
- **Latest** technical patterns
- **Detailed** implementation examples
- **Up-to-date** model names, APIs
- **Best practices** for specific domains
- **Single source of truth** for technical knowledge

---

## Common Questions

### Q: When should an agent use a skill?
**A:** Whenever they need the **latest** patterns or **technical specifics** (model names, API syntax, etc.)

### Q: Can agents work without skills?
**A:** Yes, but they might use **outdated patterns** from their markdown file examples.

### Q: How do I ensure agents use skills?
**A:** Add **explicit instructions** in the agent markdown file (see `ai-engineer.md` for example).

### Q: Can the Main Orchestrator use skills?
**A:** Yes! The Main Orchestrator can also invoke skills to get latest information before delegating.

### Q: How often should skills be updated?
**A:** When technology changes (new model versions, new API patterns, deprecations).

---

## Memory Files: The Contextualized Index

### Philosophy

Memory files are **contextualized indexes**, not detailed documentation. They provide:

1. **High-level context** - Enough to understand what's happened and why
2. **Key rationale** - 1-2 line summaries of decisions
3. **Pointers to detailed docs** - Links to full specifications
4. **Continuous learning** - Lessons section updated after each session

**NOT** in memory files:
- ❌ Full implementation details (those go in docs/)
- ❌ Complete step-by-step guides (those go in docs/)
- ❌ Duplicate information from docs (just point to them)

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

## Lessons
- Project-specific discoveries
- Collaboration gotchas
- Performance/cost insights
- Security considerations

## Documentation Map
- Table linking topics to docs
- Brief description of what's in each doc
```

### Usage Pattern

**When agent is delegated a task:**
1. Agent receives only their instruction file automatically
2. Agent reads memory file (as instructed in delegation prompt)
3. Memory file points to relevant docs for current phase
4. Agent loads specific docs (as listed in delegation prompt)
5. Agent invokes skills (as listed in delegation + agent instructions)

**During work:**
1. Agent notes important discoveries
2. Agent prepares memory updates with new learnings

**At end of task:**
1. Agent updates memory with new context (status, decisions with brief rationale)
2. Agent adds pointers to any new docs created
3. Agent preserves lessons for future sessions (using STAR format for bugs)
4. Agent returns results to Main Orchestrator

**Critical**: Memory files are NOT automatically loaded. The Main Orchestrator must
explicitly instruct agents to read their memory file in the delegation prompt.

### Why This Works

**Efficient Context Management:**
- Memory = 1-2 pages (loads quickly, doesn't bloat context)
- Docs = 5-20 pages (loaded only when needed for implementation)
- Skills = Technical reference (loaded only when implementing)

**Prevents Duplication:**
- Memory: "We decided X because Y. Details: [link]"
- Docs: Full ADR with alternatives, trade-offs, implementation steps

**Enables Learning:**
- "Lessons" section grows over time
- Each agent builds institutional knowledge
- Future sessions benefit from past discoveries

**Example:**

**Memory (Concise)**:
```markdown
### ADR-002: GCS CloudStorageMemory (2025-11-28)
**Decision**: ADK CloudStorageMemory + regional GCS bucket
**Rationale**: Native ADK support, low cost ($0.01/mo vs Redis $30-50/mo), strong consistency
**Configuration**: Bucket `[bucket-name]` (europe-west1, REGIONAL, STANDARD, 30-day lifecycle)
**Full details**: [docs/reference/ARCHITECTURE_DECISION_SUMMARY.md](docs/reference/ARCHITECTURE_DECISION_SUMMARY.md)#ADR-002
```

**Doc (Comprehensive)**:
```markdown
### ADR-002: GCS CloudStorageMemory for Session Storage

**Context**: Need persistent session storage that scales with Cloud Run...
**Decision**: Use Google ADK's CloudStorageMemory backed by GCS regional bucket...
**Alternatives Considered**:
1. Redis Memorystore - Cost: $30-50/month, latency: 1-5ms...
2. PostgreSQL Cloud SQL - Cost: $10-20/month, wrong tool...
3. Custom backend - NIH syndrome...
**Detailed Comparison**: [table with latency, cost, complexity, scalability]
**Implementation Steps**: [15 detailed steps]
**Rollback Plan**: [4 steps]
**Monitoring**: [metrics to track]
```

---

## Summary

**The three-tier knowledge system solves:**

1. ✅ **Skills** - Centralizing technical knowledge, latest patterns
2. ✅ **Memory** - Efficient context management, continuous learning
3. ✅ **Docs** - Detailed specifications without duplication
4. ✅ **Consistency** - All agents use same patterns and understand project context

**The workflow:**
```
User Task → Main Orchestrator → Crafts delegation with full context
                                      ↓
                                Task tool invoked with subagent_type
                                      ↓
                                Agent spawned (receives instruction file only)
                                      ↓
                                Agent reads Memory (as instructed in delegation)
                                      ↓
                                Agent loads relevant Docs (as instructed in delegation)
                                      ↓
                                Agent invokes Skills (from instructions + delegation)
                                      ↓
                                Agent implements correctly with full context
                                      ↓
                                Agent updates Memory (as requested in delegation)
                                      ↓
                                Returns to Main Orchestrator
```

**Key Insight (Verified 2025-12-05):**
Agents start with a **clean slate** - they only see their instruction file automatically.
ALL other context (memory, docs, skills, background) must be explicitly provided in the
delegation prompt. This is why the Main Orchestrator role is critical: you must craft
complete delegation prompts that give agents everything they need to succeed.

**Result:**
- Agents always have **accurate context** without token bloat
- Agents use **latest patterns and models**
- Agents **learn continuously** from past sessions
- Easy to maintain: Update one file in the right tier

---

## Next Steps

1. ✅ Skills created: `google-adk-patterns.md`, `vertex-ai-models.md`, `gcp-deployment.md`
2. ✅ Skills registered in `.claude/config.json`
3. ✅ Agents updated to use skills: `ai-engineer.md`
4. ✅ Memory files restructured as contextualized indexes
5. ✅ Documentation in `docs/` for detailed specs
6. 🔄 **Maintain:** Update memories after each session, skills when tech changes, docs during planning

**Try it now:** Delegate a task to a sub-agent and watch them use Memory → Docs → Skills to complete it efficiently!
