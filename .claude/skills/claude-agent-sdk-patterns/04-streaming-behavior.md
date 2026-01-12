# Claude Agent SDK Streaming Behavior

Detailed streaming patterns validated via spike testing (2026-01-01).

> **Source**: SDK validation spike in `prototype/sdk_spike.py`

**For current syntax**: `get-library-docs: /anthropics/claude-agent-sdk-python (topic: "streaming include_partial_messages")`

---

## Critical Questions Answered

| Question | Answer | Evidence |
|----------|--------|----------|
| How often does `receive_response()` yield? | Per-delta (many StreamEvents) + final AssistantMessage | ~120 StreamEvents for 1600-char response |
| Are long responses streamed incrementally? | YES, via `content_block_delta` events | 5-30 chars per delta |
| When does ToolResultBlock appear? | In SEPARATE UserMessage after ToolUseBlock | Distinct messages, ~1s apart |
| What happens on interrupt()? | Clean exit, no exception, client reusable | Returns immediately, ResultMessage still yielded |
| How to persist/resume sessions? | `ResultMessage.session_id` + `resume=` option | Same session ID preserved |
| Can we query() while iterating? | Technically yes, but queued | Wait for response completion |

---

## Streaming Architecture

### Event Sequence (with `include_partial_messages=True`)

```
SystemMessage (subtype='init')
    │
    ▼
StreamEvent (type='message_start')
StreamEvent (type='content_block_start')
StreamEvent (type='content_block_delta')  ← Many of these
StreamEvent (type='content_block_delta')
    ... (5-30 chars each)
StreamEvent (type='content_block_stop')
    │
    ▼
AssistantMessage  ← Contains COMPLETE TextBlock
    │
    ▼
StreamEvent (type='message_delta')
StreamEvent (type='message_stop')
    │
    ▼
ResultMessage (session_id, cost, usage)
```

### Tool Use Sequence

```
AssistantMessage
  └── ToolUseBlock (name, id, input)
        │
        ▼ [Tool executes]
        │
UserMessage
  └── ToolResultBlock (tool_use_id, content, is_error)
        │
        ▼
AssistantMessage
  └── TextBlock (response after tool)
```

---

## StreamEvent Import

```python
# StreamEvent is exported from main module
from claude_agent_sdk import StreamEvent

# Type check
if isinstance(message, StreamEvent):
    event = message.event  # dict with 'type' key
```

### Event Types

| Type | Description |
|------|-------------|
| `message_start` | Response beginning, contains model info |
| `content_block_start` | New block starting (text, tool_use, etc.) |
| `content_block_delta` | Incremental content chunk |
| `content_block_stop` | Block complete |
| `message_delta` | Message metadata (stop_reason) |
| `message_stop` | Response complete |

---

## Streaming Patterns

### Pattern 1: Real-Time UI Updates

For WebSocket streaming to frontend:

```python
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions
from claude_agent_sdk import AssistantMessage, TextBlock, ToolUseBlock, StreamEvent

async def stream_to_websocket(websocket, query: str):
    options = ClaudeAgentOptions(
        include_partial_messages=True,
        allowed_tools=["Read", "Bash"],
        permission_mode="acceptEdits",
    )

    async with ClaudeSDKClient(options=options) as client:
        await client.query(query)

        full_text = ""

        async for msg in client.receive_response():
            if isinstance(msg, StreamEvent):
                event = msg.event
                event_type = event.get('type')

                if event_type == 'content_block_delta':
                    delta = event.get('delta', {})
                    delta_type = delta.get('type')

                    if delta_type == 'text_delta':
                        text_chunk = delta.get('text', '')
                        full_text += text_chunk
                        # Send delta to UI for typing effect
                        await websocket.send_json({
                            "type": "text_delta",
                            "content": text_chunk
                        })

            elif isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, ToolUseBlock):
                        await websocket.send_json({
                            "type": "tool_use",
                            "id": block.id,
                            "name": block.name,
                            "input": block.input,
                            "status": "started"
                        })
```

### Pattern 2: Accumulate Text, Ignore Deltas

For simpler use cases where you don't need real-time streaming:

```python
async for msg in client.receive_response():
    # Skip StreamEvents entirely
    if isinstance(msg, StreamEvent):
        continue

    if isinstance(msg, AssistantMessage):
        for block in msg.content:
            if isinstance(block, TextBlock):
                # Complete text, no assembly needed
                print(block.text)
```

### Pattern 3: Tool Status Updates

```python
tool_statuses = {}  # id -> status

async for msg in client.receive_response():
    if isinstance(msg, AssistantMessage):
        for block in msg.content:
            if isinstance(block, ToolUseBlock):
                tool_statuses[block.id] = "running"
                await emit_tool_status(block.id, block.name, "running")

    elif isinstance(msg, UserMessage):
        if hasattr(msg, 'content') and not isinstance(msg.content, str):
            for block in msg.content:
                if isinstance(block, ToolResultBlock):
                    status = "error" if block.is_error else "completed"
                    tool_statuses[block.tool_use_id] = status
                    await emit_tool_status(
                        block.tool_use_id,
                        None,  # name not in result
                        status,
                        result=block.content
                    )
```

---

## Interrupt Behavior

### Verified Behavior

1. `await client.interrupt()` returns immediately (no exception)
2. The response iteration exits cleanly
3. A `ResultMessage` with `cost=0` is still yielded
4. Client remains usable for new queries

```python
async with ClaudeSDKClient(options=options) as client:
    await client.query("Count from 1 to 1000")

    async def consume_with_timeout():
        async for msg in client.receive_response():
            # Process messages
            pass

    task = asyncio.create_task(consume_with_timeout())

    # Interrupt after delay
    await asyncio.sleep(2)
    await client.interrupt()
    await task  # Wait for clean exit

    # Client is still usable
    await client.query("Say hello")
    async for msg in client.receive_response():
        # Works normally
        pass
```

---

## Session Persistence

### Getting Session ID

```python
session_id = None

async for msg in client.receive_response():
    if isinstance(msg, ResultMessage):
        session_id = msg.session_id
        # Store this for later resume

# session_id is a UUID string like "36935749-bf19-4882-81aa-0497bbc8d803"
```

### Resuming a Session

```python
# Resume previous session
options = ClaudeAgentOptions(
    resume=session_id,  # UUID string from previous ResultMessage
    include_partial_messages=True,
    # Other options...
)

async with ClaudeSDKClient(options=options) as client:
    # Agent has full context from previous session
    await client.query("What did we discuss before?")
    # Agent will remember previous conversation
```

### Session Continuity Within Client

Within a single `ClaudeSDKClient` context:
- Session ID remains constant across multiple queries
- Agent maintains full conversation context
- No need to resume - just send another query

```python
async with ClaudeSDKClient() as client:
    await client.query("Remember the number 42")
    async for msg in client.receive_response():
        pass

    await client.query("What number did I mention?")
    async for msg in client.receive_response():
        # Agent remembers "42"
        pass
```

---

## Concurrent Queries

### Observed Behavior

- `query()` during iteration returns SUCCESS (no exception)
- The original response continues to completion
- New query appears to be queued

### Recommendation

**Wait for response completion before sending new query.**

```python
# Safe pattern
async with ClaudeSDKClient() as client:
    await client.query("First question")
    async for msg in client.receive_response():
        # Process ALL messages
        pass  # Let iteration complete

    # Now safe to send next query
    await client.query("Second question")
    async for msg in client.receive_response():
        pass
```

---

## SystemMessage Details

The first message received is always a `SystemMessage` with `subtype='init'`:

```python
if isinstance(msg, SystemMessage) and msg.subtype == 'init':
    data = msg.data
    # Available info:
    session_id = data.get('session_id')
    model = data.get('model')
    tools = data.get('tools')  # List of available tools
    cwd = data.get('cwd')
    permission_mode = data.get('permissionMode')
    claude_code_version = data.get('claude_code_version')
```

---

## Gotchas

### 1. StreamEvent Import

```python
# Correct - StreamEvent is exported from main module
from claude_agent_sdk import StreamEvent

# All message types can be imported together
from claude_agent_sdk import (
    AssistantMessage, UserMessage, SystemMessage,
    ResultMessage, StreamEvent, TextBlock, ToolUseBlock
)
```

### 2. AssistantMessage Comes AFTER Deltas

The complete `AssistantMessage` with full `TextBlock` is yielded AFTER all `content_block_delta` events. If you need real-time streaming, process the deltas.

### 3. ToolResultBlock in UserMessage

Tool results are NOT in AssistantMessage. They come in a subsequent UserMessage:

```python
elif isinstance(msg, UserMessage):
    # Check for ToolResultBlock in content
    if not isinstance(msg.content, str):
        for block in msg.content:
            if isinstance(block, ToolResultBlock):
                # Tool result here
```

### 4. Cost is Zero After Interrupt

After `interrupt()`, the `ResultMessage` shows `cost=0` for the interrupted portion.

---

## Context7 Topics

| Need | Topic |
|------|-------|
| Streaming config | `include_partial_messages streaming` |
| Event types | `StreamEvent content_block_delta` |
| Session resume | `resume session ClaudeAgentOptions` |
| Interrupt | `interrupt ClaudeSDKClient` |
