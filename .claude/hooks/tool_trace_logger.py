#!/usr/bin/env python3
"""
Tool Trace Logger - PostToolUse Hook

Logs detailed tool usage data to `.claude/logs/tool-trace.jsonl`.
Captures MCP tool parsing, agent context, and tool-specific fields.

Trigger: PostToolUse (all tools)
Output: Appends JSON lines to tool-trace.jsonl

Features:
- MCP tool detection and parsing (mcp__<server>__<tool>)
- Agent context tracking (agent_name, subagent_type from Task tool)
- Tool-specific field extraction (file_path, command, pattern, etc.)
- Model tracking from hook input, Task input, or environment
- Long value truncation for manageable log entries
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


# Truncation limits for log fields
TRUNCATE_LIMITS = {
    "file_path": 150,
    "command": 150,
    "query": 150,
    "description": 100,
    "pattern": 100,
    "tool_input": 200,
    "tool_response": 200,
}

# Map subagent_type to agent nickname
AGENT_NAME_MAP = {
    "Main Orchestrator": "Ezio",
    "General Worker": "Scout",
    "Solution Architect": "Sage",
    "AI Engineer": "Kai",
    "Frontend Engineer": "Iris",
    "DevOps Engineer": "Devo",
    "QA Tester": "Vera",
    "Frontend QA Specialist": "Luna",
    # Lowercase variants for flexibility
    "general-purpose": "Scout",
    "Explore": "Scout",
}


def get_state_file() -> Path:
    """Get path to agent context state file."""
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
    return Path(project_dir) / ".claude" / "logs" / ".agent_context_state"


def get_active_tasks_file() -> Path:
    """Get path to active tasks state file (managed by task_context_tracker.py)."""
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
    return Path(project_dir) / ".claude" / "logs" / ".active_tasks.json"


def get_current_agent_context() -> dict:
    """
    Read current agent context from active tasks file.
    Returns dict with agent_name, model if available.
    """
    # First try the new active_tasks file (managed by task_context_tracker.py)
    active_tasks_file = get_active_tasks_file()
    try:
        if active_tasks_file.exists():
            with open(active_tasks_file, "r") as f:
                state = json.load(f)
                # Get the current running agent info
                current_agent = state.get("current_agent")

                # If there's an active task, get its details
                tasks = state.get("tasks", {})
                for task_id, task in tasks.items():
                    if task.get("status") == "running":
                        return {
                            "agent_name": task.get("agent_name"),
                            "model": task.get("model"),
                            "subagent_type": task.get("subagent_type"),
                        }

                # Return current agent if set
                if current_agent:
                    return {
                        "agent_name": current_agent,
                        "model": None,
                        "subagent_type": None,
                    }
    except (json.JSONDecodeError, IOError):
        pass

    # Fall back to legacy state file
    state_file = get_state_file()
    try:
        if state_file.exists():
            with open(state_file, "r") as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError):
        pass

    return {"agent_name": None, "model": None, "subagent_type": None}


def set_current_agent_context(agent_name: Optional[str]):
    """Write current agent context to state file."""
    state_file = get_state_file()
    try:
        state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(state_file, "w") as f:
            json.dump({"agent_name": agent_name}, f)
    except IOError:
        pass


def clear_agent_context():
    """Clear the agent context state file."""
    state_file = get_state_file()
    try:
        if state_file.exists():
            state_file.unlink()
    except IOError:
        pass


def get_agent_name(subagent_type: Optional[str]) -> Optional[str]:
    """Map subagent_type to agent nickname."""
    if not subagent_type:
        return None
    return AGENT_NAME_MAP.get(subagent_type, subagent_type)


def get_model_name() -> Optional[str]:
    """
    Get model name from environment variables.
    Checks multiple possible env vars used by Claude Code.
    """
    for var in ["ANTHROPIC_MODEL", "CLAUDE_MODEL", "MODEL"]:
        model = os.environ.get(var)
        if model:
            return model
    return None


def get_input() -> dict:
    """Read and parse JSON input from stdin. Handle malformed JSON gracefully."""
    try:
        return json.load(sys.stdin)
    except json.JSONDecodeError:
        return {}


def parse_json_field(value: Any) -> Any:
    """Parse a field that may be JSON string or already an object."""
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    return value


def truncate(value: Optional[str], limit: int) -> Optional[str]:
    """Truncate string to limit, adding ellipsis if truncated."""
    if value is None:
        return None
    if not isinstance(value, str):
        value = str(value)
    if len(value) <= limit:
        return value
    return value[:limit - 3] + "..."


def parse_mcp_tool(tool_name: str) -> dict:
    """
    Parse MCP tool name format: mcp__<server>__<tool>

    Returns:
        dict with is_mcp, mcp_server, mcp_tool

    Example:
        mcp__memory__create_entities -> server="memory", tool="create_entities"
    """
    if tool_name.startswith("mcp__"):
        parts = tool_name.split("__", 2)  # Split into max 3 parts
        if len(parts) >= 3:
            return {
                "is_mcp": True,
                "mcp_server": parts[1],
                "mcp_tool": parts[2],
            }
    return {
        "is_mcp": False,
        "mcp_server": None,
        "mcp_tool": None,
    }


def extract_nested(data: Any, *keys: str) -> Any:
    """
    Extract value from nested dict, trying multiple keys.

    Example:
        extract_nested(data, "file_path", "filePath")
        -> tries data["file_path"] then data["filePath"]
    """
    if not isinstance(data, dict):
        return None
    for key in keys:
        if key in data:
            return data[key]
    return None


def extract_tool_fields(tool_name: str, tool_input: Any, tool_response: Any) -> dict:
    """
    Extract tool-specific fields from input and response.

    Returns dict with:
        file_path, command, description, pattern, url, query, model,
        status, num_files, num_matches, http_code, bytes, has_stderr, interrupted
    """
    fields = {
        "file_path": None,
        "command": None,
        "description": None,
        "pattern": None,
        "url": None,
        "query": None,
        "model": None,
        "status": None,
        "num_files": None,
        "num_matches": None,
        "http_code": None,
        "bytes": None,
        "has_stderr": False,
        "interrupted": None,
    }

    # Parse inputs if they're JSON strings
    inp = parse_json_field(tool_input) if tool_input else {}
    resp = parse_json_field(tool_response) if tool_response else {}

    # Ensure we have dicts to work with
    if not isinstance(inp, dict):
        inp = {}
    if not isinstance(resp, dict):
        resp = {}

    # File path - common across Read, Write, Edit, Glob
    fields["file_path"] = truncate(
        extract_nested(inp, "file_path", "filePath", "path") or
        extract_nested(resp, "file_path", "filePath", "path"),
        TRUNCATE_LIMITS["file_path"]
    )

    # Bash-specific fields
    if tool_name == "Bash":
        fields["command"] = truncate(
            extract_nested(inp, "command", "cmd"),
            TRUNCATE_LIMITS["command"]
        )
        fields["description"] = truncate(
            extract_nested(inp, "description"),
            TRUNCATE_LIMITS["description"]
        )
        # Check for stderr in response
        stderr = extract_nested(resp, "stderr")
        fields["has_stderr"] = bool(stderr)

    # Pattern for Glob/Grep
    if tool_name in ("Glob", "Grep"):
        fields["pattern"] = truncate(
            extract_nested(inp, "pattern"),
            TRUNCATE_LIMITS["pattern"]
        )

    # URL for web tools
    if tool_name in ("WebFetch", "WebSearch"):
        fields["url"] = extract_nested(inp, "url")

    # Query for search tools
    if tool_name in ("WebSearch", "Grep"):
        fields["query"] = truncate(
            extract_nested(inp, "query"),
            TRUNCATE_LIMITS["query"]
        )

    # Model for Task tool
    if tool_name == "Task":
        fields["model"] = extract_nested(inp, "model")

    # Response fields - status, counts, web response data
    fields["status"] = extract_nested(resp, "status")
    fields["num_files"] = extract_nested(resp, "numFiles", "num_files", "file_count")
    fields["num_matches"] = extract_nested(resp, "numMatches", "num_matches", "match_count")
    fields["http_code"] = extract_nested(resp, "httpCode", "http_code", "status_code")
    fields["bytes"] = extract_nested(resp, "bytes", "content_length")
    fields["interrupted"] = extract_nested(resp, "interrupted")

    return fields


def extract_agent_context(tool_name: str, tool_input: Any, tool_response: Any) -> dict:
    """
    Extract agent context from Task tool calls or active tasks state.

    Returns dict with:
        subagent_type, agent_name, model
    """
    context = {
        "subagent_type": None,
        "agent_name": None,
        "model": None,
    }

    if tool_name != "Task":
        # For non-Task tools, try to get context from active tasks file
        stored_context = get_current_agent_context()
        context["agent_name"] = stored_context.get("agent_name")
        context["model"] = stored_context.get("model")
        context["subagent_type"] = stored_context.get("subagent_type")
        return context

    # Parse inputs if they're JSON strings
    inp = parse_json_field(tool_input) if tool_input else {}

    if isinstance(inp, dict):
        context["subagent_type"] = inp.get("subagent_type")
        context["agent_name"] = get_agent_name(context["subagent_type"])
        context["model"] = inp.get("model")

    return context


def serialize_for_log(value: Any, limit: int) -> Optional[str]:
    """
    Serialize value for logging, truncating to limit.
    Handles dicts, lists, and strings.
    """
    if value is None:
        return None

    if isinstance(value, str):
        return truncate(value, limit)

    try:
        serialized = json.dumps(value, ensure_ascii=False)
        return truncate(serialized, limit)
    except (TypeError, ValueError):
        return truncate(str(value), limit)


def create_log_entry(input_data: dict) -> dict:
    """
    Create the complete log entry from hook input data.
    """
    # Extract basic fields from input
    session_id = input_data.get("session_id", "")
    tool_use_id = input_data.get("tool_use_id", "")
    tool_name = input_data.get("tool_name", "")
    permission_mode = input_data.get("permission_mode", "")
    cwd = input_data.get("cwd", "")
    tool_input = input_data.get("tool_input")
    tool_response = input_data.get("tool_response")

    # Parse MCP tool info
    mcp_info = parse_mcp_tool(tool_name)

    # Extract agent context (for Task tool)
    agent_context = extract_agent_context(tool_name, tool_input, tool_response)

    # Extract tool-specific fields
    tool_fields = extract_tool_fields(tool_name, tool_input, tool_response)

    # Determine model: check multiple sources
    # 1. Direct from hook input_data (if Claude Code provides it)
    # 2. From Task tool input (for subagent spawns)
    # 3. From agent context state
    # 4. From environment variables
    model = (
        input_data.get("model") or
        tool_fields["model"] or
        agent_context.get("model") or
        get_model_name()
    )

    # Determine agent_name for this log entry
    # For Task: it's the spawned subagent
    # For non-Task: default to "Ezio" (orchestrator) unless state file says otherwise
    agent_name = agent_context.get("agent_name")
    if not agent_name and tool_name != "Task":
        agent_name = "Ezio"  # Default to orchestrator for direct tool calls

    # Build log entry (agent_id removed per user feedback)
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "session_id": session_id,
        "tool_use_id": tool_use_id,
        "tool_name": tool_name,
        "is_mcp": mcp_info["is_mcp"],
        "mcp_server": mcp_info["mcp_server"],
        "mcp_tool": mcp_info["mcp_tool"],
        "permission_mode": permission_mode,
        "cwd": cwd,
        "agent_name": agent_name,
        "subagent_type": agent_context["subagent_type"],
        "model": model,
        "file_path": tool_fields["file_path"],
        "command": tool_fields["command"],
        "description": tool_fields["description"],
        "pattern": tool_fields["pattern"],
        "url": tool_fields["url"],
        "query": tool_fields["query"],
        "status": tool_fields["status"],
        "num_files": tool_fields["num_files"],
        "num_matches": tool_fields["num_matches"],
        "http_code": tool_fields["http_code"],
        "bytes": tool_fields["bytes"],
        "has_stderr": tool_fields["has_stderr"],
        "interrupted": tool_fields["interrupted"],
        "tool_input": serialize_for_log(tool_input, TRUNCATE_LIMITS["tool_input"]),
        "tool_response": serialize_for_log(tool_response, TRUNCATE_LIMITS["tool_response"]),
    }

    return entry


def get_log_file() -> Path:
    """Get path to tool trace log file."""
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
    log_dir = Path(project_dir) / ".claude" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir / "tool-trace.jsonl"


def append_log_entry(entry: dict):
    """Append log entry to JSONL file."""
    log_file = get_log_file()
    try:
        with open(log_file, "a") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except IOError as e:
        # Don't crash the hook on write errors
        print(f"Warning: Failed to write tool trace: {e}", file=sys.stderr)


def main():
    """Main entry point for the hook."""
    # Read input from stdin
    input_data = get_input()

    # Skip if no input (malformed JSON)
    if not input_data:
        sys.exit(0)

    # Create log entry
    entry = create_log_entry(input_data)

    # Append to log file
    append_log_entry(entry)

    # Exit successfully (don't block the tool)
    sys.exit(0)


if __name__ == "__main__":
    main()
