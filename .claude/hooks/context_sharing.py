#!/usr/bin/env python3
"""
Level 4.5: Cross-Agent Context Sharing
Trigger: PostToolUse with matcher "Task"

Maintains shared context between agents. When one agent discovers important
information (architecture decisions, gotchas, patterns), it's stored and
made available to subsequent agents.

This enables:
- AI Engineer learns about a performance constraint → Frontend Engineer sees it
- QA Tester identifies a bug pattern → DevOps knows to test for it
- Solution Architect makes a decision → All agents follow it

The context is stored in a JSON file and injected via UserPromptSubmit.
"""

import json
import os
import re
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


@dataclass
class SharedContext:
    """A piece of shared context between agents."""
    id: str
    agent: str
    category: str  # "decision", "constraint", "pattern", "warning", "insight"
    content: str
    timestamp: str
    session_id: Optional[str] = None  # Session that created this context
    expires_at: Optional[str] = None  # ISO format, None = never expires
    tags: list[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


# Patterns that indicate shareable context
CONTEXT_PATTERNS = {
    "decision": [
        r"decided to use",
        r"we('ll| will) go with",
        r"the approach is",
        r"architecture decision",
        r"design choice",
    ],
    "constraint": [
        r"must (not |never )?",
        r"cannot",
        r"limitation",
        r"constraint",
        r"required to",
        r"performance requirement",
    ],
    "pattern": [
        r"pattern (is|we use)",
        r"convention is",
        r"standard approach",
        r"best practice",
        r"always use",
    ],
    "warning": [
        r"gotcha",
        r"be careful",
        r"watch out",
        r"don't forget",
        r"common mistake",
        r"bug (in|with)",
    ],
    "insight": [
        r"learned that",
        r"discovered that",
        r"found out",
        r"realized",
        r"key insight",
    ],
}


def get_input() -> dict:
    """Read and parse JSON input from stdin."""
    try:
        return json.load(sys.stdin)
    except json.JSONDecodeError:
        return {}


def get_context_file() -> Path:
    """Get path to shared context file."""
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
    context_dir = Path(project_dir) / ".claude" / "context"
    context_dir.mkdir(parents=True, exist_ok=True)
    return context_dir / "shared-context.json"


def load_contexts() -> list[SharedContext]:
    """Load existing shared contexts."""
    context_file = get_context_file()
    if not context_file.exists():
        return []

    try:
        with open(context_file) as f:
            data = json.load(f)
            return [SharedContext(**item) for item in data]
    except (json.JSONDecodeError, TypeError):
        return []


def save_contexts(contexts: list[SharedContext]):
    """Save shared contexts."""
    context_file = get_context_file()

    # Remove expired contexts
    now = datetime.now()
    valid_contexts = []
    for ctx in contexts:
        if ctx.expires_at:
            try:
                expires = datetime.fromisoformat(ctx.expires_at)
                if expires < now:
                    continue
            except ValueError:
                pass
        valid_contexts.append(ctx)

    # Keep only last 50 contexts
    valid_contexts = valid_contexts[-50:]

    with open(context_file, "w") as f:
        json.dump([asdict(c) for c in valid_contexts], f, indent=2)


def detect_context_category(text: str) -> Optional[str]:
    """Detect if text contains shareable context and its category."""
    text_lower = text.lower()

    for category, patterns in CONTEXT_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text_lower):
                return category

    return None


def detect_all_context_categories(text: str) -> list[tuple[str, str]]:
    """Detect ALL shareable contexts in text, returning (category, matching_sentence) pairs."""
    results = []
    sentences = re.split(r'[.!?]\s+', text)

    for sentence in sentences:
        sentence_lower = sentence.lower().strip()
        if len(sentence_lower) < 20:  # Skip very short sentences
            continue

        for category, patterns in CONTEXT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, sentence_lower):
                    # Clean up the sentence
                    cleaned = sentence.strip()
                    if len(cleaned) > 200:
                        cleaned = cleaned[:200] + "..."
                    results.append((category, cleaned))
                    break  # Only one category per sentence
            else:
                continue
            break  # Found a match for this sentence, move to next

    return results


def extract_agent_output(input_data: dict) -> tuple[str, str]:
    """Extract agent name and output from Task result."""
    tool_input = input_data.get("tool_input", {})
    tool_result = input_data.get("tool_response", {})

    # Parse tool_input if it's a JSON string
    if isinstance(tool_input, str):
        try:
            tool_input = json.loads(tool_input)
        except json.JSONDecodeError:
            tool_input = {}

    # Parse tool_result if it's a JSON string
    if isinstance(tool_result, str):
        try:
            tool_result = json.loads(tool_result)
        except json.JSONDecodeError:
            tool_result = {}

    # Get agent type
    agent = tool_input.get("subagent_type", "unknown")

    # Map to friendly names
    agent_names = {
        "general-purpose": "General Agent",
        "Explore": "Code Explorer",
        "Plan": "Solution Architect",
        "claude-code-guide": "Documentation Guide",
    }
    agent = agent_names.get(agent, agent)

    # Get output - handle different response structures
    output = ""
    if isinstance(tool_result, dict):
        # Check for content field (Task tool uses this)
        content = tool_result.get("content", [])

        # Content is a list of message blocks like [{'type': 'text', 'text': '...'}]
        if isinstance(content, list):
            text_parts = []
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    text_parts.append(block.get("text", ""))
            output = "\n".join(text_parts)

        # Fallback: try other common keys
        if not output:
            for key in ["output", "result", "message", "text", "response"]:
                val = tool_result.get(key)
                if isinstance(val, str) and val:
                    output = val
                    break

    return agent, output


def extract_key_sentences(text: str, max_length: int = 200) -> str:
    """Extract the most relevant sentences from text."""
    sentences = re.split(r'[.!?]\s+', text)

    # Find sentences with context patterns
    relevant = []
    for sentence in sentences:
        if detect_context_category(sentence):
            # Clean up the sentence
            cleaned = sentence.strip()
            if len(cleaned) > 20:  # Skip very short sentences
                relevant.append(cleaned)

    if relevant:
        # Return first few relevant sentences
        result = ". ".join(relevant[:3])
        return result[:max_length] + "..." if len(result) > max_length else result

    return ""


def generate_context_id() -> str:
    """Generate a unique context ID."""
    import random
    import string
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=8))


def main():
    input_data = get_input()

    # Get session_id from input
    session_id = input_data.get("session_id")

    # Get agent output
    agent, output = extract_agent_output(input_data)

    if not output:
        sys.exit(0)

    # Detect ALL shareable contexts (multiple learnings)
    found_contexts = detect_all_context_categories(output)
    if not found_contexts:
        sys.exit(0)

    # Load existing contexts
    contexts = load_contexts()

    # Track what we add
    added = []
    now = datetime.now()

    for category, content in found_contexts:
        # Check for duplicate (similar content in last 10)
        is_duplicate = False
        for recent in contexts[-10:]:
            if recent.content[:50] == content[:50]:
                is_duplicate = True
                break

        if is_duplicate:
            continue

        # Create new context
        new_context = SharedContext(
            id=generate_context_id(),
            agent=agent,
            category=category,
            content=content,
            timestamp=now.isoformat(),
            session_id=session_id,
            # Decisions never expire, others expire in 24 hours
            expires_at=None if category == "decision" else (now + timedelta(hours=24)).isoformat(),
            tags=[],
        )

        contexts.append(new_context)
        added.append((category, content))

    if added:
        save_contexts(contexts)

        # Output notification for each added context
        for category, content in added:
            print(f"💡 Context shared [{category}]: {content[:80]}...")

    sys.exit(0)


if __name__ == "__main__":
    main()
