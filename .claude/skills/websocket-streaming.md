---
name: websocket-streaming
description: WebSocket and SSE patterns for real-time communication. Use when implementing streaming, real-time features, or bidirectional communication.
---

# WebSocket Streaming Patterns

> **Purpose**: Patterns for implementing real-time WebSocket streaming with FastAPI backend and React frontend.

**Last Updated**: 2025-12-09
**Source**: Session 4A implementation (Real-Time Pipeline Updates)

---

## Backend: FastAPI WebSocket Streaming

### ADK Async Generator Pattern

**Discovery**: ADK `runner.run_async()` is already an async generator - just forward events!

```python
from fastapi import WebSocket, WebSocketDisconnect
import json
from datetime import datetime, timezone

@router.websocket("/chat/stream")
async def chat_stream(websocket: WebSocket):
    """Stream agent execution events in real-time."""
    await websocket.accept()

    try:
        # Receive initial request
        data = await websocket.receive_json()
        session_id = data["session_id"]
        message = data["message"]

        # Stream events from ADK async generator
        async for event in agent_service.chat_stream(session_id, message):
            await websocket.send_json(event)

        # Send completion signal
        await websocket.send_json({"type": "done"})

    except WebSocketDisconnect:
        logger.info("[WebSocket] Client disconnected")
    except Exception as e:
        logger.error(f"[WebSocket] Error: {e}", exc_info=True)
        await websocket.send_json({"type": "error", "message": str(e)})
    finally:
        await websocket.close()
```

**Key Points**:
- ✅ WebSocket support built into FastAPI (no extra dependencies)
- ✅ Always accept connection first: `await websocket.accept()`
- ✅ Handle `WebSocketDisconnect` gracefully in try/except
- ✅ Close connection in finally block

---

### Streaming Agent Service

```python
async def chat_stream(self, session_id: str, message: str):
    """Stream agent execution events."""
    # ... session setup (identical to batch chat) ...

    # Track tool calls for final response
    tool_calls = []

    # Run agent and stream events as they occur
    events = []
    async for event in self.runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=user_message_content,
        state_delta=state_delta
    ):
        events.append(event)

        # Parse event and yield streaming update
        if hasattr(event, 'content') and hasattr(event.content, 'parts'):
            for part in event.content.parts:
                if hasattr(part, 'function_call'):
                    fc = part.function_call
                    yield {
                        "type": "tool_start",
                        "tool_id": fc.id,
                        "tool_name": fc.name,
                        "arguments": fc.args,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }

                elif hasattr(part, 'function_response'):
                    fr = part.function_response
                    yield {
                        "type": "tool_complete",
                        "tool_id": fr.id,
                        "tool_name": fr.name,
                        "result": fr.response,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }

    # Yield final response
    yield {
        "type": "response",
        "content": self._extract_response_text(events),
        "tool_calls": tool_calls,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    # Persist session (same as batch chat)
    await self.save_session(...)
```

**Key Points**:
- ✅ Session persistence identical to batch chat
- ✅ Collect events for final response extraction
- ✅ Yield events as they occur (don't wait for completion)

---

### JSON Serialization Gotcha

**Problem**: ADK objects contain Protobuf types that aren't JSON-serializable

**Solution**: Always use `default=str` fallback

```python
import json

def serialize_event(event):
    """Safely serialize ADK event to JSON."""
    try:
        return json.dumps(event, default=str)
    except TypeError as e:
        logger.warning(f"Serialization fallback: {e}")
        return json.dumps({"error": "Serialization failed", "type": type(event).__name__})
```

**Common Issues**:
- `function_call.args` may contain Protobuf `Struct` objects
- `datetime` objects need `.isoformat()` or `default=str`
- Always wrap in try/except for safety

---

### Null Safety Pattern

**Problem**: ADK can return `None` for function_call or function_response

**Solution**: Always check with `hasattr()` before accessing

```python
if hasattr(event, 'content') and hasattr(event.content, 'parts'):
    for part in event.content.parts:
        # Check function_call exists
        if hasattr(part, 'function_call') and part.function_call is not None:
            fc = part.function_call
            # Still check fields exist
            if hasattr(fc, 'id') and hasattr(fc, 'name'):
                # Safe to use fc.id and fc.name
```

**Never assume**:
- `function_call` or `function_response` exist
- Fields like `id`, `name`, `args` are present
- Objects have expected methods (e.g., `.keys()` on State)

---

## Frontend: React WebSocket Client

### WebSocket Client with Callbacks

```typescript
// services/api.ts
export const chatApi = {
  sendMessageStream: (
    data: { session_id: string; message: string },
    callbacks: {
      onToolStart: (toolId: string, toolName: string, args: object, timestamp: string) => void;
      onToolComplete: (toolId: string, toolName: string, result: any, timestamp: string) => void;
      onResponse: (content: string, toolCalls: ToolCall[], timestamp: string) => void;
      onDone: () => void;
      onError: (error: string) => void;
    }
  ): WebSocket => {
    const ws = new WebSocket(`ws://localhost:8000/api/v1/chat/stream`);

    ws.onopen = () => {
      console.log('[WebSocket] Connected');
      ws.send(JSON.stringify(data));
    };

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);

      switch (message.type) {
        case 'tool_start':
          callbacks.onToolStart(message.tool_id, message.tool_name, message.arguments, message.timestamp);
          break;
        case 'tool_complete':
          callbacks.onToolComplete(message.tool_id, message.tool_name, message.result, message.timestamp);
          break;
        case 'response':
          callbacks.onResponse(message.content, message.tool_calls, message.timestamp);
          break;
        case 'done':
          callbacks.onDone();
          ws.close();
          break;
        case 'error':
          callbacks.onError(message.message);
          ws.close();
          break;
      }
    };

    ws.onerror = (error) => {
      console.error('[WebSocket] Error:', error);
      callbacks.onError('WebSocket connection failed');
    };

    return ws;
  }
};
```

**Key Points**:
- ✅ Return WebSocket instance for cancellation support
- ✅ Close connection on 'done' and 'error' events
- ✅ Always handle `onerror` for network failures

---

### Incremental State Updates

**Pattern**: Update React state incrementally as events arrive

```typescript
const [allToolCalls, setAllToolCalls] = useState<ToolCall[]>([]);
const [isStreaming, setIsStreaming] = useState(false);

const handleSendMessageStream = () => {
  setIsStreaming(true);

  const ws = chatApi.sendMessageStream(
    { session_id, message },
    {
      onToolStart: (toolId, toolName, args, timestamp) => {
        // Add tool with null result (in progress)
        setAllToolCalls(prev => [...prev, {
          name: toolName,
          arguments: args,
          result: null,  // null = in progress
          error: undefined
        }]);
      },

      onToolComplete: (toolId, toolName, result, timestamp) => {
        // Update tool with result (completed)
        setAllToolCalls(prev =>
          prev.map(tc =>
            tc.name === toolName && tc.result === null
              ? { ...tc, result }
              : tc
          )
        );
      },

      onResponse: (content, toolCalls, timestamp) => {
        // Add assistant message
        setMessages(prev => [...prev, {
          role: 'assistant',
          content,
          tool_calls: toolCalls,
          timestamp
        }]);
      },

      onDone: () => {
        setIsStreaming(false);
      },

      onError: (error) => {
        setIsStreaming(false);
        alert(`Failed: ${error}`);
      }
    }
  );
};
```

**Key Points**:
- ✅ Use `prev => ...` pattern for state updates (React batches these efficiently)
- ✅ Identify in-progress tools with `result === null`
- ✅ Update by matching tool name (or tool_id if available)

---

### Cancel Support

```typescript
const [currentWs, setCurrentWs] = useState<WebSocket | null>(null);

// Store WebSocket reference
const ws = chatApi.sendMessageStream(...);
setCurrentWs(ws);

// Cancel button
<button onClick={() => {
  currentWs?.close();
  setIsStreaming(false);
  setCurrentWs(null);
}}>
  Cancel
</button>
```

---

## Production Considerations

### WebSocket URL Configuration

**Development**: `ws://localhost:8000/api/v1/chat/stream`
**Production**: `wss://your-domain.com/api/v1/chat/stream` (secure WebSocket)

```typescript
const WEBSOCKET_URL = import.meta.env.VITE_WEBSOCKET_URL || 'ws://localhost:8000/api/v1/chat/stream';
```

---

### Connection Timeout

**Problem**: Long-running agents may timeout WebSocket

**Solutions**:
1. Increase timeout (FastAPI side)
2. Send keep-alive pings every 30s
3. Show progress indicator to user

```python
# FastAPI WebSocket with longer timeout
@router.websocket("/chat/stream")
async def chat_stream(websocket: WebSocket):
    websocket.timeout = 300  # 5 minutes
    ...
```

---

### Error Recovery

**Pattern**: Fallback to batch HTTP if WebSocket fails

```typescript
try {
  const ws = chatApi.sendMessageStream(...);
} catch (error) {
  console.error('[WebSocket] Failed, falling back to HTTP POST');
  // Fallback to existing chatMutation
  await chatApi.sendMessage(...);
}
```

---

## Common Gotchas

### 1. Don't Batch Events

❌ **Wrong** (collecting events):
```python
events = []
async for event in runner.run_async(...):
    events.append(event)

# Send all at once (defeats purpose of streaming!)
await websocket.send_json({"events": events})
```

✅ **Correct** (streaming):
```python
async for event in runner.run_async(...):
    # Send immediately
    await websocket.send_json(serialize_event(event))
```

---

### 2. Session Persistence Race Condition

**Problem**: User disconnects mid-stream → session may not save

**Solution**: Save in finally block

```python
try:
    async for event in runner.run_async(...):
        await websocket.send_json(event)
finally:
    # Always save session, even if connection drops
    await self.save_session(...)
```

---

### 3. React State Updates Out of Order

**Problem**: Multiple `setState` calls may batch incorrectly

**Solution**: Always use functional updates

❌ **Wrong**:
```typescript
setAllToolCalls([...allToolCalls, newTool]);  // Uses stale state!
```

✅ **Correct**:
```typescript
setAllToolCalls(prev => [...prev, newTool]);  // Uses latest state
```

---

## Testing

### Backend WebSocket Test (Python)

```python
import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/api/v1/chat/stream"

    async with websockets.connect(uri) as websocket:
        # Send request
        await websocket.send(json.dumps({
            "session_id": "test-session-001",
            "message": "List my GTM accounts"
        }))

        # Receive events
        while True:
            message = await websocket.recv()
            event = json.loads(message)
            print(f"Event: {event['type']}")

            if event['type'] == 'done':
                break

asyncio.run(test_websocket())
```

---

### Frontend Integration Test

**Manual test**:
1. Open DevTools → Network → WS tab
2. Send message
3. Watch WebSocket frames in real-time
4. Verify events arrive incrementally (not batched)

**Expected frames**:
```
{"type": "user_message", ...}
{"type": "tool_start", ...}
{"type": "tool_complete", ...}
{"type": "response", ...}
{"type": "done"}
```

---

## Related Patterns

- **Frontend State Management**: `.claude/skills/frontend-patterns/07-state-management.md`
- **ADK Integration**: `.claude/skills/google-adk-patterns/05-fastapi-integration.md`
- **Error Handling**: `.claude/skills/debugging-patterns.md`

---

**Verified Working**: Session 4A (2025-12-09)
**Files**: `backend/app/api/routes.py:178-236`, `backend/app/services/agent_service.py:251-458`, `frontend-v2/src/services/api.ts:89-195`
