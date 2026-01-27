#!/bin/bash
# Level 2.3: Environment Loader
# Trigger: SessionStart
#
# Sets up the development environment when a Claude Code session starts.
# Uses $CLAUDE_ENV_FILE to persist environment variables across the session.

# Source common environment files if they exist
[ -f ~/.bashrc ] && source ~/.bashrc 2>/dev/null || true
[ -f ~/.zshrc ] && source ~/.zshrc 2>/dev/null || true

# Read input to get session context
INPUT=$(cat)
SESSION_SOURCE=$(echo "$INPUT" | jq -r '.source // "startup"')

# Only run full setup on fresh startup, not resume/clear
if [ "$SESSION_SOURCE" != "startup" ]; then
    echo "Session resumed from: $SESSION_SOURCE"
    exit 0
fi

# Function to persist env vars
persist_env() {
    if [ -n "$CLAUDE_ENV_FILE" ]; then
        echo "export $1=\"$2\"" >> "$CLAUDE_ENV_FILE"
    fi
}

# ========================================
# Node.js Setup (for Frontend Engineer)
# ========================================
if [ -f ~/.nvm/nvm.sh ]; then
    source ~/.nvm/nvm.sh

    # Use project's .nvmrc if it exists, otherwise default to LTS
    if [ -f "$CLAUDE_PROJECT_DIR/.nvmrc" ]; then
        nvm use 2>/dev/null || nvm install
    else
        nvm use --lts 2>/dev/null || true
    fi

    # Persist Node path for the session
    if [ -n "$CLAUDE_ENV_FILE" ]; then
        echo "export PATH=\"$(dirname $(which node)):\$PATH\"" >> "$CLAUDE_ENV_FILE"
    fi
fi

# ========================================
# Python Setup (for AI Engineer)
# ========================================
# Activate virtual environment if it exists
VENV_PATHS=(
    "$CLAUDE_PROJECT_DIR/.venv"
    "$CLAUDE_PROJECT_DIR/venv"
    "$CLAUDE_PROJECT_DIR/.conda"
)

for venv in "${VENV_PATHS[@]}"; do
    if [ -f "$venv/bin/activate" ]; then
        source "$venv/bin/activate"
        persist_env "VIRTUAL_ENV" "$venv"
        persist_env "PATH" "$venv/bin:\$PATH"
        break
    fi
done

# Set Python-specific env vars
persist_env "PYTHONDONTWRITEBYTECODE" "1"
persist_env "PYTHONUNBUFFERED" "1"

# ========================================
# Project Context Output
# ========================================
# This output is added as context for Claude

echo "=== Development Environment Ready ==="
echo "Project: $(basename "$CLAUDE_PROJECT_DIR")"
echo "Directory: $CLAUDE_PROJECT_DIR"

# Detect project type and show relevant info
if [ -f "$CLAUDE_PROJECT_DIR/package.json" ]; then
    echo "Node.js: $(node --version 2>/dev/null || echo 'not found')"
    echo "npm: $(npm --version 2>/dev/null || echo 'not found')"
fi

if [ -f "$CLAUDE_PROJECT_DIR/pyproject.toml" ] || [ -f "$CLAUDE_PROJECT_DIR/requirements.txt" ]; then
    echo "Python: $(python --version 2>/dev/null || python3 --version 2>/dev/null || echo 'not found')"
    if [ -n "$VIRTUAL_ENV" ]; then
        echo "Venv: $VIRTUAL_ENV"
    fi
fi

# Git info
if [ -d "$CLAUDE_PROJECT_DIR/.git" ]; then
    BRANCH=$(git -C "$CLAUDE_PROJECT_DIR" branch --show-current 2>/dev/null)
    echo "Git Branch: $BRANCH"
fi

echo "===================================="

# ========================================
# Orchestrator Protocol Reminder (MANDATORY)
# ========================================
# This reminder ensures Ezio follows session start protocol

cat << 'ORCHESTRATOR_REMINDER'

⚠️ ORCHESTRATOR SESSION START PROTOCOL (MANDATORY)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

If you are Ezio (Main Orchestrator), BEFORE any work:

1. ✅ Read instructions: .claude/agents/orchestrator.md
2. 📖 Read memory: .claude/memory/memory-orchestrator.md
3. 💬 State: "Memory loaded: [brief summary of current status]"

THEN proceed with task handling using orchestrator protocol.

Reference: .claude/rules/orchestrator-protocol.md
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ORCHESTRATOR_REMINDER

exit 0