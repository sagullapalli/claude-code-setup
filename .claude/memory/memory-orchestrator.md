# Ezio - Main Orchestrator

Last updated: [Date]

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
| Scout | `General Worker` |
| Sage | `Solution Architect` |
| Kai | `AI Engineer` |
| Iris | `Frontend Engineer` |
| Devo | `DevOps Engineer` |
| Vera | `QA Tester` |
| Luna | `Frontend QA Specialist` |

---

## Project Config
- **Project**: [Your Project Name]
- **GCP Project**: [To be configured]
- **Region**: europe-west1 (ALWAYS use Europe regions)
- **Stack**: Python/FastAPI/Google ADK (backend), React/TypeScript (frontend)
- **Repository**: /path/to/your-project

## Current Status

**Phase**: Setup/Organization
- Claude configuration in progress
- Skills and agents framework ready

---

## Key Decisions

| Decision | Rationale | Details |
|----------|-----------|---------|
| [Decision] | [Rationale] | [Details] |

---

## Critical Files & Commands

[To be documented as project develops]

---

## Lessons Learned

[No lessons recorded yet - use STAR format for bugs/issues]

---

## Documentation Map

### Current Project Docs
| Document | Use When | Key Contents |
|----------|----------|--------------|
| [README.md](README.md) | Project overview | Project description |
| [docs/SKILLS_AND_AGENTS_GUIDE.md](docs/SKILLS_AND_AGENTS_GUIDE.md) | Understanding skills/memory | Three-tier knowledge system |
| [docs/rules-reference.md](docs/rules-reference.md) | Rules reference | How rules work |

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
Skills: deployment
```

---

**Memory Guidelines:**
- Keep entries concise with bullet points
- Record specifics (paths, commands, project IDs, regions)
- Focus on project-specific context, not general patterns (those go in skills)
- Update after significant milestones or discoveries
