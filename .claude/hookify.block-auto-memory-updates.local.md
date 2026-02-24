---
name: block-auto-memory-updates
enabled: true
event: file
action: block
conditions:
  - field: file_path
    operator: regex_match
    pattern: memory/MEMORY\.md$
  - field: new_text
    operator: regex_match
    pattern: [\s\S]
---

**BLOCKED: Auto memory file is read-only.**

Do NOT update `/home/sunny/.claude/projects/-home-sunny-projects-lanestream/memory/MEMORY.md`.

This project uses a dedicated MCP memory system (`mcp__memory__write`, `mcp__memory__search`, etc.) for all persistent memory. The auto memory file is a static bootstrap file only.

**Instead of updating MEMORY.md, use:**
- `mcp__memory__write` to create new memory entries
- `mcp__memory__update` to update existing entries
- `.claude/memory/memory-orchestrator.md` for orchestrator-specific session context
