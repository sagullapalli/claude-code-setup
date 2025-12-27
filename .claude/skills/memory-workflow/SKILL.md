---
name: memory-workflow
description: Templates and examples for memory file management. STAR format template, what to record vs not record, good/bad examples. Use when updating memory or at session start/end.
---

# Memory Workflow

Templates and detailed guidance for maintaining agent memory files.

**For mandatory protocol, see**: `.claude/rules/memory-protocol.md`

---

## STAR Format Template

For bugs, issues, and significant learnings:

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

### Example

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

---

## What to Record

### DO Record

| Category | Examples |
|----------|----------|
| **Project config** | GCP project ID, region, stack |
| **Current status** | Phase, what's complete, what's pending |
| **Key decisions** | 1-2 line rationale + link to docs |
| **Critical paths** | File paths, commands, gotchas |
| **Lessons learned** | STAR format entries |
| **Doc pointers** | Links with brief description |

### DON'T Record

| Category | Where It Goes Instead |
|----------|----------------------|
| Full implementation details | `docs/` |
| Step-by-step guides | `docs/` |
| Duplicate info from docs | Just link to docs |
| General technical patterns | `.claude/skills/` |

---

## Memory File Structure

```markdown
# Agent Name - Role

Last updated: YYYY-MM-DD

## Project Config
- GCP Project: [project-id]
- Region: europe-west1
- Stack: Python/FastAPI/Google ADK

## Current Status
- Phase: [current phase]
- Complete: [bullet list]
- Pending: [bullet list]
- See: [link to detailed phase doc]

## Key Decisions
| Decision | Rationale | Details |
|----------|-----------|---------|
| [What] | [1-2 line why] | [link to ADR] |

## Critical Commands
```bash
# Start backend
cd backend && uvicorn main:app --reload

# Run tests
pytest backend/tests/ -v
```

## Lessons Learned
[STAR format entries]

## Documentation Map
| Topic | Document | Contents |
|-------|----------|----------|
| [topic] | [path] | [brief description] |
```

---

## Good vs Bad Examples

### Bad: Too Detailed
```markdown
## Session Storage Implementation
We implemented GCS session storage by first creating a bucket using
terraform with the following configuration... [500 more lines]
```
**Problem**: This belongs in `docs/`, not memory.

### Good: Contextualized Index
```markdown
## Session Storage
- Decision: GCS CloudStorageMemory (not Firestore)
- Rationale: Simpler, cheaper, ADK-native
- Full details: [docs/adr/002-gcs-session-storage.md]
```
**Why it works**: Brief context + pointer to full doc.

### Bad: No Context
```markdown
## Decisions
- Use GCS
- Use Cloud Run
```
**Problem**: No rationale, no links.

### Good: With Rationale
```markdown
## Key Decisions
| Decision | Rationale | Details |
|----------|-----------|---------|
| GCS over Firestore | Simpler, ADK-native, 10x cheaper | [ADR-002] |
| Cloud Run over GKE | Managed, auto-scaling, no K8s overhead | [ADR-003] |
```

---

## Size Guidelines

- **Target**: 10-15k characters (2.5-3.75k tokens)
- **Max sections**: 6-8 major sections
- **Lessons**: Keep last 5-10 most relevant
- **Archive old lessons**: Move to `docs/archive/lessons/` if needed

If memory exceeds target, move detailed content to `docs/` and keep pointers.
