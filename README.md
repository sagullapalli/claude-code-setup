# Claude Code Multi-Agent Setup

Production-ready Claude Code configuration with multi-agent orchestration, persistent memory, auto-discovered skills, and automation hooks for building fullstack applications.

## Key Features

- **Multi-Agent Orchestration**: 8 specialized agents coordinated by a central orchestrator (Ezio)
- **Persistent Memory**: Agents retain context and learnings across sessions
- **Auto-Discovered Skills**: 60+ technical patterns activated by context keywords
- **Mandatory Rules**: 6 protocols enforcing quality, boundaries, and honest feedback
- **Hook Automation**: Logging, session archiving, context sharing, and response tracking
- **Slash Commands**: `/handover`, `/prepare-pr`, `/discard-changes`

---

## Tech Stack

| Layer | Technologies |
|-------|--------------|
| **Backend** | Python 3.11+, FastAPI, PostgreSQL |
| **AI/Agents** | Claude Code SDK, Google ADK, Vertex AI (Gemini) |
| **Frontend** | React + TypeScript, Vite, Tailwind CSS, TanStack Query |
| **Cloud** | Cloud-agnostic (Europe regions preferred) |
| **Infrastructure** | Terraform, GitHub Actions |

---

## Claude Code Architecture

### The Two-System Principle

```
┌─────────────────────────────────────────────────────────────┐
│                    Planning System (Ezio)                   │
│  User Request → Plan → Delegate → Synthesize → Report       │
└─────────────────────────┬───────────────────────────────────┘
                          │
        ┌─────────────────┼──────────────────┐
        ▼                 ▼                  ▼
┌────────────────┐ ┌───────────────┐ ┌───────────────┐
│ Scout: Research│ │ Specialists:  │ │ QA Agents:    │
│ & Exploration  │ │ Implementation│ │ Testing       │
└────────────────┘ └───────────────┘ └───────────────┘
```

The orchestrator (Ezio) **plans and coordinates** but never executes directly. Specialists handle implementation with their own context windows.

### Agents

| Nickname | Role | Responsibilities |
|----------|------|------------------|
| **Ezio** | Main Orchestrator | Plans tasks, delegates to specialists, synthesizes results |
| **Scout** | General Worker | Research, codebase exploration, routine tasks |
| **Sage** | Solution Architect | Architecture decisions, design reviews, ADRs |
| **Kai** | AI Engineer | Backend, APIs, AI agents (Python/FastAPI/ADK) |
| **Iris** | Frontend Engineer | UI components, React/TypeScript, accessibility |
| **Devo** | DevOps Engineer | Infrastructure, deployment, CI/CD (Terraform) |
| **Vera** | QA Tester | Testing strategy, test automation, coverage |
| **Luna** | Frontend QA | Component tests, E2E, accessibility audits |

### Three-Tier Knowledge System

| Tier | Location | Purpose | Load Behavior |
|------|----------|---------|---------------|
| **Memory** | `.claude/memory/` | Project context, lessons learned | Every session |
| **Docs** | `docs/` | Detailed plans, ADRs, guides | On-demand |
| **Skills** | `.claude/skills/` | Technical patterns, code examples | Auto-discovered |

---

## Project Structure

```
.
├── CLAUDE.md                 # Universal context (auto-loaded)
├── PROJECT_GUIDELINES.md     # Coding standards
│
├── .claude/
│   ├── agents/               # 8 agent definitions
│   ├── commands/             # Slash commands (/handover, /prepare-pr, /discard-changes)
│   ├── rules/                # 6 mandatory protocols (auto-loaded)
│   │   ├── boundaries.md
│   │   ├── compression-protocol.md
│   │   ├── honest-feedback-protocol.md
│   │   ├── memory-protocol.md
│   │   ├── pre-work-protocol.md
│   │   └── quality-gates.md
│   │
│   ├── skills/               # 60+ patterns (auto-discovered)
│   │   ├── google-adk-patterns/
│   │   ├── deployment/
│   │   ├── testing-strategy/
│   │   ├── frontend-patterns/
│   │   ├── llm-evaluation/
│   │   ├── llm-observability/
│   │   └── ...
│   │
│   ├── memory/               # Per-agent persistent files
│   ├── hooks/                # Automation scripts (Python/Bash)
│   ├── context/              # Shared inter-agent state
│   └── settings.json         # Hooks & permissions config
│
└── docs/
    ├── ONBOARDING.md         # Comprehensive setup guide
    ├── SKILLS_AND_AGENTS_GUIDE.md
    ├── rules-reference.md
    └── adr/                  # Architecture Decision Records
```

---

## Rules (Mandatory Protocols)

These are auto-loaded and enforce consistent behavior:

| Rule | Purpose |
|------|---------|
| **boundaries** | Three-tier permission system (Always Do / Ask First / Never Do) |
| **compression-protocol** | Summarize findings, use file:line references |
| **honest-feedback** | Challenge ideas, state confidence levels |
| **memory-protocol** | STAR format for lessons, keep memory lean |
| **pre-work-protocol** | Check skills before implementation |
| **quality-gates** | Code review checklists (cloud-agnostic) |

---

## Skills (Auto-Discovered Patterns)

Skills are discovered by keyword mentions. Major domains:

| Domain | Files | Coverage |
|--------|-------|----------|
| `google-adk-patterns/` | 8 | ADK agents, events, state, tools, memory |
| `deployment/` | 7 | Cloud Run, Terraform, OAuth, Cloud Build |
| `testing-strategy/` | 13 | Unit, integration, E2E, accessibility, security |
| `frontend-patterns/` | 9 | React, routing, state, forms, animations |
| `llm-evaluation/` | 6 | DeepEval, RAGAS, Vertex AI evaluation |
| `llm-observability/` | 6 | Langfuse, Phoenix, OpenLLMetry tracing |

**Example**: Mentioning "ADK event persistence" auto-discovers relevant patterns from `google-adk-patterns/`.

---

## Hooks and Observability (Optional)

Hooks provide observability, workflow automation, and protocol enforcement. **All hooks are optional** — customize via `.claude/settings.json`.

### Configured Hooks

| Event | Script | Purpose |
|-------|--------|---------|
| `SessionStart` | `setup-environment.sh` | Environment setup, Node/Python activation, orchestrator reminder |
| `PreToolUse[Task]` | `task_context_tracker.py` | Track agent task lifecycle (start) |
| `PostToolUse[*]` | `tool_trace_logger.py` | Log all tool calls to JSONL |
| `PostToolUse[Task]` | `task_context_tracker.py` | Track agent task lifecycle (end) |
| `PostToolUse[Task]` | `context_sharing.py` | Share context between agents |
| `PostToolUse[Task]` | `agent_response_logger.py` | Log agent responses and deliverables |
| `SessionEnd` | `session_analytics.py` | Generate session metrics report |
| `SessionEnd` | `session_archiver.py` | Archive session data for future reference |

### Available but Not Configured

| Script | Recommended Event | Purpose |
|--------|-------------------|---------|
| `inject_shared_context.py` | `UserPromptSubmit` | Injects shared context from previous agents into prompts |

### Output Files

Generated by hooks, safely deletable, and git-ignored:

| Location | File | Generated By |
|----------|------|--------------|
| `.claude/logs/` | `tool-trace.jsonl` | `tool_trace_logger.py` |
| `.claude/logs/` | `session-metrics.jsonl` | `session_analytics.py` |
| `.claude/logs/` | `latest-session-report.txt` | `session_analytics.py` |
| `.claude/logs/` | `.active_tasks.json` | `task_context_tracker.py` |
| `.claude/context/` | `shared-context.json` | `context_sharing.py` |

### Customization

- **Disable**: Remove entry from `.claude/settings.json`
- **Enable**: Add to appropriate event in `settings.json`
- **Modify**: Edit scripts in `.claude/hooks/` (standard stdin/stdout)
- **Hook types**: `command` (shell) or `prompt` (LLM-powered, Stop events only)

---

## Getting Started

### Prerequisites

- Node.js 18+ (for frontend)
- Python 3.11+ (for backend)
- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) installed

### Quick Start

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/claude-code-setup.git
cd claude-code-setup

# Open Claude Code — everything auto-loads
claude
```

### How It Works

1. `CLAUDE.md` loads universal context automatically
2. Rules in `.claude/rules/` enforce protocols on every interaction
3. Skills in `.claude/skills/` are auto-discovered by keyword mentions
4. Hooks in `.claude/hooks/` run on lifecycle events (session start/end, tool use)

**Example interaction**:
```
You: "Add a new API endpoint for user profiles"

Ezio: [Plans task with TodoWrite]
    → [Delegates to Scout for codebase research]
    → [Delegates to Kai for implementation]
    → [Reports completion with summary]
```

---

## Customization

### Adding an Agent

1. Create `.claude/agents/new-agent.md` with YAML frontmatter
2. Add to the agent map in `CLAUDE.md`
3. Create `.claude/memory/memory-new-agent.md`

### Creating a Skill

1. Create file in `.claude/skills/` with frontmatter:
   ```yaml
   ---
   name: Pattern Name
   description: What this covers
   tags: [keyword1, keyword2]
   ---
   ```
2. Add technical patterns with code examples
3. Skills are auto-discovered by tag keywords

### Writing a Rule

1. Create `.claude/rules/new-rule.md`
2. Rules auto-load and enforce mandatory behavior
3. Use for protocols that must always apply

---

## Documentation

| Document | Purpose |
|----------|---------|
| [ONBOARDING.md](docs/ONBOARDING.md) | Comprehensive setup walkthrough |
| [TUTORIAL.md](docs/TUTORIAL.md) | Hands-on tutorial with examples |
| [SKILLS_AND_AGENTS_GUIDE.md](docs/SKILLS_AND_AGENTS_GUIDE.md) | Knowledge system deep dive |
| [rules-reference.md](docs/rules-reference.md) | Complete rules documentation |

---

## Design Philosophy

### Simplicity First
- Build exactly what's needed, nothing more
- Prefer open source; use managed services only when significantly beneficial
- Start monolithic, scale when necessary

### Honest Feedback Over Validation
- Agents challenge ideas before validating
- State confidence levels explicitly
- Disagree respectfully when warranted

### Context Preservation
- Orchestrator context stays strategic
- Raw data processing delegated to agents
- Compression protocol prevents context bloat

---

## License

MIT
