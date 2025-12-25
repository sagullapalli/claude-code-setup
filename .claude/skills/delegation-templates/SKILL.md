---
name: delegation-templates
description: Context templates and examples for Main Orchestrator agent delegation. Standard delegation template, good/bad examples. Use when delegating tasks to specialized agents.
---

# Delegation Templates

Templates and examples for delegating to specialized agents.

**For mandatory protocol, see**: `.claude/rules/agent-delegation.md`

---

## Standard Delegation Template

```markdown
[Nickname], I need your [specific expertise] on [topic].

BACKGROUND CONTEXT:
[Explain what led to this task - the agent cannot see conversation history]
- What problem are we solving?
- Why is this needed now?
- What decisions have already been made?

MEMORY & KNOWLEDGE:
1. Read your memory file (.claude/memory/memory-[agent-name].md) for project context
2. Load these docs for detailed specs:
   - [doc1]: [what it contains]
   - [doc2]: [what it contains]
3. These skills may be relevant:
   - [skill1]: [what patterns it has]
   - [skill2]: [what patterns it has]

TASK:
[Clear, specific task with numbered steps if applicable]
1. [Step 1]
2. [Step 2]
3. [Step 3]

DELIVERABLES:
- [Expected output 1]
- [Expected output 2]

CONSTRAINTS:
- [Any limitations, requirements, or must-follow patterns]

MEMORY UPDATE:
After completing the task, update your memory file with:
- Status/outcome
- Brief rationale for key decisions
- Lessons learned (using STAR format for bugs/issues)
```

---

## Good Example

```python
Task(
    subagent_type="Solution Architect",
    prompt="""
Sage, I need your architecture expertise on testing infrastructure.

BACKGROUND CONTEXT:
The user wants production-ready testing for the backend before deployment.
We currently have 103 tests with 76% coverage, but no CI/CD pipeline.
A security audit identified vulnerabilities, highlighting the need for
robust testing before production.

MEMORY & KNOWLEDGE:
1. Read your memory file (.claude/memory/memory-solution-architect.md)
2. Load these docs for detailed specs:
   - docs/current/PHASE_2_PLAN.md: Track A2 - Testing Infrastructure details
   - docs/reference/ARCHITECTURE_DECISION_SUMMARY.md: Existing ADRs
3. These skills may be relevant:
   - testing-strategy: Unit, integration, E2E testing patterns
   - gcp-deployment: CI/CD options (GitHub Actions vs Cloud Build)

TASK:
Design a comprehensive testing architecture for our FastAPI + Google ADK backend:
1. Choose CI/CD platform (GitHub Actions vs Cloud Build) with rationale
2. Recommend integration testing approach (GCS emulator vs real bucket)
3. Define performance testing strategy (tools, targets)
4. Draft ADRs for key architectural decisions
5. Create implementation roadmap

DELIVERABLES:
- Testing architecture recommendation (written)
- ADR drafts for major decisions
- Phased implementation roadmap

CONSTRAINTS:
- Must use GCP Europe regions (europe-west1/west3)
- Follow existing project patterns (see PROJECT_GUIDELINES.md)
- Target: >70% coverage, all critical paths tested

MEMORY UPDATE:
After completing the task, update your memory file with:
- Testing architecture decision and brief rationale
- Link to ADRs created
- Lessons learned about testing ADK-based applications
"""
)
```

---

## Bad Examples

### Missing Context
```python
Task(
    subagent_type="Solution Architect",
    prompt="Design the testing architecture"
)
```
**Problems**:
- No background (why we need this)
- No mention of memory file or docs
- No deliverables specified
- Agent works in a vacuum

### Wrong subagent_type
```python
Task(
    subagent_type="solution-architect",  # Wrong!
    prompt="..."
)
```
**Problem**: Must use `"Solution Architect"` (capital letters + spaces)

### No Nickname
```python
Task(
    subagent_type="AI Engineer",
    prompt="Build a poem generator agent..."
)
```
**Problem**: Should start with "Kai, I need you to build..."

### Imperative Skill Language
```python
prompt="""
...
3. Invoke the google-adk-patterns skill for patterns
...
"""
```
**Better**:
```python
prompt="""
...
3. The google-adk-patterns skill has relevant agent setup patterns
...
"""
```

---

## Agent Quick Reference

| Nickname | subagent_type | Expertise |
|----------|---------------|-----------|
| Scout | `General Worker` | Research, exploration, file ops, context gathering |
| Sage | `Solution Architect` | Architecture, GCP services, ADRs |
| Kai | `AI Engineer` | Python, FastAPI, Google ADK, data layer |
| Iris | `Frontend Engineer` | React, TypeScript, Vite, accessibility |
| Devo | `DevOps Engineer` | Cloud Run, Terraform, CI/CD |
| Vera | `QA Tester` | pytest, Playwright, AI testing |
| Luna | `Frontend QA Specialist` | Vitest, a11y testing, visual regression |

---

## Common Delegation Scenarios

### Building a New Feature
1. **Sage**: Design architecture
2. **Kai**: Implement backend/API
3. **Iris**: Build frontend (if needed)
4. **Vera**: Write tests

### Fixing a Bug
1. **Kai/Iris**: Investigate and fix
2. **Vera**: Add regression test

### Infrastructure Setup
1. **Sage**: Architecture decision
2. **Devo**: Terraform + deployment

### Test-Driven Development
1. **Vera**: Write failing test (RED)
2. **Kai**: Implement to pass (GREEN)
3. **Kai**: Refactor (REFACTOR)
4. **Vera**: Add edge cases
