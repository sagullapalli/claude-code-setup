# ADR-002: Critic Agent Pattern

## Status
Proposed

## Context
The Interface includes a "Critic Agent" that observes the main coding agent's work and provides insights. Key requirements:
1. Observe all agent actions (thinking, tool calls, outputs)
2. Provide third-eye perspective for the user
3. Detect patterns, potential issues, missed opportunities
4. Must NOT slow down or block the main agent

The challenge: How to implement observation without coupling to the main agent's execution?

## Decision
Implement the Critic as an **async observer** using an event queue pattern:

```
Main Agent Stream
       │
       ▼
  Event Queue (async)
       │
       ▼
  Critic Agent (periodic processing)
       │
       ▼
  Insights Panel (frontend)
```

### Key Design Choices

| Aspect | Decision | Rationale |
|--------|----------|-----------|
| **SDK** | Lightweight `anthropic` SDK | No need for full Agent SDK, just analysis |
| **Processing** | Batched, periodic (every N events or T seconds) | Avoids per-event overhead |
| **Model** | Haiku or small model | Fast, cheap, sufficient for observation |
| **Coupling** | Event queue, no direct dependency | Main agent unaware of critic |

### Event Flow

1. Main agent streams events via WebSocket
2. Backend copies events to async queue (non-blocking)
3. Critic service consumes queue periodically
4. Critic analyzes batch, generates insights
5. Insights pushed to frontend via separate channel

## Consequences

### Positive
- Main agent performance unaffected
- Critic can be enabled/disabled without code changes
- Can adjust observation frequency based on load
- Failure in critic doesn't break main agent

### Negative
- Insights are delayed (not real-time)
- Duplicate data flow (events copied to queue)
- Additional API costs for critic model calls

### Neutral
- Need to define what "insights" the critic provides
- User can toggle critic on/off

## Critic Responsibilities

The critic should watch for:

1. **Errors & Issues**
   - Failed tool calls the agent ignores
   - Syntax errors in generated code
   - Security concerns (exposed secrets, vulnerable code)

2. **Missed Opportunities**
   - Existing code the agent could have reused
   - Better patterns available in the codebase
   - Tests not written for new code

3. **Process Quality**
   - Agent going in circles
   - Excessive tool calls for simple tasks
   - Context window filling up

4. **User Assistance**
   - Summarize what agent is doing (for long operations)
   - Highlight key decisions for user review
   - Suggest when user input would help

## Implementation Notes

```python
# backend/services/critic_service.py

class CriticService:
    def __init__(self):
        self.event_queue = asyncio.Queue()
        self.client = anthropic.Anthropic()

    async def observe(self, event: AgentEvent):
        """Non-blocking: just queue the event"""
        await self.event_queue.put(event)

    async def process_loop(self):
        """Background task: periodically analyze queued events"""
        while True:
            events = await self._drain_queue(max_events=10)
            if events:
                insights = await self._analyze(events)
                await self._publish_insights(insights)
            await asyncio.sleep(5)  # Process every 5 seconds

    async def _analyze(self, events: list[AgentEvent]) -> list[Insight]:
        response = await self.client.messages.create(
            model="claude-3-haiku-20240307",
            messages=[{
                "role": "user",
                "content": f"Analyze these agent events and identify issues:\n{events}"
            }]
        )
        return self._parse_insights(response)
```

```typescript
// frontend: CriticPanel component
const CriticPanel = () => {
  const { insights } = useCriticStream();

  return (
    <div className="critic-panel">
      <h3>Critic Insights</h3>
      {insights.map(insight => (
        <InsightCard
          key={insight.id}
          type={insight.type}  // error, suggestion, summary
          message={insight.message}
        />
      ))}
    </div>
  );
};
```

## Alternatives Considered

1. **Synchronous observation** - Rejected: Would slow main agent
2. **Separate parallel agent** - Rejected: Complex coordination, race conditions
3. **Post-hoc analysis only** - Rejected: User wants real-time-ish insights
4. **Full Agent SDK for critic** - Rejected: Overkill, just need simple analysis

## Future Considerations

- Could evolve into a "supervisor" that can intervene (with user permission)
- Could maintain its own memory for cross-session pattern detection
- Could integrate with `.claude/rules/` to enforce project standards

## References
- Sage validation (2025-12-27)
- Anthropic multi-agent research on observer patterns
