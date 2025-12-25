# Scout - General Worker

Last updated: 2025-12-25

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
- **Project**: Interface
- **Repository**: /home/sunny/projects/interface
- **Region**: europe-west1

## Current Status

**Phase**: Setup/Organization
- Claude configuration in progress
- Two-system architecture implemented (2025-12-25)

---

## Key Discoveries

[Record important codebase discoveries here]

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

[Use STAR format for significant learnings]

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
