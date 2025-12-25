# Compression Protocol (Mandatory for All Agents)

**CRITICAL**: When returning results to Ezio (Main Orchestrator), you MUST compress your findings.

## The Principle

> "The essence of search is compression: distilling insights from a vast corpus."
> — Anthropic Multi-Agent Research

Ezio's context window is precious. Your job is to **transform noise into signal**.

---

## Compression Requirements

### 1. Never Dump Raw Data

**Wrong**:
```
Here are the contents of the file:
[500 lines of code]
```

**Right**:
```
## Summary
The auth module uses JWT tokens with 15-minute expiry.

## Key Findings
- Token generation: `auth_service.py:45-67`
- Validation middleware: `auth_middleware.py:23-40`
- Refresh logic: `auth_service.py:89-120`

## Recommendation
Kai should review the refresh logic for the new requirement.
```

### 2. Use Structured Reports

Always format your response:

```markdown
## Summary
[2-3 sentences: What did you find? What's the answer?]

## Key Findings
- [Finding 1 with file:line reference]
- [Finding 2 with file:line reference]
- [Finding 3 with file:line reference]

## Recommendations
- [What should happen next?]
- [Who should be engaged?]

## References
- [Files explored, for context]
```

### 3. Include References, Not Content

**Wrong**: Pasting code blocks
**Right**: `auth_service.py:45-67 handles token generation`

### 4. Quantify When Possible

- "Found 3 files" not "found some files"
- "12 tests passing, 2 failing" not "most tests pass"
- "~500 lines of code" not "a large file"

---

## Response Length Guidelines

| Task Type | Target Length |
|-----------|---------------|
| Simple lookup | 50-100 words |
| Research/exploration | 200-400 words |
| Complex analysis | 400-600 words |
| Architecture review | 500-800 words |

**Exception**: If Ezio explicitly requests detailed output, provide it.

---

## What to Include

### Always Include
- Direct answer to the question asked
- File:line references for key findings
- Clear recommendation for next steps
- Confidence level if uncertain

### Include If Relevant
- Trade-offs discovered
- Risks or concerns identified
- Related findings that may be useful
- Dependencies or blockers

### Never Include
- Full file contents (unless explicitly requested)
- Lengthy code blocks (use references)
- Tangential information
- Speculation without evidence

---

## Handoff Compression

When recommending handoff to another agent, compress context:

```markdown
## Handoff to [Agent Name]

**Context** (for their delegation prompt):
- [Key fact 1]
- [Key fact 2]
- [Relevant files: list with descriptions]

**Suggested Task**:
[Clear, specific task description]

**Constraints**:
- [Any limitations discovered]
```

This helps Ezio craft effective delegation prompts without re-researching.

---

## Examples by Agent

### Scout (General Worker)
```
## Summary
The codebase uses a service-repository pattern. Found 8 services
and 6 repositories in backend/services/ and backend/repositories/.

## Key Findings
- Services handle business logic: `backend/services/*.py`
- Repositories handle DB access: `backend/repositories/*.py`
- Dependency injection via FastAPI Depends: `backend/dependencies.py:12-45`

## Recommendations
- Sage should confirm this pattern for new features
- Kai should follow this pattern for implementation

## References
- Explored: backend/services/, backend/repositories/, backend/main.py
```

### Sage (Solution Architect)
```
## Summary
Recommend Option B: Cloud Run with managed Redis for caching.

## Key Findings
- Option A (Cloud Functions): Cheaper but cold start issues
- Option B (Cloud Run): Better latency, simpler deployment
- Option C (GKE): Overkill for current scale

## Trade-offs
- Option B costs ~$50/month more than A
- Option B provides <100ms response times vs 500ms+ for A

## Recommendation
Proceed with Option B. Kai should implement the caching layer.
ADR drafted: Ezio to review before implementation.
```

### Kai (AI Engineer)
```
## Summary
Implemented user authentication endpoint with JWT tokens.

## Key Changes
- New file: `backend/services/auth_service.py` (120 lines)
- New file: `backend/routers/auth.py` (45 lines)
- Modified: `backend/main.py:34` (added router)

## Tests
- 8 unit tests added: `backend/tests/test_auth.py`
- All passing, 94% coverage on new code

## Next Steps
- Vera should add integration tests
- Iris can now implement login UI
```

---

## Remember

Every token you save in Ezio's context is a token available for strategic thinking.

*Compress ruthlessly. Reference precisely. Recommend clearly.*
