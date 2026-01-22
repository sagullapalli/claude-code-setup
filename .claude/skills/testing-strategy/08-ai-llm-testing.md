# AI/LLM Testing

**When to use**: Testing AI agents, LLM outputs, prompt engineering.

**CRITICAL**: LLMs are non-deterministic - never assert exact strings!

---

## Core Principle: Non-Deterministic Outputs

### ❌ NEVER Do This

```python
# ❌ BAD: Exact match (will fail due to non-determinism)
def test_llm_bad():
    response = llm.generate("What is the capital of France?")
    assert response == "The capital of France is Paris."  # WILL FAIL!
```

### ✅ ALWAYS Do This

```python
# ✅ GOOD: Keyword presence
def test_llm_keyword():
    response = llm.generate("What is the capital of France?")
    assert "Paris" in response  # Flexible

# ✅ GOOD: Length bounds
def test_llm_length():
    response = llm.generate("Summarize this article...")
    assert 50 < len(response) < 200

# ✅ GOOD: Format check
def test_llm_format():
    response = llm.generate("What is the capital of France?")
    assert response.startswith("The capital")

# ✅ GOOD: JSON mode for deterministic structure
def test_llm_json():
    prompt = "Return JSON with capital of France. Use JSON mode."
    response = llm.generate(prompt, response_format="json")
    data = json.loads(response)

    assert "capital" in data
    assert data["capital"] == "Paris"  # Can check value in JSON
```

---

## Semantic Assertion Patterns

### 1. Keyword Presence

```python
def test_llm_contains_keywords():
    response = llm.generate("What is the capital of France?")
    keywords = ["Paris", "France", "capital"]
    assert all(keyword.lower() in response.lower() for keyword in keywords)
```

### 2. Length Bounds

```python
def test_llm_summary_length():
    article = "..." * 1000  # Long article
    summary = llm.summarize(article)

    assert 50 <= len(summary) <= 500  # Reasonable summary length
```

### 3. Format Validation (JSON Mode - BEST)

```python
def test_llm_returns_valid_json():
    prompt = "Extract person's name and age. Return JSON."
    response = llm.generate(prompt, response_format="json")

    data = json.loads(response)  # Should parse
    assert "name" in data
    assert "age" in data
    assert isinstance(data["age"], int)
```

### 4. Regex Matching

```python
import re

def test_llm_matches_pattern():
    response = llm.generate("What is the capital of France?")
    assert re.match(r"^The capital .* is \w+\.$", response)
```

---

## Google ADK Agent Testing

### Testing Agent State

```python
from google.adk.runners import InMemoryRunner

def test_agent_maintains_context():
    agent = create_gtm_agent()
    runner = InMemoryRunner(agent=agent, app_name="test")

    # First message
    response1 = await runner.run_async("My name is John")
    assert "John" in str(response1.events)

    # Second message (should remember name)
    response2 = await runner.run_async("What's my name?")
    assert "John" in str(response2.events)
```

### Testing Tool Calls

```python
def test_agent_calls_correct_tool():
    agent = create_agent_with_tools()
    runner = InMemoryRunner(agent=agent, app_name="test")

    response = await runner.run_async("Search for Python tutorials")

    # Verify tool was called
    events = response.events
    tool_calls = [e for e in events if hasattr(e, 'function_calls')]
    assert len(tool_calls) > 0
    assert "search" in str(tool_calls[0])
```

---

## What NOT to Test

### ❌ Don't Test

- **Exact output strings** (non-deterministic)
- **LLM quality** (that's Google/OpenAI's responsibility)
- **Hallucinations** (can't reliably test without ground truth)
- **Style/tone** (subjective, varies per run)

### ✅ DO Test

- **Output structure** (JSON format, required fields)
- **Keyword presence** (important entities mentioned)
- **Length constraints** (summaries are shorter than input)
- **Tool calling logic** (correct tools invoked)
- **State management** (context preserved across turns)

---

## Cost and Performance Testing

### Track Token Usage

```python
def test_agent_token_efficiency():
    agent = create_agent()
    runner = InMemoryRunner(agent=agent, app_name="test")

    response = await runner.run_async("Simple query")

    # Verify reasonable token usage
    # (Check runner metrics or ADK usage data if available)
    assert len(str(response.events)) < 5000  # Rough proxy
```

---

## Prompt Testing

### Test Prompt Variations

```python
@pytest.mark.parametrize("prompt_template", [
    "Summarize this text: {text}",
    "Provide a brief summary of: {text}",
    "TL;DR: {text}"
])
def test_prompt_variations(prompt_template):
    text = "Long article content..."
    prompt = prompt_template.format(text=text)
    result = llm.generate(prompt)

    assert len(result) < len(text)  # Summary should be shorter
    assert len(result) > 10  # Not too short
```

---

## Best Practices

### ✅ Do

- **Use JSON mode** for deterministic testing (best option)
- **Test structure, not content** (required fields, data types)
- **Use keyword presence** for semantic checks
- **Set length bounds** (min/max characters)
- **Test state management** (context across turns)
- **Track token usage** (cost control)

### ❌ Don't

- **Assert exact strings** (non-deterministic!)
- **Test LLM quality** (trust the model)
- **Test every edge case** (expensive, slow)
- **Over-test prompts** (test critical paths only)

---

## Summary

### Key Points

1. **NEVER assert exact LLM strings** (non-deterministic)
2. **Use JSON mode** for structured outputs (most reliable)
3. **Test structure, not content** (keywords, format, length)
4. **Test state management** (ADK session persistence)
5. **Track costs** (token usage, API calls)

### Checklist

- [ ] No exact string assertions
- [ ] JSON mode used where possible
- [ ] Keyword presence tested
- [ ] Length bounds validated
- [ ] State management tested (multi-turn)
- [ ] Tool calling logic verified
- [ ] Token usage tracked

---

## Cross-References

- **Google ADK patterns**: See `.claude/skills/google-adk-patterns/` for agent creation
- **State management**: See `.claude/skills/google-adk-patterns/03-state-management.md`
- **Testing philosophy**: [01-testing-philosophy.md](01-testing-philosophy.md)
- **Integration testing**: [03-integration-testing.md](03-integration-testing.md)
