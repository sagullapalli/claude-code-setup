---
name: Claude Agent SDK Patterns
description: Claude Agent SDK patterns for building AI agents with Claude Code capabilities. Use when creating agents, custom tools, hooks, or MCP integrations.
tags: [claude, anthropic, agent-sdk, tools, hooks, mcp]
context7_libraries:
  - /anthropics/claude-agent-sdk-python
  - /anthropics/anthropic-cookbook
last_verified: 2025-12-26
---

# Claude Agent SDK Patterns - Quick Reference

The **Claude Agent SDK** (`claude-agent-sdk`) enables building AI agents with Claude Code's capabilities: file operations, code execution, tool use, and multi-turn conversations.

**Package**: `pip install claude-agent-sdk`

---

## ⚠️ SDK Disambiguation

| SDK | Package | Purpose | Use When |
|-----|---------|---------|----------|
| **Claude Agent SDK** | `claude-agent-sdk` | Build agents with Claude Code capabilities | You need file ops, code execution, tools, multi-turn |
| **Anthropic SDK** | `anthropic` | Direct Claude API access | Simple chat, messages API, basic tool calling |

**This skill covers the Claude Agent SDK** - for agentic applications that need Claude Code's full capabilities (file system access, bash execution, MCP tools).

**If you need the Anthropic SDK** (basic Claude API):
- Use Context7: `/anthropics/anthropic-sdk-python`
- See Anthropic docs: https://docs.anthropic.com/en/api/

---

## Modules

1. **[01-sdk-basics.md](01-sdk-basics.md)** - Core SDK Usage
   - Installation and setup
   - `query()` vs `ClaudeSDKClient`
   - Message handling and streaming
   - ClaudeAgentOptions configuration

2. **[02-tool-calling.md](02-tool-calling.md)** - Custom Tools
   - @tool decorator pattern
   - MCP server creation
   - Tool registration and naming
   - Error handling in tools

3. **[03-hooks.md](03-hooks.md)** - Hooks & Permissions
   - PreToolUse hooks (validation, blocking)
   - PostToolUse hooks (review, context injection)
   - Permission callbacks (can_use_tool)
   - Stop/interrupt patterns

4. **[04-streaming-behavior.md](04-streaming-behavior.md)** - Streaming Details (validated 2026-01-01)
   - StreamEvent vs AssistantMessage timing
   - Real-time text delta streaming
   - Tool use/result message sequence
   - Interrupt behavior and client reuse
   - Session persistence and resume

---

## When to Use Claude Agent SDK

| Need | Use Agent SDK? | Why |
|------|----------------|-----|
| Simple chat completion | No | Use `anthropic` SDK directly |
| File operations | Yes | Built-in Read/Write/Edit tools |
| Code execution | Yes | Bash tool with sandboxing |
| Multi-turn agents | Yes | Session management |
| Custom tools | Yes | @tool decorator + MCP |
| Tool validation | Yes | PreToolUse hooks |

---

## Quick Lookup

**Common Issues:**
- Messages not appearing? -> Check `receive_response()` iteration
- Tool not found? -> Verify `allowed_tools` includes MCP prefix
- Hook not firing? -> Check `HookMatcher` pattern
- Session lost? -> Use `ClaudeSDKClient` context manager

**For current syntax, use Context7:**
```
get-library-docs: /anthropics/claude-agent-sdk-python (topic: "query options")
```

---

## Two Usage Patterns

### 1. One-Shot Query (Stateless)
```python
from claude_agent_sdk import query, AssistantMessage, TextBlock

async for message in query(prompt="What is 2 + 2?"):
    if isinstance(message, AssistantMessage):
        for block in message.content:
            if isinstance(block, TextBlock):
                print(block.text)
```

### 2. Interactive Client (Stateful)
```python
from claude_agent_sdk import ClaudeSDKClient

async with ClaudeSDKClient() as client:
    await client.query("What's the capital of France?")
    async for msg in client.receive_response():
        # Handle response
        pass

    # Follow-up in same session
    await client.query("What's its population?")
    async for msg in client.receive_response():
        pass
```

---

## Core Concepts

### Message Types
| Type | Contains | When |
|------|----------|------|
| `AssistantMessage` | Claude's response, tool uses | Every turn |
| `UserMessage` | User prompts, tool results | With replay |
| `SystemMessage` | Claude Code events | System events |
| `ResultMessage` | Cost, usage, output | End of query |
| `StreamEvent` | Partial updates | With `include_partial_messages=True` |

### Content Blocks
| Block | Found In | Contains |
|-------|----------|----------|
| `TextBlock` | AssistantMessage | `.text` |
| `ToolUseBlock` | AssistantMessage | `.name`, `.input`, `.id` |
| `ThinkingBlock` | AssistantMessage | `.thinking` |
| `ToolResultBlock` | UserMessage | `.content`, `.tool_use_id` |

---

## Anti-Patterns

**Forgetting async context manager**
```python
# Wrong - session may not clean up
client = ClaudeSDKClient()
await client.query(...)

# Right
async with ClaudeSDKClient() as client:
    await client.query(...)
```

**Not iterating response**
```python
# Wrong - messages never consumed
await client.query("Hello")

# Right
await client.query("Hello")
async for msg in client.receive_response():
    ...
```

**MCP tool naming**
```python
# Wrong - missing mcp__ prefix
allowed_tools=["my_tool"]

# Right
allowed_tools=["mcp__server_name__tool_name"]
```

---

## Project Conventions

1. **Always use context manager** for `ClaudeSDKClient`
2. **Set `max_turns`** to prevent runaway agents
3. **Set `max_budget_usd`** for cost control
4. **Use hooks** for security-sensitive operations
5. **Name MCP servers** descriptively (e.g., `"calculator"`, `"database"`)

---

## Resources

- **GitHub**: https://github.com/anthropics/claude-agent-sdk-python
- **Claude Code Docs**: https://docs.anthropic.com/en/docs/claude-code

**Context7 for live docs:**
- `/anthropics/claude-agent-sdk-python` - SDK reference

---

**Last Updated**: 2026-01-01
