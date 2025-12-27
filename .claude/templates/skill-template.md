# Skill Template

Copy this file to `.claude/skills/your-skill-name.md` (or create a subdirectory for complex skills).

---

## Simple Skill (Single File)

```markdown
---
name: [Skill Name]
description: [What patterns/knowledge this skill provides]
tags: [keyword1, keyword2, keyword3]
context7_libraries: ["/org/repo"]  # Optional: external docs to fetch
last_verified: YYYY-MM-DD
---

# [Skill Name]

## Overview

[2-3 sentences explaining what this skill covers and when to use it]

## When to Use

- [Scenario 1 where this skill applies]
- [Scenario 2 where this skill applies]

## Core Pattern

### [Pattern Name]

**Problem**: [What problem this solves]

**Solution**:
```[language]
# Code example here
```

**Key Points**:
- [Important detail 1]
- [Important detail 2]

## Common Gotchas

- **[Gotcha 1]**: [Explanation and how to avoid]
- **[Gotcha 2]**: [Explanation and how to avoid]

## Related Skills

- `[related-skill-1]`: [How it relates]
- `[related-skill-2]`: [How it relates]
```

---

## Complex Skill (Directory Structure)

For skills with multiple related patterns, create a directory:

```
.claude/skills/your-skill-domain/
├── SKILL.md           # Main entry point (required)
├── pattern-1.md       # Specific pattern
├── pattern-2.md       # Another pattern
└── examples/          # Optional: full examples
    └── example-1.md
```

### SKILL.md Template (Main Entry)

```markdown
---
name: [Domain Name]
description: [Comprehensive description of this skill domain]
tags: [keyword1, keyword2, keyword3, keyword4]
last_verified: YYYY-MM-DD
---

# [Domain Name] Patterns

## Overview

[Description of this skill domain]

## Patterns in This Domain

| Pattern | File | Use When |
|---------|------|----------|
| [Pattern 1] | `pattern-1.md` | [Scenario] |
| [Pattern 2] | `pattern-2.md` | [Scenario] |

## Quick Reference

### [Most Common Pattern]
```[language]
# Quick code snippet
```

## Getting Started

1. [First step for using these patterns]
2. [Second step]
```

---

## Skill Discovery Tips

Skills are auto-discovered by **keyword matching**. To ensure your skill is found:

1. **Tags**: Include all relevant keywords users might mention
2. **Name**: Use descriptive, searchable terms
3. **Description**: Include technology names and use cases

**Good tags example**:
```yaml
tags: [authentication, jwt, oauth, login, session, security, fastapi]
```

---

## Complexity Levels

| Level | Structure | When to Use |
|-------|-----------|-------------|
| **1** | Single file, <100 lines | One pattern, simple concept |
| **2** | Single file, 100-500 lines | Multiple related patterns |
| **3** | Directory with 3-7 files | Domain with distinct sub-patterns |
| **4** | Directory with 8+ files | Complex ecosystem (ADK, deployment) |

---

## Checklist After Creating

- [ ] File/directory created in `.claude/skills/`
- [ ] YAML frontmatter includes name, description, tags
- [ ] Code examples are tested and working
- [ ] Related skills are cross-referenced
- [ ] Tested discovery with keyword mentions
