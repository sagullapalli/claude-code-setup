---
name: Phoenix Local Development
description: Local-first LLM observability with Arize Phoenix. Use for experimentation, debugging, and combined tracing+evaluation in development.
tags: [phoenix, arize, tracing, evaluation, local, opentelemetry, experimentation]
context7_libraries:
  - /arize-ai/phoenix
last_verified: 2025-12-26
---

# Phoenix Local Development - Quick Reference

**Phoenix** is an open-source AI observability platform - local-first, OpenTelemetry-based, with built-in evaluation.

**Package**: `pip install arize-phoenix`

---

## When to Use Phoenix vs Langfuse

| Factor | Phoenix | Langfuse |
|--------|---------|----------|
| **Best for** | Local dev, experimentation, notebooks | Production monitoring, team collaboration |
| **Deployment** | Local-first (single command) | Cloud-first (self-host available) |
| **Evaluation** | Built-in LLM evals | Separate integration needed |
| **Storage** | SQLite (local) or PostgreSQL | PostgreSQL required |

**Decision**: Phoenix for dev/experimentation, Langfuse for production.

---

## Quick Start

### Installation

```bash
# With evaluation support (recommended)
pip install "arize-phoenix[evals]"

# With provider instrumentation
pip install arize-phoenix-otel openinference-instrumentation-openai
```

### Launch Local Server

```bash
# CLI - runs at http://localhost:6006
phoenix serve
```

```python
# In notebook/script
import phoenix as px

session = px.launch_app()
print(f"Phoenix running at: {session.url}")

# With persistent storage (recommended)
session = px.launch_app(database_url="sqlite:///~/.phoenix/phoenix.db")
```

### Auto-Instrumentation

```python
from phoenix.otel import register
from openinference.instrumentation.openai import OpenAIInstrumentor
from openai import OpenAI

# Setup tracing (sends to local Phoenix)
register(service_name="my-app")
OpenAIInstrumentor().instrument()

# Use OpenAI as normal - traces captured automatically
client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello"}]
)
```

---

## Provider Integrations

| Provider | Package | Instrumentor |
|----------|---------|--------------|
| OpenAI | `openinference-instrumentation-openai` | `OpenAIInstrumentor()` |
| Anthropic | `openinference-instrumentation-anthropic` | `AnthropicInstrumentor()` |
| LiteLLM | `openinference-instrumentation-litellm` | `LiteLLMInstrumentor()` |
| LangChain | `openinference-instrumentation-langchain` | `LangChainInstrumentor()` |

```python
# Pattern: pip install <package>, then:
from openinference.instrumentation.<provider> import <Provider>Instrumentor
<Provider>Instrumentor().instrument()
```

---

## Built-in Evaluation

Phoenix includes LLM-as-judge evaluators - a key differentiator from Langfuse.

### Quick Classification

```python
from phoenix.evals import llm_classify, OpenAIModel
import pandas as pd

results = llm_classify(
    data=pd.DataFrame([{"query": "What is 2+2?", "response": "4"}]),
    template="Is this response correct? {query} -> {response}",
    model=OpenAIModel(model="gpt-4o-mini"),
    rails=["correct", "incorrect"],
    provide_explanation=True,
)
```

### Built-in Evaluators

```python
from phoenix.evals import RelevanceEvaluator, run_evals
from phoenix.models.openai import OpenAIModel

relevance_eval = RelevanceEvaluator(OpenAIModel(model="gpt-4o"))
results = run_evals(evaluators=[relevance_eval], dataframe=traces_df)
```

### Custom LLM Judge

```python
from phoenix.evals import create_classifier
from phoenix.evals.llm import LLM

judge = create_classifier(
    name="helpfulness",
    llm=LLM(model="gpt-4o", provider="openai"),
    prompt_template="Rate if helpful. Query: {input} Response: {output}",
    choices={"helpful": 1, "not_helpful": 0},
)
```

---

## Integration with Our Stack

### With Google ADK (Manual Spans)

```python
import phoenix as px
from phoenix.otel import register
from opentelemetry import trace

px.launch_app()
register(service_name="adk-agent")
tracer = trace.get_tracer(__name__)

async def run_agent(query: str):
    with tracer.start_as_current_span("agent-execution") as span:
        span.set_attribute("input.value", query)
        result = await runner.run_async(user_id, session_id, query)
        span.set_attribute("output.value", str(result))
        return result
```

### With Claude SDK

```python
from phoenix.otel import register
from openinference.instrumentation.anthropic import AnthropicInstrumentor

register(service_name="claude-app")
AnthropicInstrumentor().instrument()
# Claude calls automatically traced
```

---

## Common Gotchas

1. **Port conflicts**: Default 6006 (same as TensorBoard). Use `--port 8080`.
2. **Notebook async**: Use `nest_asyncio.apply()` before `px.launch_app()`.
3. **Temp storage**: Default loses traces on restart. Use `database_url` for persistence.
4. **No ADK instrumentor**: Use manual OpenTelemetry spans for Google ADK.
5. **Eval costs**: Evaluators call LLM APIs - use `gpt-4o-mini` for dev.

---

## Environment Variables

```bash
PHOENIX_PORT=6006
PHOENIX_HOST=0.0.0.0
PHOENIX_COLLECTOR_ENDPOINT=http://localhost:6006
PHOENIX_DATABASE_URL=sqlite:///~/.phoenix/phoenix.db
```

---

## Context7 Lookup Topics

```
get-library-docs: /arize-ai/phoenix (topic: "launch app server")
get-library-docs: /arize-ai/phoenix (topic: "instrumentation openai")
get-library-docs: /arize-ai/phoenix (topic: "evals llm classify")
get-library-docs: /arize-ai/phoenix (topic: "experiments datasets")
```

---

## Related Skills

- **[SKILL.md](SKILL.md)** - LLM Observability overview
- **[../llm-evaluation/SKILL.md](../llm-evaluation/SKILL.md)** - DeepEval patterns

---

**Last Updated**: 2025-12-26
