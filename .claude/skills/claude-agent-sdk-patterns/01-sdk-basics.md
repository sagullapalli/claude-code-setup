# Claude Agent SDK Basics

Core patterns for the `claude-agent-sdk` package.

> **Note**: This is the **Claude Agent SDK** (`claude-agent-sdk`), not the Anthropic SDK (`anthropic`).
> See [SKILL.md](SKILL.md#sdk-disambiguation) for the difference.

**For current syntax**: `get-library-docs: /anthropics/claude-agent-sdk-python (topic: "query client")`

---

## Installation

```bash
pip install claude-agent-sdk
```

**Requirements**: Python 3.10+, Claude Code CLI installed

---

## Two Usage Patterns

### 1. `query()` - One-Shot, Stateless

Best for: Simple tasks, fire-and-forget operations.

```python
import anyio
from claude_agent_sdk import query, AssistantMessage, TextBlock, ResultMessage

async def main():
    async for message in query(prompt="What is 2 + 2?"):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"Claude: {block.text}")
        elif isinstance(message, ResultMessage):
            print(f"Cost: ${message.total_cost_usd:.4f}")

anyio.run(main)
```

### 2. `ClaudeSDKClient` - Multi-Turn, Stateful

Best for: Conversations, follow-up questions, interactive agents.

```python
import asyncio
from claude_agent_sdk import ClaudeSDKClient, AssistantMessage, TextBlock

async def main():
    async with ClaudeSDKClient() as client:
        # First turn
        await client.query("What's the capital of France?")
        async for msg in client.receive_response():
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")

        # Follow-up (same session, maintains context)
        await client.query("What's its population?")
        async for msg in client.receive_response():
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")

asyncio.run(main)
```

**Project Convention**: Use `ClaudeSDKClient` for multi-turn; `query()` for one-shot.

---

## ClaudeAgentOptions

Configure agent behavior with `ClaudeAgentOptions`:

```python
from claude_agent_sdk import ClaudeAgentOptions, query

options = ClaudeAgentOptions(
    # Tools and permissions
    allowed_tools=["Read", "Write", "Bash", "Edit"],
    disallowed_tools=["Bash"],  # Overrides allowed
    permission_mode="acceptEdits",  # Auto-accept file edits

    # System behavior
    system_prompt="You are a helpful Python assistant.",
    cwd="/path/to/project",  # Working directory

    # Limits (ALWAYS SET THESE)
    max_turns=10,
    max_budget_usd=5.0,

    # Model
    model="claude-sonnet-4-5",
)

async for message in query(prompt="Analyze this code", options=options):
    # Process messages
    pass
```

### Key Options

| Option | Type | Purpose |
|--------|------|---------|
| `allowed_tools` | `list[str]` | Tools agent can use |
| `permission_mode` | `str` | `"default"`, `"acceptEdits"`, `"bypassPermissions"` |
| `system_prompt` | `str` | Custom instructions |
| `cwd` | `str | Path` | Working directory |
| `max_turns` | `int` | Limit agent iterations |
| `max_budget_usd` | `float` | Cost limit |
| `model` | `str` | Model to use |
| `hooks` | `dict` | PreToolUse/PostToolUse hooks |
| `mcp_servers` | `dict` | Custom MCP tool servers |
| `tools` | `list[str]` | Base toolset (e.g., `["Read", "Write"]`) |

> **Note**: `tools` sets the base toolset available; `allowed_tools` further restricts which tools the agent can actually use. If both are set, `allowed_tools` takes precedence.

**Project Convention**: Always set `max_turns` and `max_budget_usd`.

---

## Message Handling

### Message Types

```python
from claude_agent_sdk import (
    AssistantMessage,  # Claude's response
    UserMessage,       # User input (with replay)
    SystemMessage,     # Claude Code events
    ResultMessage,     # Final cost/usage
)
```

### Content Blocks

```python
from claude_agent_sdk import (
    TextBlock,       # Text content
    ToolUseBlock,    # Tool invocation
    ThinkingBlock,   # Extended thinking
    ToolResultBlock, # Tool output
)
```

### Processing Pattern

```python
async for message in query(prompt="...", options=options):
    if isinstance(message, AssistantMessage):
        for block in message.content:
            if isinstance(block, TextBlock):
                print(f"Text: {block.text}")
            elif isinstance(block, ToolUseBlock):
                print(f"Tool: {block.name}, Input: {block.input}")
            elif isinstance(block, ThinkingBlock):
                print(f"Thinking: {block.thinking}")

    elif isinstance(message, ResultMessage):
        print(f"Cost: ${message.total_cost_usd:.4f}")
        if message.structured_output:
            print(f"Output: {message.structured_output}")
```

---

## Structured Output

Get validated JSON responses:

```python
options = ClaudeAgentOptions(
    output_format={
        "type": "json_schema",
        "schema": {
            "type": "object",
            "properties": {
                "sentiment": {"type": "string", "enum": ["positive", "negative", "neutral"]},
                "confidence": {"type": "number", "minimum": 0, "maximum": 1},
            },
            "required": ["sentiment", "confidence"]
        }
    },
    max_turns=1
)

async for message in query(prompt="Analyze: 'Great product!'", options=options):
    if isinstance(message, ResultMessage):
        print(message.structured_output)
        # {"sentiment": "positive", "confidence": 0.95}
```

---

## Interruption

Stop long-running operations:

```python
import asyncio
from claude_agent_sdk import ClaudeSDKClient

async def main():
    async with ClaudeSDKClient() as client:
        await client.query("Count from 1 to 1000 slowly")

        # Consume in background
        async def consume():
            async for msg in client.receive_response():
                pass

        task = asyncio.create_task(consume())

        # Interrupt after 2 seconds
        await asyncio.sleep(2)
        await client.interrupt()
        await task

        # New instruction
        await client.query("Just say hello instead")
        async for msg in client.receive_response():
            # Process new response
            pass

asyncio.run(main)
```

---

## Error Handling

```python
from claude_agent_sdk import query, AssistantMessage, ResultMessage

async for message in query(prompt="...", options=options):
    if isinstance(message, AssistantMessage):
        if message.error:
            print(f"Error: {message.error}")
            # Handle rate limits, auth errors, etc.
            continue

        for block in message.content:
            # Process normally
            pass

    elif isinstance(message, ResultMessage):
        if message.total_cost_usd > 1.0:
            print("Warning: High cost query")
```

---

## Gotchas

### 1. Must Iterate Response
```python
# Wrong - messages never consumed
await client.query("Hello")

# Right
await client.query("Hello")
async for msg in client.receive_response():
    ...
```

### 2. Use Context Manager
```python
# Wrong - may leak resources
client = ClaudeSDKClient()

# Right
async with ClaudeSDKClient() as client:
    ...
```

### 3. anyio vs asyncio
```python
# query() works with anyio
import anyio
anyio.run(main)

# ClaudeSDKClient works with asyncio
import asyncio
asyncio.run(main)
```

---

## Context7 Topics

| Need | Topic |
|------|-------|
| Query options | `query options ClaudeAgentOptions` |
| Client usage | `ClaudeSDKClient` |
| Messages | `message types AssistantMessage` |
| Streaming | `streaming response` |

---

**Next**: [02-tool-calling.md](02-tool-calling.md) for custom tools
