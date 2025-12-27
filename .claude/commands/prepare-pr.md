---
description: Review modified files and suggest branch name, commit message, and PR description
allowed-tools: Bash(git status:*), Bash(git diff:*), Bash(find:*), Bash(ls:*)
---

# Prepare PR

Review the git changes and provide suggestions for creating a pull request.

## Current State

Git status: !`git status --short`

Changed files: !`git diff --stat HEAD`

## Instructions

1. Analyze the changes shown above
2. If there are untracked directories, list their contents to understand what was added
3. Determine the scope and purpose of the work

## Provide the following:

### Branch Name
```
<prefix>/<descriptive-name>
```
- Prefixes: `feature/`, `fix/`, `refactor/`, `docs/`, `chore/`
- Use kebab-case, keep concise

### Commit Message (1 line)
```
<type>: <description under 72 chars>
```
- Types: feat, fix, docs, refactor, chore, test
- Use imperative mood ("Add" not "Added")

### PR Description
```markdown
## Summary
<2-3 bullet points>

## Changes
<Categorized list>

## Files Changed
<Grouped summary>

## Test Plan
- [ ] <verification steps>

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

Make the output copy-pasteable. Focus on "why" and "what", not "how".
