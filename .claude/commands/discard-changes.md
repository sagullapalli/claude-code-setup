# Discard All Changes Since Last Commit

Discard all uncommitted changes and return to a clean working state.

## Steps

1. Show current git status to see what will be affected
2. Discard all tracked file changes with `git checkout .`
3. Remove untracked files and directories with `git clean -fd`

## Execute

```bash
git status && git checkout . && git clean -fd && git status
```

Confirm before running: This will permanently discard all uncommitted changes.
