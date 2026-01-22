# DeepEval Setup & pytest Integration

**When to use**: Setting up LLM evaluation infrastructure, integrating with pytest.

---

## Installation

```bash
# Core package
pip install -U deepeval

# For RAG evaluation (optional)
pip install ragas

# Set API key for LLM-as-judge
export OPENAI_API_KEY="your-key"
# Or for Azure OpenAI / custom models, see Context7
```

**Python Version**: 3.9+

---

## Two Execution Modes

### 1. Standalone (Notebooks, Scripts)

```python
from deepeval import evaluate
from deepeval.metrics import AnswerRelevancyMetric
from deepeval.test_case import LLMTestCase

metric = AnswerRelevancyMetric(threshold=0.7)
test_case = LLMTestCase(
    input="What is the return policy?",
    actual_output="We offer a 30-day full refund.",
)

# Run evaluation
evaluate([test_case], [metric])
```

### 2. pytest Integration (CI/CD, Regression)

```python
# tests/evals/test_rag_quality.py
import pytest
from deepeval import assert_test
from deepeval.metrics import AnswerRelevancyMetric
from deepeval.test_case import LLMTestCase

def test_answer_relevancy():
    metric = AnswerRelevancyMetric(threshold=0.7)
    test_case = LLMTestCase(
        input="What is the return policy?",
        actual_output="We offer a 30-day full refund.",
    )
    assert_test(test_case, [metric])
```

**Run with**: `deepeval test run tests/evals/`

---

## pytest Test Organization

### Directory Structure

```
tests/
  evals/                        # LLM evaluations
    conftest.py                 # Fixtures, datasets
    test_rag_quality.py         # RAG evaluations
    test_chatbot_evals.py       # Chatbot evaluations
    datasets/                   # Golden datasets (JSON/CSV)
      rag_goldens.json
  unit/                         # Fast unit tests (no LLM calls)
  integration/                  # Integration tests
```

### Separation Rationale

| Test Type | Speed | Cost | When to Run |
|-----------|-------|------|-------------|
| **Unit** | ms | Free | Every commit |
| **Integration** | seconds | Free | Every PR |
| **Evals** | seconds/min | $$ | Nightly, before deploy |

---

## Dataset-Driven Testing

### With EvaluationDataset

```python
import pytest
from deepeval import assert_test
from deepeval.dataset import EvaluationDataset, Golden
from deepeval.metrics import AnswerRelevancyMetric
from deepeval.test_case import LLMTestCase

# Load or create dataset
dataset = EvaluationDataset(goldens=[
    Golden(input="What is the return policy?"),
    Golden(input="How do I track my order?"),
])

# Generate test cases (call your LLM app)
for golden in dataset.goldens:
    actual_output = your_llm_app(golden.input)  # Your app
    dataset.add_test_case(LLMTestCase(
        input=golden.input,
        actual_output=actual_output,
    ))

@pytest.mark.parametrize("test_case", dataset.test_cases)
def test_customer_chatbot(test_case: LLMTestCase):
    metric = AnswerRelevancyMetric(threshold=0.5)
    assert_test(test_case, [metric])
```

---

## Configuration

### Environment Variables

```bash
# Required: LLM for evaluation
export OPENAI_API_KEY="sk-..."

# Optional: Custom model
export DEEPEVAL_MODEL="gpt-4o-mini"  # Cheaper for dev

# Optional: Disable telemetry
export DEEPEVAL_TELEMETRY_OPT_OUT="YES"
```

### Metric Configuration

```python
from deepeval.metrics import AnswerRelevancyMetric

metric = AnswerRelevancyMetric(
    threshold=0.7,           # Minimum score to pass
    model="gpt-4",           # Model for evaluation
    include_reason=True,     # Get explanation
    strict_mode=True,        # Fail on any issue
)
```

---

## Running Evaluations

### CLI Commands

```bash
# Run all evals
deepeval test run tests/evals/

# Run specific file
deepeval test run tests/evals/test_rag_quality.py

# Parallel execution (faster)
deepeval test run tests/evals/ -n 4

# With verbose output
deepeval test run tests/evals/ -v
```

### pytest Commands (Alternative)

```bash
# Standard pytest (works but less features)
pytest tests/evals/

# With DeepEval reporting
deepeval test run tests/evals/ --report
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
# .github/workflows/llm-evals.yml
name: LLM Evaluations

on:
  schedule:
    - cron: '0 2 * * *'  # Nightly at 2 AM
  workflow_dispatch:      # Manual trigger

jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -U deepeval
          pip install -r requirements.txt

      - name: Run evaluations
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: deepeval test run tests/evals/ -n 4
```

### Pre-deploy Gate

```yaml
# Add to existing deploy workflow
- name: LLM Quality Gate
  run: deepeval test run tests/evals/critical/ --fail-fast
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

---

## Hooks & Events

### After Test Run

```python
import deepeval

@deepeval.on_test_run_end
def after_all_tests():
    print("All evaluations complete!")
    # Send Slack notification, update dashboard, etc.
```

### Logging Hyperparameters

```python
import deepeval

@deepeval.log_hyperparameters(model="gpt-4", prompt_template="v2")
def hyperparameters():
    return {"temperature": 0.7, "chunk_size": 500}
```

---

## Context7 Lookup

For current API patterns:
```
get-library-docs: /confident-ai/deepeval (topic: "pytest integration")
get-library-docs: /confident-ai/deepeval (topic: "EvaluationDataset")
get-library-docs: /confident-ai/deepeval (topic: "CI CD")
```

---

## Cross-References

- **pytest patterns**: `.claude/skills/testing-strategy/02-unit-testing.md`
- **CI/CD patterns**: `.claude/skills/testing-strategy/11-ci-cd-integration.md`
- **Metric selection**: [02-metrics-guide.md](02-metrics-guide.md)
