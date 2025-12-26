# Scout - General Worker

Last updated: 2025-12-26

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

### Agent File Locations (2025-12-26)
All agent files are in `.claude/agents/`:
- `ai-engineer.md` (Kai) - 579 lines
- `devops-engineer.md` (Devo) - 802 lines
- `solution-architect.md` (Sage) - 425 lines
- `frontend-engineer.md` (Iris) - 657 lines
- `qa-tester.md` (Vera) - 759 lines
- `frontend-qa-specialist.md` (Luna) - 633 lines
- `general-worker.md` (Scout) - 202 lines

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

### Phase 1: Memory Section Cleanup (2025-12-26)
**Situation**: Agent files had verbose memory sections (70-90 lines each) duplicating memory-protocol.md
**Task**: Replace with minimal 15-line template referencing the protocol
**Action**: Edited 7 agent files, replacing inline instructions with protocol reference
**Result**: ~75 lines removed per file (except Scout which gained ~7 lines for consistency)
**Pattern**: DRY principle - reference protocol files instead of duplicating instructions

### Phase 2: Skill Invocation Update (2025-12-26)
**Situation**: 3 agent files (Kai, Devo, Sage) used outdated `Skill(skill="...")` syntax
**Task**: Update to explain skills are auto-discovered, keep reference tables
**Action**: Edited skill sections in ai-engineer.md, devops-engineer.md, solution-architect.md
**Result**:
- Renamed "CRITICAL: Use Skills Before Implementation" to "Skills Discovery"
- Removed `Skill(skill="...")` syntax and "How to Invoke" sections
- Added "Trigger Keywords" column to tables
- Preserved task-to-skill mappings
**Pattern**: Skills are auto-loaded by Claude based on context keywords, not explicitly invoked

### Phase 4: Devo Content Migration (2025-12-26)
**Situation**: Devo's agent file (722 lines) had ~100+ lines of detailed IaC/CI/CD content duplicating deployment skills (2000+ lines across 6 files)
**Task**: Slim Devo's file by replacing detailed patterns with skill pointers while keeping high-level principles
**Action**: Edited devops-engineer.md:
- Consolidated Compute Options into table (lines 173-183) + skill pointer
- Consolidated CI/CD Pipeline Principles (lines 247-265) + skill pointer
- Slimmed Terraform section (lines 269-288) - removed file structure details, added skill pointer
- Consolidated Docker section into table (lines 292-303) + skill pointer
**Result**:
- File reduced from 722 to ~640 lines (~80 lines removed)
- 4 skill pointers added to deployment skills
- Preserved: Secrets Management, Database details, Security section, Error Handling, Checklists, Anti-patterns
**Pattern**: Keep high-level principles and decision tables in agent files; detailed code examples and step-by-step procedures belong in skill files

### Phase 5: Skills Discovery Alignment (Iris, Vera, Luna) (2025-12-26)
**Situation**: Iris, Vera, Luna had inconsistent skills sections compared to the new pattern (Kai, Devo, Sage)
**Task**: Update skills sections to match new "Skills Discovery" format with auto-discovery explanation and trigger keywords table
**Action**: Edited 3 agent files:
- `frontend-engineer.md:45-99`: Renamed header, added auto-discovery explanation, converted to new table format with trigger keywords
- `qa-tester.md:45-106`: Renamed header, removed outdated `INVOKE` syntax at line 86, consolidated resource sections, added trigger keywords table
- `frontend-qa-specialist.md:510-530`: Converted bullet list to full Skills Discovery section with table
**Result**:
- All 3 agents now match Kai's pattern
- Consistent headers: "Skills Discovery"
- Consistent table format: Task Type | Trigger Keywords | Related Skill
- Removed outdated syntax and consolidated verbose sections
**Pattern**: Skills Discovery sections should be concise with trigger keywords table + auto-discovery explanation

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
