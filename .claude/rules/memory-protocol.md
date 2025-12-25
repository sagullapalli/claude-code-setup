# Memory Protocol (Mandatory)

All agents maintain memory files in `.claude/memory/` for persistent learning across sessions.

## At Session Start

1. Read your memory file: `.claude/memory/memory-[agent-name].md`
2. Load relevant docs referenced in memory for current work
3. Note the current phase/status

## At Session End

1. Update memory with new context (status, decisions with brief rationale)
2. Add pointers to any new docs created
3. Ensure "Lessons" section captures new discoveries
4. Keep memory concise - detailed info stays in docs

## Standards

### Memory Philosophy: Contextualized Indexes
Memory files are **indexes**, not detailed documentation:
- High-level context refresh (1-2 pages max)
- Key rationale (1-2 lines per decision)
- Pointers to detailed docs
- Lessons learned (STAR format)

### Three-Tier Knowledge System
- **Memory** (.claude/memory/): Project-specific context + learnings
- **Docs** (docs/): Detailed implementation plans, ADRs, guides
- **Skills** (.claude/skills/): Technical patterns (auto-discovered)

### STAR Format for Lessons
Use for bugs, issues, and significant learnings:
- **S**ituation: Context/problem
- **T**ask: Goal
- **A**ction: Steps taken
- **R**esult: Outcome + Fix + Pattern

### Size Target
- Memory files: 10-15k characters (2.5-3.75k tokens)
- Detailed specs go in docs/, not memory

## What to Record

**DO**: Project config, current status, key decisions (1-2 line rationale), file paths, gotchas, lessons, doc pointers

**DON'T**: Full implementation details, step-by-step guides, duplicate info from docs, general technical patterns

For detailed templates and examples, see: `.claude/skills/memory-workflow/SKILL.md`
