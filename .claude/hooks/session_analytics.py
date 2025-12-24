#!/usr/bin/env python3
"""
Level 4.4: Session Analytics
Trigger: SessionEnd

Comprehensive session analytics and reporting. When a Claude Code session ends,
this hook:
1. Analyzes the session transcript
2. Calculates metrics (files changed, commands run, etc.)
3. Generates a summary report
4. Optionally sends to a team dashboard

This helps you understand how your multi-agent team is performing.
"""

import json
import os
import sys
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass
class SessionMetrics:
    """Metrics collected from a session."""
    session_id: str = ""
    duration_seconds: int = 0
    files_created: list[str] = field(default_factory=list)
    files_modified: list[str] = field(default_factory=list)
    files_read: list[str] = field(default_factory=list)
    bash_commands: list[str] = field(default_factory=list)
    agents_used: Counter = field(default_factory=Counter)
    tools_used: Counter = field(default_factory=Counter)
    errors_encountered: list[str] = field(default_factory=list)
    user_prompts: int = 0
    assistant_messages: int = 0


def get_input() -> dict:
    """Read and parse JSON input from stdin."""
    try:
        return json.load(sys.stdin)
    except json.JSONDecodeError:
        return {}


def parse_transcript(transcript_path: str) -> SessionMetrics:
    """Parse the session transcript to extract metrics."""
    metrics = SessionMetrics()

    if not transcript_path or not Path(transcript_path).exists():
        return metrics

    try:
        with open(transcript_path, 'r') as f:
            first_timestamp = None
            last_timestamp = None

            for line in f:
                try:
                    entry = json.loads(line.strip())
                except json.JSONDecodeError:
                    continue

                # Track timestamps for duration
                if "timestamp" in entry:
                    ts = entry["timestamp"]
                    if first_timestamp is None:
                        first_timestamp = ts
                    last_timestamp = ts

                # Track message types
                msg_type = entry.get("type", "")
                if msg_type == "human":
                    metrics.user_prompts += 1
                elif msg_type == "assistant":
                    metrics.assistant_messages += 1

                # Track tool usage
                if "tool_name" in entry:
                    tool_name = entry["tool_name"]
                    metrics.tools_used[tool_name] += 1

                    tool_input = entry.get("tool_input", {})

                    # File operations
                    if tool_name == "Write":
                        path = tool_input.get("file_path", "")
                        if path:
                            metrics.files_created.append(path)
                    elif tool_name == "Edit":
                        path = tool_input.get("file_path", "")
                        if path:
                            metrics.files_modified.append(path)
                    elif tool_name == "Read":
                        path = tool_input.get("file_path", "")
                        if path:
                            metrics.files_read.append(path)
                    elif tool_name == "Bash":
                        cmd = tool_input.get("command", "")
                        if cmd:
                            metrics.bash_commands.append(cmd[:100])
                    elif tool_name == "Task":
                        agent = tool_input.get("subagent_type", "unknown")
                        metrics.agents_used[agent] += 1

                # Track errors
                if entry.get("is_error"):
                    error_msg = str(entry.get("content", ""))[:100]
                    metrics.errors_encountered.append(error_msg)

            # Calculate duration (simplified - assumes ISO format)
            if first_timestamp and last_timestamp:
                try:
                    # Try parsing common formats
                    for fmt in ["%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"]:
                        try:
                            start = datetime.strptime(first_timestamp[:19], fmt[:len(first_timestamp[:19])])
                            end = datetime.strptime(last_timestamp[:19], fmt[:len(last_timestamp[:19])])
                            metrics.duration_seconds = int((end - start).total_seconds())
                            break
                        except ValueError:
                            continue
                except Exception:
                    pass

    except IOError:
        pass

    return metrics


def generate_report(metrics: SessionMetrics) -> str:
    """Generate a human-readable session report."""
    lines = [
        "═" * 50,
        "           SESSION ANALYTICS REPORT",
        "═" * 50,
        "",
        f"📊 Session Duration: {metrics.duration_seconds // 60}m {metrics.duration_seconds % 60}s",
        f"💬 User Prompts: {metrics.user_prompts}",
        f"🤖 Assistant Responses: {metrics.assistant_messages}",
        "",
    ]

    # File operations
    if metrics.files_created or metrics.files_modified:
        lines.append("📁 FILE OPERATIONS")
        lines.append("-" * 30)
        if metrics.files_created:
            lines.append(f"   Created: {len(metrics.files_created)} files")
            for f in metrics.files_created[:5]:
                lines.append(f"     • {Path(f).name}")
            if len(metrics.files_created) > 5:
                lines.append(f"     ... and {len(metrics.files_created) - 5} more")
        if metrics.files_modified:
            lines.append(f"   Modified: {len(metrics.files_modified)} files")
            for f in metrics.files_modified[:5]:
                lines.append(f"     • {Path(f).name}")
            if len(metrics.files_modified) > 5:
                lines.append(f"     ... and {len(metrics.files_modified) - 5} more")
        lines.append("")

    # Agent usage
    if metrics.agents_used:
        lines.append("🤖 AGENT UTILIZATION")
        lines.append("-" * 30)
        for agent, count in metrics.agents_used.most_common():
            lines.append(f"   {agent}: {count} tasks")
        lines.append("")

    # Tool usage
    if metrics.tools_used:
        lines.append("🔧 TOOL USAGE")
        lines.append("-" * 30)
        for tool, count in metrics.tools_used.most_common(5):
            lines.append(f"   {tool}: {count} calls")
        lines.append("")

    # Bash commands
    if metrics.bash_commands:
        lines.append(f"⌨️  BASH COMMANDS: {len(metrics.bash_commands)} total")
        lines.append("-" * 30)
        # Show unique commands
        unique_cmds = list(set(cmd.split()[0] if cmd.split() else cmd for cmd in metrics.bash_commands))
        lines.append(f"   Types: {', '.join(unique_cmds[:10])}")
        lines.append("")

    # Errors
    if metrics.errors_encountered:
        lines.append(f"⚠️  ERRORS: {len(metrics.errors_encountered)}")
        lines.append("-" * 30)
        for error in metrics.errors_encountered[:3]:
            lines.append(f"   • {error[:60]}...")
        lines.append("")

    lines.append("═" * 50)
    lines.append(f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("═" * 50)

    return "\n".join(lines)


def save_analytics(metrics: SessionMetrics, report: str):
    """Save analytics to log file."""
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
    log_dir = Path(project_dir) / ".claude" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    # Save JSON metrics
    metrics_file = log_dir / "session-metrics.jsonl"
    metrics_dict = {
        "timestamp": datetime.now().isoformat(),
        "session_id": metrics.session_id,
        "duration_seconds": metrics.duration_seconds,
        "files_created_count": len(metrics.files_created),
        "files_modified_count": len(metrics.files_modified),
        "bash_commands_count": len(metrics.bash_commands),
        "agents_used": dict(metrics.agents_used),
        "tools_used": dict(metrics.tools_used),
        "errors_count": len(metrics.errors_encountered),
        "user_prompts": metrics.user_prompts,
    }

    with open(metrics_file, "a") as f:
        f.write(json.dumps(metrics_dict) + "\n")

    # Save latest report
    report_file = log_dir / "latest-session-report.txt"
    with open(report_file, "w") as f:
        f.write(report)


def main():
    input_data = get_input()

    # Get transcript path
    transcript_path = input_data.get("transcript_path", "")
    session_id = input_data.get("session_id", "unknown")

    # Parse transcript and collect metrics
    metrics = parse_transcript(transcript_path)
    metrics.session_id = session_id

    # Generate report
    report = generate_report(metrics)

    # Save analytics
    save_analytics(metrics, report)

    # Output report (shown to user)
    print(report)

    sys.exit(0)


if __name__ == "__main__":
    main()
