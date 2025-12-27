---
name: LLM Observability Patterns
description: Tracing and monitoring patterns for LLM applications using Langfuse, Phoenix, and OpenLLMetry. Use when adding observability, debugging AI calls, or tracking costs.
tags: [llm, observability, tracing, langfuse, phoenix, arize, openllmetry, opentelemetry, monitoring, cost, tokens]
context7_libraries:
  - /langfuse/langfuse-docs
  - /langfuse/langfuse-python
  - /arize-ai/phoenix
  - /traceloop/openllmetry
last_verified: 2025-12-26
---

# LLM Observability Patterns - Quick Reference

This skill covers three complementary observability platforms:
- **Langfuse** - Production-focused, cloud-first, team collaboration
- **Phoenix** - Local-first, combined tracing+evaluation, experimentation
- **OpenLLMetry** - OpenTelemetry-based, export to any OTLP backend (Datadog, GCP, etc.)

**Packages**: `pip install langfuse` | `pip install arize-phoenix` | `pip install traceloop-sdk`

---

## Modules

### Langfuse (Production)

1. **[01-langfuse-setup.md](01-langfuse-setup.md)** - Setup & Configuration
   - Installation and environment setup
   - Cloud vs self-hosted deployment
   - Project conventions

2. **[02-tracing-patterns.md](02-tracing-patterns.md)** - Tracing Patterns
   - @observe decorator usage
   - Manual spans and generations
   - Integration with OpenAI, Anthropic, ADK

3. **[03-cost-tracking.md](03-cost-tracking.md)** - Cost & Evaluation
   - Token usage tracking
   - Cost monitoring and budgets
   - Scores and user feedback

### Phoenix (Local Development)

4. **[04-phoenix-local-dev.md](04-phoenix-local-dev.md)** - Local-First Observability
   - Quick local server setup
   - OpenTelemetry-based instrumentation
   - Built-in LLM evaluators
   - Notebook integration

### OpenLLMetry (OpenTelemetry Export)

5. **[05-openllmetry-otel.md](05-openllmetry-otel.md)** - OpenTelemetry Integration
   - Export to any OTLP backend (Datadog, Honeycomb, Grafana)
   - GCP Cloud Trace integration
   - OpenTelemetry semantic conventions for LLMs
   - Auto-instrumentation for major providers

---

## When to Use Which Platform

| Need | Langfuse | Phoenix | OpenLLMetry | Recommendation |
|------|----------|---------|-------------|----------------|
| Local experimentation | OK | Best | OK | Phoenix |
| Production monitoring | Best | OK | Good | Langfuse or OpenLLMetry |
| Team collaboration | Best | Limited | Via backend | Langfuse |
| Built-in LLM evals | No | Yes | No | Phoenix |
| Existing OTEL infra | No | Yes | Best | OpenLLMetry |
| GCP Cloud Trace | No | Manual | Native | OpenLLMetry |
| Datadog/Honeycomb | No | No | Native | OpenLLMetry |
| Cost tracking | Best | Basic | Via backend | Langfuse |
| No account/setup | No | Yes | No | Phoenix |

**Rule of thumb**:
- Phoenix for dev/experimentation
- Langfuse for LLM-focused production monitoring
- OpenLLMetry when you have existing OTEL infrastructure or need GCP Cloud Trace

---

## Decision: Cloud vs Self-Hosted

| Factor | Langfuse Cloud | Self-Hosted |
|--------|----------------|-------------|
| **Setup** | Instant (sign up) | Docker Compose or K8s |
| **Cost** | Free tier + paid plans | Infrastructure cost |
| **Data privacy** | Data on Langfuse servers | Full data control |
| **Maintenance** | Managed by Langfuse | You maintain |
| **Recommendation** | Start here, migrate if needed | Regulated industries |

**Decision**: Use **Langfuse Cloud** for development and most production. Self-host only if data residency requirements mandate it.

---

## Quick Start Pattern

```python
# 1. Install
# pip install langfuse

# 2. Set environment variables
# LANGFUSE_PUBLIC_KEY="pk-lf-..."
# LANGFUSE_SECRET_KEY="sk-lf-..."
# LANGFUSE_HOST="https://cloud.langfuse.com"  # or self-hosted URL

# 3. Use @observe decorator
from langfuse import observe

@observe()
def my_llm_function(prompt: str) -> str:
    # Your LLM call here
    return response
```

---

## Integration with Our Stack

### With FastAPI
- Use `@observe()` on route handlers or service functions
- Flush on shutdown: `langfuse.flush()` in lifespan

### With Google ADK
- Wrap agent execution with `@observe()`
- Use manual spans for tool calls
- See [02-tracing-patterns.md](02-tracing-patterns.md) for patterns

### With Claude SDK
- Use `@observe()` on functions calling Claude
- Manual generation spans for detailed tracking

---

## What to Trace

**Always trace:**
- LLM API calls (input, output, model, tokens)
- Agent tool invocations
- Retrieval/RAG operations
- Error states and retries

**Metadata to include:**
- `user_id` - For per-user analytics
- `session_id` - Group related requests
- `tags` - Categorize by feature/endpoint
- `version` - Track prompt/model versions

---

## Project Conventions

### Span Naming
```
# Pattern: {component}-{operation}
chat-completion
rag-retrieval
agent-tool-call
```

### Metadata Structure
```python
{
    "user_id": "user-123",
    "session_id": "session-abc",
    "environment": "production",
    "version": "v1.2.0",
    "feature": "chat-assistant"
}
```

---

## Common Gotchas

1. **Async context**: `@observe()` works with async functions automatically
2. **Flushing**: Call `langfuse.flush()` before shutdown in short-lived processes
3. **Batching**: Langfuse batches events; traces may not appear instantly
4. **Data privacy**: Never log PII in inputs/outputs; use filtering
5. **Cost calculation**: Requires model definitions in Langfuse for auto-cost

---

## Context7 Lookup Topics

For current API patterns, use Context7:

**Langfuse:**
```
get-library-docs: /langfuse/langfuse-docs (topic: "observe decorator")
get-library-docs: /langfuse/langfuse-docs (topic: "cost tracking usage")
get-library-docs: /langfuse/langfuse-docs (topic: "scores evaluation")
get-library-docs: /langfuse/langfuse-docs (topic: "openai integration")
```

**Phoenix:**
```
get-library-docs: /arize-ai/phoenix (topic: "launch app server")
get-library-docs: /arize-ai/phoenix (topic: "instrumentation openai")
get-library-docs: /arize-ai/phoenix (topic: "evals llm classify")
get-library-docs: /arize-ai/phoenix (topic: "experiments datasets")
```

**OpenLLMetry:**
```
get-library-docs: /traceloop/openllmetry (topic: "traceloop sdk init")
get-library-docs: /traceloop/openllmetry (topic: "instrumentation openai anthropic")
get-library-docs: /traceloop/openllmetry (topic: "workflow decorator")
```

---

## Related Skills

- **[llm-evaluation](../llm-evaluation/SKILL.md)** - DeepEval patterns for testing
- **[google-adk-patterns](../google-adk-patterns/SKILL.md)** - ADK agent patterns

---

**Last Updated**: 2025-12-26
