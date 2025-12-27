# claude-code-best-setup-guide

A comprehensive guide to unlocking the full potential of Claude Code through skills, commands, hooks, MCP servers, subagents, and more.

---

## Table of Contents

1. [Skills: Beyond Markdown Files](#1-skills-beyond-markdown-files)
2. [Slash Commands](#2-slash-commands)
3. [Hooks: Deterministic Automation](#3-hooks-deterministic-automation)
4. [MCP Servers: External Integrations](#4-mcp-servers-external-integrations)
5. [Subagents: Specialized Assistants](#5-subagents-specialized-assistants)
6. [CLAUDE.md & Rules: Project Memory](#6-claudemd--rules-project-memory)
7. [Settings & Configuration](#7-settings--configuration)
8. [Plugins: Distribution & Reusability](#8-plugins-distribution--reusability)
9. [Recommended Setup Path](#9-recommended-setup-path)
10. [Example Project Structure](#10-example-project-structure)

---

## 1. Skills: Beyond Markdown Files

Skills are modular capabilities that extend Claude's functionality. They're **auto-invoked** based on context - Claude discovers and uses them automatically.

### Rich Skill Structure

```
my-skill/
├── SKILL.md                    # Required entry point
├── REFERENCE.md                # Optional documentation
├── EXAMPLES.md                 # Optional examples
├── scripts/
│   ├── helper.py               # Executable scripts
│   └── validate.sh
└── templates/
    └── template.txt
```

### Skill Frontmatter

```yaml
---
name: skill-name                # lowercase, alphanumeric, hyphens
description: When and why to use this skill  # Critical for discovery!
allowed-tools: Read, Grep, Glob # Optional - restricts tool access
---
```

### Skill Locations

| Location | Scope |
|----------|-------|
| `~/.claude/skills/skill-name/` | Personal (all projects) |
| `.claude/skills/skill-name/` | Project (team shared) |
| Plugin bundled | Distributed via plugins |

### Best Practices for Skill Discovery

- Make descriptions specific: "Analyze Excel files, create pivot tables, generate charts. Use when working with .xlsx files"
- Include trigger keywords users might mention
- Test with your team to ensure it activates when expected

### Example: PDF Processing Skill

```
pdf-processing/
├── SKILL.md
├── FORMS.md                 # Form-filling documentation
├── REFERENCE.md             # Detailed API reference
└── scripts/
    ├── fill_form.py
    └── validate.py
```

---

## 2. Slash Commands

Slash commands are **user-invoked** prompts stored as Markdown files. You explicitly type `/command-name` to trigger them.

### Command Locations

| Location | Scope |
|----------|-------|
| `.claude/commands/` | Project (shared via git) |
| `~/.claude/commands/` | Personal (all projects) |
| Plugin bundled | Namespaced: `/plugin-name:command` |

### Arguments

```markdown
# All arguments with $ARGUMENTS
Fix issue #$ARGUMENTS

# Individual arguments with $1, $2, etc.
Review PR #$1 with priority $2
```

### Bash Execution

```markdown
---
allowed-tools: Bash(git add:*), Bash(git status:*)
---

Current status: !`git status`
Recent commits: !`git log --oneline -10`

Create a commit based on these changes.
```

### File References

```markdown
Review the implementation in @src/utils/helpers.js
Compare @src/old-version.js with @src/new-version.js
```

### Full Frontmatter Options

```yaml
---
allowed-tools: Bash(git:*), Read, Edit
argument-hint: "[pr-number] [priority] [assignee]"
description: Review pull request
model: claude-3-5-haiku-20241022
disable-model-invocation: false
---
```

### Skills vs. Slash Commands

| Aspect | Slash Commands | Skills |
|--------|----------------|--------|
| Invocation | Explicit (`/command`) | Automatic (context-based) |
| Structure | Single .md file | Directory with supporting files |
| Best for | Quick prompts you use repeatedly | Complex workflows with multiple steps |
| Sharing | Via git or plugins | Via git or plugins |

---

## 3. Hooks: Deterministic Automation

Hooks are custom commands that execute automatically at specific lifecycle events.

### Available Hook Events

| Event | Purpose | When it fires |
|-------|---------|---------------|
| `PreToolUse` | Block or modify tool calls | Before any tool runs |
| `PostToolUse` | React to tool results, auto-format | After tool execution |
| `PermissionRequest` | Allow/deny permissions automatically | When permission is requested |
| `UserPromptSubmit` | Validate/enhance user prompts | When user submits input |
| `Notification` | Customize notification behavior | When Claude needs input |
| `Stop` | React when Claude finishes | After Claude's response |
| `SubagentStop` | React to subagent completion | When subagent finishes |
| `SessionStart` | Setup environment | Session initialization |
| `SessionEnd` | Cleanup | Session termination |
| `PreCompact` | Pre-compact actions | Before context compaction |

### Hook Configuration

Located in `.claude/settings.json` or `~/.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "echo 'Running bash command' >> /tmp/log.txt"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "npx prettier --write \"$file_path\""
          }
        ]
      }
    ]
  }
}
```

### Real-World Hook Examples

**Auto-format TypeScript after edits:**
```json
{
  "PostToolUse": [
    {
      "matcher": "Edit|Write",
      "hooks": [{
        "type": "command",
        "command": "jq -r '.tool_input.file_path' | { read fp; [[ $fp == *.ts ]] && npx prettier --write \"$fp\"; }"
      }]
    }
  ]
}
```

**File protection (block .env edits):**
```json
{
  "PreToolUse": [
    {
      "matcher": "Edit|Write",
      "hooks": [{
        "type": "command",
        "command": "python3 -c \"import json, sys; data=json.load(sys.stdin); path=data.get('tool_input',{}).get('file_path',''); sys.exit(2 if '.env' in path else 0)\""
      }]
    }
  ]
}
```

**Custom notifications:**
```json
{
  "Notification": [
    {
      "matcher": "",
      "hooks": [{
        "type": "command",
        "command": "notify-send 'Claude Code' 'Awaiting your input'"
      }]
    }
  ]
}
```

---

## 4. MCP Servers: External Integrations

MCP (Model Context Protocol) servers are external tools and data sources that Claude Code can connect to.

### What You Can Do

- Implement features from issue trackers automatically
- Query databases naturally
- Integrate with GitHub, Sentry, monitoring tools
- Access Slack, Figma, Notion, and hundreds of other services
- Build custom integrations for internal tools

### Installation Methods

**HTTP Servers (Recommended for cloud services):**
```bash
claude mcp add --transport http notion https://mcp.notion.com/mcp
claude mcp add --transport http sentry https://mcp.sentry.dev/mcp
claude mcp add --transport http github https://api.githubcopilot.com/mcp/
```

**Local Stdio Servers:**
```bash
# With environment variables
claude mcp add --transport stdio airtable \
  --env AIRTABLE_API_KEY=YOUR_KEY \
  -- npx -y airtable-mcp-server

# On Windows, use cmd /c wrapper
claude mcp add --transport stdio my-server -- cmd /c npx -y @some/package
```

**Authentication:**
```bash
# Many servers support OAuth 2.0
> /mcp
# Select "Authenticate" for the server
```

### MCP Configuration Scopes

| Scope | Location | Purpose |
|-------|----------|---------|
| Local | `~/.claude.json` (per-project) | Personal, project-specific |
| Project | `.mcp.json` in project root | Shared with team via git |
| User | `~/.claude.json` | Available across all projects |

### Project Scope Example (.mcp.json)

```json
{
  "mcpServers": {
    "shared-db": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@bytebase/dbhub"],
      "env": {
        "DATABASE_URL": "${DB_URL:-postgresql://localhost}"
      }
    }
  }
}
```

### Using MCP Features

**MCP as Slash Commands:**
```bash
/mcp__github__list_prs
/mcp__github__pr_review 456
/mcp__jira__create_issue "Bug in login" high
```

**MCP Resources (@ references):**
```bash
> Can you analyze @github:issue://123 and suggest a fix?
> Compare @postgres:schema://users with @docs:file://database/user-model
```

---

## 5. Subagents: Specialized Assistants

Subagents are specialized AI assistants that Claude Code delegates specific tasks to. Each has its own context window, custom system prompt, and configurable tools.

### Key Benefits

- **Context preservation**: Each subagent operates independently
- **Specialized expertise**: Fine-tuned for specific domains
- **Reusability**: Use across projects, share with teams
- **Flexible permissions**: Different tool access levels per agent

### Creating Subagents

**Via Interactive Menu (Recommended):**
```bash
/agents  # Opens interactive subagent manager
```

**File-Based (Manual):**

Create `~/.claude/agents/code-reviewer.md`:
```markdown
---
name: code-reviewer
description: Expert code reviewer. Proactively reviews code for quality and security.
tools: Read, Grep, Glob, Bash
model: inherit
---

You are a senior code reviewer ensuring high standards of code quality and security.

When invoked, run git diff to see recent changes, then review for:
- Code clarity and readability
- Security vulnerabilities
- Performance issues
- Test coverage
- Error handling
```

### Built-in Subagents

1. **General-purpose**: Complex multi-step tasks with full capabilities
2. **Plan subagent**: Research during plan mode
3. **Explore subagent**: Fast, read-only codebase exploration

### Subagent Configuration Fields

```yaml
---
name: agent-name
description: When and how Claude should use this agent
tools: Read, Edit, Bash, Grep  # Optional, inherits all if omitted
model: sonnet|opus|haiku|inherit  # Optional model selection
permissionMode: default|acceptEdits|bypassPermissions|plan|ignore
skills: skill-name1, skill-name2  # Auto-load skills
---
```

### Invocation

```bash
# Explicit invocation
> Use the code-reviewer subagent to check my recent changes

# Automatic invocation
> Review my code (Claude chooses appropriate subagent)
```

---

## 6. CLAUDE.md & Rules: Project Memory

CLAUDE.md files contain instructions, preferences, and context that Claude loads automatically.

### Memory Hierarchy (Highest to Lowest Priority)

| Level | Location | Scope | Purpose |
|-------|----------|-------|---------|
| Enterprise | System-wide managed file | All users | IT-enforced policies |
| Project | `./CLAUDE.md` or `./.claude/CLAUDE.md` | Team | Shared conventions |
| Project Rules | `./.claude/rules/*.md` | Team | Modular topic-specific rules |
| User | `~/.claude/CLAUDE.md` | Personal | Your preferences everywhere |
| Project Local | `./CLAUDE.local.md` | You only | Personal project preferences |

### Initialize Project Memory

```bash
/init    # Creates .claude/CLAUDE.md with codebase overview
/memory  # Edit CLAUDE.md files directly in your editor
```

### CLAUDE.md Content Best Practices

```markdown
# Project Architecture
- API layer in src/api/
- Component library in src/components/
- See @README for more

# Code Style
- 2-space indentation
- Use TypeScript strict mode
- Function comments for complex logic

# Common Commands
- `npm run dev` - Start dev server
- `npm run test` - Run tests
- `npm run lint` - Check style
```

### Modular Rules with .claude/rules/

```
.claude/
├── CLAUDE.md
└── rules/
    ├── code-style.md
    ├── testing.md
    ├── api-design.md
    ├── frontend/
    │   ├── react.md
    │   └── styling.md
    └── backend/
        └── database.md
```

### Path-Specific Rules

```yaml
---
paths: src/api/**/*.ts
---

# API Development Rules
- All endpoints must include input validation
- Use standard error response format
- Include OpenAPI documentation
```

### Importing Files

```markdown
See @README for project overview
Review git workflow: @docs/git-instructions.md
My personal setup: @~/.claude/my-project-instructions.md
```

---

## 7. Settings & Configuration

### Configuration Scopes (Priority Order)

1. **Enterprise** (highest) - System-wide policies
2. **Local** - Personal project overrides
3. **Project** - Team-shared settings
4. **User** - Personal defaults

### Core Settings (.claude/settings.json)

```json
{
  "permissions": {
    "allow": [
      "Bash(npm run lint)",
      "Bash(npm run test:*)",
      "Read(~/.zshrc)"
    ],
    "deny": [
      "Bash(curl:*)",
      "Read(./.env*)",
      "Read(./secrets/**)"
    ]
  },
  "env": {
    "NODE_ENV": "development"
  },
  "outputStyle": "Explanatory",
  "model": "claude-opus-4-5-20251101",
  "statusLine": {
    "type": "command",
    "command": "~/.claude/statusline.sh"
  },
  "hooks": {
    "PostToolUse": [{
      "matcher": "Edit|Write",
      "hooks": [{"type": "command", "command": "npx prettier --write"}]
    }]
  }
}
```

### Tool Permissions Available

- `Read` - File reading
- `Edit` - File editing
- `Write` - File creation
- `Bash` - Command execution
- `WebFetch` - URL fetching
- `WebSearch` - Web searching
- `SlashCommand` - Custom command execution

### Environment Variables for Power Users

```bash
# Increase context window
export CLAUDE_CODE_MAX_OUTPUT_TOKENS=8000

# Enable extended thinking
export MAX_THINKING_TOKENS=10000

# Configure MCP timeouts
export MCP_TIMEOUT=10000
export MAX_MCP_OUTPUT_TOKENS=50000

# Shell prefix for auditing
export CLAUDE_CODE_SHELL_PREFIX=/path/to/logger.sh
```

---

## 8. Plugins: Distribution & Reusability

### When to Use Plugins vs. Standalone

| Approach | Use When |
|----------|----------|
| Standalone (`.claude/`) | Personal, project-specific, short command names |
| Plugins | Sharing with team, distributing, versioned releases |

### Creating a Plugin

```
my-plugin/
├── .claude-plugin/
│   └── plugin.json
├── commands/
│   └── hello.md
├── agents/
│   └── code-reviewer.md
├── skills/
│   └── pdf-processing/
│       └── SKILL.md
├── .mcp.json
└── README.md
```

### Plugin Manifest (plugin.json)

```json
{
  "name": "my-plugin",
  "description": "Plugin description",
  "version": "1.0.0",
  "author": {
    "name": "Your Name"
  }
}
```

### Plugin Capabilities

- **Commands**: In `commands/` directory
- **Agents (Subagents)**: In `agents/` directory
- **Skills**: In `skills/` directory with SKILL.md
- **Hooks**: In `hooks/hooks.json`
- **MCP Servers**: In `.mcp.json`
- **LSP Servers**: In `.lsp.json` (for language support)

### Testing Locally

```bash
claude --plugin-dir ./my-plugin

# Test multiple plugins
claude --plugin-dir ./plugin-one --plugin-dir ./plugin-two
```

### Distribution

1. Create plugin marketplace (GitHub or git repository)
2. Publish marketplace
3. Add marketplace to project: `/plugin install-marketplace`
4. Install plugins: `/plugin install plugin-name`

---

## 9. Recommended Setup Path

| Phase | Action |
|-------|--------|
| **1. Foundation** | Run `/init` to create CLAUDE.md, set up `.claude/settings.json` with permissions |
| **2. Commands** | Create 3-5 slash commands for frequent tasks |
| **3. Automation** | Add hooks for auto-formatting, file protection |
| **4. Integration** | Add MCP servers (GitHub, DB, monitoring) |
| **5. Specialization** | Create subagents + multi-file skills |
| **6. Distribution** | Bundle as plugins for team sharing |

### Quick Start Checklist

- [ ] Run `/init` to initialize CLAUDE.md
- [ ] Configure `.claude/settings.json` with permissions
- [ ] Create 3-5 most-used slash commands
- [ ] Set up 2-3 key Skills (one per major workflow)
- [ ] Add 1-2 MCP servers for external integrations
- [ ] Create subagents for specialized tasks
- [ ] Configure hooks for auto-formatting
- [ ] Set up `.claude/rules/` for modular guidelines
- [ ] Test and iterate with team feedback
- [ ] Convert successful configs to plugins for sharing

---

## 10. Example Project Structure

```
your-project/
├── .claude/
│   ├── CLAUDE.md                    # Main memory
│   ├── settings.json                # Permissions & config
│   ├── settings.local.json          # Personal overrides (gitignored)
│   ├── commands/
│   │   ├── test-debug.md
│   │   ├── fix-issue.md
│   │   └── review.md
│   ├── skills/
│   │   ├── test-expert/
│   │   │   ├── SKILL.md
│   │   │   └── scripts/
│   │   └── db-explorer/
│   │       ├── SKILL.md
│   │       └── queries.sql
│   ├── agents/
│   │   ├── code-reviewer.md
│   │   ├── debugger.md
│   │   └── test-runner.md
│   ├── rules/
│   │   ├── code-style.md
│   │   ├── testing.md
│   │   └── api/
│   │       └── endpoints.md
│   └── hooks/
│       └── hooks.json
├── .mcp.json                        # Shared MCP servers
├── CLAUDE.local.md                  # Personal project notes (gitignored)
└── .gitignore                       # Include: .claude/settings.local.json, CLAUDE.local.md
```

---

## Summary

This setup transforms Claude Code from a basic coding assistant into a powerful development platform with:

- **Custom workflows** via skills and commands
- **Automated quality checks** via hooks
- **External integrations** via MCP servers
- **Specialized AI agents** via subagents
- **Team knowledge sharing** via plugins

Start with the foundation (CLAUDE.md + settings), then progressively add capabilities as needed.
