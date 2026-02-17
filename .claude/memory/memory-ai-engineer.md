# Kai - AI Engineer

Last updated: 2026-02-17

## Active Protocols (Read Every Session)

### Skills-First Protocol
**MANDATORY**: Before ANY AI/ML implementation or debugging:
1. Identify technology/domain (ADK, Vertex AI, Claude Agent SDK, etc.)
2. Check `.claude/skills/[technology]-patterns/`
3. Search for relevant pattern (2 minutes)
4. Use documented pattern if found, OR investigate + document after verification

**Full protocol**: See CLAUDE.md

## Project Config
- **Project**: [Your Project Name]
- **GCP Project**: [To be configured]
- **Region**: europe-west1 (ALWAYS use Europe regions)
- **Stack**: [To be configured]
- **Repository**: /path/to/your-project

## Current Status

**Phase**: Active Development
- News Research Agent built (greenfield ADK app)
- Location: `/home/user/claude-code-setup/news_agent/`
- Runnable via `adk web` (from project root) or `python run_cli.py`

## AI/Agent Architecture

**Available Agent Frameworks**:
| Framework | Package | Use Case |
|-----------|---------|----------|
| Google ADK | `google-adk` | GCP-native agents, Vertex AI |
| Claude Agent SDK | `claude-agent-sdk` | Claude Code capabilities |

## Code Patterns

- **Claude Agent SDK**: See `.claude/skills/claude-agent-sdk-patterns/SKILL.md`
  - `query()` for one-shot, `ClaudeSDKClient` for multi-turn
  - `@tool` decorator + `create_sdk_mcp_server()` for custom tools
  - Hooks for tool validation (PreToolUse/PostToolUse)

- **Google ADK**: See `.claude/skills/google-adk-patterns/SKILL.md`
  - `LlmAgent` + `InMemoryRunner` pattern
  - Manual event persistence required

## Critical Files & Commands

**Skills Locations**:
- `.claude/skills/google-adk-patterns/` - Google ADK
- `.claude/skills/claude-agent-sdk-patterns/` - Claude Agent SDK
- `.claude/skills/llm-evaluation/` - DeepEval LLM evaluation
- `.claude/skills/llm-observability/` - Langfuse tracing & monitoring

**Context7 Libraries**:
- `/anthropics/claude-agent-sdk-python` - Agent SDK docs
- `/anthropics/anthropic-sdk-python` - Base SDK docs
- `/google/adk-docs` - Google ADK docs
- `/confident-ai/deepeval` - DeepEval LLM evaluation
- `/langfuse/langfuse-docs` - Langfuse observability

## Lessons Learned

- **ADK Built-in Google Search**: Import is `from google.adk.tools import google_search`. Pass directly to `tools=[google_search]`.
- **Built-in tool limitation**: Only ONE built-in tool per agent allowed. No other tools (custom or built-in) can be mixed with `google_search` in the same agent. Use multi-agent pattern if needed.
- **ADK project structure for `adk web`**: Requires `agent_dir/agent.py` (with `root_agent` variable) + `agent_dir/__init__.py` (with `from . import agent`). Run `adk web` from parent directory.
- **ADK `.env` support**: ADK automatically loads `.env` from the agent directory for env vars like `GOOGLE_API_KEY`.
- **Agent class alias**: Newer ADK versions (1.19+) support `Agent` as alias for `LlmAgent`. Both work.

## Documentation Map

| Topic | Document | What It Contains |
|-------|----------|------------------|
| Claude Agent SDK | `.claude/skills/claude-agent-sdk-patterns/SKILL.md` | Basics, tools, hooks |
| Google ADK | `.claude/skills/google-adk-patterns/SKILL.md` | Events, state, tools |
| LLM Evaluation | `.claude/skills/llm-evaluation/SKILL.md` | DeepEval, metrics, RAG |
| LLM Observability | `.claude/skills/llm-observability/SKILL.md` | Langfuse, tracing, cost |

---

**Memory Guidelines:**
- Keep entries concise with bullet points
- Record specifics (paths, commands, project IDs, regions)
- Focus on project-specific context, not general patterns (those go in skills)
- Update after significant milestones or discoveries
