# Ezio - Main Orchestrator

Last updated: 2025-12-25

## Active Protocols

### Skills-First Protocol
**MANDATORY**: Before ANY technical work, check `.claude/skills/` first.
**Full protocol**: `.claude/rules/pre-work-protocol.md`

### Agent Delegation Protocol
**Full protocol**: `.claude/rules/agent-delegation.md`
**Templates**: `.claude/skills/delegation-templates/SKILL.md`

**Quick Reference**:
| Nickname | subagent_type |
|----------|---------------|
| Sage | `Solution Architect` |
| Kai | `AI Engineer` |
| Iris | `Frontend Engineer` |
| Devo | `DevOps Engineer` |
| Vera | `QA Tester` |
| Luna | `Frontend QA Specialist` |

---

## Project Config
- **Project**: Interface
- **GCP Project**: [To be configured]
- **Region**: europe-west1 (ALWAYS use Europe regions)
- **Stack**: Python/FastAPI/Google ADK (backend), React/TypeScript (frontend)
- **Repository**: /home/sunny/projects/interface

## Current Status

**Phase**: Setup/Organization
- Claude configuration in progress
- Skills and agents framework restructured (2025-12-25)
- Memory files reset for fresh start

---

## Key Decisions

| Decision | Rationale | Details |
|----------|-----------|---------|
| Split agent-delegation into rule + skill | Rules enforce standards, skills provide templates | This session |
| Split memory-workflow into rule + skill | Rules enforce standards, skills provide templates | This session |
| Move Documentation Map to memory | Project-specific context, not reusable across projects | This session |

---

## Critical Files & Commands

[To be documented as project develops]

---

## Lessons Learned

### Reorganization: CLAUDE.md & orchestrator.md (2025-12-25)
**Situation**: CLAUDE.md (209 lines) and orchestrator.md (850 lines) were too large with mixed concerns
**Task**: Reorganize per Three-Tier Knowledge System
**Action**: Split into rules (mandates) + skills (procedures) + memory (project context)
**Result**: CLAUDE.md → 97 lines, orchestrator.md → 180 lines
**Pattern**: Rules = "You MUST", Skills = "Here's HOW", Memory = project-specific indexes

---

## Documentation Map

### Current Project Docs
| Document | Use When | Key Contents |
|----------|----------|--------------|
| [README.md](README.md) | Project overview | Project description |
| [docs/SKILLS_AND_AGENTS_GUIDE.md](docs/SKILLS_AND_AGENTS_GUIDE.md) | Understanding skills/memory | Three-tier knowledge system |
| [docs/claude-code-best-setup.md](docs/claude-code-best-setup.md) | Claude Code setup | Best practices for Claude configuration |
| [docs/rules-reference.md](docs/rules-reference.md) | Rules reference | How rules work |
| [docs/skill-complexity-levels.md](docs/skill-complexity-levels.md) | Skill design | Skill complexity levels |

### Rules (Auto-loaded)
| Rule | Purpose |
|------|---------|
| `.claude/rules/pre-work-protocol.md` | Skills-first checklist before any work |
| `.claude/rules/memory-protocol.md` | Memory read/update requirements |
| `.claude/rules/agent-delegation.md` | Delegation standards for Ezio |
| `.claude/rules/quality-gates.md` | Code quality standards |

### Skills (Auto-discovered)
| Skill | Purpose |
|-------|---------|
| `memory-workflow/` | STAR format templates, memory examples |
| `delegation-templates/` | Delegation context templates, examples |
| `orchestrator-workflows/` | Phase workflows, TDD coordination |

---

## Common Delegation Scenarios

**Note**: Update these as project develops with specific doc references.

### Building a New Feature
```
1. Delegate to Sage for architecture
2. Delegate to Kai for backend implementation
3. Delegate to Iris for frontend (if needed)
4. Delegate to Vera for testing
Skills: Depends on feature domain
```

### Testing Implementation
```
Skills: testing-strategy, tdd-workflow
```

### Infrastructure Setup
```
Skills: gcp-deployment (when created)
```

---

**Memory Guidelines:**
- Keep entries concise with bullet points
- Record specifics (paths, commands, project IDs, regions)
- Focus on project-specific context, not general patterns (those go in skills)
- Update after significant milestones or discoveries
