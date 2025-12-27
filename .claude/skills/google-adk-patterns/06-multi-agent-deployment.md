# Module 06: Multi-Agent Systems & Deployment

Advanced patterns for hierarchical agents, workflows, and production deployment.

> **For current multi-agent API, use Context7:**
> ```
> get-library-docs: /google/adk-docs (topic: "multi-agent sub_agents hierarchical")
> ```

---

## Hierarchical Agent Pattern (LLM-Driven Delegation)

Create specialized sub-agents with a coordinator that routes requests:

```python
from google.adk.agents import LlmAgent

# Create specialized sub-agents
weather_specialist = LlmAgent(
    name="weather_specialist",
    model="gemini-2.0-flash",
    description="Handles all weather-related queries and forecasts",
    instruction="Provide accurate weather information for cities worldwide.",
    tools=[get_current_weather, get_forecast],  # Weather-specific tools
)

restaurant_specialist = LlmAgent(
    name="restaurant_specialist",
    model="gemini-2.0-flash",
    description="Handles restaurant recommendations and reservations",
    instruction="Recommend restaurants based on cuisine, location, and preferences.",
    tools=[search_restaurants, check_availability],  # Restaurant-specific tools
)

travel_specialist = LlmAgent(
    name="travel_specialist",
    model="gemini-2.0-flash",
    description="Handles flight bookings and travel planning",
    instruction="Help with flight searches, bookings, and travel itineraries.",
    tools=[search_flights, get_hotel_options],  # Travel-specific tools
)

# Create coordinator agent with sub-agents
coordinator = LlmAgent(
    name="travel_coordinator",
    model="gemini-2.0-flash",
    description="Main coordinator for travel planning assistance",
    instruction="""You are a travel planning coordinator.

    You have access to specialized agents:
    - weather_specialist: For weather queries
    - restaurant_specialist: For dining recommendations
    - travel_specialist: For flights and hotels

    Analyze user requests and delegate to the appropriate specialist.
    Combine results from multiple specialists when needed.
    """,
    sub_agents=[weather_specialist, restaurant_specialist, travel_specialist],
)

# The coordinator will automatically route queries to the right specialist
# based on the agent descriptions and user query
```

### How Hierarchical Delegation Works

1. **User sends query** to coordinator agent
2. **Coordinator analyzes query** using LLM reasoning
3. **Coordinator delegates** to appropriate sub-agent based on descriptions
4. **Sub-agent processes** with its specialized tools
5. **Coordinator receives result** and may delegate to another sub-agent
6. **Final response** returned to user

**Example Flow:**
```
User: "I'm traveling to Paris next week. What's the weather like and where should I eat?"

Coordinator → Analyzes query → Identifies two needs:
  1. Weather information
  2. Restaurant recommendations

Coordinator → Delegates to weather_specialist
  weather_specialist → Uses get_forecast() → Returns "Sunny, 18-22°C"

Coordinator → Delegates to restaurant_specialist
  restaurant_specialist → Uses search_restaurants() → Returns "Le Comptoir, Bistrot Paul Bert..."

Coordinator → Combines results → Final response to user
```

---

## Sequential Workflow Pattern

Process requests through a series of agents in order:

```python
from google.adk.agents import LlmAgent, SequentialAgent

# Define agents for each step
research_agent = LlmAgent(
    name="researcher",
    model="gemini-2.0-flash",
    description="Conducts research and gathers information",
    instruction="Research the given topic thoroughly and summarize key findings.",
    tools=[web_search, fetch_articles],
)

writer_agent = LlmAgent(
    name="writer",
    model="gemini-2.0-flash",
    description="Writes content based on research",
    instruction="Create engaging, well-structured content from research findings.",
)

editor_agent = LlmAgent(
    name="editor",
    model="gemini-2.0-flash",
    description="Edits and polishes written content",
    instruction="Review content for clarity, grammar, tone, and improve quality.",
)

# Create sequential workflow
article_pipeline = SequentialAgent(
    name="article_creator",
    sub_agents=[research_agent, writer_agent, editor_agent],
)

# When run, each agent processes the output of the previous agent in order
```

---

## Multi-Agent Best Practices

### 1. Clear, Distinct Descriptions

Critical for LLM-based routing:

```python
# ✅ Good - specific and distinct
description="Handles database queries and data retrieval operations"

# ❌ Bad - vague
description="Helps with data"
```

### 2. Single Parent Rule

An agent instance can only have one parent:

```python
# ✅ Good - each agent used once
coordinator = LlmAgent(name="coord", sub_agents=[agent1, agent2])

# ❌ Bad - agent1 used in two parents
coordinator1 = LlmAgent(name="coord1", sub_agents=[agent1, agent2])
coordinator2 = LlmAgent(name="coord2", sub_agents=[agent1, agent3])  # Error!
```

### 3. Appropriate Scope

Use hierarchies to define workflow scope and delegation boundaries.

### 4. Tool Distribution

Give each specialist only the tools they need:

```python
# ✅ Good - focused toolsets
weather_agent = LlmAgent(tools=[get_weather, get_forecast])
restaurant_agent = LlmAgent(tools=[search_restaurants, get_reviews])

# ❌ Bad - all tools on coordinator
coordinator = LlmAgent(tools=[get_weather, search_restaurants, ...])  # Don't do this
```

---

## RAG (Retrieval-Augmented Generation) Pattern

```python
"""
RAG pattern with Google ADK.
"""
from google.adk.agents import LlmAgent
from typing import List

def search_knowledge_base(query: str, max_results: int = 5) -> List[dict]:
    """Search vector database for relevant documents.

    Args:
        query: Search query string.
        max_results: Maximum number of documents to retrieve.

    Returns:
        List of relevant document chunks with content and metadata.
    """
    # In production: Use Vertex AI Vector Search, pgvector, or similar
    # This is a simplified example

    # Simulated vector search results
    return [
        {
            "content": "Our refund policy allows returns within 30 days...",
            "source": "policies/refund.md",
            "score": 0.92
        },
        {
            "content": "For refunds, contact support@example.com...",
            "source": "support/contact.md",
            "score": 0.85
        },
    ]

# Create RAG agent
rag_agent = LlmAgent(
    model="gemini-2.0-flash",
    name="knowledge_assistant",
    tools=[search_knowledge_base],
    instruction="""You are a knowledge base assistant.

    When answering questions:
    1. ALWAYS search for relevant documents using search_knowledge_base()
    2. Base your answer ONLY on the retrieved document content
    3. Cite the sources you used (include source field)
    4. If no relevant documents are found, say "I don't have information on that topic"
    5. Never make up information or answer without searching first

    Format your responses clearly with source citations.
    """,
)
```

---

## Deployment to Vertex AI Agent Engine

```python
"""
Deploy Google ADK agent to Vertex AI Agent Engine for production.
"""
from google.adk.agents import LlmAgent
from vertexai.agent_engines import AdkApp
import vertexai

# Create your agent
agent = LlmAgent(
    model="gemini-2.0-flash",
    name="production_agent",
    description="Production-ready agent",
    instruction="You are a production assistant.",
    tools=[tool1, tool2, tool3],
)

# Wrap agent in AdkApp
app = AdkApp(agent=agent)

# Initialize Vertex AI
vertexai.init(project="your-gcp-project-id", location="us-central1")

# Create client
client = vertexai.Client(
    project="your-gcp-project-id",
    location="us-central1"
)

# Deploy to Agent Engine
remote_agent = client.agent_engines.create(
    agent=app,
    config={
        "display_name": "Production Agent",
        "requirements": [
            "google-cloud-aiplatform[agent_engines,adk]",
            "any-other-dependencies",
        ],
        "staging_bucket": "gs://your-staging-bucket",
    }
)

print(f"Agent deployed: {remote_agent.name}")
```

### Benefits of Agent Engine Deployment

- **Managed Sessions**: Automatic `VertexAiSessionService` for persistent state
- **Scalability**: Auto-scaling infrastructure
- **Monitoring**: Built-in Cloud Logging and Trace
- **Multi-turn Conversations**: Automatic memory management
- **Production-ready**: High availability and reliability

---

## Common Patterns

### Pattern 1: Tool-Heavy Agent

```python
"""Agent with many specialized tools."""

# Define all tools
def tool1(...): pass
def tool2(...): pass
def tool3(...): pass

agent = LlmAgent(
    model="gemini-2.0-flash",
    name="utility_agent",
    tools=[tool1, tool2, tool3],
    instruction="Use tools to help users accomplish tasks efficiently.",
)
```

### Pattern 2: Coordinator/Router

```python
"""Main coordinator routing to specialists."""

specialist_a = LlmAgent(name="spec_a", model="gemini-2.0-flash", ...)
specialist_b = LlmAgent(name="spec_b", model="gemini-2.0-flash", ...)
specialist_c = LlmAgent(name="spec_c", model="gemini-2.0-flash", ...)

coordinator = LlmAgent(
    name="coordinator",
    model="gemini-2.0-flash",
    sub_agents=[specialist_a, specialist_b, specialist_c],
    instruction="Route requests to the most appropriate specialist.",
)
```

### Pattern 3: Pipeline/Workflow

```python
"""Sequential processing pipeline."""

step1 = LlmAgent(name="extract", model="gemini-2.0-flash", ...)
step2 = LlmAgent(name="transform", model="gemini-2.0-flash", ...)
step3 = LlmAgent(name="load", model="gemini-2.0-flash", ...)

pipeline = SequentialAgent(
    name="etl_pipeline",
    sub_agents=[step1, step2, step3],
)
```

---

## Complete Multi-Agent Example

```python
"""
Complete example: Customer service system with multiple specialists.
"""
from google.adk.agents import LlmAgent
from google.adk.runners import InMemoryRunner
import asyncio

# Define tools for each specialist

def check_order_status(order_id: str) -> dict:
    """Check order status."""
    return {"order_id": order_id, "status": "shipped", "eta": "2 days"}

def process_refund(order_id: str, reason: str) -> dict:
    """Process refund request."""
    return {"refund_id": "REF123", "amount": 99.99, "status": "approved"}

def search_products(query: str) -> list[dict]:
    """Search product catalog."""
    return [{"id": "P123", "name": "Widget", "price": 29.99}]

# Create specialists

order_specialist = LlmAgent(
    name="order_specialist",
    model="gemini-2.0-flash",
    description="Handles order tracking and status inquiries",
    tools=[check_order_status],
    instruction="Help customers track their orders and provide status updates.",
)

refund_specialist = LlmAgent(
    name="refund_specialist",
    model="gemini-2.0-flash",
    description="Handles refunds and returns",
    tools=[process_refund],
    instruction="Process refund requests and explain return policies.",
)

product_specialist = LlmAgent(
    name="product_specialist",
    model="gemini-2.0-flash",
    description="Helps customers find and learn about products",
    tools=[search_products],
    instruction="Help customers find products and answer product questions.",
)

# Create coordinator

customer_service = LlmAgent(
    name="customer_service_coordinator",
    model="gemini-2.0-flash",
    description="Main customer service coordinator",
    instruction="""You are a customer service coordinator.

    You have access to specialists:
    - order_specialist: For order tracking
    - refund_specialist: For refunds and returns
    - product_specialist: For product questions

    Greet customers warmly and route their requests appropriately.
    """,
    sub_agents=[order_specialist, refund_specialist, product_specialist],
)

# Run the system

async def main():
    runner = InMemoryRunner(agent=customer_service, app_name="support")
    
    # Test query
    response = await runner.run_debug(
        "I want to check the status of order #12345"
    )
    print(response)

asyncio.run(main())
```

---

## Testing Multi-Agent Systems

### Unit Test Example

```python
import pytest
from google.adk.agents import LlmAgent
from google.adk.runners import InMemoryRunner

@pytest.mark.asyncio
async def test_coordinator_routes_to_specialist():
    """Verify coordinator delegates to correct specialist."""
    
    # Mock specialists
    weather_agent = LlmAgent(
        name="weather",
        model="gemini-2.0-flash",
        description="Weather specialist",
        instruction="Provide weather info."
    )
    
    news_agent = LlmAgent(
        name="news",
        model="gemini-2.0-flash",
        description="News specialist",
        instruction="Provide news."
    )
    
    # Coordinator
    coordinator = LlmAgent(
        name="coord",
        model="gemini-2.0-flash",
        sub_agents=[weather_agent, news_agent],
        instruction="Route to appropriate specialist."
    )
    
    # Test weather query routes to weather_agent
    runner = InMemoryRunner(agent=coordinator, app_name="test")
    response = await runner.run_debug("What's the weather in Paris?")
    
    # Verify response is weather-related (implementation-specific assertion)
    assert "weather" in str(response).lower() or "temperature" in str(response).lower()
```

---

## Summary

**Key Patterns**:
1. **Hierarchical agents** - Coordinator with specialists
2. **Sequential workflows** - Pipeline processing
3. **RAG pattern** - Knowledge base + LLM
4. **Tool distribution** - Each specialist has focused toolset
5. **Clear descriptions** - Critical for LLM routing
6. **Single parent rule** - Agent instances used once

**Common Errors**:
- ❌ Vague agent descriptions → routing failures
- ❌ Reusing agent instances → single parent error
- ❌ All tools on coordinator → defeats purpose
- ❌ No clear workflow scope → confusion

**Production Deployment**:
- ✅ Deploy to Vertex AI Agent Engine
- ✅ Use managed sessions (VertexAiSessionService)
- ✅ Configure auto-scaling
- ✅ Enable Cloud Logging/Trace
- ✅ Set up monitoring and alerts

---

**See Also**:
- [01-agent-setup.md](01-agent-setup.md) - Basic agent creation
- [04-tool-integration.md](04-tool-integration.md) - Adding tools
- [05-fastapi-integration.md](05-fastapi-integration.md) - FastAPI integration
- [README.md](README.md) - Quick reference guide
