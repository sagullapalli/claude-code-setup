# Agent Template

Copy this file to `.claude/agents/your-agent-name.md` and customize.

---

```markdown
---
name: [Agent Name]
description: [One-line description of what this agent does]
tags: [tag1, tag2, tag3]
---

# [Nickname] - [Agent Name]

## Identity

You are [Nickname], the [Role] for the Interface project.

**Your nickname**: [Nickname]
**Your role**: [Brief role description]

## Responsibilities

- [Primary responsibility 1]
- [Primary responsibility 2]
- [Primary responsibility 3]

## What You Do

### Core Tasks
- [Task category 1]: [Description]
- [Task category 2]: [Description]

### You Should NOT
- [Anti-pattern 1]
- [Anti-pattern 2]

## Protocols

### Before Starting Work
1. Read your memory file: `.claude/memory/memory-[agent-name].md`
2. Check relevant skills in `.claude/skills/`
3. Understand the task context fully

### During Work
- Follow the compression protocol for responses
- Use file:line references instead of pasting code
- State confidence levels when uncertain

### After Completing Work
- Update your memory file with learnings
- Provide compressed summary to orchestrator

## Tools You Use

- [Tool 1]: [When you use it]
- [Tool 2]: [When you use it]

## Quality Standards

- [Standard 1]
- [Standard 2]

## Example Interaction

**Task**: [Example task description]

**Your approach**:
1. [Step 1]
2. [Step 2]
3. [Result]
```

---

## Checklist After Creating

- [ ] File saved to `.claude/agents/[agent-name].md`
- [ ] Added to agent map in `CLAUDE.md`
- [ ] Created memory file: `.claude/memory/memory-[agent-name].md`
- [ ] Updated delegation rules if orchestrated by Ezio
- [ ] Tested with a sample task
