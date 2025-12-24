# Module 05: FastAPI Integration Patterns

Production-ready patterns for integrating Google ADK agents with FastAPI.

---

## Basic FastAPI Integration

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

## Production Pattern: GCS Session Storage

```python
from fastapi import FastAPI
from contextlib import asynccontextmanager
from google.adk.agents import LlmAgent
from google.adk.runners import InMemoryRunner

# Import custom GCS session service (see Module 03)
from services.gcs_session_service import GcsSessionService

runner = None

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

---

## Complete Production Example

```python
"""
Production-ready FastAPI + Google ADK integration.
Includes: GCS sessions, error handling, logging, metrics.
"""
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google.adk.agents import LlmAgent
from google.adk.runners import InMemoryRunner
from google.genai import types
from contextlib import asynccontextmanager
import logging
import uuid
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global runner
runner = None

# Models
class ChatRequest(BaseModel):
    message: str
    user_id: str
    session_id: str | None = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    timestamp: str

class SessionListResponse(BaseModel):
    sessions: list[dict]

# Lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize agent and runner."""
    global runner
    
    logger.info("Initializing ADK agent...")
    
    # Create agent with tools
    agent = LlmAgent(
        model="gemini-2.0-flash",
        name="production_assistant",
        instruction="You are a production assistant. Be helpful and concise.",
        tools=[],  # Add production tools
    )
    
    # Create runner
    runner = InMemoryRunner(agent=agent, app_name="prod_app")
    
    # TODO: Replace with GCS session service for production
    # from services.gcs_session_service import GcsSessionService
    # gcs_service = GcsSessionService(bucket_name="sessions", project="project-id")
    # runner.session_service = gcs_service
    
    logger.info("ADK agent initialized successfully")
    
    yield
    
    logger.info("Shutting down ADK agent...")
    runner = None

# FastAPI app
app = FastAPI(
    title="ADK Agent API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoints

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send message to agent and get response."""
    start_time = datetime.now()
    
    try:
        # Validate
        if not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Generate session ID
        session_id = request.session_id or str(uuid.uuid4())
        
        logger.info(f"Chat request - user: {request.user_id}, session: {session_id}")
        
        # Create or get session
        session_service = runner.session_service
        try:
            await session_service.create_session(
                app_name="prod_app",
                user_id=request.user_id,
                session_id=session_id,
            )
        except:
            # Session already exists
            pass
        
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
        
        # Log metrics
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"Chat completed in {duration:.2f}s")
        
        return ChatResponse(
            response=response_text,
            session_id=session_id,
            timestamp=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/sessions/{user_id}", response_model=SessionListResponse)
async def list_sessions(user_id: str):
    """List all sessions for a user."""
    try:
        session_service = runner.session_service
        result = await session_service.list_sessions(
            app_name="prod_app",
            user_id=user_id
        )
        
        sessions = [
            {
                "session_id": session.id,
                "user_id": session.user_id,
                "state": session.state
            }
            for session in result.sessions
        ]
        
        return SessionListResponse(sessions=sessions)
        
    except Exception as e:
        logger.error(f"List sessions error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to list sessions")

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str, user_id: str):
    """Delete a session."""
    try:
        session_service = runner.session_service
        await session_service.delete_session(
            app_name="prod_app",
            user_id=user_id,
            session_id=session_id
        )
        
        return {"status": "deleted", "session_id": session_id}
        
    except Exception as e:
        logger.error(f"Delete session error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to delete session")

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "runner_initialized": runner is not None,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "ADK Agent API",
        "version": "1.0.0",
        "status": "running"
    }

# Run with: uvicorn main:app --reload
```

---

## Error Handling Patterns

### Input Validation

```python
@app.post("/api/chat")
async def chat(request: ChatRequest):
    # Validate message
    if not request.message.strip():
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty"
        )
    
    # Validate message length
    if len(request.message) > 10000:
        raise HTTPException(
            status_code=400,
            detail="Message too long (max 10000 characters)"
        )
    
    # Validate user_id format
    if not request.user_id or not request.user_id.isalnum():
        raise HTTPException(
            status_code=400,
            detail="Invalid user_id format"
        )
    
    # Process request...
```

### Timeout Protection

```python
import asyncio

@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        # Set 30-second timeout
        response_text = await asyncio.wait_for(
            run_agent_async(request),
            timeout=30.0
        )
        
        return ChatResponse(response=response_text, ...)
        
    except asyncio.TimeoutError:
        logger.error("Agent request timed out")
        raise HTTPException(
            status_code=504,
            detail="Agent request timed out"
        )

async def run_agent_async(request: ChatRequest) -> str:
    """Helper to run agent with timeout."""
    response_text = ""
    async for event in runner.run_async(...):
        if event.is_final_response() and event.content:
            response_text = event.content.parts[0].text.strip()
    return response_text
```

### Rate Limiting

```python
from fastapi import Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/chat")
@limiter.limit("10/minute")  # 10 requests per minute per IP
async def chat(request: Request, chat_request: ChatRequest):
    # Process chat request...
    pass
```

---

## Authentication & Authorization

### Bearer Token Auth

```python
from fastapi import Header, HTTPException

async def verify_token(authorization: str = Header(None)):
    """Verify bearer token."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    
    token = authorization[7:]  # Remove "Bearer " prefix
    
    # Verify token (implement your auth logic)
    if not is_valid_token(token):
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return token

@app.post("/api/chat")
async def chat(
    request: ChatRequest,
    token: str = Depends(verify_token)
):
    # Token is verified, process request
    pass
```

### User Context from Token

```python
async def get_current_user(token: str = Depends(verify_token)) -> dict:
    """Extract user context from token."""
    user = decode_token(token)  # Your JWT decode logic
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user")
    return user

@app.post("/api/chat")
async def chat(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user)
):
    # Use current_user["user_id"] instead of request.user_id
    user_id = current_user["user_id"]
    
    # Process with authenticated user_id...
```

---

## Testing

### Unit Test

```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_endpoint():
    """Test health check."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_chat_endpoint():
    """Test chat endpoint."""
    response = client.post(
        "/api/chat",
        json={
            "message": "Hello!",
            "user_id": "test_user"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "session_id" in data

def test_chat_empty_message():
    """Test chat with empty message."""
    response = client.post(
        "/api/chat",
        json={
            "message": "",
            "user_id": "test_user"
        }
    )
    assert response.status_code == 400
```

---

## Deployment

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8080

# Run with production settings
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### Cloud Run

```yaml
# cloud-run.yaml
service: adk-agent-api
runtime: python311
entrypoint: uvicorn main:app --host 0.0.0.0 --port $PORT

env_variables:
  GOOGLE_GENAI_USE_VERTEXAI: "TRUE"
  GOOGLE_CLOUD_PROJECT: "your-project-id"
  GOOGLE_CLOUD_LOCATION: "us-central1"

resources:
  cpu: 2
  memory: 4Gi
  
automatic_scaling:
  min_instances: 1
  max_instances: 10
```

---

## Summary

**Key Patterns**:
1. **Lifespan context manager** for agent initialization
2. **Global runner** shared across requests
3. **GCS session service** for production persistence
4. **Error handling** at API layer (HTTPException)
5. **Logging** for debugging and metrics
6. **Validation** on all inputs
7. **Timeout protection** for long-running agents
8. **Authentication** via tokens/headers

**Common Errors**:
- ❌ Creating new agent per request (slow)
- ❌ No timeout on agent calls (hangs)
- ❌ Missing error handling (500 errors)
- ❌ No input validation (security risk)

**Production Checklist**:
- ✅ Use lifespan for initialization
- ✅ Replace InMemorySessionService with GCS
- ✅ Add timeout to agent calls
- ✅ Validate all inputs
- ✅ Add authentication
- ✅ Configure CORS properly
- ✅ Add rate limiting
- ✅ Log metrics (latency, errors)
- ✅ Health check endpoint
- ✅ Graceful error handling

---

**Next Module**: [06-multi-agent-deployment.md](06-multi-agent-deployment.md) - Multi-agent systems

**See Also**:
- [03-state-management.md](03-state-management.md) - GCS session service
- [04-tool-integration.md](04-tool-integration.md) - Adding tools to agents
