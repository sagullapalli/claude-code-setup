# ADR-001: Dual Streaming Channels

## Status
Proposed

## Context
The Interface needs to stream two types of real-time data to the frontend:
1. **Agent events** - Thinking traces, tool calls, text output (variable frequency, text-heavy)
2. **Browser frames** - CDP screencast JPEG images (high frequency, ~10-30fps, binary-heavy)

Combining these on a single WebSocket connection creates problems:
- Frame floods can block agent messages
- Different QoS requirements (agent = reliable, frames = best-effort)
- Difficult to throttle one without affecting the other

## Decision
Use **two separate streaming channels**:

| Channel | Technology | Purpose | Priority |
|---------|------------|---------|----------|
| Agent Events | WebSocket (`/ws/agent`) | Thinking, tools, output | High (reliable) |
| Browser Frames | Socket.io (`/browser`) | CDP screencast, console | Medium (best-effort) |

### Why WebSocket for Agent?
- Native browser support
- Simple protocol for structured JSON messages
- Easy integration with FastAPI
- Reliable message delivery

### Why Socket.io for Browser?
- Built-in reconnection handling
- Room/namespace support (multiple browser sessions)
- Binary message optimization
- Automatic frame dropping under load
- Fallback to polling if needed

## Consequences

### Positive
- Agent messages never blocked by frame floods
- Independent throttling and quality control
- Cleaner separation of concerns
- Can disable browser streaming without affecting agent

### Negative
- Two connection protocols to manage
- Slightly more complex frontend setup
- Need to coordinate timestamps across channels

### Neutral
- Frontend needs two connection hooks (`useWebSocket`, `useSocketIO`)

## Implementation Notes

```python
# Backend: Two separate endpoints
@app.websocket("/ws/agent")
async def agent_websocket(websocket: WebSocket):
    # Agent events - reliable delivery
    pass

# Socket.io for browser frames
sio = socketio.AsyncServer(async_mode='asgi')
@sio.on('connect', namespace='/browser')
async def browser_connect(sid, environ):
    # Browser frames - best effort
    pass
```

```typescript
// Frontend: Two hooks
const { messages } = useAgentWebSocket('/ws/agent');
const { frame, console } = useBrowserSocket('/browser');
```

## Alternatives Considered

1. **Single WebSocket with message types** - Rejected: Frame floods block agent messages
2. **WebRTC for browser** - Rejected: Overkill, complex setup for our use case
3. **HTTP polling for browser** - Rejected: Too slow, wastes bandwidth

## References
- Sage validation (2025-12-27)
- Scout research on browser embedding approaches
