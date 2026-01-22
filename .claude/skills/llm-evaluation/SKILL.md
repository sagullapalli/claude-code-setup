---
name: LLM Evaluation Patterns
description: Testing and evaluation patterns for LLM applications using DeepEval and RAGAS. Use for formal evaluation before deployment, after prompt changes, or model updates.
tags: [llm, evaluation, testing, deepeval, metrics, rag, ragas]
context7_libraries:
  - /confident-ai/deepeval
  - /explodinggradients/ragas
  - /googleapis/python-aiplatform
last_verified: 2025-12-26
---

# LLM Evaluation Patterns - Quick Reference

**Principle**: "Eyeballing outputs is ending" - formal evaluation is required for production AI.

**Package**: `pip install -U deepeval`

---

## Modules

1. **[01-deepeval-setup.md](01-deepeval-setup.md)** - Installation & Integration
   - Installation and environment setup
   - pytest integration patterns
   - Test organization conventions

2. **[02-metrics-guide.md](02-metrics-guide.md)** - Metric Selection
   - Metric selection by use case
   - Built-in vs custom metrics (GEval)
   - Threshold tuning guidelines

3. **[03-rag-evaluation.md](03-rag-evaluation.md)** - RAG Evaluation (DeepEval)
   - Retrieval metrics (precision, recall, relevancy)
   - Generation metrics (faithfulness, answer relevancy)
   - End-to-end RAG pipeline evaluation

4. **[04-ragas-rag-evaluation.md](04-ragas-rag-evaluation.md)** - RAGAS Framework
   - Reference-free RAG evaluation
   - RAGAS vs DeepEval decision guide
   - Vertex AI integration patterns

5. **[05-vertex-ai-evaluation.md](05-vertex-ai-evaluation.md)** - Vertex AI Gen AI Evaluation
   - GCP-native evaluation service
   - Adaptive rubrics (auto-generated criteria)
   - Agent trajectory evaluation (tool sequence analysis)
   - Pairwise model comparison

---

## When to Evaluate

| Trigger | What to Evaluate |
|---------|-----------------|
| **Before deployment** | Full test suite (all metrics) |
| **After prompt changes** | Affected metrics only |
| **After model updates** | Regression tests + key metrics |
| **After RAG pipeline changes** | Retrieval + faithfulness metrics |

---

## Evaluation vs Unit Testing

| Aspect | Unit Testing | LLM Evaluation |
|--------|--------------|----------------|
| **Purpose** | Code correctness | Output quality |
| **Determinism** | Deterministic | Non-deterministic |
| **Speed** | Fast (ms) | Slow (seconds per test) |
| **Cost** | Free | LLM-as-judge costs |
| **Assertions** | Exact match | Semantic scoring |

**Key Insight**: LLM evaluation complements unit tests - both are needed.

---

## Quick Start Pattern

```python
from deepeval import evaluate
from deepeval.metrics import AnswerRelevancyMetric
from deepeval.test_case import LLMTestCase

# 1. Create test case
test_case = LLMTestCase(
    input="What is the return policy?",
    actual_output="We offer a 30-day full refund.",
    retrieval_context=["30 day full refund at no extra cost."]
)

# 2. Define metric with threshold
metric = AnswerRelevancyMetric(threshold=0.7)

# 3. Evaluate
evaluate([test_case], [metric])
```

**For pytest integration**, see [01-deepeval-setup.md](01-deepeval-setup.md).

---

## Metric Quick Reference

| Use Case | Primary Metrics | Framework |
|----------|----------------|-----------|
| **General Q&A** | AnswerRelevancy, Correctness (GEval) | DeepEval |
| **RAG Applications** | Faithfulness, ContextualPrecision, ContextualRecall | DeepEval or RAGAS |
| **RAG (reference-free)** | Faithfulness, ResponseRelevancy, LLMContextPrecision | RAGAS |
| **Chatbots** | ConversationalGEval, RoleAdherence | DeepEval |
| **Factual Tasks** | Hallucination, Correctness | DeepEval |
| **Safety/Compliance** | Bias, Toxicity, PIILeakage | DeepEval |

**For detailed metric selection**, see [02-metrics-guide.md](02-metrics-guide.md).
**For RAGAS vs DeepEval decision**, see [04-ragas-rag-evaluation.md](04-ragas-rag-evaluation.md).

---

## Project Conventions

### Test Organization

```
tests/
  evals/                    # LLM evaluations (separate from unit tests)
    test_rag_quality.py     # RAG pipeline evaluations
    test_chatbot_evals.py   # Chatbot evaluations
    conftest.py             # Shared fixtures, datasets
  unit/                     # Fast unit tests
  integration/              # Integration tests
```

### Naming Convention

```python
# Pattern: test_[feature]_[metric]_[scenario]
def test_rag_faithfulness_with_context():
    ...

def test_chatbot_relevancy_simple_query():
    ...
```

### Thresholds

| Metric Type | Development | Staging | Production |
|-------------|-------------|---------|------------|
| **Relevancy** | 0.5 | 0.6 | 0.7 |
| **Faithfulness** | 0.6 | 0.7 | 0.8 |
| **Precision/Recall** | 0.5 | 0.6 | 0.7 |

**Rule**: Start low, increase as system matures.

---

## Common Gotchas

### 1. LLM-as-Judge Costs
DeepEval uses LLMs to evaluate LLM outputs. **Each metric = API call**.
- Set `OPENAI_API_KEY` or configure custom model
- Default: `gpt-4` for evaluation (most accurate, most expensive)
- Cost-saving: Use `gpt-4o-mini` for development

### 2. Async Handling
DeepEval runs async internally. If using in async code:
```python
# Standalone (not pytest)
import asyncio
asyncio.run(evaluate([test_case], [metric]))
```

### 3. Test Data Preparation
`retrieval_context` must be a list of strings, not dict:
```python
# Wrong
retrieval_context={"doc1": "content"}

# Right
retrieval_context=["Document 1 content", "Document 2 content"]
```

### 4. Non-Deterministic Scores
Same input can produce different scores (LLM variance).
- Run multiple times for stability checks
- Use `include_reason=True` to understand scoring

---

## Context7 Lookup

For current API syntax:
```
get-library-docs: /confident-ai/deepeval (topic: "metrics AnswerRelevancy")
get-library-docs: /confident-ai/deepeval (topic: "GEval custom metrics")
get-library-docs: /confident-ai/deepeval (topic: "synthesizer test data")
```

---

## Cross-References

- **AI/LLM Testing**: `.claude/skills/testing-strategy/08-ai-llm-testing.md` (semantic assertions)
- **pytest patterns**: `.claude/skills/testing-strategy/02-unit-testing.md`
- **CI/CD integration**: `.claude/skills/testing-strategy/11-ci-cd-integration.md`

---

**Last Updated**: 2025-12-26
