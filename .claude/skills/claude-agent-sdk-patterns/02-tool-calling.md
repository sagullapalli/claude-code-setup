# Custom Tools with Claude Agent SDK

Create custom tools using the `@tool` decorator and MCP servers.

**For current syntax**: `get-library-docs: /anthropics/claude-agent-sdk-python (topic: "tool decorator MCP")`

---

## Overview

Claude Agent SDK supports custom tools via:
1. **@tool decorator** - Define Python functions as tools
2. **MCP servers** - Bundle tools into servers
3. **allowed_tools** - Enable tools for the agent

---

## Basic Tool Pattern

```python
from typing import Any
from claude_agent_sdk import tool, create_sdk_mcp_server, ClaudeAgentOptions, ClaudeSDKClient

# 1. Define tool with @tool decorator
@tool("greet", "Greet a user by name", {"name": str})
async def greet_user(args: dict[str, Any]) -> dict[str, Any]:
    return {
        "content": [
            {"type": "text", "text": f"Hello, {args['name']}!"}
        ]
    }

# 2. Create MCP server
server = create_sdk_mcp_server(
    name="my-tools",
    version="1.0.0",
    tools=[greet_user]
)

# 3. Configure and use
options = ClaudeAgentOptions(
    mcp_servers={"tools": server},
    allowed_tools=["mcp__tools__greet"]  # Note: mcp__<server>__<tool>
)

async with ClaudeSDKClient(options=options) as client:
    await client.query("Greet Alice")
    async for msg in client.receive_response():
        print(msg)
```

---

## @tool Decorator

```python
@tool(name, description, input_schema)
```

| Parameter | Type | Purpose |
|-----------|------|---------|
| `name` | `str` | Tool name (used in `allowed_tools`) |
| `description` | `str` | What the tool does (shown to Claude) |
| `input_schema` | `dict` | Parameter types: `{"param": type}` |

### Input Schema Types

```python
# Simple types
{"name": str}
{"count": int}
{"price": float}
{"enabled": bool}

# Complex (use JSON schema in description)
{"data": dict}  # Describe structure in description
```

---

## Tool Return Format

Tools must return a dict with `content` list:

```python
@tool("example", "Example tool", {"input": str})
async def example_tool(args: dict[str, Any]) -> dict[str, Any]:
    # Success response
    return {
        "content": [
            {"type": "text", "text": "Result here"}
        ]
    }
```

### Error Response

```python
@tool("divide", "Divide two numbers", {"a": float, "b": float})
async def divide(args: dict[str, Any]) -> dict[str, Any]:
    if args["b"] == 0:
        return {
            "content": [{"type": "text", "text": "Error: Division by zero"}],
            "is_error": True  # Marks as error
        }

    result = args["a"] / args["b"]
    return {
        "content": [{"type": "text", "text": f"{args['a']} / {args['b']} = {result}"}]
    }
```

---

## Multiple Tools Example

```python
from typing import Any
from claude_agent_sdk import (
    tool, create_sdk_mcp_server, ClaudeAgentOptions, ClaudeSDKClient,
    AssistantMessage, TextBlock, ToolUseBlock
)

# Calculator tools
@tool("add", "Add two numbers", {"a": float, "b": float})
async def add(args: dict[str, Any]) -> dict[str, Any]:
    result = args["a"] + args["b"]
    return {"content": [{"type": "text", "text": f"{result}"}]}

@tool("multiply", "Multiply two numbers", {"a": float, "b": float})
async def multiply(args: dict[str, Any]) -> dict[str, Any]:
    result = args["a"] * args["b"]
    return {"content": [{"type": "text", "text": f"{result}"}]}

@tool("subtract", "Subtract b from a", {"a": float, "b": float})
async def subtract(args: dict[str, Any]) -> dict[str, Any]:
    result = args["a"] - args["b"]
    return {"content": [{"type": "text", "text": f"{result}"}]}

# Bundle into server
calculator = create_sdk_mcp_server(
    name="calculator",
    version="1.0.0",
    tools=[add, multiply, subtract]
)

# Use with Claude
options = ClaudeAgentOptions(
    mcp_servers={"calc": calculator},
    allowed_tools=[
        "mcp__calc__add",
        "mcp__calc__multiply",
        "mcp__calc__subtract"
    ]
)

async def main():
    async with ClaudeSDKClient(options=options) as client:
        await client.query("Calculate (10 + 5) * 3")

        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")
                    elif isinstance(block, ToolUseBlock):
                        print(f"Tool: {block.name}({block.input})")

import asyncio
asyncio.run(main)
```

---

## Stateful Tools

Tools can access shared state:

```python
from typing import Any
from claude_agent_sdk import tool, create_sdk_mcp_server

# Shared state
class DataStore:
    def __init__(self):
        self.items: list[str] = []

store = DataStore()

@tool("add_item", "Add an item to the store", {"item": str})
async def add_item(args: dict[str, Any]) -> dict[str, Any]:
    store.items.append(args["item"])
    return {
        "content": [{"type": "text", "text": f"Added '{args['item']}'. Total: {len(store.items)}"}]
    }

@tool("list_items", "List all items", {})
async def list_items(args: dict[str, Any]) -> dict[str, Any]:
    if not store.items:
        return {"content": [{"type": "text", "text": "Store is empty"}]}

    items_text = "\n".join(f"- {item}" for item in store.items)
    return {"content": [{"type": "text", "text": f"Items:\n{items_text}"}]}

@tool("clear_items", "Clear all items", {})
async def clear_items(args: dict[str, Any]) -> dict[str, Any]:
    count = len(store.items)
    store.items.clear()
    return {"content": [{"type": "text", "text": f"Cleared {count} items"}]}

server = create_sdk_mcp_server("store", tools=[add_item, list_items, clear_items])
```

---

## Tool Naming Convention

Tools follow the pattern: `mcp__<server_name>__<tool_name>`

```python
# Server named "calc" with tool named "add"
allowed_tools=["mcp__calc__add"]

# Server named "database" with tool named "query"
allowed_tools=["mcp__database__query"]

# Multiple tools
allowed_tools=[
    "mcp__calc__add",
    "mcp__calc__subtract",
    "mcp__database__query",
]
```

**Project Convention**: Use descriptive server names that indicate purpose.

---

## External MCP Servers

Connect to external MCP servers:

```python
options = ClaudeAgentOptions(
    mcp_servers={
        # In-process SDK server
        "calc": calculator_server,

        # External stdio server
        "external": {
            "type": "stdio",
            "command": "python",
            "args": ["-m", "my_mcp_server"]
        }
    },
    allowed_tools=[
        "mcp__calc__add",
        "mcp__external__some_tool"
    ]
)
```

---

## Gotchas

### 1. Tool Name in allowed_tools
```python
# Wrong - just tool name
allowed_tools=["greet"]

# Right - full MCP path
allowed_tools=["mcp__tools__greet"]
```

### 2. Return Format
```python
# Wrong - just a string
return "Hello!"

# Right - content list
return {"content": [{"type": "text", "text": "Hello!"}]}
```

### 3. Async Required
```python
# Wrong - sync function
@tool("sync_tool", "...", {})
def sync_tool(args):
    return {...}

# Right - async function
@tool("async_tool", "...", {})
async def async_tool(args):
    return {...}
```

---

## Context7 Topics

| Need | Topic |
|------|-------|
| Tool decorator | `@tool decorator` |
| MCP servers | `create_sdk_mcp_server` |
| Tool examples | `custom tools examples` |

---

**Next**: [03-hooks.md](03-hooks.md) for hooks and permissions
