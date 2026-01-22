# Langfuse Setup & Configuration

## Installation

```bash
pip install langfuse
```

**With integrations:**
```bash
# OpenAI auto-instrumentation
pip install langfuse openai

# LangChain callback
pip install langfuse langchain
```

---

## Environment Configuration

### Required Variables
```bash
# Langfuse Cloud (recommended)
LANGFUSE_PUBLIC_KEY="pk-lf-..."
LANGFUSE_SECRET_KEY="sk-lf-..."
LANGFUSE_HOST="https://cloud.langfuse.com"  # EU region (default)
# LANGFUSE_HOST="https://us.cloud.langfuse.com"  # US region
```

### Optional Variables
```bash
# Enable debug logging
LANGFUSE_DEBUG="true"

# Flush interval (seconds)
LANGFUSE_FLUSH_INTERVAL="5"

# Enable/disable SDK
LANGFUSE_ENABLED="true"
```

---

## Client Initialization

### Automatic (Recommended)
```python
# SDK auto-initializes from environment variables
from langfuse import observe, get_client

@observe()
def my_function():
    pass

# Access singleton client if needed
langfuse = get_client()
```

### Manual Initialization
```python
from langfuse import Langfuse

langfuse = Langfuse(
    public_key="pk-lf-...",
    secret_key="sk-lf-...",
    host="https://cloud.langfuse.com"
)

# Verify connection (dev only - adds latency)
langfuse.auth_check()
```

---

## Deployment Options

### Option 1: Langfuse Cloud (Recommended)

**Pros:** Instant setup, managed infrastructure, free tier
**Cons:** Data on Langfuse servers

1. Sign up at [cloud.langfuse.com](https://cloud.langfuse.com)
2. Create project
3. Copy API keys to environment

### Option 2: Self-Hosted (Docker Compose)

**Pros:** Full data control
**Cons:** Not production-ready (no HA, no backups)

```bash
# Quick local testing only
git clone https://github.com/langfuse/langfuse.git
cd langfuse
docker-compose up -d
```

Access at: `http://localhost:3000`

### Option 3: Self-Hosted (Production)

For production self-hosting, use Kubernetes with Helm:
- [Kubernetes deployment guide](https://langfuse.com/self-hosting/deployment/kubernetes-helm)
- Requires PostgreSQL and ClickHouse databases
- Consider AWS ECS, GCP Cloud Run, or Azure Container Instances

**Context7 for current deployment docs:**
```
get-library-docs: /langfuse/langfuse-docs (topic: "self-hosting kubernetes")
```

---

## FastAPI Integration

### Basic Setup
```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from langfuse import get_client

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown - flush pending events
    get_client().flush()

app = FastAPI(lifespan=lifespan)
```

### With Middleware (Optional)
```python
from langfuse import observe

@app.post("/chat")
@observe()  # Traces entire request
async def chat(request: ChatRequest):
    response = await process_chat(request.message)
    return {"response": response}
```

---

## GCP Deployment Notes

### Cloud Run
- Set env vars in Cloud Run service configuration
- Use Secret Manager for API keys
- Ensure flush on shutdown (SIGTERM handling)

```yaml
# cloudbuild.yaml example
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/my-service', '.']

env:
  - 'LANGFUSE_HOST=https://cloud.langfuse.com'
  # Keys from Secret Manager
```

### Secret Manager Integration
```python
from google.cloud import secretmanager

def get_langfuse_keys():
    client = secretmanager.SecretManagerServiceClient()
    project_id = "your-project"

    public_key = client.access_secret_version(
        name=f"projects/{project_id}/secrets/langfuse-public-key/versions/latest"
    ).payload.data.decode()

    secret_key = client.access_secret_version(
        name=f"projects/{project_id}/secrets/langfuse-secret-key/versions/latest"
    ).payload.data.decode()

    return public_key, secret_key
```

---

## Verification

### Test Connection
```python
from langfuse import get_client

langfuse = get_client()

# Simple trace test
with langfuse.start_as_current_span(name="test-trace") as span:
    span.update(output="Connection test successful")

langfuse.flush()
print("Check Langfuse UI for 'test-trace'")
```

### Troubleshooting

| Issue | Solution |
|-------|----------|
| No traces appearing | Check `LANGFUSE_HOST`, call `flush()` |
| Auth errors | Verify API keys match project |
| Missing env vars | Ensure loaded before import |
| Delayed traces | Normal - batching up to 5s |

---

## Project Conventions

### Environment-Based Configuration
```python
import os

LANGFUSE_CONFIG = {
    "development": {
        "host": "https://cloud.langfuse.com",
        "debug": True,
    },
    "production": {
        "host": "https://cloud.langfuse.com",
        "debug": False,
    }
}

env = os.getenv("ENVIRONMENT", "development")
config = LANGFUSE_CONFIG[env]
```

### Naming Conventions
- **Project names**: `{service}-{environment}` (e.g., `chat-api-prod`)
- **Trace names**: `{feature}-{operation}` (e.g., `rag-query`)

---

**Next**: [02-tracing-patterns.md](02-tracing-patterns.md) - Learn tracing patterns
