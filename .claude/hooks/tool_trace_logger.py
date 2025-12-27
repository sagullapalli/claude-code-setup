#!/usr/bin/env python3
"""
Tool Trace Logger - PostToolUse Hook

Logs detailed tool usage data to `.claude/logs/tool-trace.jsonl`.
Captures MCP tool parsing, agent context, and tool-specific fields.

Trigger: PostToolUse (all tools)
Output: Appends JSON lines to tool-trace.jsonl
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
    "general-purpose": "Scout",
    "Explore": "Scout",
}

# Declarative tool field extraction map
# Format: tool_name -> [(field_name, limit_key, [input_keys...], [response_keys...])]
TOOL_FIELD_MAP = {
    "Bash": [
        ("command", "command", ["command", "cmd"], []),
        ("description", "description", ["description"], []),
    ],
    "Glob": [("pattern", "pattern", ["pattern"], [])],
    "Grep": [
        ("pattern", "pattern", ["pattern"], []),
        ("query", "query", ["query"], []),
    ],
    "WebFetch": [("url", None, ["url"], [])],
    "WebSearch": [
        ("url", None, ["url"], []),
        ("query", "query", ["query"], []),
    ],
    "Task": [("model", None, ["model"], [])],
}


def get_project_dir() -> Path:
    """Get project directory from env or cwd."""
    return Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))


def get_current_agent_context() -> dict:
    """Read current agent context from active tasks file."""
    active_tasks_file = get_project_dir() / ".claude" / "logs" / ".active_tasks.json"
    try:
        if active_tasks_file.exists():
            state = json.loads(active_tasks_file.read_text())
            # Check for running tasks first
            for task in state.get("tasks", {}).values():
                if task.get("status") == "running":
                    return {
                        "agent_name": task.get("agent_name"),
                        "model": task.get("model"),
                        "subagent_type": task.get("subagent_type"),
                    }
            # Fall back to current_agent
            if current := state.get("current_agent"):
                return {"agent_name": current, "model": None, "subagent_type": None}
    except (json.JSONDecodeError, IOError):
        pass
    return {"agent_name": None, "model": None, "subagent_type": None}


def truncate(value: Any, limit: int) -> Optional[str]:
    """Truncate value to limit, adding ellipsis if truncated."""
    if value is None:
        return None
    s = str(value) if not isinstance(value, str) else value
    return s if len(s) <= limit else s[: limit - 3] + "..."


def parse_json_field(value: Any) -> Any:
    """Parse a field that may be JSON string or already an object."""
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            pass
    return value


def extract_nested(data: dict, *keys: str) -> Any:
    """Extract value from dict, trying multiple keys."""
    if not isinstance(data, dict):
        return None
    for key in keys:
        if key in data:
            return data[key]
    return None


def get_truncated(data: dict, limit_key: Optional[str], *keys: str) -> Optional[str]:
    """Extract and truncate a field from data."""
    value = extract_nested(data, *keys)
    if value is None or limit_key is None:
        return value
    return truncate(value, TRUNCATE_LIMITS.get(limit_key, 100))


def parse_mcp_tool(tool_name: str) -> tuple[bool, Optional[str], Optional[str]]:
    """Parse MCP tool name format: mcp__<server>__<tool>."""
    if tool_name.startswith("mcp__"):
        parts = tool_name.split("__", 2)
        if len(parts) >= 3:
            return True, parts[1], parts[2]
    return False, None, None


def extract_tool_fields(tool_name: str, inp: dict, resp: dict) -> dict:
    """Extract tool-specific fields using declarative mapping."""
    fields = {
        "file_path": get_truncated(inp, "file_path", "file_path", "filePath", "path")
        or get_truncated(resp, "file_path", "file_path", "filePath", "path"),
        "command": None,
        "description": None,
        "pattern": None,
        "url": None,
        "query": None,
        "model": None,
        "status": extract_nested(resp, "status"),
        "num_files": extract_nested(resp, "numFiles", "num_files", "file_count"),
        "num_matches": extract_nested(resp, "numMatches", "num_matches", "match_count"),
        "http_code": extract_nested(resp, "httpCode", "http_code", "status_code"),
        "bytes": extract_nested(resp, "bytes", "content_length"),
        "has_stderr": bool(extract_nested(resp, "stderr")),
        "interrupted": extract_nested(resp, "interrupted"),
    }

    # Apply tool-specific field mappings
    for field_name, limit_key, inp_keys, resp_keys in TOOL_FIELD_MAP.get(tool_name, []):
        value = None
        if inp_keys:
            value = get_truncated(inp, limit_key, *inp_keys)
        if value is None and resp_keys:
            value = get_truncated(resp, limit_key, *resp_keys)
        fields[field_name] = value

    return fields


def serialize_for_log(value: Any, limit: int) -> Optional[str]:
    """Serialize value for logging, truncating to limit."""
    if value is None:
        return None
    if isinstance(value, str):
        return truncate(value, limit)
    try:
        return truncate(json.dumps(value, ensure_ascii=False), limit)
    except (TypeError, ValueError):
        return truncate(str(value), limit)


def create_log_entry(data: dict) -> dict:
    """Create the complete log entry from hook input data."""
    tool_name = data.get("tool_name", "")
    tool_input = parse_json_field(data.get("tool_input"))
    tool_response = parse_json_field(data.get("tool_response"))

    inp = tool_input if isinstance(tool_input, dict) else {}
    resp = tool_response if isinstance(tool_response, dict) else {}

    # Parse MCP tool info
    is_mcp, mcp_server, mcp_tool = parse_mcp_tool(tool_name)

    # Extract agent context
    if tool_name == "Task":
        subagent_type = inp.get("subagent_type")
        agent_name = AGENT_NAME_MAP.get(subagent_type, subagent_type)
        agent_model = inp.get("model")
    else:
        ctx = get_current_agent_context()
        subagent_type = ctx.get("subagent_type")
        agent_name = ctx.get("agent_name") or "Ezio"
        agent_model = ctx.get("model")

    # Determine model from multiple sources
    model = (
        data.get("model")
        or agent_model
        or os.environ.get("ANTHROPIC_MODEL")
        or os.environ.get("CLAUDE_MODEL")
        or os.environ.get("MODEL")
    )

    # Extract tool-specific fields
    fields = extract_tool_fields(tool_name, inp, resp)

    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "session_id": data.get("session_id", ""),
        "tool_use_id": data.get("tool_use_id", ""),
        "tool_name": tool_name,
        "is_mcp": is_mcp,
        "mcp_server": mcp_server,
        "mcp_tool": mcp_tool,
        "permission_mode": data.get("permission_mode", ""),
        "cwd": data.get("cwd", ""),
        "agent_name": agent_name,
        "subagent_type": subagent_type,
        "model": model,
        **fields,
        "tool_input": serialize_for_log(tool_input, TRUNCATE_LIMITS["tool_input"]),
        "tool_response": serialize_for_log(tool_response, TRUNCATE_LIMITS["tool_response"]),
    }


def main():
    """Main entry point for the hook."""
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    if not data:
        sys.exit(0)

    entry = create_log_entry(data)

    # Write to log file
    log_file = get_project_dir() / ".claude" / "logs" / "tool-trace.jsonl"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(log_file, "a") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except IOError as e:
        print(f"Warning: Failed to write tool trace: {e}", file=sys.stderr)

    sys.exit(0)


if __name__ == "__main__":
    main()
