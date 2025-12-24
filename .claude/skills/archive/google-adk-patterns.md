# Google ADK (Agent Development Kit) Patterns Skill

This skill provides accurate, up-to-date patterns for building AI agents using **Google ADK (Agent Development Kit)** - the official framework for production-ready multi-agent applications.

## What is Google ADK?

**Google ADK** is a framework for building sophisticated AI agent applications with:
- Multi-agent systems with hierarchical delegation
- Function calling and custom tools
- Session management and conversational memory
- Deployment to Vertex AI Agent Engine
- Workflow agents (sequential, parallel, loop)

**IMPORTANT**: Google ADK (`google-adk`) is NOT the same as Google GenAI SDK (`google-genai`). ADK is a complete agent framework; GenAI SDK is for direct Gemini API calls.

## When to Use This Skill

Use this skill when you need to:
- Build production-ready AI agents with Google ADK
- Implement multi-agent systems
- Create agents with custom tools
- Deploy agents to Vertex AI
- Follow Google ADK best practices (2025)

---

## Installation & Setup

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

## Tools (Function Calling)

### Simple Python Function Tools

**Google ADK automatically converts Python functions to tools using:**
- Type hints for parameter types
- Docstrings for descriptions
- Return type hints

```python
def get_current_weather(city: str, unit: str = "celsius") -> dict:
    """Get the current weather for a specified city.

    Args:
        city: The name of the city to get weather for.
        unit: Temperature unit (celsius or fahrenheit). Defaults to celsius.

    Returns:
        A dictionary containing weather information including temperature and conditions.
    """
    # Simulated weather data
    return {
        "city": city,
        "temperature": 22,
        "unit": unit,
        "conditions": "Partly cloudy",
    }

def calculate_sum(numbers: list[float]) -> float:
    """Calculate the sum of a list of numbers.

    Args:
        numbers: List of numbers to sum.

    Returns:
        The total sum of all numbers.
    """
    return sum(numbers)

# Create agent with tools
agent = LlmAgent(
    model="gemini-2.0-flash",
    name="weather_agent",
    tools=[get_current_weather, calculate_sum],  # Just pass functions
    instruction="You can check weather and do calculations.",
)
```

### Tool Best Practices

1. **Type Hints Required**: All parameters must have type hints
   ```python
   # ✅ Good
   def get_user(user_id: int) -> dict:
       pass

   # ❌ Bad - no type hints
   def get_user(user_id):
       pass
   ```

2. **Clear Docstrings**: ADK parses docstrings to generate tool schemas
   ```python
   # ✅ Good
   def search_products(query: str, max_results: int = 10) -> list[dict]:
       """Search for products in the catalog.

       Args:
           query: Search query string.
           max_results: Maximum number of results to return.

       Returns:
           List of product dictionaries with name, price, and description.
       """
       pass

   # ❌ Bad - no docstring
   def search_products(query: str, max_results: int = 10) -> list[dict]:
       return []
   ```

3. **Specific Types**: Use specific types (list[str], dict, int) not generic (any, object)

4. **Return Values**: Always return structured data (dict, list, str, int), not None

### Using @adk_tool Decorator

```python
from google.adk.tools import adk_tool

@adk_tool
def fetch_user_profile(user_id: int) -> dict:
    """Fetch user profile information from database.

    Args:
        user_id: The unique user identifier.

    Returns:
        User profile dictionary with id, name, email, and preferences.
    """
    # Database lookup (simulated)
    return {
        "id": user_id,
        "name": "Alice Smith",
        "email": "alice@example.com",
        "preferences": {"theme": "dark", "notifications": True}
    }
```

The `@adk_tool` decorator standardizes responses and provides additional metadata.

---

## Complete Example: Data Analysis Agent

```python
"""
Complete example: Data Analysis Agent with tools using Google ADK
"""
import asyncio
from typing import List, Dict
from google.adk.agents import LlmAgent
from google.adk.runners import InMemoryRunner
from google.genai import types
import statistics

# Define tools as Python functions

def query_sales_data(product: str, days: int = 30) -> List[Dict]:
    """Query sales data for a specific product.

    Args:
        product: Product name to query.
        days: Number of days of historical data. Defaults to 30.

    Returns:
        List of daily sales records with date, units, and revenue.
    """
    # Simulated database query
    return [
        {"date": "2025-01-20", "units": 42, "revenue": 4200.00},
        {"date": "2025-01-21", "units": 38, "revenue": 3800.00},
        {"date": "2025-01-22", "units": 55, "revenue": 5500.00},
    ]

def calculate_statistics(values: List[float]) -> Dict:
    """Calculate statistical metrics for a dataset.

    Args:
        values: List of numerical values.

    Returns:
        Dictionary with mean, median, min, max, and standard deviation.
    """
    if not values:
        return {"error": "No data provided"}

    return {
        "mean": statistics.mean(values),
        "median": statistics.median(values),
        "min": min(values),
        "max": max(values),
        "std_dev": statistics.stdev(values) if len(values) > 1 else 0,
    }

def create_recommendation(analysis: str) -> str:
    """Generate actionable recommendations based on analysis.

    Args:
        analysis: Text description of the analysis findings.

    Returns:
        Formatted recommendations string.
    """
    # In production, this might use another LLM call or business logic
    return f"Based on the analysis: {analysis}\n\nRecommendations:\n- Monitor trends closely\n- Adjust inventory accordingly"

# Create agent with tools
data_agent = LlmAgent(
    model="gemini-2.0-flash",
    name="data_analyst",
    description="Analyzes sales data and provides insights",
    tools=[query_sales_data, calculate_statistics, create_recommendation],
    instruction="""You are a data analysis assistant.

    Your capabilities:
    - Query sales data using query_sales_data()
    - Calculate statistics using calculate_statistics()
    - Generate recommendations using create_recommendation()

    Always:
    1. Query relevant data first
    2. Calculate meaningful statistics
    3. Provide clear, actionable insights
    4. Support recommendations with data
    """,
)

# Run the agent
async def main():
    runner = InMemoryRunner(agent=data_agent, app_name="analytics_app")

    # Create session
    session_service = runner.session_service
    await session_service.create_session(
        app_name="analytics_app",
        user_id="analyst_001",
        session_id="session_001",
    )

    # Analyze product
    async for event in runner.run_async(
        user_id="analyst_001",
        session_id="session_001",
        new_message=types.Content(
            role="user",
            parts=[types.Part(text="Analyze sales performance for ProductX")]
        ),
    ):
        if event.is_final_response() and event.content:
            print("\n=== Analysis Result ===")
            print(event.content.parts[0].text)

asyncio.run(main())
```

---

## Multi-Agent Systems

### Hierarchical Agent Pattern (LLM-Driven Delegation)

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

### Sequential Workflow Pattern

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

### Multi-Agent Best Practices

1. **Clear, Distinct Descriptions**: Critical for LLM-based routing
   ```python
   # ✅ Good - specific and distinct
   description="Handles database queries and data retrieval operations"

   # ❌ Bad - vague
   description="Helps with data"
   ```

2. **Single Parent Rule**: An agent instance can only have one parent
   ```python
   # ✅ Good - each agent used once
   coordinator = LlmAgent(name="coord", sub_agents=[agent1, agent2])

   # ❌ Bad - agent1 used in two parents
   coordinator1 = LlmAgent(name="coord1", sub_agents=[agent1, agent2])
   coordinator2 = LlmAgent(name="coord2", sub_agents=[agent1, agent3])  # Error!
   ```

3. **Appropriate Scope**: Use hierarchies to define workflow scope and delegation boundaries

4. **Tool Distribution**: Give each specialist only the tools they need

---

## FastAPI Integration

```python
"""
Integrate Google ADK agents into FastAPI applications.
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google.adk.agents import LlmAgent
from google.adk.runners import InMemoryRunner
from google.genai import types
from contextlib import asynccontextmanager
import uuid

# Global runner
runner = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize agent and runner on startup."""
    global runner

    # Create agent
    agent = LlmAgent(
        model="gemini-2.0-flash",
        name="api_assistant",
        instruction="You are a helpful API assistant.",
        tools=[],  # Add your tools here
    )

    # Create runner
    runner = InMemoryRunner(agent=agent, app_name="api_app")

    yield

    # Cleanup on shutdown
    runner = None

app = FastAPI(lifespan=lifespan)

# Request/Response models
class ChatRequest(BaseModel):
    message: str
    user_id: str = "default_user"
    session_id: str | None = None

class ChatResponse(BaseModel):
    response: str
    session_id: str

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send message to ADK agent."""
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())

        # Create session if it doesn't exist
        session_service = runner.session_service
        try:
            await session_service.create_session(
                app_name="api_app",
                user_id=request.user_id,
                session_id=session_id,
            )
        except:
            pass  # Session may already exist

        # Run agent
        response_text = ""
        async for event in runner.run_async(
            user_id=request.user_id,
            session_id=session_id,
            new_message=types.Content(
                role="user",
                parts=[types.Part(text=request.message)]
            ),
        ):
            if event.is_final_response() and event.content:
                response_text = event.content.parts[0].text.strip()

        return ChatResponse(
            response=response_text,
            session_id=session_id,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "runner": runner is not None}
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

## Conversational Memory & Sessions

### Session Management

```python
import asyncio
from google.adk.runners import InMemoryRunner
from google.genai import types

async def multi_turn_conversation():
    agent = LlmAgent(
        model="gemini-2.0-flash",
        name="assistant",
    )

    runner = InMemoryRunner(agent=agent, app_name="chat_app")
    session_service = runner.session_service

    user_id = "user123"
    session_id = "session456"

    # Create session
    await session_service.create_session(
        app_name="chat_app",
        user_id=user_id,
        session_id=session_id,
    )

    # Helper function for sending messages
    async def send_message(message: str):
        print(f"\nUser: {message}")
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=types.Content(
                role="user",
                parts=[types.Part(text=message)]
            ),
        ):
            if event.is_final_response() and event.content:
                print(f"Agent: {event.content.parts[0].text.strip()}")

    # Multi-turn conversation with memory
    await send_message("My name is Alice.")
    await send_message("What's my name?")  # Agent remembers: "Alice"
    await send_message("I like pizza.")
    await send_message("What food do I like?")  # Agent remembers: "pizza"

asyncio.run(multi_turn_conversation())
```

### GCS-Backed Session Storage (Production Pattern)

**IMPORTANT**: Google ADK does NOT have a `CloudStorageMemory` class. For persistent session storage in production, you need to implement a custom session service using `BaseSessionService`.

```python
"""
Custom GCS session service for persistent session storage.
Extends BaseSessionService to store sessions in Google Cloud Storage.
"""
from google.adk.sessions import BaseSessionService, Session, ListSessionResponse
from google.cloud import storage
import json
from typing import Optional

class GcsSessionService(BaseSessionService):
    """Session service that persists sessions to Google Cloud Storage."""

    def __init__(self, bucket_name: str, project: Optional[str] = None):
        """Initialize GCS session service.

        Args:
            bucket_name: Name of the GCS bucket for session storage
            project: GCP project ID (uses default credentials if not provided)
        """
        self.bucket_name = bucket_name
        self.client = storage.Client(project=project)
        self.bucket = self.client.bucket(bucket_name)

    def _get_blob_path(self, app_name: str, user_id: str, session_id: str) -> str:
        """Generate GCS blob path for a session."""
        return f"sessions/{app_name}/{user_id}/{session_id}.json"

    async def create_session(
        self,
        app_name: str,
        user_id: str,
        session_id: str,
        state: Optional[dict] = None,
    ) -> Session:
        """Create a new session and save to GCS."""
        session = Session(
            id=session_id,
            user_id=user_id,
            state=state or {},
        )

        # Save to GCS
        blob_path = self._get_blob_path(app_name, user_id, session_id)
        blob = self.bucket.blob(blob_path)
        blob.upload_from_string(
            json.dumps({
                "id": session.id,
                "user_id": session.user_id,
                "state": session.state,
            }),
            content_type="application/json"
        )

        return session

    async def get_session(
        self,
        app_name: str,
        user_id: str,
        session_id: str,
    ) -> Optional[Session]:
        """Retrieve session from GCS."""
        blob_path = self._get_blob_path(app_name, user_id, session_id)
        blob = self.bucket.blob(blob_path)

        if not blob.exists():
            return None

        data = json.loads(blob.download_as_text())
        return Session(
            id=data["id"],
            user_id=data["user_id"],
            state=data.get("state", {}),
        )

    async def list_sessions(
        self,
        app_name: str,
        user_id: str,
    ) -> ListSessionResponse:
        """List all sessions for a user from GCS."""
        prefix = f"sessions/{app_name}/{user_id}/"
        blobs = self.bucket.list_blobs(prefix=prefix)

        sessions = []
        for blob in blobs:
            if blob.name.endswith(".json"):
                data = json.loads(blob.download_as_text())
                sessions.append(Session(
                    id=data["id"],
                    user_id=data["user_id"],
                    state=data.get("state", {}),
                ))

        return ListSessionResponse(sessions=sessions)

    async def delete_session(
        self,
        app_name: str,
        user_id: str,
        session_id: str,
    ) -> None:
        """Delete session from GCS."""
        blob_path = self._get_blob_path(app_name, user_id, session_id)
        blob = self.bucket.blob(blob_path)

        if blob.exists():
            blob.delete()

# Usage in FastAPI with GCS sessions
from fastapi import FastAPI
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize with GCS session service."""
    global runner

    # Create agent
    agent = LlmAgent(
        model="gemini-2.0-flash",
        name="assistant",
        instruction="You are helpful.",
    )

    # Create runner with in-memory session service first
    runner = InMemoryRunner(agent=agent, app_name="my_app")

    # IMPORTANT: Replace session service AFTER runner creation
    # InMemoryRunner doesn't accept session_service in constructor
    gcs_service = GcsSessionService(
        bucket_name="my-session-bucket",
        project="my-gcp-project"
    )
    runner.session_service = gcs_service  # Replace after initialization

    yield

    runner = None

app = FastAPI(lifespan=lifespan)
```

**Key Implementation Notes:**

1. **BaseSessionService Methods**: Only 4 methods required:
   - `create_session()`: Create and persist session
   - `get_session()`: Retrieve session from storage
   - `list_sessions()`: List sessions by user/app
   - `delete_session()`: Remove session

2. **Runner Integration Pattern**:
   ```python
   # ❌ This doesn't work - InMemoryRunner doesn't accept session_service
   runner = InMemoryRunner(agent=agent, app_name="app", session_service=gcs_service)

   # ✅ This works - set session_service after initialization
   runner = InMemoryRunner(agent=agent, app_name="app")
   runner.session_service = gcs_service
   ```

3. **GCS Bucket Configuration**:
   - **Region**: Use regional buckets in your target region (e.g., `europe-west1`)
   - **Storage Class**: `REGIONAL` or `STANDARD`
   - **Lifecycle**: Add lifecycle rule to delete sessions after 30 days
   - **Cost**: ~$0.0002/month for 1000 sessions (negligible vs Redis $30-50/month)

4. **Session JSON Structure**:
   ```json
   {
     "id": "session-123",
     "user_id": "user-456",
     "state": {
       "key": "value",
       "context": "data"
     }
   }
   ```

5. **Blob Path Pattern**: `sessions/{app_name}/{user_id}/{session_id}.json`

### Session Best Practices

1. **Unique Session IDs**: Use UUIDs or user-specific identifiers
2. **Session Cleanup**: Delete old sessions periodically to manage memory
3. **User Isolation**: Different users should have different sessions
4. **Context Window**: ADK manages context automatically, but be aware of token limits
5. **Production Storage**: Use GCS-backed sessions for production (sessions persist across restarts)
6. **Development Storage**: Use `InMemorySessionService` for local development
7. **Lifecycle Policies**: Configure GCS bucket with 30-day lifecycle to auto-delete old sessions

---

## Event Serialization & Persistence

### Understanding ADK Events

When you run an agent, the runner returns a list of Event objects that represent the conversation turn:

```python
result = await runner.run_debug("Hello, agent!")
# result is a list of Event objects (typically google.genai.types.Content)

for event in result:
    print(f"Event type: {type(event).__name__}")
    print(f"Role: {event.content.role if hasattr(event, 'content') else event.role}")
```

**Event Structure**:
- Events are Pydantic models (typically `google.genai.types.Content` or `google.genai.types.Event`)
- Each event has:
  - `content`: The actual content (role, parts, etc.)
  - `role`: "user" or "model"
  - `parts`: List of Part objects (text, function_call, function_response, inline_data with bytes, etc.)
  - Metadata: timestamp, model_version, usage_metadata, etc.

### Serializing Events to JSON

**CRITICAL**: Always use `model_dump(mode='json')` when serializing ADK events to JSON.

**Problem**: Events may contain bytes data (images, files, etc.) which are not JSON-serializable.

**Anti-Pattern** ❌:
```python
# WRONG: Bytes data will cause JSON serialization to fail
event_dict = event.model_dump()  # mode='python' by default (keeps bytes as bytes)
json_str = json.dumps(event_dict)  # ERROR: Object of type bytes is not JSON serializable
```

**Correct Pattern** ✅:
```python
# CORRECT: Pydantic automatically converts bytes → base64
event_dict = event.model_dump(mode='json')  # Converts bytes to base64 strings
json_str = json.dumps(event_dict)  # SUCCESS
```

**Example: Saving Events to GCS**:
```python
from google.cloud import storage
import json

def save_session_events(session_id: str, events: list):
    """Save ADK events to GCS as JSON."""
    client = storage.Client()
    bucket = client.bucket("my-sessions-bucket")
    blob = bucket.blob(f"sessions/{session_id}.json")

    # Serialize events using mode='json' to handle bytes → base64
    events_data = [
        event.model_dump(mode='json')
        for event in events
    ]

    session_data = {
        "session_id": session_id,
        "events": events_data,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    # Save to GCS
    blob.upload_from_string(
        json.dumps(session_data, indent=2),
        content_type="application/json"
    )
```

### Deserializing Events from JSON

When loading events back, Pydantic automatically converts base64 strings back to bytes:

```python
from google.genai import types

def load_session_events(session_id: str) -> list:
    """Load ADK events from GCS JSON."""
    client = storage.Client()
    bucket = client.bucket("my-sessions-bucket")
    blob = bucket.blob(f"sessions/{session_id}.json")

    # Download and parse JSON
    json_str = blob.download_as_text()
    session_data = json.loads(json_str)

    # Reconstruct Event objects (base64 → bytes automatically)
    events = []
    for event_data in session_data["events"]:
        # Remove custom fields before validation
        event_dict = {k: v for k, v in event_data.items() if k != 'type'}

        # Pydantic validates and converts base64 back to bytes
        event = types.Content.model_validate(event_dict)
        events.append(event)

    return events
```

### Persisting Complete Conversation History

**CRITICAL**: ADK's `run_async()` does NOT automatically persist events to the session. You must manually manage session.events.

**The Problem**:
1. `run_async()` returns agent response events
2. These events are NOT automatically added to `session.events`
3. User message is NOT in the returned events
4. Result: If you don't manually manage events, nothing persists!

**Anti-Pattern** ❌:
```python
# WRONG: Assumes run_async() automatically persists events
user_message = types.Content(
    parts=[types.Part(text="Hello!")],
    role="user"
)

result = await runner.run_async(
    user_id="user",
    session_id="session",
    new_message=user_message
)
# BUG: session.events is empty! Nothing saved!
```

**Correct Pattern** ✅:
```python
# CORRECT: Manually manage session.events
# 1. Load session
session = await session_service.get_session(
    app_name="app",
    user_id="user",
    session_id="session_id"
)

# 2. Wrap user message in Event (if needed for ADK consistency)
user_event = Event(
    content=types.Content(
        parts=[types.Part(text="Hello!")],
        role="user"
    ),
    author="user",  # IMPORTANT: Set author (not None to avoid Pydantic errors)
    branch=None
)

# 3. Run agent (returns only agent events)
agent_events = []
async for event in runner.run_async(
    user_id="user",
    session_id="session_id",
    new_message=user_event.content,
):
    agent_events.append(event)

# 4. Add both user and agent events to session
session.events.append(user_event)
session.events.extend(agent_events)

# 5. Save session (ONE save at end, not multiple)
await session_service._save_session(session)
```

**Key Learnings from Production**:
1. **User message NOT in run_async() result** - You must add it manually
2. **Agent events NOT auto-added to session** - You must extend session.events
3. **Save once at end** - Batch all updates, don't save multiple times
4. **Set author field** - Use `author="user"` or `author=""`, NOT `None` (Pydantic validation error)
5. **Event wrapping** - ADK may require user Content wrapped in Event with `branch` attribute
6. **Session reload creates NEW object** - Any uncommitted state is lost on reload (see State Management below)

### Extracting Messages from Events

To display chat history from persisted events:

```python
def extract_messages(events: list) -> list[dict]:
    """Extract user and assistant messages from ADK events."""
    messages = []

    for event in events:
        # Events have content.role (nested), not top-level role
        if not hasattr(event, 'content'):
            continue

        role = event.content.role  # "user" or "model"

        # Extract text from parts
        content = ""
        if hasattr(event.content, 'parts'):
            for part in event.content.parts:
                if hasattr(part, 'text') and part.text:
                    content += part.text

        # Only include messages with actual text content
        if content:
            messages.append({
                "role": "user" if role == "user" else "assistant",
                "content": content,
                "timestamp": getattr(event, 'create_time', None)
            })

    return messages
```

### Performance Considerations

**Anti-Pattern** ❌: Multiple saves per request
```python
# WRONG: 3 GCS uploads = 150-600ms latency
session.state["subject"] = subject
await session_service._save_session(session)  # Save #1

session.state["last_activity"] = timestamp
await session_service._save_session(session)  # Save #2

session.events.extend(new_events)
await session_service._save_session(session)  # Save #3
```

**Correct Pattern** ✅: Batch updates, save once
```python
# CORRECT: 1 GCS upload = 50-200ms latency
session.state["subject"] = subject
session.state["last_activity"] = timestamp
session.events.extend(new_events)

# Single save with all changes
await session_service._save_session(session)
```

### State Management Across Session Reloads

**CRITICAL GOTCHA**: When you reload a session from storage, you get a NEW Session object. Any uncommitted state changes are LOST.

**The Problem**:
```python
# Set metadata in session
session.state["subject"] = "My subject"
session.state["last_activity"] = "2025-12-03T10:00:00"

# Run agent (may internally reload session from storage)
result = await runner.run_async(...)

# BUG: session.state["subject"] and "last_activity" are GONE!
# The reload created a new Session object from GCS, losing uncommitted changes
```

**Why This Happens**:
1. You set `session.state["subject"]` in memory
2. ADK's `run_async()` or `get_session()` reloads from storage
3. Reload creates NEW Session object from persisted state (which doesn't have your changes yet)
4. Your in-memory changes are discarded

**Correct Pattern** ✅:
```python
# Use a separate dict to track changes
metadata_updates = {}

# Set metadata in local dict
metadata_updates["subject"] = "My subject"
metadata_updates["last_activity"] = "2025-12-03T10:00:00"

# Run agent (reload may happen)
result = await runner.run_async(...)

# IMPORTANT: Restore metadata after reload
for key, value in metadata_updates.items():
    session.state[key] = value

# Now save (metadata is preserved)
await session_service._save_session(session)
```

**Real-World Example** (Subject Field Bug):
```python
# Bug: Subject lost on reload
session_state = {}  # Local tracking dict
session_state["subject"] = message[:100]
runner_session.state["subject"] = message[:100]

result = await runner.run_async(...)  # Reloads session internally
# runner_session.state["subject"] is NOW GONE!

await session_service._save_session(runner_session)  # Saves without subject!

# Fix: Restore after reload
if session_state.get("subject"):
    runner_session.state["subject"] = session_state["subject"]  # Restore from local dict

await session_service._save_session(runner_session)  # Now subject is saved!
```

**Key Principles**:
1. **Track changes separately** - Use a local dict for uncommitted state
2. **Assume reload happens** - Treat session objects as ephemeral
3. **Restore before save** - Re-apply uncommitted changes after any operation that might reload
4. **Save atomically** - Batch all changes, save once at the end

**State Machine Testing**:
To catch these reload-related bugs, always test across state boundaries:
```python
# Test: Set metadata → Run agent → Verify metadata still present
session.state["subject"] = "Test"
await runner.run_async(...)  # May reload
assert session.state.get("subject") == "Test"  # Will FAIL if reload loses state
```

### Key Takeaways

1. **Always use `model_dump(mode='json')`** when serializing ADK events to JSON
2. **Pydantic handles bytes ↔ base64** automatically (don't write custom encoding!)
3. **User messages are NOT in agent response events** - add them manually
4. **Batch state changes** - save once per request, not per field update
5. **Event structure**: `event.content.role`, not `event.role` (nested)
6. **Session reloads lose uncommitted state** - track changes separately and restore after reload

---

## Advanced Model Configuration

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

- **gemini-2.0-flash**: Fastest, best for most use cases (RECOMMENDED)
- **gemini-2.5-flash**: Experimental, newer version
- **gemini-pro**: More capable, higher cost
- **gemini-3-pro-preview**: Latest preview model

---

## Best Practices

### 1. Always Use Type Hints

```python
# ✅ Good
def process_order(order_id: int, items: list[str], priority: bool = False) -> dict:
    """Process a customer order."""
    return {"order_id": order_id, "status": "processing"}

# ❌ Bad - no type hints
def process_order(order_id, items, priority=False):
    return {"order_id": order_id, "status": "processing"}
```

### 2. Write Clear Docstrings

```python
# ✅ Good
def analyze_sentiment(text: str) -> dict:
    """Analyze the sentiment of given text.

    Args:
        text: The text to analyze for sentiment.

    Returns:
        Dictionary with sentiment (positive/negative/neutral) and confidence score.
    """
    pass

# ❌ Bad - missing docstring
def analyze_sentiment(text: str) -> dict:
    pass
```

### 3. Clear Agent Instructions

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

### 4. Minimal Tools Per Agent

```python
# ✅ Good - focused set of related tools
agent = LlmAgent(
    name="weather_agent",
    model="gemini-2.0-flash",
    tools=[get_current_weather, get_forecast, get_air_quality],
)

# ❌ Bad - too many unrelated tools
agent = LlmAgent(
    name="assistant",
    model="gemini-2.0-flash",
    tools=[tool1, tool2, tool3, ... tool25],  # Confuses agent
)
```

### 5. Error Handling

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

### 6. Use run_debug() for Development

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

### Issue: Agent not calling tools

**Problem**: Missing type hints or unclear docstrings

**Solution**: Ensure all tools have:
- Type hints on all parameters
- Clear docstrings with Args and Returns sections
- Specific return types

### Issue: Multi-agent delegation not working

**Problem**: Agent descriptions too similar or vague

**Solution**: Write distinct, specific descriptions for each sub-agent

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

## Resources

- **Official Documentation**: https://google.github.io/adk-docs/
- **GitHub Repository**: https://github.com/google/adk-python
- **PyPI Package**: https://pypi.org/project/google-adk/
- **API Reference**: https://google.github.io/adk-docs/api-reference/python/
- **Examples**: https://github.com/google/adk-python/tree/main/examples

---

## Quick Reference Card

```python
# Install
pip install google-adk  # Python 3.10+ required

# Imports
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.runners import InMemoryRunner
from google.genai import types

# Auth (Vertex AI)
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "TRUE"
os.environ["GOOGLE_CLOUD_PROJECT"] = "project-id"
os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"

# Create Agent
agent = LlmAgent(
    model="gemini-2.0-flash",  # Required
    name="agent_name",         # Required
    instruction="...",         # Optional
    tools=[func1, func2],      # Optional
    sub_agents=[...],          # Optional
)

# Run Agent (Development)
runner = InMemoryRunner(agent=agent, app_name="app")
response = await runner.run_debug("Query")

# Run Agent (Production)
async for event in runner.run_async(
    user_id="user",
    session_id="session",
    new_message=types.Content(role="user", parts=[types.Part(text="Query")]),
):
    if event.is_final_response():
        print(event.content.parts[0].text)

# Define Tool
def my_tool(param: str) -> dict:
    """Tool description.

    Args:
        param: Parameter description.

    Returns:
        Return value description.
    """
    return {"result": param}

# Multi-Agent
coordinator = LlmAgent(
    name="coordinator",
    model="gemini-2.0-flash",
    sub_agents=[agent1, agent2],  # Hierarchical
)

# Deploy to Agent Engine
from vertexai.agent_engines import AdkApp
app = AdkApp(agent=agent)
remote_agent = client.agent_engines.create(agent=app, config={...})
```

---

## Remember

✅ **DO:**
- Use `google-adk` package (not `google-genai`)
- Include `name` parameter on all agents
- Use `InMemoryRunner` or `Runner` to execute agents
- Provide type hints on all tool functions
- Write clear docstrings for tools
- Set environment variables for Vertex AI authentication
- Use `gemini-2.0-flash` as default model

❌ **DON'T:**
- Use `genai.Client()` pattern (that's for GenAI SDK, not ADK)
- Call `agent.generate_content()` directly without a runner
- Omit type hints or docstrings on tools
- Use Python < 3.10
- Mix up Google ADK with Google GenAI SDK

---

**This skill is based on official Google ADK documentation (January 2025)**
