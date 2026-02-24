#!/usr/bin/env python3
"""
Agent Response Logger - PostToolUse Hook for Task Tool

Captures the full agent response from Task tool completions and writes it
to a human-readable markdown file. This provides:
  1. An audit trail of what each agent delivered
  2. A follow-along view for the user during long sessions
  3. Documentation of agent outputs for reference

Trigger: PostToolUse (Task tool only)
Output: Individual .md files in `.claude/logs/agent-responses/`

File naming: {YYYYMMDD_HHMMSS}_{agent}_{description-slug}.md
"""

import json
import os
import re
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
    "general-purpose": "Scout",
    "Explore": "Scout",
    "Plan": "Sage",
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
            pass
    return value


def get_output_dir() -> Path:
    """Get path to agent responses log directory."""
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
    output_dir = Path(project_dir) / ".claude" / "logs" / "agent-responses"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def slugify(text: str, max_length: int = 40) -> str:
    """Convert text to a filesystem-safe slug."""
    slug = text.lower().strip()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s-]+", "-", slug)
    slug = slug.strip("-")
    return slug[:max_length].rstrip("-")


def extract_agent_response(input_data: dict) -> tuple[str, str, str, str]:
    """
    Extract agent name, description, response text, and agent_id from Task result.

    Returns: (agent_name, description, response_text, agent_id)
    """
    tool_input = parse_json_field(input_data.get("tool_input", {}))
    tool_response = parse_json_field(input_data.get("tool_response", {}))

    if not isinstance(tool_input, dict):
        tool_input = {}
    if not isinstance(tool_response, dict):
        tool_response = {}

    # Agent info
    subagent_type = tool_input.get("subagent_type", "unknown")
    agent_name = AGENT_NAME_MAP.get(subagent_type, subagent_type)
    description = tool_input.get("description", "task")

    # Agent ID
    agent_id = tool_response.get("agent_id") or tool_response.get("agentId") or ""

    # Extract response text from content blocks
    response_text = ""
    content = tool_response.get("content", [])

    if isinstance(content, list):
        text_parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                text_parts.append(block.get("text", ""))
        response_text = "\n".join(text_parts)

    # Fallback: try other common response keys
    if not response_text:
        for key in ("output", "result", "message", "text", "response"):
            val = tool_response.get(key)
            if isinstance(val, str) and val:
                response_text = val
                break

    return agent_name, description, response_text, agent_id


def write_response_file(
    agent_name: str,
    description: str,
    response_text: str,
    agent_id: str,
    session_id: str,
    subagent_type: str,
    model: Optional[str],
) -> Optional[Path]:
    """Write the agent response to a markdown file."""
    if not response_text:
        return None

    now = datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    slug = slugify(description)

    filename = f"{timestamp}_{agent_name.lower()}_{slug}.md"
    filepath = get_output_dir() / filename

    # Build markdown content
    lines = [
        f"# {agent_name}: {description}",
        "",
        "| Field | Value |",
        "|-------|-------|",
        f"| Agent | {agent_name} ({subagent_type}) |",
        f"| Timestamp | {now.strftime('%Y-%m-%d %H:%M:%S')} |",
        f"| Session | `{session_id}` |",
        f"| Agent ID | `{agent_id}` |",
    ]

    if model:
        lines.append(f"| Model | {model} |")

    char_count = len(response_text)
    word_count = len(response_text.split())
    lines.extend([
        f"| Response size | {char_count:,} chars / ~{word_count} words |",
        "",
        "---",
        "",
        "## Response",
        "",
        response_text,
        "",
    ])

    try:
        filepath.write_text("\n".join(lines), encoding="utf-8")
        return filepath
    except IOError as e:
        print(f"Warning: Failed to write agent response: {e}", file=sys.stderr)
        return None


def main():
    input_data = get_input()
    if not input_data:
        sys.exit(0)

    session_id = input_data.get("session_id", "")

    # Extract agent response
    agent_name, description, response_text, agent_id = extract_agent_response(input_data)

    if not response_text:
        sys.exit(0)

    # Get additional metadata
    tool_input = parse_json_field(input_data.get("tool_input", {}))
    if not isinstance(tool_input, dict):
        tool_input = {}

    subagent_type = tool_input.get("subagent_type", "unknown")
    model = tool_input.get("model") or input_data.get("model")

    # Write response file
    filepath = write_response_file(
        agent_name=agent_name,
        description=description,
        response_text=response_text,
        agent_id=agent_id,
        session_id=session_id,
        subagent_type=subagent_type,
        model=model,
    )

    if filepath:
        # Output the file path so it appears in hook output
        project_dir = Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))
        relative = filepath.relative_to(project_dir)
        print(f"Agent response logged: {relative}")

    sys.exit(0)


if __name__ == "__main__":
    main()
