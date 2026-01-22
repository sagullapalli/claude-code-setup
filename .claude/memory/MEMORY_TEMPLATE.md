# [Agent Name] - [Role]

Last updated: YYYY-MM-DD

## Active Protocols (Read Every Session)

### Skills-First Protocol
**MANDATORY**: Before ANY technical work (investigation, debugging, implementation, design):
1. Identify technology/domain relevant to your role
2. Check `.claude/skills/[technology]-patterns.md`
3. Search for relevant pattern (2 minutes)
4. Use documented pattern if found, OR proceed + document after verification

**Full protocol**: See CLAUDE.md

## Project Config
- **Project**: [Your Project Name]
- **GCP Project**: [To be configured]
- **Region**: europe-west1 (ALWAYS use Europe regions - CRITICAL)
- **Stack**: [Relevant stack components for this agent]
- **Repository**: /path/to/your-project

## Current Status

**Phase [X]**: [STATUS] (YYYY-MM-DD)
- [High-level summary of what's done]
- [What's pending or in progress]
- **Details**: [Link to detailed doc]

**Next Phase**: [Brief description]
- [Key milestones]
- **Plan**: [Link to implementation plan doc]

## [Section Specific to Agent Role]

For **Solution Architects**:
### Architecture Decisions (ADRs)
- Decision: [1-line what]
- Rationale: [1-2 lines why, key trade-off]
- Configuration: [Critical settings if applicable]
- Alternatives Rejected: [Brief list]
- **Full details**: [Link to doc]

For **Engineers** (Fullstack, Frontend, DevOps):
### Code Patterns
- **Pattern Name**: [Brief description]
- **Example**: [Short code snippet or file path]
- **When to use**: [1-line guidance]

### Critical Files & Commands
- **File/Command**: [Path or command]
- **Purpose**: [What it does]
- **Gotcha**: [Important note if any]

For **QA Testers**:
### Testing Patterns
- **Test Type**: [Unit/Integration/E2E]
- **Coverage**: [Current %]
- **Framework**: [Tool used]
- **Critical Tests**: [List of must-have tests]

## [Optional: Key Decisions / Patterns / Infrastructure]

[Agent-specific critical information that doesn't fit above]

## Lessons (Use STAR Format)

**For bugs, issues, and significant learnings, use STAR format**:

### [Bug/Issue Title] (Date)
**Situation**: [Context - what was the problem/scenario]
**Task**: [Goal - what needed to be accomplished]
**Action**: [Steps taken to resolve/implement]
**Result**: [Outcome and verification]
**Fix**: [File:line reference or specific change made]
**Pattern**: [Reusable lesson/gotcha for future work]
**Full details**: [Link to detailed doc in docs/ or docs/archive/]

**Example**:
```markdown
### Phase 2A Bug #2: Message History Empty (2025-12-03)
**Situation**: GET /sessions/{id}/messages returned 0 messages
**Task**: Fix chat history endpoint
**Action**: Manually append user + extend agent events before save
**Result**: All 6 messages retrieved, history working
**Fix**: agent_service.py:209-215
**Pattern**: ADK run_async() doesn't auto-persist events
**Full details**: [docs/archive/handoffs/SESSION_HANDOFF_BUGFIX.md]
```

### [General Lessons Category - e.g., Performance, Cost, Security]
- **[Brief lesson]**: [1-2 line insight]
- **[Brief lesson]**: [1-2 line insight]

## Documentation Map

| Topic | Document | What It Contains |
|-------|----------|------------------|
| **[Topic 1]** | [doc-name.md](docs/doc-name.md) | [1-line description of what's in this doc] |
| **[Topic 2]** | [doc-name.md](docs/doc-name.md) | [1-line description of what's in this doc] |
| **[Topic 3]** | [doc-name.md](docs/doc-name.md) | [1-line description of what's in this doc] |

**Usage Pattern**:
1. Read this memory for [role-specific] context refresh
2. Load specific doc for detailed [implementation/design/test] specs
3. Invoke skills for latest technical patterns when implementing
4. Update "Lessons" section with new discoveries

---

**Memory Guidelines:**
- Keep entries concise with bullet points
- Record specifics (paths, commands, project IDs, regions, decisions)
- Include key rationale (1-2 lines why) but link to docs for full details
- Focus on project-specific context, not general patterns (those go in skills)
- Update "Lessons" after every session with new discoveries
- Add pointers to new docs created during sessions
