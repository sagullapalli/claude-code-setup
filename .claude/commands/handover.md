Perform a session handover. Memory updates follow `.claude/rules/memory-protocol.md` — this command adds the handover document.

## 1. Update Memory (per memory protocol)
Update `.claude/memory/memory-orchestrator.md` with session accomplishments, decisions, and next steps.

## 2. Create Handover Document
Create `docs/archive/handoffs/SESSION_<N>_<SHORT_TITLE>_HANDOFF.md` with:
- **Header**: Date, session number, branch, status
- **What Was Accomplished**: Changes with file paths, line counts, test results
- **Recommended Next Session Plan**: Priority-ordered tasks with agent assignments
- **Design Decisions Still in Effect**: Active architectural decisions
- **Git State**: Branch, uncommitted changes, test status
- Make sure to include all the necessary context that would be needed to continue the work in the next session

## 3. Review User Context (per orchestrator.md Special Permissions)
Check if anything observed this session warrants updating `.claude/rules/user-context.md`:
- Skill level changes (e.g., "Learning" → "Intermediate+" after demonstrated competence)
- New tools, technologies, or domains being explored
- Workflow or collaboration preference shifts

**Rules**: Only update on clear patterns (not single data points), unless explicitly requested by user. Skip if nothing notable.

## 4. Confirm
Tell the user what was updated and summarize next session priorities.
