# Rule Template

Copy this file to `.claude/rules/your-rule-name.md` and customize.

**Important**: Rules are auto-loaded and enforced in EVERY session. Only create rules for behaviors that must ALWAYS apply.

---

```markdown
# [Rule Name] (Mandatory)

**Purpose**: [One sentence explaining why this rule exists]

---

## When This Rule Applies

This rule applies when:
- [Condition 1]
- [Condition 2]

This rule does NOT apply when:
- [Exception 1]
- [Exception 2]

---

## Requirements

### 1. [First Requirement]

[Explanation of what must be done]

**Example**:
```
[Good example]
```

### 2. [Second Requirement]

[Explanation of what must be done]

**Example**:
```
[Good example]
```

---

## Anti-Patterns (Avoid These)

### [Anti-Pattern Name]
**Wrong**:
```
[Example of what NOT to do]
```

**Right**:
```
[Example of correct behavior]
```

---

## Enforcement

How to verify compliance:
- [ ] [Checkpoint 1]
- [ ] [Checkpoint 2]

---

## Exceptions

The only exceptions to this rule are:
1. [Specific exception case]
2. [Another exception case]

When in doubt, follow the rule.

---

## Related Rules

- `[related-rule.md]`: [How they interact]
```

---

## Rule vs Skill Decision Guide

| Create a RULE when... | Create a SKILL when... |
|----------------------|------------------------|
| Behavior must ALWAYS apply | Pattern is domain-specific |
| Failure to follow causes problems | Following is optional/contextual |
| Applies to all agents | Applies to specific work types |
| Is a protocol/process | Is a technical pattern |

**Examples**:
- Compression protocol → RULE (always compress responses)
- React component patterns → SKILL (only when doing frontend)
- Memory updates → RULE (always update after sessions)
- Database query patterns → SKILL (only when doing backend)

---

## Checklist After Creating

- [ ] File saved to `.claude/rules/[rule-name].md`
- [ ] Purpose is clearly stated
- [ ] Requirements are specific and actionable
- [ ] Anti-patterns show wrong vs right
- [ ] Exceptions are explicitly listed
- [ ] Tested that rule is auto-loaded in new sessions
