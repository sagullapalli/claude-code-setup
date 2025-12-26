# Interface - Universal Project Context

## How Instruction Files Work

**Claude Code automatically loads TWO instruction files for every agent:**

1. **CLAUDE.md (this file)** - Universal project context that ALL agents see
2. **Your agent-specific file** - Your unique role and responsibilities

### Agent Identity Map

| Nickname | Technical Role | Agent File Path |
|----------|---------------|-----------------|
| **Ezio** | Main Orchestrator | `.claude/agents/orchestrator.md` |
| **Scout** | General Worker | `.claude/agents/general-worker.md` |
| **Sage** | Solution Architect | `.claude/agents/solution-architect.md` |
| **Kai** | AI Engineer | `.claude/agents/ai-engineer.md` |
| **Iris** | Frontend Engineer | `.claude/agents/frontend-engineer.md` |
| **Devo** | DevOps Engineer | `.claude/agents/devops-engineer.md` |
| **Vera** | QA Tester | `.claude/agents/qa-tester.md` |
| **Luna** | Frontend QA Specialist | `.claude/agents/frontend-qa-specialist.md` |

Your nickname and detailed instructions are in your agent-specific file.

---

## Core Principles

### Simplicity First
- Build exactly what's needed, nothing more
- Minimize code, maximize utility and readability
- Use managed services over custom solutions
- Start monolithic, scale only when necessary
- YAGNI (You Aren't Gonna Need It)

### Honest Feedback Over Validation
- Challenge ideas before validating them
- State confidence levels explicitly ("I'm confident..." / "I have reservations...")
- Disagree respectfully when warranted—provide rationale, not just agreement
- See `.claude/rules/honest-feedback-protocol.md` for full protocol

### Technology Stack (Mandatory)
- **Backend**: Python 3.11+, FastAPI, PostgreSQL (Cloud SQL)
- **AI/Agents**: Google ADK, Vertex AI (Gemini models)
- **Cloud**: GCP (Cloud Run preferred, Europe regions: `europe-west1` or `europe-west3`)
- **Frontend**: React + TypeScript (Vite, Tailwind CSS, TanStack Query)
- **Infrastructure**: Terraform, Cloud Build/GitHub Actions

See [PROJECT_GUIDELINES.md](PROJECT_GUIDELINES.md) for complete guidelines.

---

## Pre-Work Protocol

**Before ANY technical work**: Check skills first.

See `.claude/rules/pre-work-protocol.md` for the full checklist.

**Quick version**:
1. Identify the technology (ADK, FastAPI, GCS, React, etc.)
2. Search `.claude/skills/` for existing patterns
3. Found? Use it. Not found? Investigate, then document.

---

## Agent Memory

All agents maintain memory files in `.claude/memory/` for persistent learning.

See `.claude/rules/memory-protocol.md` for the mandatory protocol.

**Key points**:
- Memory files are **contextualized indexes** (1-2 pages max)
- Read at session start, update at session end
- Use STAR format for lessons learned
- Detailed specs go in `docs/`, not memory

**Your memory file**: `.claude/memory/memory-[agent-name].md`

---

## Three-Tier Knowledge System

| Tier | Location | Purpose |
|------|----------|---------|
| **Memory** | `.claude/memory/` | Project-specific context + learnings |
| **Docs** | `docs/` | Detailed implementation plans, ADRs |
| **Skills** | `.claude/skills/` | Technical patterns (auto-discovered) |

**Rules** (`.claude/rules/`) load automatically and enforce standards.

See [SKILLS_AND_AGENTS_GUIDE.md](docs/SKILLS_AND_AGENTS_GUIDE.md) for complete philosophy.

---

## Resources

- **[PROJECT_GUIDELINES.md](PROJECT_GUIDELINES.md)** - Complete project guidelines
- **[README.md](README.md)** - Project overview and setup
- **[.claude/rules/](.claude/rules/)** - Mandatory protocols (auto-loaded)
- **[.claude/skills/](.claude/skills/)** - Technical patterns (auto-discovered)
- **[.claude/memory/](.claude/memory/)** - Agent memory files
- **[docs/](docs/)** - Detailed documentation
