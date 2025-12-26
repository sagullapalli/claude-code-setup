---
name: OpenLLMetry OpenTelemetry Integration
description: LLM observability using OpenTelemetry standards with OpenLLMetry. Use when you have existing OTEL infrastructure or need export to Datadog, Honeycomb, Grafana, or GCP Cloud Trace.
tags: [openllmetry, opentelemetry, otel, tracing, gcp, cloud-trace, datadog, honeycomb, grafana, llm]
context7_libraries:
  - /traceloop/openllmetry
last_verified: 2025-12-26
---

# OpenLLMetry (OpenTelemetry) - Quick Reference

**OpenLLMetry** is a set of OpenTelemetry extensions for LLM observability. Export to any OTLP-compatible backend.

**Package**: `pip install traceloop-sdk`

---

## When to Use OpenLLMetry vs Langfuse/Phoenix

| Factor | OpenLLMetry | Langfuse | Phoenix |
|--------|-------------|----------|---------|
| **Best for** | Existing OTEL infrastructure | LLM-first production | Local dev |
| **Backend** | Any OTLP (Datadog, Honeycomb, GCP) | Langfuse Cloud/self-host | Local SQLite |
| **Setup** | Configure OTLP exporter | API keys | Zero config |
| **Standards** | OpenTelemetry semantic conventions | Proprietary | OpenTelemetry |

**Decision tree**:
- Existing OTEL infrastructure (Datadog, Honeycomb, Grafana)? -> OpenLLMetry
- Need LLM-specific UI, prompt management, scores? -> Langfuse
- Local experimentation with built-in evals? -> Phoenix
- GCP-native, want Cloud Trace integration? -> OpenLLMetry + GCP exporter

---

## Quick Start

### Installation

```bash
# Core SDK (auto-instruments common providers)
pip install traceloop-sdk

# Individual instrumentors (if not using SDK)
pip install opentelemetry-instrumentation-openai
pip install opentelemetry-instrumentation-anthropic
pip install opentelemetry-instrumentation-vertexai
pip install opentelemetry-instrumentation-google-generativeai
```

### Basic Setup

```python
from traceloop.sdk import Traceloop

# Initialize - auto-instruments OpenAI, Anthropic, etc.
Traceloop.init(app_name="my-llm-app")

# For local development (see traces immediately)
Traceloop.init(app_name="my-llm-app", disable_batch=True)
```

### Environment Variables

```bash
# OTLP endpoint (required for non-Traceloop backends)
OTEL_EXPORTER_OTLP_ENDPOINT=https://your-collector:4317
OTEL_EXPORTER_OTLP_HEADERS="Authorization=Bearer your-token"

# Service identification
OTEL_SERVICE_NAME=my-llm-app

# Privacy: disable prompt/completion logging
TRACELOOP_TRACE_CONTENT=false

# Disable anonymous telemetry
TRACELOOP_TELEMETRY=false
```

---

## Provider Auto-Instrumentation

OpenLLMetry auto-instruments these LLM providers:

| Provider | Package | Instrumentor |
|----------|---------|--------------|
| OpenAI | `opentelemetry-instrumentation-openai` | `OpenAIInstrumentor()` |
| Anthropic | `opentelemetry-instrumentation-anthropic` | `AnthropicInstrumentor()` |
| Vertex AI | `opentelemetry-instrumentation-vertexai` | `VertexAIInstrumentor()` |
| Google GenAI | `opentelemetry-instrumentation-google-generativeai` | `GoogleGenerativeAiInstrumentor()` |
| Bedrock | `opentelemetry-instrumentation-bedrock` | `BedrockInstrumentor()` |

### Manual Instrumentation (without SDK)

```python
from opentelemetry.instrumentation.openai import OpenAIInstrumentor
from opentelemetry.instrumentation.anthropic import AnthropicInstrumentor

OpenAIInstrumentor().instrument()
AnthropicInstrumentor().instrument()
```

---

## GCP Cloud Trace Integration

Export OpenLLMetry traces directly to Google Cloud Trace.

### Installation

```bash
pip install traceloop-sdk opentelemetry-exporter-gcp-trace
```

### Setup with Cloud Trace Exporter

```python
from traceloop.sdk import Traceloop
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter

# Create Cloud Trace exporter
gcp_exporter = CloudTraceSpanExporter(project_id="your-gcp-project")

# Initialize with GCP exporter
Traceloop.init(
    app_name="my-llm-app",
    exporter=gcp_exporter,
)

# Now all LLM calls trace to Cloud Trace
```

### Native OTLP to GCP (Recommended - 2025)

Google Cloud now supports native OTLP ingestion - no vendor-specific exporter needed:

```python
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from traceloop.sdk import Traceloop

# Send directly to GCP's OTLP endpoint
exporter = OTLPSpanExporter(
    endpoint="https://telemetry.googleapis.com:443",
)

Traceloop.init(app_name="my-llm-app", exporter=exporter)
```

**Note**: Requires GCP authentication (ADC or service account with `cloudtrace.traces.patch` permission).

---

## Export to Common Backends

| Backend | Endpoint | Auth Header |
|---------|----------|-------------|
| Datadog | `https://trace.agent.datadoghq.com:443` | `DD_API_KEY=...` |
| Honeycomb | `https://api.honeycomb.io` | `x-honeycomb-team=...` |
| Grafana | `https://otlp-gateway-prod-xx.grafana.net/otlp` | `Authorization=Basic ...` |

Set via `OTEL_EXPORTER_OTLP_ENDPOINT` and `OTEL_EXPORTER_OTLP_HEADERS`.

---

## Workflow Decorators

```python
from traceloop.sdk.decorators import workflow, task, agent

@workflow(name="chat")       # Groups nested LLM calls
@task(name="retrieval")      # Marks specific operations
@agent(name="researcher")    # Marks agent-level spans
```

---

## Integration with Our Stack

### With Google ADK

```python
from traceloop.sdk import Traceloop
from traceloop.sdk.decorators import workflow
from opentelemetry.instrumentation.vertexai import VertexAIInstrumentor

Traceloop.init(app_name="adk-agent")
VertexAIInstrumentor().instrument()

@workflow(name="agent_execution")
async def run_agent(query: str):
    result = await runner.run_async(user_id, session_id, query)
    return result
```

### With FastAPI

```python
from fastapi import FastAPI
from traceloop.sdk import Traceloop
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    Traceloop.init(app_name="api-service")
    yield
    # Traces flushed on shutdown

app = FastAPI(lifespan=lifespan)
```

---

## Common Gotchas

1. **Auth for GCP**: Ensure ADC configured or `GOOGLE_APPLICATION_CREDENTIALS` set
2. **Batching delay**: Traces batched by default. Use `disable_batch=True` for local dev
3. **Content privacy**: Set `TRACELOOP_TRACE_CONTENT=false` to avoid logging prompts
4. **SSL errors**: Set `OTEL_EXPORTER_OTLP_INSECURE=true` for self-signed certs
5. **No dedicated ADK instrumentor**: Use Vertex AI instrumentor + manual spans

---

## Context7 Lookup Topics

```
get-library-docs: /traceloop/openllmetry (topic: "traceloop sdk init")
get-library-docs: /traceloop/openllmetry (topic: "instrumentation openai anthropic")
get-library-docs: /traceloop/openllmetry (topic: "workflow decorator")
```

---

## Related Skills

- **[SKILL.md](SKILL.md)** - LLM Observability overview
- **[04-phoenix-local-dev.md](04-phoenix-local-dev.md)** - Phoenix local tracing

---

**Last Updated**: 2025-12-26
