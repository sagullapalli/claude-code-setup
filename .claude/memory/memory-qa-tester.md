# Vera - QA Tester

Last updated: 2025-12-24

## Active Protocols (Read Every Session)

### Skills-First Protocol
**MANDATORY**: Before ANY testing work:
1. Identify technology/domain (pytest, E2E, integration testing, etc.)
2. Check `.claude/skills/[technology]-patterns.md`
3. Search for relevant pattern (2 minutes)
4. Use documented pattern if found, OR investigate + document after verification

**Full protocol**: See CLAUDE.md

## Project Config
- **Project**: [Project Name]
- **GCP Project**: [To be configured]
- **Region**: europe-west1 (ALWAYS use Europe regions)
- **Stack**: [To be configured]
- **Repository**: /home/sunny/projects/interface

## Current Status

**Phase**: Active testing
- Tool trace logger tests created and passing (2025-12-26)

## Testing Architecture

### Hook Testing Pattern
- Test file location: `.claude/hooks/test_tool_trace_logger.py`
- Pattern: Direct Python assertions (pytest not available in system)
- Coverage: 64 test assertions across 6 test categories

## Testing Patterns

### Tool Trace Logger Testing (2025-12-26)
- **Test File**: `/home/sunny/projects/interface/.claude/hooks/test_tool_trace_logger.py`
- **Functions Tested**: `parse_mcp_tool`, `extract_agent_context`, `extract_tool_fields`, `truncate`, `parse_json_field`, `create_log_entry`
- **Results**: 64 assertions passing, 0 failures

**Pattern Format**:
- **Test Type**: [Unit/Integration/E2E]
- **Coverage**: [Current %]
- **Framework**: [Tool used]
- **Critical Tests**: [List of must-have tests]

## Critical Files & Commands

[To be documented as project develops]

## Lessons Learned

[No lessons recorded yet - use STAR format for bugs/issues]

## Documentation Map

| Topic | Document | What It Contains |
|-------|----------|------------------|
| [Topic] | [doc-path] | [Description] |

---

**Memory Guidelines:**
- Keep entries concise with bullet points
- Record specifics (paths, commands, project IDs, regions)
- Focus on project-specific context, not general patterns (those go in skills)
- Update after significant milestones or discoveries
