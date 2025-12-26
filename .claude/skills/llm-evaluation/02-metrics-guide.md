# Metrics Selection Guide

**When to use**: Choosing appropriate metrics for your LLM evaluation needs.

---

## Metric Selection by Use Case

| Use Case | Primary Metrics | Secondary Metrics |
|----------|----------------|-------------------|
| **General Q&A** | AnswerRelevancy | Correctness (GEval) |
| **RAG Applications** | Faithfulness, ContextualRecall | ContextualPrecision, ContextualRelevancy |
| **Chatbots/Agents** | ConversationalGEval | RoleAdherence, Coherence |
| **Factual Tasks** | Hallucination | Correctness (GEval) |
| **Safety/Compliance** | Bias, Toxicity | PIILeakage |
| **Summarization** | Summarization | AnswerRelevancy |
| **Custom Criteria** | GEval | - |

---

## Built-in Metrics

### AnswerRelevancyMetric

**Use when**: Evaluating if output addresses the input question.

```python
from deepeval.metrics import AnswerRelevancyMetric

metric = AnswerRelevancyMetric(
    threshold=0.7,
    model="gpt-4",
    include_reason=True
)
```

**Measures**: How well the actual output answers the input query.

### FaithfulnessMetric

**Use when**: RAG applications - checking output is grounded in context.

```python
from deepeval.metrics import FaithfulnessMetric

metric = FaithfulnessMetric(
    threshold=0.8,
    model="gpt-4"
)
```

**Requires**: `retrieval_context` in test case.
**Measures**: Whether claims in output are supported by retrieved context.

### HallucinationMetric

**Use when**: Detecting fabricated information.

```python
from deepeval.metrics import HallucinationMetric

metric = HallucinationMetric(threshold=0.5)
```

**Requires**: `context` (ground truth) in test case.
**Measures**: Presence of unsupported claims.

### BiasMetric / ToxicityMetric

**Use when**: Safety evaluation before deployment.

```python
from deepeval.metrics import BiasMetric, ToxicityMetric

bias = BiasMetric(threshold=0.5)
toxicity = ToxicityMetric(threshold=0.5)
```

**Measures**: Harmful content, stereotypes, offensive language.

---

## Custom Metrics with GEval

**Use when**: Built-in metrics don't cover your criteria.

### Basic GEval Pattern

```python
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCaseParams

correctness = GEval(
    name="Correctness",
    criteria="Determine if the actual output is factually correct based on the expected output.",
    evaluation_params=[
        LLMTestCaseParams.ACTUAL_OUTPUT,
        LLMTestCaseParams.EXPECTED_OUTPUT
    ],
    threshold=0.7
)
```

### GEval with Evaluation Steps

```python
professionalism = GEval(
    name="Professionalism",
    evaluation_steps=[
        "Check if the response maintains a professional tone.",
        "Evaluate if language reflects domain expertise.",
        "Ensure response avoids casual expressions.",
        "Verify clarity and respectfulness."
    ],
    evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT],
    threshold=0.6
)
```

### Domain-Specific GEval Example

```python
medical_accuracy = GEval(
    name="Medical Accuracy",
    criteria="Evaluate factual alignment with medical context.",
    evaluation_steps=[
        "Extract medical claims from actual output.",
        "Verify each claim against retrieved medical literature.",
        "Identify contradictions or unsupported claims.",
        "Heavily penalize hallucinations affecting patient safety."
    ],
    evaluation_params=[
        LLMTestCaseParams.ACTUAL_OUTPUT,
        LLMTestCaseParams.RETRIEVAL_CONTEXT
    ],
    threshold=0.9  # High bar for medical
)
```

---

## Available LLMTestCaseParams

| Parameter | Description | Use With |
|-----------|-------------|----------|
| `INPUT` | User query/prompt | Most metrics |
| `ACTUAL_OUTPUT` | LLM's response | All metrics |
| `EXPECTED_OUTPUT` | Ground truth | Correctness |
| `CONTEXT` | Ground truth context | Hallucination |
| `RETRIEVAL_CONTEXT` | Retrieved docs | RAG metrics |

---

## Threshold Tuning Guidelines

### Starting Points

| Metric | Dev | Staging | Prod |
|--------|-----|---------|------|
| **AnswerRelevancy** | 0.5 | 0.6 | 0.7 |
| **Faithfulness** | 0.6 | 0.7 | 0.8 |
| **ContextualPrecision** | 0.5 | 0.6 | 0.7 |
| **ContextualRecall** | 0.5 | 0.6 | 0.7 |
| **Hallucination** | 0.5 | 0.4 | 0.3 |
| **Bias/Toxicity** | 0.5 | 0.3 | 0.2 |

### Tuning Process

1. **Start low** - Get baseline passing
2. **Analyze failures** - Use `include_reason=True`
3. **Raise incrementally** - +0.1 per iteration
4. **Monitor variance** - Same input, multiple runs
5. **Set per-environment** - Higher for production

---

## Combining Multiple Metrics

```python
from deepeval import evaluate
from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    ContextualRecallMetric
)
from deepeval.test_case import LLMTestCase

# Define metrics
metrics = [
    AnswerRelevancyMetric(threshold=0.7),
    FaithfulnessMetric(threshold=0.8),
    ContextualRecallMetric(threshold=0.6),
]

# Create test case
test_case = LLMTestCase(
    input="What are aspirin side effects?",
    actual_output="Common side effects include stomach upset and nausea.",
    retrieval_context=[
        "Aspirin side effects: stomach upset, heartburn, nausea.",
        "Serious effects: bleeding, allergic reactions."
    ]
)

# Evaluate all metrics
evaluate([test_case], metrics)
```

---

## Cost Considerations

### LLM-as-Judge Costs

| Model | Cost/1K tokens | Speed | Accuracy |
|-------|---------------|-------|----------|
| `gpt-4` | $0.03-0.06 | Slow | Highest |
| `gpt-4o` | $0.005-0.015 | Fast | High |
| `gpt-4o-mini` | $0.00015-0.0006 | Fast | Good |

**Recommendation**:
- **Development**: `gpt-4o-mini` (cheap, fast)
- **Staging**: `gpt-4o` (balanced)
- **Production gate**: `gpt-4` (highest accuracy)

### Reducing Costs

```python
# Use cheaper model for development
metric = AnswerRelevancyMetric(
    threshold=0.7,
    model="gpt-4o-mini"  # Much cheaper
)
```

---

## Getting Help with Metrics

```bash
# CLI tool to recommend metrics
deepeval recommend metrics
```

---

## Context7 Lookup

For current metric parameters:
```
get-library-docs: /confident-ai/deepeval (topic: "AnswerRelevancyMetric")
get-library-docs: /confident-ai/deepeval (topic: "FaithfulnessMetric")
get-library-docs: /confident-ai/deepeval (topic: "GEval custom")
```

---

## Cross-References

- **RAG-specific metrics**: [03-rag-evaluation.md](03-rag-evaluation.md)
- **Setup & pytest**: [01-deepeval-setup.md](01-deepeval-setup.md)
- **AI testing philosophy**: `.claude/skills/testing-strategy/08-ai-llm-testing.md`
