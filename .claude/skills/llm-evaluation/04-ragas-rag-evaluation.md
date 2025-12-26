# RAGAS - RAG Evaluation Framework

**When to use**: Reference-free RAG evaluation, lightweight alternative to DeepEval for RAG-specific metrics.

**Context7 Library**: `/explodinggradients/ragas`

---

## RAGAS vs DeepEval Decision Table

| Criteria | Use RAGAS | Use DeepEval |
|----------|-----------|--------------|
| **RAG-only evaluation** | Yes | Overkill |
| **Reference-free metrics** | Yes (core strength) | Limited |
| **pytest integration** | Basic | Native |
| **Broader metrics (safety, bias)** | No | Yes |
| **LangChain integration** | Native | Requires setup |

**Rule of Thumb**: RAG-only? RAGAS. Full LLM testing? DeepEval. Both? DeepEval for CI/CD, RAGAS for experiments.

---

## Installation

```bash
pip install ragas                          # Basic
pip install ragas langchain-google-vertexai  # With Vertex AI
```

---

## Core Metrics Overview

| Metric | Measures | Reference Required? |
|--------|----------|---------------------|
| **Faithfulness** | Response grounded in context? | No |
| **ResponseRelevancy** | Response addresses question? | No |
| **LLMContextPrecisionWithoutReference** | Retrieved context relevant? | No |
| **LLMContextPrecisionWithReference** | Retrieved context relevant? | Yes |
| **LLMContextRecall** | Retrieved all needed info? | Yes |
| **NonLLMContextRecall** | Recall via similarity | Yes (reference contexts) |

---

## Basic Setup Pattern

```python
from ragas import evaluate, EvaluationDataset
from ragas.metrics import Faithfulness, ResponseRelevancy
from ragas.dataset_schema import SingleTurnSample

# 1. Create sample
sample = SingleTurnSample(
    user_input="What is the return policy?",
    response="We offer a 30-day full refund.",
    retrieved_contexts=["30 day full refund at no extra cost."]
)

# 2. Initialize metrics with evaluator LLM
faithfulness = Faithfulness(llm=evaluator_llm)
relevancy = ResponseRelevancy(llm=evaluator_llm, embeddings=evaluator_embeddings)

# 3. Evaluate single sample (async)
score = await faithfulness.single_turn_ascore(sample)

# 4. Or evaluate dataset
dataset = EvaluationDataset(samples=[sample])
results = evaluate(dataset, metrics=[faithfulness, relevancy])
results.to_pandas()
```

---

## Key Metrics Examples

### Faithfulness (Hallucination Detection)
```python
from ragas.metrics import Faithfulness, FaithfulnesswithHHEM

# LLM-based
scorer = Faithfulness(llm=evaluator_llm)
score = await scorer.single_turn_ascore(sample)

# HHEM (faster, no LLM calls)
scorer = FaithfulnesswithHHEM(device="cuda:0", batch_size=10)
```

### Context Precision
```python
from ragas.metrics import LLMContextPrecisionWithoutReference, LLMContextPrecisionWithReference

# Without reference (most common)
precision = LLMContextPrecisionWithoutReference(llm=evaluator_llm)

# With reference
precision = LLMContextPrecisionWithReference(llm=evaluator_llm)
sample = SingleTurnSample(
    user_input="...", reference="ground truth", retrieved_contexts=[...]
)
```

### Context Recall
```python
from ragas.metrics import LLMContextRecall, NonLLMContextRecall

# LLM-based (needs reference answer)
recall = LLMContextRecall(llm=evaluator_llm)
sample = SingleTurnSample(reference="ground truth answer", ...)

# Non-LLM (needs reference contexts)
recall = NonLLMContextRecall()
sample = SingleTurnSample(reference_contexts=["Doc1", "Doc2"], ...)
```

---

## Creating Evaluation Datasets

```python
from ragas import EvaluationDataset

# From list of dicts
data = [{"user_input": "...", "response": "...", "retrieved_contexts": [...]}]
dataset = EvaluationDataset.from_list(data)

# From RAG pipeline
dataset = []
for query, ref in zip(queries, references):
    docs = rag.get_relevant_docs(query)
    response = rag.generate_answer(query, docs)
    dataset.append({
        "user_input": query, "retrieved_contexts": docs,
        "response": response, "reference": ref
    })
eval_dataset = EvaluationDataset.from_list(dataset)
```

---

## Vertex AI Integration

```python
from langchain_google_vertexai import ChatVertexAI, VertexAIEmbeddings
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper

# Wrap Vertex AI models for RAGAS
llm = ChatVertexAI(model="gemini-2.0-flash")
embeddings = VertexAIEmbeddings(model_name="text-embedding-004")

evaluator_llm = LangchainLLMWrapper(llm)
evaluator_embeddings = LangchainEmbeddingsWrapper(embeddings)

# Use in metrics
faithfulness = Faithfulness(llm=evaluator_llm)
relevancy = ResponseRelevancy(llm=evaluator_llm, embeddings=evaluator_embeddings)
```

---

## Common Gotchas

### 1. Async Required
```python
# Wrong - returns coroutine
score = scorer.single_turn_ascore(sample)

# Right
score = await scorer.single_turn_ascore(sample)
# Or: asyncio.run(scorer.single_turn_ascore(sample))
```

### 2. LLM Wrapper Required
```python
# Wrong
faithfulness = Faithfulness(llm=ChatVertexAI(...))

# Right
faithfulness = Faithfulness(llm=LangchainLLMWrapper(ChatVertexAI(...)))
```

### 3. Reference vs Reference Contexts
- `reference`: Ground truth answer (string) - for LLMContextRecall
- `reference_contexts`: Ground truth docs (list) - for NonLLMContextRecall

### 4. ResponseRelevancy Needs Embeddings
```python
# Wrong
relevancy = ResponseRelevancy(llm=evaluator_llm)

# Right
relevancy = ResponseRelevancy(llm=evaluator_llm, embeddings=evaluator_embeddings)
```

---

## Context7 Lookup

```
get-library-docs: /explodinggradients/ragas (topic: "Faithfulness metric")
get-library-docs: /explodinggradients/ragas (topic: "ResponseRelevancy metric")
get-library-docs: /explodinggradients/ragas (topic: "context precision recall")
get-library-docs: /explodinggradients/ragas (topic: "EvaluationDataset")
get-library-docs: /explodinggradients/ragas (topic: "LangchainLLMWrapper VertexAI")
```

---

## Cross-References

- **DeepEval RAG**: [03-rag-evaluation.md](03-rag-evaluation.md)
- **Metric selection**: [02-metrics-guide.md](02-metrics-guide.md)
- **AI testing strategy**: `.claude/skills/testing-strategy/08-ai-llm-testing.md`
