# Memory Protocol (Mandatory)

All agents maintain memory files in `.claude/memory/` for persistent learning across sessions.

---

## At Session Start

1. **Read** your memory file: `.claude/memory/memory-[agent-name].md`
2. **State in your response**: "Memory check: [summary of past learnings OR 'empty - first session']"
3. **Load** relevant docs referenced in memory for current work
4. **Apply** previous knowledge to current task

## At Session End

1. **Update** memory with new context (status, decisions with brief rationale)
2. **Add** pointers to any new docs created
3. **Ensure** "Lessons" section captures new discoveries
4. **Confirm explicitly**: "Updated memory with [brief summary of additions]"

---

## Memory Philosophy: Contextualized Index

Your memory is a **contextualized index** (1-2 pages max), NOT detailed documentation:

- **High-level context**: Current status, what's been built, project config
- **Brief rationale** (1-2 lines): Enough to understand "why" a decision was made
- **Pointers to docs**: Links to detailed implementation plans in `docs/`
- **Lessons learned**: Gotchas, discoveries, best practices

**Target Size**: 10-15k characters (2.5-3.75k tokens) - Keep it lean!

---

## Three-Tier Knowledge System

| Tier | Location | Purpose | When to Use |
|------|----------|---------|-------------|
| **Memory** | `.claude/memory/` | Project context + learnings | Read every session |
| **Docs** | `docs/` | Detailed plans, ADRs, guides | Load when implementing |
| **Skills** | `.claude/skills/` | Technical patterns | Auto-discovered by context |

---

## STAR Format for Lessons

**For bugs, issues, and significant learnings (>10 lines worth of detail)**, use the **STAR format**:

```markdown
### [Bug/Issue Title] (Date)
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
**Situation**: GET /sessions/{id}/messages returned 0 messages
**Task**: Fix chat history endpoint
**Action**: Manually append user + extend agent events before save
**Result**: All 6 messages retrieved, history working
**Fix**: agent_service.py:209-215
**Pattern**: ADK run_async() doesn't auto-persist events
**Full details**: docs/archive/handoffs/SESSION_HANDOFF_BUGFIX.md
```

---

## Brief Bullet Points Format

**For simple insights, patterns, and configuration details (< 10 lines)**, use brief bullets:

```markdown
## Code Patterns
- **Custom GCS Session Service**: Extends ADK BaseSessionService (`gcs_session_service.py:45-120`)
- **Why**: ADK has no built-in CloudStorageMemory (contrary to initial assumption)
- **Bucket**: `[bucket-name]` (europe-west1, REGIONAL, 30-day lifecycle)
```

---

## What to Record

**DO Record:**
- Project config (GCP project, regions, bucket names)
- Current status and what's been built
- Key decisions with brief rationale (1-2 lines)
- Code patterns with file path examples
- Critical commands and gotchas
- Lessons learned (STAR format for bugs/issues)
- Pointers to implementation docs

**DON'T Record:**
- Full implementation steps (those go in `docs/PHASE_X_PLAN.md`)
- Complete code examples (those go in `skills/`)
- Duplicate information from docs (just point to them)
- General technical patterns (those go in skills)

---

## Archive Strategy

When work is **complete and documented**, archive detailed content:

| Type | Archive Location |
|------|-----------------|
| Postmortems | `docs/archive/postmortems/` |
| Handoffs | `docs/archive/handoffs/` |
| Bugfixes | `docs/archive/bugfixes/` |

Update memory with STAR pointer, full details go to archive (lazy-load).

---

## Quick Reference

```
Session Start:
  1. Read memory → 2. State "Memory check: [summary]" → 3. Apply learnings

Session End:
  1. Update memory → 2. Confirm "Updated memory with [additions]"

Format Choice:
  - >10 lines of detail → STAR format
  - <10 lines of detail → Brief bullets
```
