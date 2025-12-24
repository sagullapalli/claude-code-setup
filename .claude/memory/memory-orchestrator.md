# Arc - Main Orchestrator

Last updated: 2025-12-24

## Active Protocols (Read Every Session)

### Skills-First Protocol
**MANDATORY**: Before ANY technical investigation, debugging, or implementation:
1. Identify technology/domain relevant to the task
2. Check `.claude/skills/[technology]-patterns.md`
3. Search for relevant pattern (2 minutes)
4. Use documented pattern if found, OR investigate + document after verification

**Full protocol**: See CLAUDE.md

### Agent Delegation Protocol
When delegating to team agents (Sage, Kai, Vera, Iris, Devo, Luna):
1. Use correct subagent_type (exact capitalization)
2. Provide COMPLETE context in delegation prompt (agents start with clean slate)

**Quick Reference**:
- Sage: `subagent_type="Solution Architect"`
- Kai: `subagent_type="AI Engineer"`
- Iris: `subagent_type="Frontend Engineer"`
- Devo: `subagent_type="DevOps Engineer"`
- Vera: `subagent_type="QA Tester"`
- Luna: `subagent_type="Frontend QA Specialist"`

## Project Config
- **Project**: [Project Name]
- **GCP Project**: [To be configured]
- **Region**: europe-west1 (ALWAYS use Europe regions)
- **Stack**: [To be configured]
- **Repository**: /home/sunny/projects/interface

## Current Status

**Phase**: Not started
- Project setup in progress
- Claude configuration copied from previous project
- Memory files reset for fresh start

## Key Decisions

[No decisions recorded yet]

## Critical Files & Commands

[To be documented as project develops]

## Lessons Learned

[No lessons recorded yet - use STAR format for bugs/issues]

## Documentation Map

| Topic | Document | What It Contains |
|-------|----------|------------------|
| [Topic] | [doc-path] | [Description] |

---

**Memory Guidelines:**
- Keep entries concise with bullet points
- Record specifics (paths, commands, project IDs, regions)
- Focus on project-specific context, not general patterns (those go in skills)
- Update after significant milestones or discoveries
