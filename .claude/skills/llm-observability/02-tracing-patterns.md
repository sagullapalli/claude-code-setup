# Tracing Patterns

## The @observe Decorator

The primary way to trace functions in Langfuse.

### Basic Usage
```python
from langfuse import observe

@observe()
def process_query(query: str) -> str:
    # Function inputs/outputs automatically captured
    result = call_llm(query)
    return result
```

### Async Support
```python
@observe()
async def async_process(query: str) -> str:
    result = await async_llm_call(query)
    return result
```

### Nested Tracing
```python
@observe()
def main_function():
    # Creates parent span
    result = nested_function()  # Creates child span
    return result

@observe()
def nested_function():
    return "nested result"
```

---

## Decorator Options

### Custom Naming
```python
@observe(name="custom-span-name")
def my_function():
    pass
```

### Generation Type (for LLM calls)
```python
@observe(as_type="generation")
def llm_call(prompt: str) -> str:
    # Marks this as an LLM generation in UI
    return client.chat(prompt)
```

### Control Input/Output Capture
```python
@observe(capture_input=False, capture_output=False)
def sensitive_function(data):
    # Inputs/outputs not logged (for PII)
    return process(data)
```

---

## Manual Spans

For fine-grained control when decorators aren't suitable.

### Context Manager Pattern
```python
from langfuse import get_client

langfuse = get_client()

def process_request(query: str):
    with langfuse.start_as_current_span(name="process-request") as span:
        # Add metadata
        span.update(
            input=query,
            metadata={"user_id": "user-123"}
        )

        result = do_work(query)

        span.update(output=result)
        return result
```

### Generation Spans (LLM Calls)
```python
with langfuse.start_as_current_generation(
    name="chat-completion",
    model="gpt-4o",
    input=[{"role": "user", "content": prompt}]
) as generation:
    # Make LLM call
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )

    generation.update(
        output=response.choices[0].message.content,
        usage_details={
            "input": response.usage.prompt_tokens,
            "output": response.usage.completion_tokens
        }
    )
```

---

## OpenAI Integration (Auto-Tracing)

Drop-in replacement for automatic tracing.

### Setup
```python
# Replace: import openai
from langfuse.openai import openai

# All calls automatically traced
client = openai.OpenAI()
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello"}]
)
```

### With Custom Metadata
```python
from langfuse.openai import openai

client = openai.OpenAI()

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello"}],
    # Langfuse-specific parameters
    name="greeting-completion",  # Custom trace name
    metadata={"feature": "chat"},
    tags=["production"],
    user_id="user-123",
    session_id="session-abc"
)
```

### Streaming with Token Tracking
```python
stream = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello"}],
    stream=True,
    stream_options={"include_usage": True}  # Required for token counts
)

for chunk in stream:
    if chunk.choices:
        print(chunk.choices[0].delta.content or "", end="")
```

---

## Anthropic Integration

### Manual Tracing Pattern
```python
from langfuse import observe, get_client
import anthropic

langfuse = get_client()
client = anthropic.Anthropic()

@observe(as_type="generation")
def claude_completion(prompt: str) -> str:
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )

    # Update generation with details
    langfuse.update_current_generation(
        model="claude-3-5-sonnet-20241022",
        input=[{"role": "user", "content": prompt}],
        output=response.content[0].text,
        usage_details={
            "input": response.usage.input_tokens,
            "output": response.usage.output_tokens
        }
    )

    return response.content[0].text
```

---

## Google ADK Integration

### Wrapping Agent Execution
```python
from langfuse import observe, get_client
from google.adk.agents import LlmAgent
from google.adk.runners import InMemoryRunner

langfuse = get_client()

@observe(name="adk-agent-run")
async def run_agent(query: str) -> str:
    agent = LlmAgent(
        model="gemini-2.0-flash",
        name="assistant",
        instruction="You are a helpful assistant."
    )

    runner = InMemoryRunner(agent=agent, app_name="my-app")

    # Trace agent execution
    with langfuse.start_as_current_span(
        name="agent-execution",
        input=query,
        metadata={"agent": "assistant"}
    ) as span:
        response = await runner.run_debug(user_id="user-1", input_text=query)

        # Extract final response
        final_response = extract_response(response)
        span.update(output=final_response)

        return final_response
```

### Tracing Tool Calls
```python
@observe(name="adk-tool-call")
def traced_tool(param: str) -> str:
    """Tool with observability."""
    result = execute_tool_logic(param)
    return result
```

---

## Trace Context Management

### Custom Trace IDs
```python
from langfuse import get_client
import uuid

langfuse = get_client()

# Deterministic trace ID from external seed
external_id = "request-12345"
trace_id = langfuse.create_trace_id(seed=external_id)

@observe()
def my_function(data, langfuse_trace_id=trace_id):
    # Uses custom trace ID
    pass
```

### Session Grouping
```python
@observe()
def chat_turn(message: str):
    langfuse = get_client()
    langfuse.update_current_trace(
        session_id="conversation-123",  # Groups related traces
        user_id="user-456"
    )
    return process(message)
```

---

## RAG Tracing Pattern

```python
from langfuse import observe, get_client

langfuse = get_client()

@observe()
def rag_query(question: str) -> str:
    # Trace retrieval
    with langfuse.start_as_current_observation(
        name="document-retrieval",
        input=question,
        as_type="retriever"
    ) as retrieval_span:
        docs = retriever.invoke(question)
        retrieval_span.update(output=docs)

    # Trace generation
    with langfuse.start_as_current_generation(
        name="answer-generation",
        model="gpt-4o",
        input={"question": question, "context": docs}
    ) as gen_span:
        answer = llm.generate(question, docs)
        gen_span.update(output=answer)

    return answer
```

---

## Anti-Patterns

### Forgetting to Flush
```python
# Wrong - traces may be lost in short-lived processes
def lambda_handler(event, context):
    process(event)
    return {"status": "ok"}

# Right
def lambda_handler(event, context):
    process(event)
    get_client().flush()  # Ensure traces are sent
    return {"status": "ok"}
```

### Over-Tracing
```python
# Wrong - tracing every tiny function
@observe()
def add(a, b):
    return a + b

# Right - trace meaningful operations
@observe()
def process_user_request(request):
    # Contains multiple steps worth tracing
    pass
```

---

**Next**: [03-cost-tracking.md](03-cost-tracking.md) - Token usage and cost monitoring
