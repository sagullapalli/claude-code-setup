---
name: Vertex AI Gen AI Evaluation
description: GCP-native LLM evaluation using Vertex AI Gen AI Evaluation Service. Adaptive rubrics, LLM-as-judge, agent trajectory evaluation.
tags: [vertex-ai, gcp, evaluation, llm, agents, rubrics]
context7_libraries:
  - /googleapis/python-aiplatform
last_verified: 2025-12-26
---

# Vertex AI Gen AI Evaluation

**Package**: `pip install google-cloud-aiplatform pandas`

---

## When to Use Which Framework

| Scenario | Recommended | Why |
|----------|-------------|-----|
| **GCP-native stack** | Vertex AI Eval | Native integration, experiment tracking |
| **Evaluating Gemini models** | Vertex AI Eval | Direct model access, adaptive rubrics |
| **Agent trajectory analysis** | Vertex AI Eval | Built-in trajectory metrics (unique) |
| **Multi-provider LLMs** | DeepEval | Provider-agnostic |
| **RAG-specific metrics** | RAGAS or DeepEval | More specialized RAG metrics |
| **Existing pytest suite** | DeepEval | `assert_test` integration |

**Rule**: Use Vertex AI Eval when all-in on GCP; use DeepEval/RAGAS for flexibility.

---

## Two API Patterns

### Pattern 1: Unified Client (Recommended)

```python
import vertexai
from vertexai import types

client = vertexai.Client(project='my-project', location='europe-west1')

inference_results = client.evals.run_inference(
    model='gemini-2.0-flash',
    src=prompts_df  # DataFrame with 'prompt' column
)

eval_result = client.evals.evaluate(
    dataset=inference_results,
    metrics=[
        types.Metric(name='exact_match'),
        types.RubricMetric.TEXT_QUALITY,
        types.RubricMetric.GROUNDEDNESS,
    ]
)
eval_result.show()
```

### Pattern 2: EvalTask (More Features)

```python
from vertexai.evaluation import EvalTask, MetricPromptTemplateExamples
from vertexai.generative_models import GenerativeModel

result = EvalTask(
    dataset=eval_df,  # DataFrame with prompt, reference columns
    metrics=["bleu", "rouge_l_sum", MetricPromptTemplateExamples.Pointwise.FLUENCY],
    experiment="my-experiment",  # Links to Vertex AI Experiments
).evaluate(
    model=GenerativeModel("gemini-2.0-flash"),
    experiment_run_name="eval-run-1"
)
```

**Decision**: Unified Client for simplicity. EvalTask for experiment tracking or pairwise comparison.

---

## Built-in Metrics

### Computation-Based (Fast, Free)

| Metric | Use Case |
|--------|----------|
| `exact_match` | Exact string matching |
| `bleu` | Translation quality |
| `rouge_1`, `rouge_l_sum` | Summarization quality |

### Rubric Metrics (LLM-as-Judge)

```python
from vertexai import types

metrics = [
    types.RubricMetric.TEXT_QUALITY,       # Overall quality
    types.RubricMetric.COHERENCE,          # Logical flow
    types.RubricMetric.FLUENCY,            # Language quality
    types.RubricMetric.SAFETY,             # Harmful content check
    types.RubricMetric.GROUNDEDNESS,       # Factual grounding
    types.RubricMetric.INSTRUCTION_FOLLOWING,
    types.RubricMetric.GENERAL_QUALITY,    # Adaptive rubrics (recommended)
]
```

### Agent-Specific Metrics (Unique to Vertex AI)

```python
metrics = [
    types.Metric(name='tool_call_quality'),
    types.Metric(name='tool_name_match'),
    types.Metric(name='tool_parameter_key_match'),
    types.Metric(name='tool_parameter_kv_match'),
]
```

---

## Agent Trajectory Evaluation

**Unique to Vertex AI**: Evaluate agent reasoning paths, not just final outputs.

| Metric | Description |
|--------|-------------|
| `trajectory_exact_match` | Perfect action sequence match |
| `trajectory_in_order_match` | All actions in correct order |
| `trajectory_precision` | Proportion of correct predicted actions |
| `trajectory_recall` | Proportion of reference actions found |

```python
agent_df = pd.DataFrame({
    "prompt": ["What's the weather in Paris?"],
    "reference_trajectory": ['[{"tool": "get_weather", "args": {"city": "Paris"}}]'],
    "predicted_trajectory": ['[{"tool": "get_weather", "args": {"city": "Paris"}}]'],
    "response": ["The weather in Paris is 22C and sunny."],
})

result = EvalTask(
    dataset=agent_df,
    metrics=["trajectory_exact_match", "trajectory_in_order_match"],
).evaluate()
```

---

## Adaptive Rubrics (Defining Feature)

Auto-generates pass/fail criteria per prompt:

```python
eval_result = client.evals.evaluate(
    dataset=inference_results,
    metrics=[types.RubricMetric.GENERAL_QUALITY]  # Triggers adaptive rubrics
)
```

**Why it matters**: Each prompt gets tailored evaluation criteria, like unit tests per case.

---

## Pairwise Model Comparison

```python
from vertexai.evaluation import EvalTask, PairwiseMetric, MetricPromptTemplateExamples
from vertexai.generative_models import GenerativeModel

baseline = GenerativeModel("gemini-1.5-flash")
candidate = GenerativeModel("gemini-2.0-flash")

pairwise_metric = PairwiseMetric(
    metric_prompt_template=MetricPromptTemplateExamples.get_prompt_template("pairwise_groundedness"),
    baseline_model=baseline,
)

result = EvalTask(
    dataset=eval_df,
    metrics=[pairwise_metric],
).evaluate(model=candidate)
```

---

## Common Gotchas

### 1. Region Availability
Not all regions support Gen AI Evaluation:
- `us-central1` (full support)
- `europe-west1` (check current availability)

### 2. Dataset Column Names (Case-Sensitive)
- **Inference**: `prompt` required
- **BYOR**: `prompt`, `response` required
- **Pairwise**: `prompt`, `response`, `baseline_model_response`
- **Agent trajectory**: `predicted_trajectory`, `reference_trajectory`

### 3. Cost Considerations
- Computation metrics (BLEU, ROUGE): Free
- Rubric metrics: LLM API calls (Gemini charges)
- Adaptive rubrics: Multiple LLM calls per evaluation

### 4. Experiment Tracking
Use `experiment` param in EvalTask to log to Vertex AI Experiments:
```python
EvalTask(dataset=df, metrics=[...], experiment="my-experiment")
# View: Cloud Console > Vertex AI > Experiments
```

### 5. Async Not Required
Unlike DeepEval, Vertex AI handles async internally - no `asyncio.run()` needed.

---

## Context7 Lookup

For current API syntax:
```
get-library-docs: /googleapis/python-aiplatform (topic: "evaluation EvalTask")
get-library-docs: /googleapis/python-aiplatform (topic: "RubricMetric types")
get-library-docs: /googleapis/python-aiplatform (topic: "agent trajectory evaluation")
```

---

## Cross-References

- **DeepEval patterns**: `01-deepeval-setup.md`, `02-metrics-guide.md`
- **RAGAS comparison**: `04-ragas-rag-evaluation.md`
- **Google ADK agents**: `.claude/skills/google-adk-patterns/SKILL.md`

---

**Last Updated**: 2025-12-26
