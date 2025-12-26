# Kai - AI Engineer

Last updated: 2025-12-26 (agent file Phase 3 updates)

## Active Protocols (Read Every Session)

### Skills-First Protocol
**MANDATORY**: Before ANY AI/ML implementation or debugging:
1. Identify technology/domain (ADK, Vertex AI, Claude Agent SDK, etc.)
2. Check `.claude/skills/[technology]-patterns/`
3. Search for relevant pattern (2 minutes)
4. Use documented pattern if found, OR investigate + document after verification

**Full protocol**: See CLAUDE.md

## Project Config
- **Project**: [Project Name]
- **GCP Project**: [To be configured]
- **Region**: europe-west1 (ALWAYS use Europe regions)
- **Stack**: [To be configured]
- **Repository**: /home/sunny/projects/interface

## Current Status

**Phase**: Skills expansion (Phase 3) - COMPLETE
- Created `claude-agent-sdk-patterns/` skill directory (renamed from claude-sdk-patterns)
- Created `llm-evaluation/` skill directory (DeepEval patterns)
- Created `llm-observability/` skill directory (Langfuse patterns)
- Updated `google-adk-patterns/` to hybrid format with Context7 integration
- Updated agent file with Phase 3 changes (Context7 awareness, flexible stack, eval/observability)

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
- `/google/adk-docs` - Google ADK docs (5419 snippets, primary)
- `/google/adk-python` - Google ADK Python SDK
- `/google/adk-samples` - Google ADK samples
- `/confident-ai/deepeval` - DeepEval LLM evaluation
- `/langfuse/langfuse-docs` - Langfuse observability (5037 snippets)
- `/arize-ai/phoenix` - Phoenix local observability (3783 snippets)

## Lessons Learned

### Hybrid Skills Approach (2025-12-26)
**Situation**: Creating new skills for Claude Agent SDK
**Task**: Document patterns without duplicating Context7 content
**Action**: Created lean skills with decision guidance + Context7 pointers
**Result**: 4 files under 200 lines each, maintainable structure
**Pattern**: Skills = decisions/conventions/gotchas; Context7 = live API reference
**Files**: `.claude/skills/claude-sdk-patterns/` (SKILL.md, 01-03 modules)

### Claude Agent SDK Key Gotchas (2025-12-26)
- **MCP tool naming**: Must use `mcp__<server>__<tool>` in `allowed_tools`
- **Response iteration**: Must iterate `receive_response()` or messages are lost
- **Context manager**: Always use `async with ClaudeSDKClient()` for cleanup
- **Hook matching**: Matcher must exactly match tool name (case-sensitive)
- **Async required**: All hooks and tools must be async functions

### DeepEval LLM Evaluation Key Patterns (2025-12-26)
- **When to evaluate**: Before deploy, after prompt changes, after model updates
- **Metric selection**: AnswerRelevancy for Q&A, Faithfulness for RAG, GEval for custom
- **RAG metrics**: ContextualPrecision/Recall/Relevancy for retrieval, Faithfulness for grounding
- **LLM-as-judge costs**: Each metric = API call; use `gpt-4o-mini` for dev
- **Gotcha**: `retrieval_context` must be list of strings, not dict
- **Thresholds**: Start low (0.5), raise per-environment (0.7+ for prod)

### Langfuse Observability Key Patterns (2025-12-26)
- **Primary pattern**: `@observe()` decorator for automatic tracing
- **OpenAI integration**: Drop-in replacement `from langfuse.openai import openai`
- **Flushing**: Always call `langfuse.flush()` in short-lived processes (Cloud Run, Lambda)
- **Cost tracking**: Requires usage_details with input/output token counts
- **Scores**: `span.score()` for observation, `span.score_trace()` for whole trace
- **Gotcha**: Traces batched (up to 5s delay); won't appear instantly in UI
- **Decision**: Use Langfuse Cloud for dev/most prod; self-host only for data residency

### Phoenix Local Development Key Patterns (2025-12-26)
- **When to use**: Local experimentation, notebooks, built-in evals (vs Langfuse for production)
- **Quick start**: `phoenix serve` CLI or `px.launch_app()` in notebooks
- **Instrumentation**: OpenTelemetry-based via `openinference-instrumentation-*` packages
- **Built-in evals**: `llm_classify()`, `RelevanceEvaluator`, `HallucinationEvaluator`
- **Gotcha**: Default `launch_app()` uses temp storage; use `database_url` for persistence
- **Gotcha**: No dedicated ADK instrumentor; use manual OpenTelemetry spans
- **Context7 library**: `/arize-ai/phoenix` (3783 snippets, benchmark 85.3)

### OpenLLMetry Key Patterns (2025-12-26)
- **When to use**: Existing OTEL infrastructure, GCP Cloud Trace, Datadog, Honeycomb
- **Package**: `traceloop-sdk` (auto-instruments) or individual `opentelemetry-instrumentation-*`
- **GCP Cloud Trace**: Use `opentelemetry-exporter-gcp-trace` or native OTLP to `telemetry.googleapis.com`
- **Providers**: OpenAI, Anthropic, Vertex AI, Google GenAI, Bedrock auto-instrumented
- **Decorators**: `@workflow`, `@task`, `@agent` for semantic grouping
- **Gotcha**: `disable_batch=True` for local dev to see traces immediately
- **Gotcha**: `TRACELOOP_TRACE_CONTENT=false` for privacy (no prompts/completions logged)
- **Context7 library**: `/traceloop/openllmetry` (97 snippets, benchmark 46.7)

### Google ADK Hybrid Format Update (2025-12-26)
- **Updated**: `google-adk-patterns/` skill to hybrid format with Context7 integration
- **Context7 libraries**: `/google/adk-docs` (5419 snippets), `/google/adk-python`, `/google/adk-samples`
- **Verified current models (Dec 2025)**:
  - `gemini-2.0-flash` - Fast, reliable, good for most agent use cases
  - `gemini-3-flash-preview` - Pro-level intelligence at Flash speed/pricing
  - `gemini-3-pro-preview` - Most capable model, best for complex reasoning
- **API verified**: `LlmAgent` class name unchanged, import paths still `from google.adk.agents import LlmAgent`
- **Pattern**: Project-specific gotchas preserved, Context7 pointers added for live API reference

### Vertex AI Gen AI Evaluation Service (2025-12-26)
- **File**: `.claude/skills/llm-evaluation/05-vertex-ai-evaluation.md` (229 lines, condensed)
- **Two API patterns**: Unified Client (`vertexai.Client().evals`) vs EvalTask (experiment tracking)
- **Unique features**: Adaptive rubrics (auto-generated criteria per prompt), trajectory evaluation
- **Agent trajectory metrics**: `trajectory_exact_match`, `trajectory_in_order_match`, precision, recall
- **When to use**: GCP-native stack, Gemini model evaluation, agent trajectory analysis
- **Gotchas**: Region availability varies; column names case-sensitive; experiment param for tracking
- **Context7 library**: `/googleapis/python-aiplatform`

### Agent File Phase 3 Update (2025-12-26)
- **Updated**: `.claude/agents/ai-engineer.md` with Phase 3 changes
- **Changes made**:
  - Added Context7 section for live documentation awareness (lines 101-128)
  - Made technology stack flexible (lines 150-187): ADK is default but alternatives acknowledged
  - Added LLM Evaluation Principles section (lines 288-303)
  - Added AI Observability Principles section (lines 307-317)
  - Updated skills reference table with new skills (lines 58-67)
  - Reorganized anti-patterns into categories: General, LLM, Agent, ADK-specific (lines 471-510)
- **Renamed**: `claude-sdk-patterns/` to `claude-agent-sdk-patterns/` for clarity

## Documentation Map

| Topic | Document | What It Contains |
|-------|----------|------------------|
| Claude Agent SDK | `.claude/skills/claude-agent-sdk-patterns/SKILL.md` | Basics, tools, hooks |
| Google ADK | `.claude/skills/google-adk-patterns/SKILL.md` | Events, state, tools |
| LLM Evaluation | `.claude/skills/llm-evaluation/SKILL.md` | DeepEval, metrics, RAG |
| LLM Observability | `.claude/skills/llm-observability/SKILL.md` | Langfuse, tracing, cost |
| Skills Expansion | `docs/PHASE_3_KAI_SKILLS_EXPANSION.md` | Roadmap for new skills |

---

**Memory Guidelines:**
- Keep entries concise with bullet points
- Record specifics (paths, commands, project IDs, regions)
- Focus on project-specific context, not general patterns (those go in skills)
- Update after significant milestones or discoveries
