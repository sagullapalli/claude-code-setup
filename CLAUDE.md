# Universal Project Context

## Agent Identity Map

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

## Core Principles

- **Simplicity First**: Build exactly what's needed, nothing more. YAGNI.
- **Open Source Over Paid**: Prefer open source unless paid is significantly cheaper, more stable, or less maintenance.
- **Start Monolithic**: Scale only when necessary.
- **Honest Feedback**: Challenge before validating.
- **Skills Before Work**: Check `.claude/skills/` before investigating.
- **Memory Every Session**: Read at start, update at end.
- **Compress Ruthlessly**: Return insights, not raw data.

### Development Philosophy

- Simple is better than complex. Complex is better than complicated.
- Explicit is better than implicit.
- Readability counts.
- Errors should never pass silently.
- Practicality beats purity.
- Now is better than never, although never is often better than right now.
- If the implementation is hard to explain, it's a bad idea.

## Technology Stack (Mandatory)

- **Backend**: Python 3.11+, FastAPI, PostgreSQL
- **AI/Agents**: Google ADK, Vertex AI (Gemini models)
- **Cloud**: Cloud-agnostic (evaluating providers, Europe regions preferred)
- **Frontend**: React + TypeScript (Vite, Tailwind CSS, TanStack Query)
- **Infrastructure**: Terraform, GitHub Actions

## Resources

| Resource | Location |
|----------|----------|
| Technical patterns | [.claude/skills/](.claude/skills/) (auto-discovered) |
| Agent memory | [.claude/memory/](.claude/memory/) |
| Documentation | [docs/](docs/) |
| Architecture guide | [docs/SKILLS_AND_AGENTS_GUIDE.md](docs/SKILLS_AND_AGENTS_GUIDE.md) |
