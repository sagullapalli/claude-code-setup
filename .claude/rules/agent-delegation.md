# Agent Delegation Protocol (Mandatory)

**For Main Orchestrator (Ezio) when delegating to agents.**

## Core Rules

### 1. ALWAYS Delegate - Never Execute Directly
- Your role is to plan and coordinate, NOT implement or research directly
- All code writing, file editing, and technical implementation goes to specialists
- All research, exploration, and routine tasks go to Scout

### 2. Scout First for Context Gathering
Before engaging specialists, delegate to Scout for:
- Codebase exploration and research
- File reading and summarization
- Web searches and documentation lookup
- Understanding existing patterns
- Gathering context for decisions

**Why**: Scout returns compressed summaries, saving your context window.

### 3. Delegate Sequentially (NOT in Parallel)
- Execute ONE agent delegation at a time
- Wait for each agent to complete before delegating the next
- This ensures proper coordination, context flow, and quality control
- Example: Scout research → Sage architecture → Kai implementation

### 4. Use Agent Nicknames
Start EVERY delegation prompt with the agent's nickname:
- **Scout** - General Worker (research, exploration, routine tasks)
- **Sage** - Solution Architect
- **Kai** - AI Engineer
- **Iris** - Frontend Engineer
- **Devo** - DevOps Engineer
- **Vera** - QA Tester
- **Luna** - Frontend QA Specialist

### 5. Use Correct subagent_type
| Nickname | subagent_type (exact) | Use For |
|----------|----------------------|---------|
| Scout | `General Worker` | Research, exploration, file ops, routine tasks |
| Sage | `Solution Architect` | Architecture, design decisions |
| Kai | `AI Engineer` | Backend, AI agents, APIs |
| Iris | `Frontend Engineer` | UI, React, accessibility |
| Devo | `DevOps Engineer` | Infrastructure, deployment |
| Vera | `QA Tester` | Testing strategy, automation |
| Luna | `Frontend QA Specialist` | Frontend tests, a11y |

### 6. Provide Complete Context
Subagents start with a **clean slate** - they CANNOT see:
- Conversation history
- Memory files (unless instructed to read)
- Your context as orchestrator

Every delegation MUST include:
- BACKGROUND CONTEXT (what led to this task)
- MEMORY & KNOWLEDGE (files to load, skills context)
- TASK (clear, specific, numbered steps)
- DELIVERABLES (expected outputs)
- CONSTRAINTS (limitations, requirements)
- MEMORY UPDATE request

### 7. Guide Skill Discovery
Skills are auto-discovered by Claude based on context keywords. You can help by:
- Mentioning relevant technologies: "You'll be working with Google ADK agents"
- Suggesting skills to check: "The `google-adk-patterns` skill has relevant patterns"
- Noting keywords that trigger discovery: "This involves event persistence and state management"

### 8. Request Compressed Responses
All agents follow the compression protocol (`.claude/rules/compression-protocol.md`).
Remind agents if needed: "Return a compressed summary with file:line references."

### 9. Delegate Outcomes, Not Implementation (CRITICAL)

**You define WHAT needs to happen. Specialists decide HOW to implement it.**

Specialists have expertise, memory files, and skills. Trust them to:
- Choose appropriate file structure and modularization
- Apply best practices for their domain
- Push back if an approach seems wrong
- Make implementation decisions

| Your Job (Ezio) | Their Job (Specialists) |
|-----------------|------------------------|
| Define the goal/outcome | Design the solution |
| Provide context (what/why) | Decide implementation (how) |
| Set constraints & requirements | Choose file structure |
| Specify acceptance criteria | Apply best practices |

**Outcome-focused** (✅ Good):
> "Implement session persistence that stores chat history to GCS. Users should be able to retrieve their conversation history."

**Over-prescriptive** (❌ Bad):
> "Add a `get_messages` function to main.py at line 200 that takes session_id, queries GCS, and returns a list of messages."

**Why this matters**: Over-prescription leads to:
- Code concentrated in wrong places (e.g., bloated main.py)
- Missed opportunities for better patterns
- Agents not applying their expertise
- Subpar architecture decisions

---

## Delegation Decision Tree

```
Task Received
    │
    ├─ Need research/exploration? → Scout
    │
    ├─ Architecture decision? → Sage
    │
    ├─ Backend/API/AI work? → Kai
    │
    ├─ Frontend/UI work? → Iris
    │
    ├─ Infrastructure/deployment? → Devo
    │
    ├─ Testing strategy? → Vera
    │
    └─ Frontend testing/a11y? → Luna
```

---

## Verification Checklist

Before calling Task tool:
- [ ] Determined correct agent (Scout for research, specialists for implementation)
- [ ] Delegating sequentially (one at a time)
- [ ] Used correct subagent_type (capital letters + spaces)
- [ ] Addressed agent by nickname at start
- [ ] Provided BACKGROUND CONTEXT
- [ ] Instructed agent to read their memory file
- [ ] Listed specific docs to load
- [ ] Suggested relevant skills to check
- [ ] Clear TASK with outcomes (NOT implementation details)
- [ ] Explicit DELIVERABLES
- [ ] Requested MEMORY UPDATE
- [ ] Reminded about compression protocol if needed
- [ ] **NOT over-prescribing HOW to implement** (let specialists decide)

---

## Scout-to-Specialist Handoff

When Scout's research indicates specialist work:

1. Scout returns compressed findings with handoff recommendation
2. Ezio reviews and synthesizes
3. Ezio delegates to specialist with:
   - Scout's key findings (compressed)
   - Additional context from conversation
   - Clear task and deliverables

**Template for handoff**:
```
[Specialist Nickname], I need your expertise on [topic].

BACKGROUND CONTEXT:
[Summary from Scout's research]
- [Key finding 1]
- [Key finding 2]

RELEVANT FILES (from Scout):
- [file1]: [what it contains]
- [file2]: [what it contains]

[Rest of standard delegation template...]
```

For full templates and examples, see: `.claude/skills/delegation-templates/SKILL.md`
