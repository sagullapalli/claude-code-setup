# Phase 3: Kai (AI Engineer) Skills Expansion

**Created**: 2025-12-26
**Purpose**: Context document for expanding Kai's capabilities as a technology-agnostic AI Engineer
**Status**: Planned (for future session)

---

## Background

During the agent instructions review (2025-12-26), we identified that Kai's current instructions focus heavily on Google ADK, FastAPI & Vertex AI. While this worked well for the previous project, a modern AI Engineer should be technology-agnostic and able to work with various AI/ML stacks.

### Current State

**Kai's agent file**: `.claude/agents/ai-engineer.md` (579 lines after Phase 1-2 cleanup)

**Current technology focus**:
- Google ADK (primary agent framework)
- Vertex AI / Gemini models
- FastAPI for APIs
- PostgreSQL for data

**Identified gaps**:
- No multi-provider LLM support patterns
- No evaluation framework knowledge
- No observability patterns for AI systems
- Limited RAG/vector database patterns
- No prompt engineering guidelines

---

## Research Findings: Modern AI Engineer Skills (2025)

### Core Skills (Technology-Agnostic)

| Skill Category | Description |
|----------------|-------------|
| **LLM Fundamentals** | Tokenization, prompt engineering, fine-tuning, RAG, context management |
| **Agent Design** | Multi-agent systems, tool use, memory management, conversation flow |
| **Evaluation & Testing** | LLM evals, accuracy metrics, hallucination detection, regression testing |
| **Observability** | Tracing, latency monitoring, token usage, cost optimization |
| **MLOps** | CI/CD for AI, model versioning, A/B testing, deployment pipelines |
| **Data Engineering** | Vector embeddings, chunking strategies, retrieval optimization |
| **Security** | Prompt injection prevention, PII filtering, output validation, guardrails |

### Key Technologies by Category

#### LLM Provider SDKs

| Provider | SDK | Notes |
|----------|-----|-------|
| Anthropic | Claude SDK / Agent SDK | Programmatic tool calling, 37% token reduction patterns |
| OpenAI | OpenAI SDK | Most widely used, GPT-4/5 |
| Google | ADK / Vertex AI | Currently in Kai's stack |

**Priority**: Add Claude SDK patterns (given this project uses Claude Code)

#### Orchestration Frameworks

| Framework | Strength | When to Use |
|-----------|----------|-------------|
| LangChain | General-purpose pipelines, tool integration | Complex workflows, multi-step reasoning |
| LangGraph | Stateful graph-based workflows | Multi-agent coordination |
| LlamaIndex | RAG-optimized, retrieval-first | Document-heavy apps, knowledge bases |
| CrewAI | Role-based task execution | Collaborative agent teams, quick prototypes |
| AutoGen | Conversational multi-agent | Complex problem-solving, auditable workflows |
| Google ADK | Google-native, Vertex AI integration | GCP projects (current default) |

#### Evaluation Frameworks

| Tool | Type | Key Feature |
|------|------|-------------|
| DeepEval | Open-source | 30+ prebuilt metrics, pytest-like syntax |
| OpenAI Evals | Open-source | Benchmark registry, custom evals |
| LangSmith | Platform | LangChain integration, fast iteration |
| Arize | Enterprise | Online evals for agents, traces |
| RAGAS | Open-source | RAG-specific evaluation metrics |

**Priority**: Add DeepEval patterns (pytest-compatible, open-source)

#### Observability Tools

| Tool | Type | Strength |
|------|------|----------|
| Langfuse | Open-source | Most used, comprehensive tracing |
| Datadog LLM Observability | Enterprise | End-to-end tracing, security evals |
| OpenTelemetry | Standard | Cross-platform, industry standard |
| Weights & Biases | Platform | Experiment tracking, model versioning |

**Priority**: Add Langfuse patterns (open-source, widely adopted)

#### Vector Databases

| Database | Strength | Best For |
|----------|----------|----------|
| Pinecone | Serverless, fast | Production RAG |
| Milvus | Scale (billions of vectors) | Enterprise, distributed |
| Qdrant | Memory efficient, Rust | Hybrid search, filtering |
| Chroma | Simple API | Prototyping, smaller projects |
| pgvector | PostgreSQL extension | Projects already using PostgreSQL |

**Priority**: Add pgvector patterns (aligns with existing PostgreSQL stack)

#### Model Serving/Inference

| Tool | Strength | Trade-off |
|------|----------|-----------|
| vLLM | PagedAttention, easy setup | Good performance, great flexibility |
| TensorRT-LLM | Max performance on NVIDIA | Complex setup, NVIDIA-only |
| Ollama | Local models, easy setup | Good for development |

---

## Recommended New Skills

### High Priority

| Skill Directory | Content | Estimated Size |
|-----------------|---------|----------------|
| `claude-sdk-patterns/` | Anthropic SDK usage, programmatic tool calling, agent SDK patterns | Level 2 (~300 lines across files) |
| `llm-evaluation/` | DeepEval setup, custom metrics, RAG evaluation (RAGAS), regression testing | Level 2 (~250 lines) |

### Medium Priority

| Skill Directory | Content | Estimated Size |
|-----------------|---------|----------------|
| `llm-observability/` | Langfuse integration, OpenTelemetry for LLMs, tracing patterns | Level 2 (~200 lines) |
| `prompt-engineering/` | Chain-of-thought, few-shot, prompt scaffolding, temperature tuning | Level 1 (~150 lines) |

### Lower Priority (Project-Dependent)

| Skill Directory | Content | Estimated Size |
|-----------------|---------|----------------|
| `rag-patterns/` | Vector DB selection (pgvector focus), chunking strategies, hybrid search | Level 2 (~300 lines) |
| `multi-provider-llm/` | Abstraction layer for Claude/OpenAI/Gemini, provider switching | Level 1 (~100 lines) |

---

## Proposed Changes to Kai's Agent File

### 1. Update Technology Stack Section

**Current** (lines 198-241): Locked to ADK/Vertex AI

**Proposed**: Make ADK the default but acknowledge alternatives

```markdown
## Technology Stack

### Default Stack (Project Preference)
- **Agent Framework**: Google ADK (primary)
- **LLM Provider**: Vertex AI / Gemini models
- **API Framework**: FastAPI
- **Database**: PostgreSQL with pgvector for embeddings

### Alternative Stacks (When Required)
- **Claude/Anthropic projects**: Use Claude SDK patterns
- **OpenAI projects**: Use OpenAI SDK patterns
- **RAG-heavy apps**: Consider LlamaIndex alongside ADK

### Cross-Cutting Concerns (Always Apply)
- **Evaluation**: Use eval framework for all AI features
- **Observability**: Trace all LLM calls in production
- **Security**: Validate inputs, sanitize outputs
```

### 2. Add New Sections

#### Evaluation Principles
```markdown
## LLM Evaluation

**Principle**: "Eyeballing outputs is ending" - formal evaluation is required.

### When to Evaluate
- Before deploying any AI feature
- After prompt changes
- After model updates

### Metrics to Track
- Accuracy/correctness for factual tasks
- Relevance for retrieval (RAG apps)
- Helpfulness for conversational agents
- Latency and cost per request

**Skill Reference**: See `llm-evaluation/` for DeepEval patterns
```

#### Observability Principles
```markdown
## AI Observability

**Principle**: Production AI needs tracing from day one.

### What to Trace
- All LLM calls (input, output, tokens, latency)
- Agent tool calls and decisions
- Error rates and failure modes
- Cost per request/session

**Skill Reference**: See `llm-observability/` for Langfuse patterns
```

### 3. Update Anti-Patterns Section

Add technology-agnostic anti-patterns:

```markdown
## Anti-Patterns (AI Engineering)

### LLM Anti-Patterns
- **No evals before deploy**: Always run evaluation suite
- **Ignoring token costs**: Track and optimize token usage
- **Hardcoded prompts**: Use templating, version prompts
- **No observability**: Trace all production LLM calls

### Agent Anti-Patterns
- **Unlimited tool loops**: Set max iterations
- **No error boundaries**: Handle LLM failures gracefully
- **Memory without limits**: Implement context window management
```

---

## Implementation Plan

### Step 1: Create New Skills (Priority Order)

1. **claude-sdk-patterns/** - Start here given project uses Claude Code
   - SKILL.md with frontmatter
   - REFERENCE.md for detailed API patterns
   - EXAMPLES.md for common use cases

2. **llm-evaluation/** - Critical for production readiness
   - SKILL.md with DeepEval setup
   - METRICS.md for metric selection guide
   - TESTING.md for integration with pytest

3. **llm-observability/** - Production essential
   - SKILL.md with Langfuse setup
   - TRACING.md for tracing patterns
   - COST.md for cost tracking

### Step 2: Update Kai's Agent File

1. Update Technology Stack section (make it flexible)
2. Add Evaluation Principles section
3. Add Observability Principles section
4. Update Anti-Patterns with AI-specific items
5. Update Quality Checklist to include eval/observability checks

### Step 3: Update Skill Reference Table

Add new skills to Kai's reference table:

| Task Type | Trigger Keywords | Related Skill |
|-----------|-----------------|---------------|
| Claude/Anthropic | "Claude SDK", "Anthropic", "tool calling" | claude-sdk-patterns/ |
| LLM Testing | "eval", "LLM testing", "accuracy" | llm-evaluation/ |
| Tracing/Monitoring | "observability", "tracing", "Langfuse" | llm-observability/ |
| RAG/Embeddings | "RAG", "vector", "embeddings" | rag-patterns/ |

---

## Resources for Implementation

### Documentation Links

- **Claude SDK**: https://docs.anthropic.com/en/docs/claude-code/sdk
- **Claude Agent SDK**: https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk
- **DeepEval**: https://github.com/confident-ai/deepeval
- **Langfuse**: https://langfuse.com/docs
- **RAGAS**: https://docs.ragas.io/

### Reference Implementations

- Claude tool calling patterns: See Anthropic engineering blog
- DeepEval pytest integration: See DeepEval docs
- Langfuse tracing: See Langfuse Python SDK docs

---

## Success Criteria

After Phase 3 completion:

1. **Skills created**: At least claude-sdk-patterns/, llm-evaluation/, llm-observability/
2. **Kai updated**: Technology-agnostic sections, eval/observability principles added
3. **Reference table updated**: New skills included
4. **No regression**: ADK patterns still work, just not the only option
5. **Validated**: Test that Kai can work with both ADK and Claude SDK projects

---

## Notes

- Keep ADK as the default for this project (backwards compatible)
- New skills should follow Level 2 structure (SKILL.md + reference files)
- Consider creating skills incrementally based on actual project needs
- The goal is flexibility, not mandating all technologies at once
