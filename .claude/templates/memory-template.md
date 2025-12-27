# Memory File Template

Copy this file to `.claude/memory/memory-[agent-name].md` when creating a new agent.

---

```markdown
# [Agent Nickname] Memory

> Last updated: YYYY-MM-DD

## Current Status

[1-2 sentences on what's currently being worked on or the project state]

---

## Project Context

### Key Configuration
- **Project**: [Project name]
- **Tech Stack**: [Relevant technologies for this agent]
- **Important Paths**:
  - [Path 1]: [What it contains]
  - [Path 2]: [What it contains]

### Architecture Understanding
- [Key architectural pattern 1]
- [Key architectural pattern 2]

---

## Active Work

### In Progress
- [ ] [Current task 1]
- [ ] [Current task 2]

### Blockers
- [Any current blockers]

---

## Key Decisions

| Decision | Rationale | Date |
|----------|-----------|------|
| [Decision 1] | [Brief why] | YYYY-MM-DD |
| [Decision 2] | [Brief why] | YYYY-MM-DD |

---

## Lessons Learned

### [Lesson Title] (YYYY-MM-DD)
**Situation**: [What was the context]
**Task**: [What needed to be done]
**Action**: [What was done to resolve]
**Result**: [Outcome]
**Fix**: [file:line reference]
**Pattern**: [Reusable insight]

---

## Quick References

### Commands
```bash
# [Useful command 1]
# [Useful command 2]
```

### Code Patterns
- [Pattern name]: `file.py:line` - [brief description]

---

## Related Docs

- `docs/[doc-name].md`: [What it contains]
```

---

## Memory Best Practices

### Keep It Lean
- Target: 1-2 pages (10-15k characters max)
- Memory is an INDEX, not full documentation
- Link to `docs/` for detailed content

### What to Include
- Project configuration and context
- Key decisions with brief rationale
- Lessons learned (STAR format)
- Quick references and commands

### What NOT to Include
- Full code examples (use skills)
- Detailed implementation steps (use docs)
- General technical patterns (use skills)

### STAR Format for Lessons
Use STAR for significant learnings (bugs, issues, discoveries):
- **S**ituation: Context
- **T**ask: Goal
- **A**ction: What was done
- **R**esult: Outcome + fix reference

---

## Update Protocol

### At Session Start
1. Read this memory file
2. State: "Memory check: [summary]"
3. Apply learnings to current task

### At Session End
1. Add new context/decisions
2. Record lessons in STAR format
3. Confirm: "Updated memory with [additions]"

---

## Checklist After Creating

- [ ] File saved to `.claude/memory/memory-[agent-name].md`
- [ ] Current status section populated
- [ ] Key project context added
- [ ] Agent will read this at session start
