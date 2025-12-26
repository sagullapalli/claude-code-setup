# Cost Tracking & Evaluation

## Token Usage Tracking

### Automatic (with OpenAI Integration)
```python
from langfuse.openai import openai

client = openai.OpenAI()

# Token usage automatically captured
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello"}]
)
# Langfuse captures: prompt_tokens, completion_tokens, total_tokens
```

### Manual Token Tracking
```python
from langfuse import get_client

langfuse = get_client()

with langfuse.start_as_current_generation(
    name="custom-llm-call",
    model="claude-3-5-sonnet-20241022"
) as generation:
    response = make_llm_call()

    generation.update(
        output=response.text,
        usage_details={
            "input": response.input_tokens,
            "output": response.output_tokens,
            # Optional: detailed breakdown
            "cache_read_input_tokens": response.cache_read_tokens,
            # "total" derived from input + output if not provided
        }
    )
```

### OpenAI-Style Usage Schema
```python
generation.update(
    usage_details={
        # Standard fields
        "prompt_tokens": 10,
        "completion_tokens": 25,
        "total_tokens": 35,
        # Detailed breakdown (optional)
        "prompt_tokens_details": {
            "cached_tokens": 5,
            "audio_tokens": 0,
        },
        "completion_tokens_details": {
            "reasoning_tokens": 15,
        },
    }
)
```

---

## Cost Calculation

### Automatic Cost (Model Definitions)

Langfuse calculates costs automatically if:
1. Model is in Langfuse's model registry
2. Token counts are provided

```python
# Costs auto-calculated for known models
generation.update(
    model="gpt-4o",  # Known model
    usage_details={"input": 100, "output": 50}
)
# Cost calculated: input_cost + output_cost
```

### Manual Cost Override
```python
generation.update(
    usage_details={
        "input": 100,
        "output": 50,
    },
    cost_details={
        # Override automatic calculation
        "input": 0.0025,   # USD for input tokens
        "output": 0.005,   # USD for output tokens
        "total": 0.0075,   # Total USD (optional, derived if not set)
    }
)
```

### Custom Model Pricing
```python
# For custom/fine-tuned models not in registry
generation.update(
    model="my-custom-model",
    usage_details={
        "input": 100,
        "output": 50,
        "unit": "TOKENS"  # or CHARACTERS, IMAGES, SECONDS
    },
    cost_details={
        "input_cost": 0.001,  # per 1000 tokens
        "output_cost": 0.002,
    }
)
```

---

## Scores & User Feedback

### Inline Scoring (During Trace)
```python
from langfuse import get_client

langfuse = get_client()

with langfuse.start_as_current_span(name="chat-request") as span:
    response = process_chat(user_input)

    # Score this specific span
    span.score(
        name="relevance",
        value=0.9,
        data_type="NUMERIC"  # NUMERIC, BOOLEAN, or CATEGORICAL
    )

    # Score the overall trace
    span.score_trace(
        name="user-feedback",
        value=1,
        data_type="NUMERIC",
        comment="User marked as helpful"
    )
```

### Deferred Scoring (After Trace)
```python
# Score later using trace ID
langfuse.create_score(
    trace_id="trace-123",
    name="quality",
    value=0.85,
    data_type="NUMERIC",
    comment="Evaluated by QA team"
)

# Score specific observation within trace
langfuse.create_score(
    trace_id="trace-123",
    observation_id="generation-456",
    name="factual-accuracy",
    value=1,
    data_type="BOOLEAN"
)
```

### Score Types

| Type | Values | Use Case |
|------|--------|----------|
| `NUMERIC` | 0.0 - 1.0 | Quality scores, relevance |
| `BOOLEAN` | True/False | Pass/fail, correct/incorrect |
| `CATEGORICAL` | String values | Sentiment, category labels |

---

## Evaluation Integration

### With DeepEval
```python
from deepeval.metrics import AnswerRelevancyMetric
from langfuse import get_client

langfuse = get_client()

def evaluate_and_score(trace_id: str, question: str, answer: str):
    # Run DeepEval metric
    metric = AnswerRelevancyMetric(threshold=0.7)
    metric.measure(
        input=question,
        actual_output=answer
    )

    # Push score to Langfuse
    langfuse.create_score(
        trace_id=trace_id,
        name="answer-relevancy",
        value=metric.score,
        comment=metric.reason
    )
```

### Batch Evaluation
```python
# Fetch traces for evaluation
traces = langfuse.fetch_traces(
    name="chat-completion",
    limit=100
)

for trace in traces.data:
    score = evaluate(trace.input, trace.output)
    langfuse.create_score(
        trace_id=trace.id,
        name="automated-eval",
        value=score
    )

langfuse.flush()
```

---

## Metrics API

### Daily Usage Metrics
```
GET /api/public/metrics/daily
?traceName=chat-api
&userId=user-123
```

Response:
```json
{
  "data": [
    {
      "date": "2025-12-26",
      "countTraces": 1500,
      "totalCost": 102.19,
      "usage": [
        {"model": "gpt-4o", "inputUsage": 50000, "outputUsage": 25000}
      ]
    }
  ]
}
```

### Usage by Trace Name
```
GET /api/public/metrics/usage?group_by=trace_name
```

---

## Cost Monitoring Patterns

### Per-User Cost Tracking
```python
@observe()
def user_request(user_id: str, query: str):
    langfuse = get_client()
    langfuse.update_current_trace(
        user_id=user_id,  # Required for per-user analytics
        tags=["chat"]
    )
    return process(query)
```

### Budget Alerts (Manual)
```python
from langfuse import get_client

def check_user_budget(user_id: str, budget_usd: float) -> bool:
    langfuse = get_client()

    # Fetch user's traces
    traces = langfuse.fetch_traces(user_id=user_id)

    total_cost = sum(t.total_cost or 0 for t in traces.data)

    if total_cost >= budget_usd:
        # Alert or block
        return False
    return True
```

### Environment-Based Tracking
```python
@observe()
def api_call(request):
    langfuse = get_client()
    langfuse.update_current_trace(
        tags=[os.getenv("ENVIRONMENT", "dev")],  # Tag by environment
        metadata={"version": "v1.2.0"}
    )
```

---

## Dashboard Patterns

### Recommended Dashboards

1. **Cost Overview**
   - Daily/weekly/monthly cost trends
   - Cost by model
   - Cost by user/feature

2. **Usage Patterns**
   - Traces per day
   - Average tokens per request
   - P95 latency

3. **Quality Metrics**
   - Average scores over time
   - Score distribution
   - Failed evaluations

### Custom Analytics
Use Langfuse's public API to build custom dashboards:
```python
# Export data for custom analytics
traces = langfuse.fetch_traces(
    from_timestamp=start_date,
    to_timestamp=end_date,
    limit=1000
)

# Process in pandas, Grafana, etc.
df = pd.DataFrame([{
    "date": t.timestamp,
    "cost": t.total_cost,
    "latency": t.latency,
    "model": t.observations[0].model if t.observations else None
} for t in traces.data])
```

---

## Project Conventions

### Score Naming
```
# Pattern: {category}-{metric}
user-feedback
automated-relevancy
automated-faithfulness
human-quality
```

### Cost Attribution Tags
```python
tags=[
    "feature:chat",
    "env:production",
    "team:ai-platform"
]
```

---

## Anti-Patterns

### Not Tracking User IDs
```python
# Wrong - can't analyze per-user costs
@observe()
def process(query):
    return llm(query)

# Right - enables per-user analytics
@observe()
def process(user_id: str, query: str):
    get_client().update_current_trace(user_id=user_id)
    return llm(query)
```

### Ignoring Cost Data
```python
# Wrong - costs not tracked for custom models
generation.update(output=response)

# Right - always provide usage for cost tracking
generation.update(
    output=response,
    usage_details={"input": tokens_in, "output": tokens_out}
)
```

---

**Back to**: [SKILL.md](SKILL.md) - Overview
