# Hooks & Permissions

Control tool execution with hooks and permission callbacks.

**For current syntax**: `get-library-docs: /anthropics/claude-agent-sdk-python (topic: "hooks PreToolUse")`

---

## Overview

Hooks intercept tool execution:

| Hook | When | Use For |
|------|------|---------|
| `PreToolUse` | Before tool runs | Validation, blocking, modification |
| `PostToolUse` | After tool runs | Review, logging, context injection |

---

## PreToolUse Hook

Block or modify tool calls before execution:

```python
import asyncio
from claude_agent_sdk import (
    ClaudeAgentOptions, ClaudeSDKClient, HookMatcher,
    HookInput, HookContext, HookJSONOutput
)

async def validate_bash(
    input_data: HookInput,
    tool_use_id: str | None,
    context: HookContext
) -> HookJSONOutput:
    """Block dangerous bash commands."""
    tool_name = input_data["tool_name"]
    tool_input = input_data["tool_input"]

    if tool_name != "Bash":
        return {}

    command = tool_input.get("command", "")

    # Block dangerous patterns
    dangerous = ["rm -rf", "sudo", "mkfs", "dd if="]
    for pattern in dangerous:
        if pattern in command:
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": f"Blocked: {pattern}"
                }
            }

    return {}  # Allow

options = ClaudeAgentOptions(
    allowed_tools=["Bash"],
    hooks={
        "PreToolUse": [
            HookMatcher(matcher="Bash", hooks=[validate_bash])
        ]
    }
)

async def main():
    async with ClaudeSDKClient(options=options) as client:
        # This will be blocked
        await client.query("Run: rm -rf /")
        async for msg in client.receive_response():
            print(msg)

asyncio.run(main)
```

---

## PostToolUse Hook

Review tool output and inject context:

```python
async def review_output(
    input_data: HookInput,
    tool_use_id: str | None,
    context: HookContext
) -> HookJSONOutput:
    """Add context when tool errors occur."""
    tool_response = input_data.get("tool_response", "")

    if "error" in str(tool_response).lower():
        return {
            "systemMessage": "The command produced an error.",
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": "Try a different approach."
            }
        }

    return {}

options = ClaudeAgentOptions(
    allowed_tools=["Bash"],
    hooks={
        "PostToolUse": [
            HookMatcher(matcher="Bash", hooks=[review_output])
        ]
    }
)
```

---

## Stop on Critical Error

Halt execution based on tool output:

```python
async def stop_on_critical(
    input_data: HookInput,
    tool_use_id: str | None,
    context: HookContext
) -> HookJSONOutput:
    """Stop if critical error detected."""
    tool_response = input_data.get("tool_response", "")

    if "critical" in str(tool_response).lower():
        return {
            "continue_": False,
            "stopReason": "Critical error - halting",
            "systemMessage": "Execution stopped due to critical error"
        }

    return {"continue_": True}

options = ClaudeAgentOptions(
    hooks={
        "PostToolUse": [
            HookMatcher(matcher=None, hooks=[stop_on_critical])  # All tools
        ]
    }
)
```

---

## HookMatcher

Match specific tools or all tools:

```python
from claude_agent_sdk import HookMatcher

# Match specific tool
HookMatcher(matcher="Bash", hooks=[my_hook])

# Match multiple tools (use separate matchers)
hooks={
    "PreToolUse": [
        HookMatcher(matcher="Bash", hooks=[bash_hook]),
        HookMatcher(matcher="Write", hooks=[write_hook]),
    ]
}

# Match all tools
HookMatcher(matcher=None, hooks=[universal_hook])
```

---

## Permission Callback

Fine-grained permission control with `can_use_tool`:

```python
from claude_agent_sdk import (
    ClaudeAgentOptions, ToolPermissionContext,
    PermissionResultAllow, PermissionResultDeny
)

async def permission_callback(
    tool_name: str,
    tool_input: dict,
    context: ToolPermissionContext
):
    """Custom permission logic."""

    # Block writes to config files
    if tool_name == "Write":
        path = tool_input.get("file_path", "")
        if "config" in path.lower() or ".env" in path:
            return PermissionResultDeny(
                behavior="deny",
                message="Cannot write to config files",
                interrupt=False
            )

    # Modify rm commands to add -i flag
    if tool_name == "Bash":
        command = tool_input.get("command", "")
        if command.startswith("rm "):
            return PermissionResultAllow(
                behavior="allow",
                updated_input={**tool_input, "command": f"{command} -i"}
            )

    # Allow everything else
    return PermissionResultAllow(behavior="allow")

options = ClaudeAgentOptions(
    allowed_tools=["Read", "Write", "Bash"],
    can_use_tool=permission_callback
)
```

---

## Hook Return Types

### PreToolUse Returns

```python
# Allow (default)
return {}

# Deny
return {
    "hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": "Reason here"
    }
}
```

### PostToolUse Returns

```python
# No action
return {}

# Add context
return {
    "systemMessage": "Message for Claude",
    "hookSpecificOutput": {
        "hookEventName": "PostToolUse",
        "additionalContext": "Extra info"
    }
}

# Stop execution
return {
    "continue_": False,
    "stopReason": "Why stopping",
    "systemMessage": "Message shown"
}
```

---

## Hook Function Signature

```python
async def my_hook(
    input_data: HookInput,      # Tool info and input
    tool_use_id: str | None,    # Tool invocation ID
    context: HookContext        # Additional context
) -> HookJSONOutput:
    ...
```

### HookInput Contents

```python
# PreToolUse
input_data["tool_name"]   # "Bash", "Write", etc.
input_data["tool_input"]  # Tool parameters

# PostToolUse
input_data["tool_name"]
input_data["tool_input"]
input_data["tool_response"]  # Tool output
```

---

## Common Patterns

### Logging All Tool Uses

```python
async def log_tool_use(input_data, tool_use_id, context):
    tool = input_data["tool_name"]
    print(f"Tool used: {tool}")
    return {}

options = ClaudeAgentOptions(
    hooks={
        "PostToolUse": [HookMatcher(matcher=None, hooks=[log_tool_use])]
    }
)
```

### Rate Limiting

```python
import time

last_call = {}
RATE_LIMIT_SECONDS = 1.0

async def rate_limit_hook(input_data, tool_use_id, context):
    tool = input_data["tool_name"]
    now = time.time()

    if tool in last_call and (now - last_call[tool]) < RATE_LIMIT_SECONDS:
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": "Rate limited"
            }
        }

    last_call[tool] = now
    return {}
```

### File Path Validation

```python
ALLOWED_DIRS = ["/project/src", "/project/tests"]

async def validate_paths(input_data, tool_use_id, context):
    tool = input_data["tool_name"]
    if tool not in ["Read", "Write", "Edit"]:
        return {}

    path = input_data["tool_input"].get("file_path", "")

    if not any(path.startswith(d) for d in ALLOWED_DIRS):
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": f"Path not allowed: {path}"
            }
        }

    return {}
```

---

## Gotchas

### 1. Matcher Must Match Tool Name
```python
# Wrong - tool name doesn't match
HookMatcher(matcher="bash", hooks=[...])  # lowercase

# Right
HookMatcher(matcher="Bash", hooks=[...])  # Exact match
```

### 2. Return Empty Dict to Allow
```python
# Wrong - returns None
async def hook(...):
    if not should_block:
        pass  # Implicit None

# Right
async def hook(...):
    if not should_block:
        return {}
```

### 3. Hooks Must Be Async
```python
# Wrong
def sync_hook(input_data, tool_use_id, context):
    return {}

# Right
async def async_hook(input_data, tool_use_id, context):
    return {}
```

---

## Context7 Topics

| Need | Topic |
|------|-------|
| PreToolUse | `PreToolUse hook validation` |
| PostToolUse | `PostToolUse hook review` |
| Permissions | `can_use_tool permission` |
| Stop execution | `stop continue hook` |

---

**Back to**: [SKILL.md](SKILL.md)
