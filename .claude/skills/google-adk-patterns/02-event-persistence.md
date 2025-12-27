# Module 02: Event Persistence & Handling

**CRITICAL MODULE**: Contains the most common gotchas in Google ADK. Read this carefully!

> **For current event API, use Context7:**
> ```
> get-library-docs: /google/adk-docs (topic: "events session persistence")
> ```

---

## Understanding ADK Events

When you run an agent, the runner returns Event objects representing the conversation turn:

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

---

## Serializing Events to JSON

### The Bytes Problem

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

### Example: Saving Events to GCS

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

Pydantic automatically converts base64 strings back to bytes:

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

---

## The Manual Persistence Gotcha

### CRITICAL: ADK Does NOT Auto-Persist Events

**The Problem**:
1. `run_async()` returns agent response events
2. These events are NOT automatically added to `session.events`
3. User message is NOT in the returned events
4. Result: If you don't manually manage events, nothing persists!

### Anti-Pattern ❌

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

### Correct Pattern ✅

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
    author="",  # IMPORTANT: Set author (not None to avoid Pydantic errors)
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

### Key Learnings from Production

1. **User message NOT in run_async() result** - You must add it manually
2. **Agent events NOT auto-added to session** - You must extend session.events
3. **Save once at end** - Batch all updates, don't save multiple times
4. **Set author field** - Use `author=""` or `author="user"`, NOT `None` (Pydantic validation error)
5. **Event wrapping** - ADK may require user Content wrapped in Event with `branch` attribute
6. **Session reload creates NEW object** - Any uncommitted state is lost on reload (see Module 03)

---

## Extracting Messages from Events

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

---

## Performance: Batch Saves

### Anti-Pattern ❌: Multiple Saves Per Request

```python
# WRONG: 3 GCS uploads = 150-600ms latency
session.state["subject"] = subject
await session_service._save_session(session)  # Save #1

session.state["last_activity"] = timestamp
await session_service._save_session(session)  # Save #2

session.events.extend(new_events)
await session_service._save_session(session)  # Save #3
```

### Correct Pattern ✅: Batch Updates, Save Once

```python
# CORRECT: 1 GCS upload = 50-200ms latency
session.state["subject"] = subject
session.state["last_activity"] = timestamp
session.events.extend(new_events)

# Single save with all changes
await session_service._save_session(session)
```

**Impact**: Reducing 3 saves to 1 save = 66% reduction in storage latency.

---

## Common Pitfalls

### 1. Forgetting to Append User Message

```python
# ❌ WRONG: User message lost
agent_events = await runner.run_async(user_id, session_id, user_msg)
session.events.extend(agent_events)  # Only agent response saved!

# ✅ CORRECT: Save both
user_event = Event(content=user_msg, author="", branch=None)
session.events.append(user_event)
session.events.extend(agent_events)
```

### 2. Using author=None

```python
# ❌ WRONG: Pydantic validation error
event = Event(content=..., author=None, branch=None)

# ✅ CORRECT: Use empty string
event = Event(content=..., author="", branch=None)
```

### 3. Missing Branch Attribute

**Context**: In some ADK versions, events loaded from storage need a `branch` attribute for the runner to process them.

```python
# ❌ WRONG: Plain Content object may cause AttributeError
session.events.append(types.Content(role="user", parts=[...]))

# ✅ CORRECT: Wrap in Event with branch
session.events.append(Event(
    content=types.Content(role="user", parts=[...]),
    author="",
    branch=None  # or "main"
))
```

**Gotcha**: If you're deserializing events from GCS and they're plain `Content` objects, wrap them:

```python
def _deserialize_event(event_data: dict):
    """Wrap Content in Event to add branch attribute."""
    content = types.Content.model_validate(event_data)
    return Event(content=content, author="", branch=None)
```

### 4. Not Handling Event Structure

```python
# ❌ WRONG: Assumes top-level role
role = event.role

# ✅ CORRECT: Role is nested in content
role = event.content.role if hasattr(event, 'content') else event.role
```

---

## Testing Event Persistence

### Unit Test Example

```python
import pytest
from google.adk.runners import InMemoryRunner
from google.genai import types

@pytest.mark.asyncio
async def test_event_persistence():
    """Verify events persist correctly."""
    agent = LlmAgent(model="gemini-2.0-flash", name="test_agent")
    runner = InMemoryRunner(agent=agent, app_name="test")
    session_service = runner.session_service

    # Create session
    await session_service.create_session(
        app_name="test",
        user_id="user1",
        session_id="session1"
    )

    # Send message
    user_msg = types.Content(role="user", parts=[types.Part(text="Hello")])
    agent_events = []
    async for event in runner.run_async(
        user_id="user1",
        session_id="session1",
        new_message=user_msg
    ):
        agent_events.append(event)

    # Manually persist (as required)
    session = await session_service.get_session("test", "user1", "session1")
    user_event = Event(content=user_msg, author="", branch=None)
    session.events.append(user_event)
    session.events.extend(agent_events)
    await session_service._save_session(session)

    # Reload and verify
    reloaded = await session_service.get_session("test", "user1", "session1")
    assert len(reloaded.events) > 0
    assert reloaded.events[0].content.role == "user"
```

---

## Summary

**Key Takeaways**:
1. **Always use `model_dump(mode='json')`** when serializing events to JSON
2. **Pydantic handles bytes ↔ base64** automatically (don't write custom encoding!)
3. **User messages are NOT in agent response events** - add them manually
4. **Batch state changes** - save once per request, not per field update
5. **Event structure**: `event.content.role`, not `event.role` (nested)
6. **Set author=""** not `author=None` (Pydantic validation)
7. **Wrap Content in Event** if runner requires `branch` attribute

**Common Errors**:
- ❌ `json.dumps(event.model_dump())` → bytes serialization fails
- ❌ `run_async()` auto-persists → events lost
- ❌ `author=None` → Pydantic validation error
- ❌ Missing user message → incomplete history
- ❌ Showing empty user events as "[Empty message]" → should skip them entirely

**Correct Workflow**:
1. Create user Event
2. Run agent → collect agent events
3. Append user event to session.events
4. Extend agent events to session.events
5. Save session ONCE at end

---

## Message Extraction from Events

### Pattern: Extracting Chat Messages for UI Display

When displaying chat history in a UI, you need to extract text content from persisted events.

**Key Gotcha**: ADK may create **intermediate events** with `role="user"` that have empty content. These are processing artifacts, not actual user messages.

```python
def get_session_messages(session) -> list[dict]:
    """Extract displayable messages from session events."""
    messages = []

    for i, event_data in enumerate(session.events):
        event_type = event_data.get('type', 'unknown')
        role = None
        content_text = ""

        # Extract role and text based on event type
        if event_type == 'Content':
            # User message: role at top level
            role = event_data.get('role')
            parts = event_data.get('parts', [])
        elif event_type == 'Event':
            # Agent message: role nested in content
            content = event_data.get('content', {})
            role = content.get('role')
            parts = content.get('parts', [])

        # Extract text from parts
        text_parts = [part.get('text', '') for part in parts if part.get('text')]
        content_text = " ".join(text_parts).strip()  # ← IMPORTANT: Use .strip()

        # ✅ CORRECT: Skip empty user messages (ADK intermediate events)
        if role == "user":
            if content_text:
                messages.append({
                    "role": "user",
                    "content": content_text,
                    "timestamp": event_data.get('create_time') or event_data.get('timestamp')
                })
            else:
                # Skip empty user events (likely ADK processing artifacts)
                logger.debug(f"Skipping empty user event {i}")

        # ✅ CORRECT: Show assistant messages only if they have text
        elif role == "model" or role == "assistant":
            if content_text:
                messages.append({
                    "role": "assistant",
                    "content": content_text,
                    "timestamp": event_data.get('timestamp')
                })

    return messages
```

**Why This Matters**:
- ❌ **Wrong**: Showing `"[Empty message]"` for empty user events → confusing UI bubbles
- ✅ **Correct**: Skip empty user events entirely → clean chat history

**Common Causes of Empty User Events**:
1. Session reload may create intermediate events during state restoration
2. Tool execution context may generate placeholder user events
3. Event replay during error recovery may duplicate events without content

**Pattern Verified**: 2025-12-07 (Phase 2B bug fix)

---

**Next Module**: [03-state-management.md](03-state-management.md) - Session reload gotchas

**See Also**:
- [01-agent-setup.md](01-agent-setup.md) - Agent creation
- [03-state-management.md](03-state-management.md) - State loss on reload
- [05-fastapi-integration.md](05-fastapi-integration.md) - Production patterns
