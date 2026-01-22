#!/usr/bin/env python3
"""
Level 4.5b: Inject Shared Context into User Prompts
Trigger: UserPromptSubmit

Completes the cross-agent context sharing loop by reading the shared context
file and injecting relevant context into the user prompt. This ensures all
agents have access to decisions, constraints, and insights from previous agents.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path


def get_input() -> dict:
    """Read and parse JSON input from stdin."""
    try:
        return json.load(sys.stdin)
    except json.JSONDecodeError:
        return {}


def get_context_file() -> Path:
    """Get path to shared context file."""
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
    return Path(project_dir) / ".claude" / "context" / "shared-context.json"


def load_contexts(current_session_id: str = None) -> list[dict]:
    """Load shared contexts, filtering out expired ones.

    Args:
        current_session_id: If provided, marks contexts from current session
    """
    context_file = get_context_file()
    if not context_file.exists():
        return []

    try:
        with open(context_file) as f:
            contexts = json.load(f)
    except (json.JSONDecodeError, IOError):
        return []

    # Filter expired contexts and mark current session
    now = datetime.now()
    valid = []
    for ctx in contexts:
        expires_at = ctx.get("expires_at")
        if expires_at:
            try:
                if datetime.fromisoformat(expires_at) < now:
                    continue
            except ValueError:
                pass

        # Mark if from current session
        ctx["is_current_session"] = (ctx.get("session_id") == current_session_id) if current_session_id else False
        valid.append(ctx)

    return valid


def format_context_for_injection(contexts: list[dict]) -> str:
    """Format contexts as a readable block for injection."""
    if not contexts:
        return ""

    # Separate current session and previous sessions
    current_session = [c for c in contexts if c.get("is_current_session")]
    previous_sessions = [c for c in contexts if not c.get("is_current_session")]

    # Group by category
    def group_by_category(ctx_list):
        by_cat = {}
        for ctx in ctx_list:
            cat = ctx.get("category", "other")
            if cat not in by_cat:
                by_cat[cat] = []
            by_cat[cat].append(ctx)
        return by_cat

    lines = ["<shared-agent-context>"]
    lines.append("The following context was shared by previous agents in this session:")
    lines.append("")

    category_icons = {
        "decision": "📋",
        "constraint": "⚠️",
        "pattern": "🔄",
        "warning": "🚨",
        "insight": "💡",
    }

    # Show current session context first (if any)
    if current_session:
        lines.append("=== Current Session ===")
        by_category = group_by_category(current_session)
        for category, items in by_category.items():
            icon = category_icons.get(category, "•")
            lines.append(f"{icon} {category.upper()}:")
            for item in items[-3:]:  # Last 3 per category
                agent = item.get("agent", "Unknown")
                content = item.get("content", "")
                lines.append(f"  - [{agent}]: {content}")
            lines.append("")

    # Show previous session context (if any)
    if previous_sessions:
        if current_session:
            lines.append("=== Previous Sessions ===")
        by_category = group_by_category(previous_sessions)
        for category, items in by_category.items():
            icon = category_icons.get(category, "•")
            lines.append(f"{icon} {category.upper()}:")
            for item in items[-3:]:  # Last 3 per category
                agent = item.get("agent", "Unknown")
                content = item.get("content", "")
                lines.append(f"  - [{agent}]: {content}")
            lines.append("")

    lines.append("</shared-agent-context>")
    return "\n".join(lines)


def main():
    # Get session_id from input
    input_data = get_input()
    session_id = input_data.get("session_id")

    # Load shared contexts with session awareness
    contexts = load_contexts(current_session_id=session_id)

    if not contexts:
        # No context to inject - allow prompt through unchanged
        sys.exit(0)

    # Format context for injection
    context_block = format_context_for_injection(contexts)

    # ==========================================================================
    # INJECTION METHOD: Plain stdout (current - visible in transcript)
    # ==========================================================================
    # This approach prints context directly, making it visible in the
    # conversation transcript (viewable with ctrl+r). Good for debugging.
    print(context_block)

    # ==========================================================================
    # INJECTION METHOD: JSON additionalContext (alternative - discrete/invisible)
    # ==========================================================================
    # Uncomment below and comment out the print() above to use discrete injection.
    # Context will be added to Claude's context without appearing in transcript.
    # More "production-ready" but harder to debug.
    #
    # output = {
    #     "hookSpecificOutput": {
    #         "hookEventName": "UserPromptSubmit",
    #         "additionalContext": context_block
    #     }
    # }
    # print(json.dumps(output))

    sys.exit(0)


if __name__ == "__main__":
    main()
