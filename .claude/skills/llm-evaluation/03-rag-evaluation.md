# RAG Evaluation Patterns

**When to use**: Evaluating Retrieval-Augmented Generation pipelines.

---

## RAG Evaluation Overview

RAG systems have two components to evaluate:

1. **Retriever**: Are we getting the right documents?
2. **Generator**: Is the LLM using them correctly?

```
Query --> [Retriever] --> Retrieved Docs --> [Generator] --> Answer
              ^                                    ^
         Retrieval Metrics              Generation Metrics
```

---

## Retrieval Metrics

### ContextualPrecisionMetric

**Measures**: Are retrieved documents ranked by relevance?

```python
from deepeval.metrics import ContextualPrecisionMetric

precision = ContextualPrecisionMetric(
    threshold=0.7,
    model="gpt-4",
    include_reason=True
)
```

**Use when**: Top-k ranking matters for your application.

### ContextualRecallMetric

**Measures**: Does retrieval context capture all info in expected output?

```python
from deepeval.metrics import ContextualRecallMetric

recall = ContextualRecallMetric(
    threshold=0.7,
    model="gpt-4"
)
```

**Requires**: `expected_output` to compare against.

### ContextualRelevancyMetric

**Measures**: How relevant are retrieved docs to the query?

```python
from deepeval.metrics import ContextualRelevancyMetric

relevancy = ContextualRelevancyMetric(
    threshold=0.7,
    model="gpt-4"
)
```

**Use when**: Filtering out irrelevant retrievals.

---

## Generation Metrics

### FaithfulnessMetric

**Measures**: Is the output grounded in retrieved context (no hallucination)?

```python
from deepeval.metrics import FaithfulnessMetric

faithfulness = FaithfulnessMetric(
    threshold=0.8,
    model="gpt-4"
)
```

**Critical for**: Any RAG application where accuracy matters.

### AnswerRelevancyMetric

**Measures**: Does the answer address the original query?

```python
from deepeval.metrics import AnswerRelevancyMetric

answer_relevancy = AnswerRelevancyMetric(
    threshold=0.7,
    model="gpt-4"
)
```

---

## Complete RAG Test Case

```python
from deepeval.test_case import LLMTestCase
from deepeval import evaluate
from deepeval.metrics import (
    ContextualPrecisionMetric,
    ContextualRecallMetric,
    ContextualRelevancyMetric,
    FaithfulnessMetric,
    AnswerRelevancyMetric
)

# Define test case with all RAG components
rag_test_case = LLMTestCase(
    input="What are the side effects of aspirin?",
    actual_output="Common side effects include stomach upset and nausea. Serious effects can include bleeding.",
    expected_output="Aspirin side effects include gastrointestinal issues and potential bleeding.",
    retrieval_context=[
        "Aspirin common side effects: stomach upset, heartburn, nausea.",
        "Serious aspirin side effects: gastrointestinal bleeding, allergic reactions.",
        "Aspirin mechanism: inhibits COX enzymes.",  # Less relevant
        "Recommended dosage: 325mg for pain relief."  # Not relevant
    ]
)

# Define metrics
rag_metrics = [
    ContextualPrecisionMetric(threshold=0.6),
    ContextualRecallMetric(threshold=0.7),
    FaithfulnessMetric(threshold=0.8),
    AnswerRelevancyMetric(threshold=0.7),
]

# Evaluate
results = evaluate([rag_test_case], rag_metrics)

# Access individual scores
for metric in rag_metrics:
    print(f"{metric.__class__.__name__}: {metric.score:.2f}")
    if metric.reason:
        print(f"  Reason: {metric.reason}")
```

---

## pytest Integration for RAG

```python
# tests/evals/test_rag_quality.py
import pytest
from deepeval import assert_test
from deepeval.metrics import FaithfulnessMetric, ContextualRecallMetric
from deepeval.test_case import LLMTestCase

from your_app import rag_pipeline  # Your RAG implementation

@pytest.fixture
def rag_metrics():
    return [
        FaithfulnessMetric(threshold=0.8),
        ContextualRecallMetric(threshold=0.7),
    ]

@pytest.mark.parametrize("query,expected", [
    ("What is the return policy?", "30-day full refund"),
    ("How to track my order?", "tracking number and status"),
])
def test_rag_quality(query, expected, rag_metrics):
    # Call your RAG pipeline
    actual_output, retrieved_docs = rag_pipeline(query)

    test_case = LLMTestCase(
        input=query,
        actual_output=actual_output,
        expected_output=expected,
        retrieval_context=retrieved_docs,
    )

    assert_test(test_case, rag_metrics)
```

---

## Evaluating Retriever Changes

When testing retriever modifications (chunking, embeddings, top-k):

```python
from deepeval.metrics import ContextualPrecisionMetric, ContextualRecallMetric
from deepeval.test_case import LLMTestCase
from deepeval import evaluate

chunking_strategies = [256, 512, 1024]
results = {}

for chunk_size in chunking_strategies:
    # Configure retriever with chunk_size
    retriever = create_retriever(chunk_size=chunk_size)

    test_cases = []
    for query, expected in test_data:
        docs = retriever.retrieve(query)
        test_case = LLMTestCase(
            input=query,
            actual_output=expected,  # Use expected as actual for retriever-only eval
            expected_output=expected,
            retrieval_context=[doc.content for doc in docs],
        )
        test_cases.append(test_case)

    metrics = [
        ContextualPrecisionMetric(threshold=0.6),
        ContextualRecallMetric(threshold=0.7),
    ]

    evaluate(test_cases, metrics)
    results[chunk_size] = {
        "precision": metrics[0].score,
        "recall": metrics[1].score,
    }

print(results)
```

---

## Synthetic Test Data for RAG

Generate test data from your documents:

```python
from deepeval.synthesizer import Synthesizer
from deepeval.dataset import EvaluationDataset

# Generate golden test cases from documents
synthesizer = Synthesizer()
synthesizer.generate_goldens_from_docs(
    document_paths=["docs/product_faq.md", "docs/returns.md"],
    include_expected_output=True
)

# Use generated goldens
goldens = synthesizer.synthetic_goldens
dataset = EvaluationDataset(goldens=goldens)
```

**Styling for specific domain**:

```python
from deepeval.synthesizer.config import StylingConfig

styling = StylingConfig(
    input_format="Customer questions about product returns",
    expected_output_format="Accurate, helpful responses",
    task="Customer support RAG system",
    scenario="Customers asking about return policies"
)

synthesizer = Synthesizer(styling_config=styling)
```

---

## RAG Metric Decision Tree

```
What are you testing?
    |
    +-- Retrieval quality?
    |       |
    |       +-- Ranking matters? --> ContextualPrecision
    |       |
    |       +-- Coverage matters? --> ContextualRecall
    |       |
    |       +-- Relevance matters? --> ContextualRelevancy
    |
    +-- Generation quality?
            |
            +-- Grounding in context? --> Faithfulness
            |
            +-- Answers the question? --> AnswerRelevancy
            |
            +-- Factual correctness? --> Correctness (GEval)
```

---

## Threshold Guidelines for RAG

| Metric | Development | Staging | Production |
|--------|-------------|---------|------------|
| **ContextualPrecision** | 0.5 | 0.6 | 0.7 |
| **ContextualRecall** | 0.5 | 0.6 | 0.7 |
| **ContextualRelevancy** | 0.5 | 0.6 | 0.7 |
| **Faithfulness** | 0.6 | 0.7 | 0.8 |
| **AnswerRelevancy** | 0.5 | 0.6 | 0.7 |

**Rule**: Faithfulness threshold should be highest (hallucinations are costly).

---

## Common Gotchas

### 1. retrieval_context Format

```python
# Wrong - dict
retrieval_context={"doc1": "content"}

# Wrong - single string
retrieval_context="document content"

# Right - list of strings
retrieval_context=["Doc 1 content", "Doc 2 content"]
```

### 2. Missing expected_output

`ContextualRecallMetric` requires `expected_output`:

```python
# Wrong - missing expected_output
test_case = LLMTestCase(
    input="...",
    actual_output="...",
    retrieval_context=["..."],
)

# Right
test_case = LLMTestCase(
    input="...",
    actual_output="...",
    expected_output="Ground truth answer",  # Required!
    retrieval_context=["..."],
)
```

### 3. Evaluating Retriever vs Full Pipeline

- **Retriever only**: Use ContextualPrecision, ContextualRecall, ContextualRelevancy
- **Full pipeline**: Add Faithfulness, AnswerRelevancy
- **Don't mix**: Evaluate components separately first

---

## Context7 Lookup

For current RAG patterns:
```
get-library-docs: /confident-ai/deepeval (topic: "RAG evaluation")
get-library-docs: /confident-ai/deepeval (topic: "ContextualRecallMetric")
get-library-docs: /confident-ai/deepeval (topic: "FaithfulnessMetric")
get-library-docs: /confident-ai/deepeval (topic: "synthesizer documents")
```

---

## Cross-References

- **Metric selection**: [02-metrics-guide.md](02-metrics-guide.md)
- **Setup & pytest**: [01-deepeval-setup.md](01-deepeval-setup.md)
- **AI testing**: `.claude/skills/testing-strategy/08-ai-llm-testing.md`
