# Module 01: Agent Setup & Configuration

Complete guide to installing, authenticating, and creating Google ADK agents.

> **For current API syntax, use Context7:**
> ```
> get-library-docs: /google/adk-docs (topic: "LlmAgent installation")
> ```

---

## Installation & Requirements

### Requirements

- **Python 3.10 or higher** (REQUIRED as of ADK v1.19.0+)
- Python 3.9 is no longer supported

### Installation

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install Google ADK
pip install google-adk

# Verify installation
pip show google-adk
```

### Development Version

```bash
# Install from GitHub main branch
pip install git+https://github.com/google/adk-python.git@main
```

---

## Core Imports

```python
# Agent classes
from google.adk.agents import LlmAgent, SequentialAgent, BaseAgent

# Runners (required to execute agents)
from google.adk.runners import InMemoryRunner, Runner

# Session management
from google.adk.sessions import InMemorySessionService

# Content types (for messages)
from google.genai import types

# Tool decorator (optional)
from google.adk.tools import adk_tool

# Pydantic for type safety
from pydantic import BaseModel, Field
```

---

## Authentication

### For Vertex AI (Production)

**Set Environment Variables:**

```python
import os

# Enable Vertex AI mode
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "TRUE"

# Set GCP project and location
os.environ["GOOGLE_CLOUD_PROJECT"] = "your-gcp-project-id"
os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"

# Optional: Suppress experimental warnings
os.environ["ADK_SUPPRESS_EXPERIMENTAL_FEATURE_WARNINGS"] = "true"
```

**Or via Shell:**

```bash
export GOOGLE_GENAI_USE_VERTEXAI=TRUE
export GOOGLE_CLOUD_PROJECT=your-project-id
export GOOGLE_CLOUD_LOCATION=us-central1
```

**Authentication Methods:**

1. **Application Default Credentials (Recommended)**
   ```bash
   gcloud auth application-default login
   ```

2. **Service Account Key**
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
   ```

### For Google AI Studio (Development)

```bash
export GOOGLE_API_KEY="your-api-key"
export GOOGLE_GENAI_USE_VERTEXAI=FALSE
```

---

## Basic Agent Creation

### Simple Agent

```python
from google.adk.agents import LlmAgent

# Create basic agent
agent = LlmAgent(
    model="gemini-2.0-flash",              # Required: Model name
    name="assistant",                       # Required: Agent identifier
    instruction="You are a helpful AI assistant.",  # Optional: System instructions
)
```

### Agent with Configuration

```python
agent = LlmAgent(
    model="gemini-2.0-flash",
    name="data_analyst",
    description="Analyzes data and provides insights",  # Used for routing/delegation
    instruction="""You are a data analysis expert.

    Your responsibilities:
    - Analyze datasets and identify patterns
    - Calculate statistics
    - Provide actionable insights
    - Communicate findings clearly
    """,
    generate_content_config={
        "temperature": 0.7,
        "top_p": 0.95,
        "max_output_tokens": 2048,
    }
)
```

### Required vs Optional Parameters

**Required:**
- `model`: Model identifier (e.g., "gemini-2.0-flash")
- `name`: Unique agent name

**Optional but Important:**
- `description`: Clear description for LLM-based routing to this agent
- `instruction`: System prompt defining agent behavior
- `tools`: List of function tools
- `sub_agents`: Child agents for hierarchical systems
- `generate_content_config`: Model parameters

---

## Running Agents

### Using InMemoryRunner (Development)

```python
import asyncio
from google.adk.runners import InMemoryRunner
from google.genai import types

async def run_agent():
    # Create agent
    agent = LlmAgent(
        model="gemini-2.0-flash",
        name="assistant",
        instruction="You are helpful.",
    )

    # Create runner
    runner = InMemoryRunner(agent=agent, app_name="my_app")

    # Get session service
    session_service = runner.session_service

    # Create session
    user_id = "user123"
    session_id = "session456"
    await session_service.create_session(
        app_name="my_app",
        user_id=user_id,
        session_id=session_id,
    )

    # Run agent
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=types.Content(
            role="user",
            parts=[types.Part(text="Hello! How are you?")]
        ),
    ):
        if event.is_final_response() and event.content:
            print(f"Agent: {event.content.parts[0].text.strip()}")

# Execute
asyncio.run(run_agent())
```

### Using run_debug() for Quick Testing

```python
import asyncio
from google.adk.runners import InMemoryRunner

async def quick_test():
    agent = LlmAgent(
        model="gemini-2.0-flash",
        name="assistant",
    )

    runner = InMemoryRunner(agent=agent, app_name="test_app")

    # Simple debug run (ADK 1.18+)
    response = await runner.run_debug("What is 2+2?")
    print(response)

asyncio.run(quick_test())
```

---

## Model Configuration

### Advanced Configuration

```python
agent = LlmAgent(
    model="gemini-2.0-flash",
    name="configured_agent",
    generate_content_config={
        "temperature": 0.9,          # Creativity (0.0-1.0)
        "top_p": 0.95,               # Nucleus sampling
        "top_k": 40,                 # Top-k sampling
        "max_output_tokens": 2048,   # Maximum response length
        "candidate_count": 1,        # Number of candidates to generate
        "stop_sequences": ["END"],   # Stop generation at these sequences
    }
)
```

### Model Selection Guide

> **For latest model names, use Context7:**
> ```
> get-library-docs: /google/adk-docs (topic: "gemini model names")
> ```

**Current Models (verified Dec 2025):**
- **gemini-2.0-flash**: Fast, reliable, good for most agent use cases
- **gemini-3-flash-preview**: Pro-level intelligence at Flash speed/pricing (RECOMMENDED for new projects)
- **gemini-3-pro-preview**: Most capable model, best for complex reasoning

**Note**: Model names change frequently. Gemini 3 models are in preview. Always verify with Context7 or official docs.

---

## Best Practices

### 1. Clear Agent Instructions

```python
# ✅ Good - specific and actionable
instruction="""You are a customer support agent.

Your responsibilities:
- Help users with product questions
- Process refund requests using the refund_tool
- Escalate complex issues to human agents
- Always be polite and professional

Never:
- Make promises about features we don't have
- Provide medical or legal advice
- Share customer data
"""

# ❌ Bad - vague
instruction="You help customers."
```

### 2. Error Handling

```python
import asyncio
from google.adk.runners import InMemoryRunner

async def safe_agent_call():
    try:
        runner = InMemoryRunner(agent=agent, app_name="app")
        response = await runner.run_debug("Hello")
        return response

    except Exception as e:
        # Log error
        print(f"Agent error: {e}")

        # Return graceful fallback
        return "I'm having trouble processing your request. Please try again."
```

### 3. Use run_debug() for Development

```python
# Development/Testing
async def dev_test():
    runner = InMemoryRunner(agent=agent, app_name="dev")
    result = await runner.run_debug("Test query")
    print(result)

# Production - full session management
async def production():
    runner = InMemoryRunner(agent=agent, app_name="prod")
    async for event in runner.run_async(...):
        # Handle events properly
        pass
```

---

## Troubleshooting

### Issue: Authentication Failures in Cloud Run

**Problem**: ADK 0.5.0 fails Vertex AI authentication in Cloud Run despite correct env vars

**Solution**: Explicitly initialize credentials
```python
import google.auth
from google.auth.transport.requests import Request

credentials, project = google.auth.default()
credentials.refresh(Request())

# Then set environment variables
os.environ["GOOGLE_CLOUD_PROJECT"] = project
```

### Issue: "Module 'deprecated' not found"

**Problem**: Some ADK versions have dependency issues

**Solution**: Explicitly install deprecated module
```bash
pip install deprecated
```

---

## Migration from Google GenAI SDK

If you have code using `google-genai` package and want to migrate to ADK:

### Before (GenAI SDK)

```python
from google import genai
from google.genai import types

client = genai.Client(vertexai=True, project="...", location="...")
response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="Hello"
)
```

### After (Google ADK)

```python
from google.adk.agents import LlmAgent
from google.adk.runners import InMemoryRunner
import os

# Set environment variables
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "TRUE"
os.environ["GOOGLE_CLOUD_PROJECT"] = "..."
os.environ["GOOGLE_CLOUD_LOCATION"] = "..."

# Create agent
agent = LlmAgent(model="gemini-2.0-flash", name="assistant")

# Run with runner
runner = InMemoryRunner(agent=agent, app_name="app")
response = await runner.run_debug("Hello")
```

---

## Quick Reference

```python
# Install
pip install google-adk  # Python 3.10+ required

# Imports
from google.adk.agents import LlmAgent
from google.adk.runners import InMemoryRunner

# Auth (Vertex AI)
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "TRUE"
os.environ["GOOGLE_CLOUD_PROJECT"] = "project-id"
os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"

# Create Agent
agent = LlmAgent(
    model="gemini-2.0-flash",  # Required
    name="agent_name",         # Required
    instruction="...",         # Optional
)

# Run Agent (Development)
runner = InMemoryRunner(agent=agent, app_name="app")
response = await runner.run_debug("Query")
```

---

**Next Module**: [02-event-persistence.md](02-event-persistence.md) - Learn critical event handling patterns

**See Also**:
- [04-tool-integration.md](04-tool-integration.md) - Adding function calling
- [05-fastapi-integration.md](05-fastapi-integration.md) - API integration
- [06-multi-agent-deployment.md](06-multi-agent-deployment.md) - Multi-agent systems
