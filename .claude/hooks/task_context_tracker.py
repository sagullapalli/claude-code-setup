#!/usr/bin/env python3
"""
Task Context Tracker - PreToolUse and PostToolUse Hook for Task Tool

Tracks subagent context when Task tool is used to spawn agents.
Works in tandem with tool_trace_logger.py to attribute tool calls to agents.

Trigger: PreToolUse and PostToolUse (Task tool only)
Output:
  - Writes context to `.claude/logs/.active_tasks.json` for real-time tracking
  - Appends to `.claude/logs/task-trace.jsonl` for historical record

Architecture:
  - PreToolUse: Captures subagent_type, agent_name, model BEFORE task runs
  - PostToolUse: Captures agent_id, status AFTER task completes
  - tool_trace_logger.py reads .active_tasks.json to attribute tool calls
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


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
    # Additional variants
    "general-purpose": "Scout",
    "Explore": "Scout",
}


def get_input() -> dict:
    """Read and parse JSON input from stdin."""
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


def get_log_dir() -> Path:
    """Get path to log directory."""
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
    log_dir = Path(project_dir) / ".claude" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def get_active_tasks_file() -> Path:
    """Get path to active tasks state file."""
    return get_log_dir() / ".active_tasks.json"


def get_task_trace_file() -> Path:
    """Get path to task trace log file."""
    return get_log_dir() / "task-trace.jsonl"


def load_active_tasks() -> dict:
    """Load active tasks from state file."""
    state_file = get_active_tasks_file()
    try:
        if state_file.exists():
            with open(state_file, "r") as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError):
        pass
    return {"tasks": {}, "current_agent": None, "current_agent_id": None}


def save_active_tasks(state: dict):
    """Save active tasks to state file."""
    state_file = get_active_tasks_file()
    try:
        with open(state_file, "w") as f:
            json.dump(state, f, indent=2)
    except IOError as e:
        print(f"Warning: Failed to save active tasks: {e}", file=sys.stderr)


def append_task_trace(entry: dict):
    """Append entry to task trace log."""
    log_file = get_task_trace_file()
    try:
        with open(log_file, "a") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except IOError as e:
        print(f"Warning: Failed to write task trace: {e}", file=sys.stderr)


def get_agent_name(subagent_type: Optional[str]) -> Optional[str]:
    """Map subagent_type to agent nickname."""
    if not subagent_type:
        return None
    return AGENT_NAME_MAP.get(subagent_type, subagent_type)


def get_model_name(tool_input: dict) -> Optional[str]:
    """Extract model from tool input or environment."""
    # First check tool input
    if tool_input.get("model"):
        return tool_input["model"]

    # Fall back to environment variables
    for var in ["ANTHROPIC_MODEL", "CLAUDE_MODEL", "MODEL"]:
        model = os.environ.get(var)
        if model:
            return model

    return None


def handle_pre_tool_use(input_data: dict):
    """
    Handle PreToolUse event for Task tool.
    Captures subagent context BEFORE the task runs.
    """
    tool_input = parse_json_field(input_data.get("tool_input", {}))
    if not isinstance(tool_input, dict):
        tool_input = {}

    session_id = input_data.get("session_id", "")
    tool_use_id = input_data.get("tool_use_id", "")

    # Extract agent info
    subagent_type = tool_input.get("subagent_type")
    agent_name = get_agent_name(subagent_type)
    model = get_model_name(tool_input)
    description = tool_input.get("description", "")
    prompt_preview = str(tool_input.get("prompt", ""))[:200]

    # Create task entry
    task_entry = {
        "tool_use_id": tool_use_id,
        "session_id": session_id,
        "subagent_type": subagent_type,
        "agent_name": agent_name,
        "model": model,
        "description": description,
        "prompt_preview": prompt_preview,
        "started_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "running",
        "agent_id": None,
        "completed_at": None,
    }

    # Update active tasks state
    state = load_active_tasks()
    state["tasks"][tool_use_id] = task_entry
    state["current_agent"] = agent_name
    state["current_agent_id"] = None
    save_active_tasks(state)

    # Append to task trace (started event)
    trace_entry = {
        "event": "task_started",
        "timestamp": task_entry["started_at"],
        **task_entry
    }
    append_task_trace(trace_entry)

    # Output nothing to not interfere with the tool
    sys.exit(0)


def handle_post_tool_use(input_data: dict):
    """
    Handle PostToolUse event for Task tool.
    Captures agent_id and status AFTER the task completes.
    """
    tool_input = parse_json_field(input_data.get("tool_input", {}))
    tool_response = parse_json_field(input_data.get("tool_response", {}))

    if not isinstance(tool_input, dict):
        tool_input = {}
    if not isinstance(tool_response, dict):
        tool_response = {}

    tool_use_id = input_data.get("tool_use_id", "")
    session_id = input_data.get("session_id", "")

    # Extract agent_id from response (try multiple locations)
    agent_id = None
    if isinstance(tool_response, dict):
        agent_id = (
            tool_response.get("agent_id") or
            tool_response.get("agentId")
        )

    # Extract status
    status = tool_response.get("status", "completed") if isinstance(tool_response, dict) else "completed"

    # Get agent info from input (in case PreToolUse didn't fire)
    subagent_type = tool_input.get("subagent_type")
    agent_name = get_agent_name(subagent_type)
    model = get_model_name(tool_input)

    # Update active tasks state
    state = load_active_tasks()

    if tool_use_id in state["tasks"]:
        # Update existing task
        state["tasks"][tool_use_id]["agent_id"] = agent_id
        state["tasks"][tool_use_id]["status"] = status
        state["tasks"][tool_use_id]["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    else:
        # Task wasn't tracked by PreToolUse, create entry now
        state["tasks"][tool_use_id] = {
            "tool_use_id": tool_use_id,
            "session_id": session_id,
            "subagent_type": subagent_type,
            "agent_name": agent_name,
            "model": model,
            "description": tool_input.get("description", ""),
            "prompt_preview": str(tool_input.get("prompt", ""))[:200],
            "started_at": None,
            "status": status,
            "agent_id": agent_id,
            "completed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    # Clear current agent if this was the active one
    if state.get("current_agent") == agent_name:
        state["current_agent"] = None
        state["current_agent_id"] = agent_id  # Keep last known ID

    save_active_tasks(state)

    # Append to task trace (completed event)
    task_data = state["tasks"].get(tool_use_id, {})
    trace_entry = {
        "event": "task_completed",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tool_use_id": tool_use_id,
        "session_id": session_id,
        "subagent_type": subagent_type,
        "agent_name": agent_name,
        "agent_id": agent_id,
        "model": model,
        "status": status,
        "started_at": task_data.get("started_at"),
        "completed_at": task_data.get("completed_at"),
    }
    append_task_trace(trace_entry)

    sys.exit(0)


def main():
    """Main entry point for the hook."""
    input_data = get_input()

    if not input_data:
        sys.exit(0)

    hook_event = input_data.get("hook_event_name", "")

    if hook_event == "PreToolUse":
        handle_pre_tool_use(input_data)
    elif hook_event == "PostToolUse":
        handle_post_tool_use(input_data)
    else:
        # Unknown event, exit silently
        sys.exit(0)


if __name__ == "__main__":
    main()
