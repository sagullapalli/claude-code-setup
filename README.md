# Claude Code Multi-Agent Setup

Custom UI and orchestration layer built on Claude Code SDK for managing multi-agent AI applications.

## Overview

This project provides a production-ready Claude Code setup with multi-agent orchestration for building fullstack applications. It includes 8 specialized agents, 60+ skill patterns, persistent memory, and automation hooks.

## Key Features

- **Multi-Agent Orchestration**: 8 specialized agents coordinated by a central orchestrator
- **Persistent Memory**: Agents learn and retain context across sessions
- **Auto-Discovered Skills**: 60+ technical patterns activated by context keywords
- **Mandatory Rules**: 7 protocols ensuring quality, consistency, and honest feedback
- **Hook Automation**: Logging, validation, and context sharing via Python/Bash scripts

---

## Tech Stack

| Layer | Technologies |
|-------|--------------|
| **Backend** | Python 3.11+, FastAPI, PostgreSQL |
| **AI/Agents** | Claude Code SDK, Google ADK, Vertex AI (Gemini) |
| **Frontend** | React + TypeScript, Vite, Tailwind CSS, TanStack Query |
| **Cloud** | GCP (Cloud Run, Cloud SQL, europe-west1/west3) |
| **Infrastructure** | Terraform, GitHub Actions, Cloud Build |

---

## Claude Code Architecture

### The Two-System Principle

```
┌─────────────────────────────────────────────────────────────┐
│                    Planning System (Ezio)                    │
│  User Request → Plan → Delegate → Synthesize → Report       │
└─────────────────────────┬───────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│ Scout: Research│ │ Specialists:  │ │ QA Agents:    │
│ & Exploration │ │ Implementation│ │ Testing       │
└───────────────┘ └───────────────┘ └───────────────┘
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
| **Devo** | DevOps Engineer | Infrastructure, deployment, CI/CD (Terraform/GCP) |
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
│   │   ├── orchestrator.md
│   │   ├── general-worker.md
│   │   ├── solution-architect.md
│   │   ├── ai-engineer.md
│   │   ├── frontend-engineer.md
│   │   ├── devops-engineer.md
│   │   ├── qa-tester.md
│   │   └── frontend-qa-specialist.md
│   │
│   ├── rules/                # 7 mandatory protocols (auto-loaded)
│   │   ├── agent-delegation.md
│   │   ├── compression-protocol.md
│   │   ├── honest-feedback-protocol.md
│   │   ├── memory-protocol.md
│   │   ├── orchestrator-protocol.md
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
│   ├── hooks/                # Automation scripts
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
| **agent-delegation** | Sequential delegation, complete context handoffs |
| **compression-protocol** | Summarize findings, use file:line references |
| **honest-feedback** | Challenge ideas, state confidence levels |
| **memory-protocol** | STAR format for lessons, keep memory lean |
| **orchestrator-protocol** | Plan before action, Scout-first pattern |
| **pre-work-protocol** | Check skills before implementation |
| **quality-gates** | Code review checklists |

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

This setup includes hooks for observability, workflow automation, and protocol enforcement. **All hooks are optional** and can be customized, enabled, or disabled by editing `.claude/settings.json`.

### Currently Configured Hooks

These hooks are active in the default configuration:

| Event | Script | Purpose |
|-------|--------|---------|
| `SessionStart` | `setup-environment.sh` | Environment setup, Node/Python activation, orchestrator reminder |
| `PreToolUse[Task]` | `task_context_tracker.py` | Track agent task lifecycle (start) |
| `PostToolUse[*]` | `tool_trace_logger.py` | Log all tool calls to JSONL |
| `PostToolUse[Task]` | `task_context_tracker.py` | Track agent task lifecycle (end) |
| `PostToolUse[Task]` | `context_sharing.py` | Share context between agents |
| `SessionEnd` | `session_analytics.py` | Generate session metrics report |

### Available but Not Configured

These hooks exist in `.claude/hooks/` but are **not enabled by default**. Enable them by adding to `settings.json`:

| Script | Recommended Event | Purpose |
|--------|-------------------|---------|
| `inject_shared_context.py` | `UserPromptSubmit` | Injects shared context from previous agents into prompts |

**To enable `inject_shared_context.py`**, add this to your `settings.json`:
```json
"UserPromptSubmit": [
  {
    "hooks": [
      {
        "type": "command",
        "command": "python3 \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/inject_shared_context.py"
      }
    ]
  }
]
```

### Output Files

These files are generated by the configured hooks. They can be safely deleted and are git-ignored.

> **Tip:** Consider adding `.gitignore` files to `.claude/logs/` and `.claude/context/` to prevent runtime files from being accidentally committed.

**Located in `.claude/logs/`:**

| File | Purpose | Generated By |
|------|---------|--------------|
| `tool-trace.jsonl` | Detailed tool call history with timestamps, agent attribution, and parameters | `tool_trace_logger.py` |
| `session-metrics.jsonl` | Session analytics (duration, files changed, agents used) | `session_analytics.py` |
| `latest-session-report.txt` | Human-readable summary of most recent session | `session_analytics.py` |
| `.active_tasks.json` | Current subagent task state (transient, auto-cleaned) | `task_context_tracker.py` |

**Located in `.claude/context/`:**

| File | Purpose | Generated By |
|------|---------|--------------|
| `shared-context.json` | Cross-agent decisions, constraints, and insights | `context_sharing.py` |

### Customization

**To disable a hook**: Remove its entry from `.claude/settings.json`.

**To enable an available hook**: Add it to the appropriate event in `settings.json` (see example above).

**To modify a hook**: Edit the script in `.claude/hooks/`. All scripts use standard stdin/stdout patterns.

**Hook types available**:
- `command` - Runs a bash command or script
- `prompt` - Uses LLM for intelligent decisions (only Stop/SubagentStop currently)

**Example - Adding a custom hook**:
```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/my-validator.py"
          }
        ]
      }
    ]
  }
}
```

---

## Getting Started

### Prerequisites

- Node.js 18+ (for frontend)
- Python 3.11+ (for backend)
- Claude Code CLI installed

### Quick Start

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/claude-code-setup.git
cd claude-code-setup

# Install dependencies
npm install

# Start development
npm run dev
```

### Using the Claude Setup

1. Open Claude Code in this directory
2. CLAUDE.md is auto-loaded with universal context
3. Rules are auto-loaded to enforce protocols
4. Skills are auto-discovered based on your conversation

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
| [PROJECT_GUIDELINES.md](PROJECT_GUIDELINES.md) | Coding standards |

---

## Design Philosophy

### Simplicity First
- Build exactly what's needed, nothing more
- Use managed services over custom solutions
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
