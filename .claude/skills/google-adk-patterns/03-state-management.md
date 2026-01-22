# Module 03: State Management & Session Reloads

**CRITICAL MODULE**: Session reload gotchas that cause state loss.

> **For current session API, use Context7:**
> ```
> get-library-docs: /google/adk-docs (topic: "session state management")
> ```

---

## The Session Reload Gotcha

### CRITICAL: Session Reload Creates NEW Object

When you reload a session from storage, you get a **NEW Session object**. Any uncommitted state changes are **LOST**.

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

---

## Correct Pattern: Separate Tracking

### Anti-Pattern ❌

```python
# WRONG: Assume state persists across reload
runner_session.state["subject"] = "My subject"
runner_session.state["last_activity"] = datetime.now().isoformat()

# Run agent (reload happens internally)
result = await runner.run_async(...)

# BUG: State is lost!
await session_service._save_session(runner_session)  # Saves without subject!
```

### Correct Pattern ✅

```python
# CORRECT: Track changes separately, restore after reload
metadata_updates = {}

# Set metadata in local dict
metadata_updates["subject"] = "My subject"
metadata_updates["last_activity"] = datetime.now().isoformat()

# Run agent (reload may happen)
result = await runner.run_async(...)

# IMPORTANT: Restore metadata after reload
for key, value in metadata_updates.items():
    runner_session.state[key] = value

# Now save (metadata is preserved)
await session_service._save_session(runner_session)
```

---

## Real-World Example: Subject Field Bug

This bug occurred in production (Phase 2A):

### The Bug

```python
# Bug: Subject lost on reload
session_state = {}  # Local tracking dict
session_state["subject"] = message[:100]
runner_session.state["subject"] = message[:100]

result = await runner.run_async(...)  # Reloads session internally
# runner_session.state["subject"] is NOW GONE!

await session_service._save_session(runner_session)  # Saves without subject!
```

### The Fix

```python
# Fix: Restore after reload
if session_state.get("subject"):
    runner_session.state["subject"] = session_state["subject"]  # Restore from local dict

await session_service._save_session(runner_session)  # Now subject is saved!
```

**Lesson**: Always track uncommitted state separately and restore before saving.

---

## Session Management Patterns

### Multi-Turn Conversation

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

---

## GCS-Backed Session Storage

### Custom GCS Session Service

**IMPORTANT**: Google ADK does NOT have a built-in `CloudStorageMemory` class. For persistent session storage, implement a custom session service using `BaseSessionService`.

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
```

### Usage: FastAPI with GCS Sessions

```python
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

1. **BaseSessionService Methods** (only 4 required):
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

---

## State Machine Testing

To catch reload-related bugs, always test across state boundaries:

```python
@pytest.mark.asyncio
async def test_metadata_survives_reload():
    """Verify metadata persists across session reload."""
    agent = LlmAgent(model="gemini-2.0-flash", name="test_agent")
    runner = InMemoryRunner(agent=agent, app_name="test")
    session_service = runner.session_service

    # Create session with metadata
    await session_service.create_session(
        app_name="test",
        user_id="user1",
        session_id="session1",
        state={"subject": "Test Subject"}
    )

    # Run agent (may reload)
    metadata_updates = {"subject": "Test Subject"}
    user_msg = types.Content(role="user", parts=[types.Part(text="Hello")])
    
    agent_events = []
    async for event in runner.run_async(
        user_id="user1",
        session_id="session1",
        new_message=user_msg
    ):
        agent_events.append(event)

    # Restore metadata after reload
    session = await session_service.get_session("test", "user1", "session1")
    for key, value in metadata_updates.items():
        session.state[key] = value

    await session_service._save_session(session)

    # Reload and verify metadata persisted
    reloaded = await session_service.get_session("test", "user1", "session1")
    assert reloaded.state.get("subject") == "Test Subject"  # Will FAIL if reload loses state
```

---

## Session Best Practices

1. **Unique Session IDs**: Use UUIDs or user-specific identifiers
2. **Session Cleanup**: Delete old sessions periodically to manage memory
3. **User Isolation**: Different users should have different sessions
4. **Context Window**: ADK manages context automatically, but be aware of token limits
5. **Production Storage**: Use GCS-backed sessions for production (sessions persist across restarts)
6. **Development Storage**: Use `InMemorySessionService` for local development
7. **Lifecycle Policies**: Configure GCS bucket with 30-day lifecycle to auto-delete old sessions

---

## Key Principles

1. **Track changes separately** - Use a local dict for uncommitted state
2. **Assume reload happens** - Treat session objects as ephemeral
3. **Restore before save** - Re-apply uncommitted changes after any operation that might reload
4. **Save atomically** - Batch all changes, save once at the end
5. **Test state transitions** - Verify state survives reload in tests

---

## Summary

**Key Takeaways**:
1. **Session reload creates NEW object** - Uncommitted state is lost
2. **Track metadata separately** - Use local dict, restore after reload
3. **Restore before save** - Re-apply changes after `run_async()` or `get_session()`
4. **Batch updates** - Set all state fields, save once
5. **Test state transitions** - Verify metadata survives reload

**Common Errors**:
- ❌ `session.state["key"] = value` → `run_async()` → state lost
- ❌ Forgetting to restore after reload
- ❌ Multiple saves per request

**Correct Workflow**:
1. Create local `metadata_updates = {}`
2. Set metadata in local dict
3. Run agent (reload may happen)
4. Restore metadata: `session.state.update(metadata_updates)`
5. Save session ONCE at end

---

**Next Module**: [04-tool-integration.md](04-tool-integration.md) - Function calling patterns

**See Also**:
- [02-event-persistence.md](02-event-persistence.md) - Event handling
- [05-fastapi-integration.md](05-fastapi-integration.md) - Production FastAPI integration
- [06-multi-agent-deployment.md](06-multi-agent-deployment.md) - Deployment patterns
