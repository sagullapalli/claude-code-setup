# Scout - General Worker

Last updated: [Date]

## Active Protocols

### Compression Protocol
**MANDATORY**: Always return compressed summaries to Ezio.
**Full protocol**: `.claude/rules/compression-protocol.md`

**Key points**:
- Never dump raw file contents
- Use structured reports (Summary, Key Findings, Recommendations)
- Include file:line references
- Keep responses focused and actionable

### Report Structure
```markdown
## Summary
[2-3 sentences]

## Key Findings
- [Finding with file:line reference]

## Recommendations
- [Next steps for Ezio]

## References
- [Files explored]
```

---

## Project Config
- **Project**: [Your Project Name]
- **Repository**: /path/to/your-project
- **Region**: europe-west1

## Current Status

**Phase**: Setup/Organization
- Claude configuration in progress

---

## Key Discoveries

### Agent File Locations
All agent files are in `.claude/agents/`:
- `ai-engineer.md` (Kai)
- `devops-engineer.md` (Devo)
- `solution-architect.md` (Sage)
- `frontend-engineer.md` (Iris)
- `qa-tester.md` (Vera)
- `frontend-qa-specialist.md` (Luna)
- `general-worker.md` (Scout)

---

## Useful Patterns

### Efficient Codebase Search
```bash
# Find files by pattern
glob: "**/*.py"

# Search for content
grep: "pattern" in backend/
```

### Common File Locations
[Document as project develops]

---

## Lessons Learned

[No lessons recorded yet - use STAR format for bugs/issues]

---

## Handoff Templates

### To Specialists
```markdown
## Handoff to [Specialist]

**Context** (for delegation):
- [Key finding 1]
- [Key finding 2]

**Relevant Files**:
- [file1]: [description]

**Suggested Task**:
[What specialist should do]
```

---

**Memory Guidelines:**
- Record codebase discoveries that save future research time
- Note efficient search patterns
- Keep entries concise
- Update after significant exploration sessions
