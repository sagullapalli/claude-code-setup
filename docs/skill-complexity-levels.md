# Claude Code Skills: Four Levels of Complexity

> A comprehensive guide to building skills from simple single-file references to self-evolving learning systems.

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Reference](#quick-reference)
3. [Level 1: Single-File Skills](#level-1-single-file-skills)
4. [Level 2: Multi-File Skills with Resources](#level-2-multi-file-skills-with-resources)
5. [Level 3: Skills with Scripts and Validation](#level-3-skills-with-scripts-and-validation)
6. [Level 4: Self-Evolving Skills with Hooks](#level-4-self-evolving-skills-with-hooks)
7. [Migration Path](#migration-path)
8. [Anti-Patterns](#anti-patterns)

---

## Overview

Skills in Claude Code exist on a spectrum of complexity. Choosing the right level depends on:

- **Frequency of use**: How often will this skill be invoked?
- **Stability**: Does the knowledge change over time?
- **Criticality**: How important is it that the skill executes correctly?
- **Learning potential**: Should the skill improve based on experience?

```
Level 1          Level 2          Level 3          Level 4
────────────────────────────────────────────────────────────►
Simple           Organized        Validated        Self-Evolving

Single file      Multiple files   Scripts +        Hooks +
Quick ref        Progressive      Automation       Learning
                 disclosure
```

---

## Quick Reference

| Level | Files | Scripts | Hooks | Self-Improving | Best For |
|-------|-------|---------|-------|----------------|----------|
| **1** | 1 SKILL.md | ❌ | ❌ | ❌ | Quick references, patterns, templates |
| **2** | Multiple .md | ❌ | ❌ | ❌ | Complex domains, detailed docs |
| **3** | .md + .py/.sh | ✅ | Optional | ❌ | Workflows needing validation |
| **4** | Full system | ✅ | ✅ Required | ✅ | Critical processes, team learning |

### When to Use Each Level

```
┌─────────────────────────────────────────────────────────────┐
│ "I need a quick template for X"           → Level 1         │
│ "I need comprehensive docs for domain Y"  → Level 2         │
│ "I need validation before doing Z"        → Level 3         │
│ "I need the system to learn and improve"  → Level 4         │
└─────────────────────────────────────────────────────────────┘
```

---

## Level 1: Single-File Skills

### Characteristics

- **One file**: Just `SKILL.md`
- **No dependencies**: No scripts, no external resources
- **Quick to create**: Can be written in minutes
- **Stable content**: Doesn't need frequent updates

### Directory Structure

```
.claude/skills/
└── skill-name/
    └── SKILL.md
```

### SKILL.md Template

```yaml
---
name: skill-name-here
description: Brief description of what this does. Use when [trigger conditions].
---

# Skill Title

## When to Use
- Condition 1
- Condition 2

## Quick Reference

[Main content - templates, patterns, commands]

## Checklist
- [ ] Step 1
- [ ] Step 2
- [ ] Step 3
```

### Example 1.1: FastAPI Endpoint Scaffolding

```yaml
---
name: fastapi-endpoint-scaffolding
description: Scaffold new FastAPI endpoints with proper structure, Pydantic models, error handling, and tests. Use when creating new API endpoints, adding routes, or when user mentions "new endpoint", "add API", or "create route".
---

# FastAPI Endpoint Scaffolding

## When to Use
- User asks to create a new API endpoint
- Adding CRUD operations for a resource
- Extending existing API with new routes

## File Structure to Create

For a resource called `{resource}`:

```
app/
├── routers/{resource}.py      # Router with endpoints
├── schemas/{resource}.py      # Pydantic models
├── services/{resource}.py     # Business logic
└── tests/test_{resource}.py   # Tests
```

## Router Template

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.{resource} import {Resource}Create, {Resource}Response
from app.services.{resource} import {Resource}Service

router = APIRouter(prefix="/{resources}", tags=["{resources}"])

@router.post("/", response_model={Resource}Response, status_code=status.HTTP_201_CREATED)
async def create_{resource}(
    data: {Resource}Create,
    db: Session = Depends(get_db)
):
    """Create a new {resource}."""
    return {Resource}Service(db).create(data)

@router.get("/{id}", response_model={Resource}Response)
async def get_{resource}(id: int, db: Session = Depends(get_db)):
    """Get {resource} by ID."""
    result = {Resource}Service(db).get(id)
    if not result:
        raise HTTPException(status_code=404, detail="{Resource} not found")
    return result
```

## Schema Template

```python
from pydantic import BaseModel
from datetime import datetime

class {Resource}Base(BaseModel):
    name: str

class {Resource}Create({Resource}Base):
    pass

class {Resource}Update(BaseModel):
    name: str | None = None

class {Resource}Response({Resource}Base):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
```

## Checklist
- [ ] Create router file
- [ ] Create schema file
- [ ] Create service file
- [ ] Register router in `app/main.py`
- [ ] Create test file
- [ ] Run tests: `pytest tests/test_{resource}.py -v`
```

### Example 1.2: React Component Scaffolding

```yaml
---
name: react-component-scaffolding
description: Scaffold new React components with TypeScript, proper file structure, and tests. Use when creating new UI components or when user mentions "new component", "create button", "add form".
---

# React Component Scaffolding

## When to Use
- Creating new UI components
- Adding interactive elements
- Building form components

## File Structure

```
src/components/{ComponentName}/
├── {ComponentName}.tsx        # Main component
├── {ComponentName}.test.tsx   # Tests
├── types.ts                   # Type definitions
└── index.ts                   # Barrel export
```

## Component Template

```tsx
// {ComponentName}.tsx
import { type {ComponentName}Props } from './types';

export function {ComponentName}({
  // destructure props
}: {ComponentName}Props) {
  return (
    <div className="">
      {/* component content */}
    </div>
  );
}
```

## Types Template

```tsx
// types.ts
export interface {ComponentName}Props {
  /** Description of prop */
  propName: string;
  /** Optional callback */
  onClick?: () => void;
  /** Children elements */
  children?: React.ReactNode;
}
```

## Test Template

```tsx
// {ComponentName}.test.tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { {ComponentName} } from './{ComponentName}';

describe('{ComponentName}', () => {
  it('renders correctly', () => {
    render(<{ComponentName} propName="test" />);
    expect(screen.getByText('test')).toBeInTheDocument();
  });

  it('handles click events', async () => {
    const handleClick = vi.fn();
    render(<{ComponentName} propName="test" onClick={handleClick} />);
    await userEvent.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalled();
  });
});
```

## Barrel Export

```tsx
// index.ts
export { {ComponentName} } from './{ComponentName}';
export type { {ComponentName}Props } from './types';
```

## Checklist
- [ ] Create component directory
- [ ] Create main component file
- [ ] Create types file
- [ ] Create test file
- [ ] Create barrel export
- [ ] Run tests: `npm test -- {ComponentName}`
```

### Example 1.3: Git PR Workflow

```yaml
---
name: github-pr-workflow
description: Create well-structured GitHub pull requests with proper descriptions and linked issues. Use when creating PRs, preparing code for review, or when user mentions "create PR", "open pull request", "submit for review".
---

# GitHub PR Workflow

## When to Use
- Code is ready for review
- Feature branch needs to be merged
- User explicitly asks for PR creation

## Pre-PR Checklist

Run these before creating PR:

```bash
# Ensure branch is up to date
git fetch origin main
git rebase origin/main

# Run all checks
make lint && make test && make typecheck
```

## PR Creation Command

```bash
gh pr create \
  --title "feat: Brief description of change" \
  --body "$(cat <<'EOF'
## Summary
- What this PR does (1-3 bullets)

## Changes
- File/module changes listed

## Testing
- [ ] Unit tests added/updated
- [ ] Manual testing performed
- [ ] Edge cases covered

## Related
- Fixes #ISSUE_NUMBER
EOF
)"
```

## Commit Message Prefixes
- `feat:` - New feature
- `fix:` - Bug fix
- `refactor:` - Code refactoring
- `docs:` - Documentation
- `test:` - Tests
- `chore:` - Maintenance

## After PR Creation
1. Request reviewers: `gh pr edit --add-reviewer @username`
2. Add labels: `gh pr edit --add-label "type:feature"`
3. Link to project: `gh pr edit --add-project "Project Name"`
```

### Level 1 Best Practices

1. **Keep it under 200 lines** - If longer, consider Level 2
2. **Include a checklist** - Makes it actionable
3. **Use concrete examples** - Not abstract descriptions
4. **Write trigger conditions** - Help Claude know when to use it
5. **Avoid explanations Claude already knows** - Be concise

---

## Level 2: Multi-File Skills with Resources

### Characteristics

- **Multiple markdown files**: Organized by sub-topic
- **Progressive disclosure**: Main SKILL.md links to details
- **Domain organization**: Reference docs loaded only when needed
- **Still no scripts**: Pure documentation

### Directory Structure

```
.claude/skills/
└── skill-name/
    ├── SKILL.md              # Entry point - overview & navigation
    ├── TOPIC_A.md            # Detailed reference for topic A
    ├── TOPIC_B.md            # Detailed reference for topic B
    ├── TROUBLESHOOTING.md    # Common issues and fixes
    └── EXAMPLES.md           # Extended examples
```

### Why Multiple Files?

**Token Efficiency**: Claude only loads what's needed.

```
User asks about RAG chunking
    │
    ▼
SKILL.md loads (~500 tokens)
    │
    ▼
Claude sees: "For chunking, see CHUNKING.md"
    │
    ▼
CHUNKING.md loads (~800 tokens)
    │
    ▼
Other files NOT loaded (saved ~2000 tokens)
```

### SKILL.md Template (Level 2)

```yaml
---
name: skill-name
description: Comprehensive description. Use when [multiple trigger conditions].
---

# Skill Title

## Quick Navigation

| Need | Reference |
|------|-----------|
| Topic A details | [TOPIC_A.md](TOPIC_A.md) |
| Topic B details | [TOPIC_B.md](TOPIC_B.md) |
| Common issues | [TROUBLESHOOTING.md](TROUBLESHOOTING.md) |

## Quick Start

[Minimal getting-started content]

## Decision Tree

**What are you trying to do?**

1. **Scenario A** → Read [TOPIC_A.md](TOPIC_A.md)
2. **Scenario B** → Read [TOPIC_B.md](TOPIC_B.md)
3. **Having issues** → Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
```

### Example 2.1: RAG System Development

**Directory Structure:**
```
.claude/skills/rag-development/
├── SKILL.md              # Entry point
├── CHUNKING.md           # Chunking strategies
├── EMBEDDINGS.md         # Embedding models
├── RETRIEVAL.md          # Retrieval patterns
├── EVALUATION.md         # Quality metrics
└── TROUBLESHOOTING.md    # Common issues
```

**SKILL.md:**
```yaml
---
name: rag-system-development
description: Build and optimize RAG (Retrieval-Augmented Generation) systems including chunking, embeddings, vector stores, and retrieval. Use when building search systems, implementing semantic search, creating knowledge bases, or when user mentions RAG, embeddings, vector search, or retrieval.
---

# RAG System Development

## Quick Navigation

| Task | Reference |
|------|-----------|
| Choosing chunk sizes | [CHUNKING.md](CHUNKING.md) |
| Embedding model selection | [EMBEDDINGS.md](EMBEDDINGS.md) |
| Retrieval strategies | [RETRIEVAL.md](RETRIEVAL.md) |
| Measuring quality | [EVALUATION.md](EVALUATION.md) |
| Debugging issues | [TROUBLESHOOTING.md](TROUBLESHOOTING.md) |

## Our Stack
- **Vector Store**: Pinecone / Qdrant / ChromaDB
- **Embeddings**: OpenAI text-embedding-3-large
- **Framework**: LangChain / LlamaIndex

## Quick Start: Basic RAG Pipeline

```python
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Pinecone
from langchain.text_splitter import RecursiveCharacterTextSplitter

# 1. Chunk documents
splitter = RecursiveCharacterTextSplitter(
    chunk_size=512,
    chunk_overlap=50,
    separators=["\n\n", "\n", ". ", " ", ""]
)
chunks = splitter.split_documents(documents)

# 2. Create embeddings and store
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
vectorstore = Pinecone.from_documents(chunks, embeddings, index_name="my-index")

# 3. Retrieve
retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
results = retriever.get_relevant_documents(query)
```

## Decision Tree

**What are you trying to do?**

1. **Starting fresh** → Read [CHUNKING.md](CHUNKING.md) first
2. **Poor retrieval quality** → Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
3. **Comparing approaches** → Use [EVALUATION.md](EVALUATION.md)
4. **Optimizing for speed** → See Hybrid Search in [RETRIEVAL.md](RETRIEVAL.md)
```

**CHUNKING.md:**
```markdown
# Chunking Strategies

## Chunk Size Guidelines

| Content Type | Chunk Size | Overlap | Rationale |
|--------------|------------|---------|-----------|
| Technical docs | 512 tokens | 50 | Preserves code blocks |
| Conversational | 256 tokens | 25 | Maintains context |
| Legal/Dense | 1024 tokens | 100 | Keeps clauses together |
| Q&A/FAQs | Per-item | 0 | Natural boundaries |

## Splitter Selection

### For Code-Heavy Content
```python
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.text_splitter import Language

code_splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.PYTHON,
    chunk_size=512,
    chunk_overlap=50
)
```

### For Markdown with Headers
```python
from langchain.text_splitter import MarkdownHeaderTextSplitter

headers = [
    ("#", "h1"),
    ("##", "h2"),
    ("###", "h3"),
]
md_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers)
```

### Semantic Chunking (Advanced)

When topic boundaries matter more than size:

```python
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import OpenAIEmbeddings

semantic_splitter = SemanticChunker(
    OpenAIEmbeddings(),
    breakpoint_threshold_type="percentile",
    breakpoint_threshold_amount=95
)
```

## Validation Checklist
- [ ] Sample 10 random chunks - do they make sense standalone?
- [ ] Check chunk size distribution - any outliers?
- [ ] Verify code blocks aren't split mid-function
- [ ] Test retrieval with known queries
```

**TROUBLESHOOTING.md:**
```markdown
# RAG Troubleshooting

## Symptom: Irrelevant Results

**Diagnosis Steps:**
1. Check embedding model matches between indexing and query
2. Verify chunk sizes aren't too large (diluting signal)
3. Test with exact phrase from document

**Debug Script:**
```python
results = vectorstore.similarity_search_with_score(query, k=10)
for doc, score in results:
    print(f"Score: {score:.3f}")
    print(f"Content: {doc.page_content[:200]}...")
    print("---")
```

**Fixes:**
- Reduce chunk size
- Try different embedding model
- Add metadata filtering

## Symptom: Missing Obvious Matches

**Common Causes:**
1. Chunking split the relevant content
2. Query phrasing differs from document
3. Metadata filters too restrictive

**Fixes:**
- Use query expansion
- Try hybrid search (BM25 + vector)
- Check metadata filter logic

## Symptom: Slow Retrieval

**Optimization Options:**
1. Use approximate nearest neighbors (HNSW)
2. Add metadata pre-filtering
3. Reduce embedding dimensions

```python
# Pre-filter to reduce search space
results = vectorstore.similarity_search(
    query,
    k=5,
    filter={"category": "technical", "year": {"$gte": 2023}}
)
```
```

### Example 2.2: Terraform Infrastructure Patterns

**Directory Structure:**
```
.claude/skills/terraform-patterns/
├── SKILL.md
├── GCP.md                # GCP-specific patterns
├── AWS.md                # AWS-specific patterns
├── MODULES.md            # Module authoring
├── STATE.md              # State management
└── SECURITY.md           # Security best practices
```

**SKILL.md:**
```yaml
---
name: terraform-infrastructure
description: Create and manage cloud infrastructure with Terraform including GCP, AWS, module patterns, and state management. Use when writing Terraform, creating cloud resources, setting up infrastructure, or when user mentions IaC, Terraform, cloud deployment, or infrastructure.
---

# Terraform Infrastructure Patterns

## Quick Navigation

| Need | Reference |
|------|-----------|
| GCP resources | [GCP.md](GCP.md) |
| AWS resources | [AWS.md](AWS.md) |
| Creating modules | [MODULES.md](MODULES.md) |
| State management | [STATE.md](STATE.md) |
| Security hardening | [SECURITY.md](SECURITY.md) |

## Project Structure

```
infra/
├── environments/
│   ├── dev/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── terraform.tfvars
│   ├── staging/
│   └── prod/
├── modules/
│   ├── networking/
│   ├── compute/
│   └── database/
└── shared/
    └── backend.tf
```

## Standard Variables

```hcl
variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "Primary region"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}
```

## Required Labels (All Resources)

```hcl
labels = {
  environment = var.environment
  managed_by  = "terraform"
  project     = var.project_name
  team        = var.team_name
}
```

## Workflow Commands

```bash
terraform init -backend-config=backend.tfvars
terraform plan -var-file=terraform.tfvars -out=plan.tfplan
terraform apply plan.tfplan
```
```

**GCP.md:**
```markdown
# GCP Terraform Patterns

## Cloud Run Service

```hcl
resource "google_cloud_run_v2_service" "app" {
  name     = "${var.project_name}-${var.environment}"
  location = var.region

  template {
    containers {
      image = var.container_image

      resources {
        limits = {
          cpu    = "1000m"
          memory = "512Mi"
        }
      }

      env {
        name  = "ENVIRONMENT"
        value = var.environment
      }

      # Secret from Secret Manager
      env {
        name = "DATABASE_URL"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.db_url.secret_id
            version = "latest"
          }
        }
      }
    }

    scaling {
      min_instance_count = var.environment == "prod" ? 1 : 0
      max_instance_count = 10
    }
  }

  labels = local.labels
}
```

## Cloud SQL with Private IP

```hcl
resource "google_sql_database_instance" "main" {
  name             = "${var.project_name}-${var.environment}-db"
  database_version = "POSTGRES_15"
  region           = var.region

  settings {
    tier = var.environment == "prod" ? "db-custom-2-4096" : "db-f1-micro"

    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.vpc.id
    }

    backup_configuration {
      enabled                        = true
      start_time                     = "03:00"
      point_in_time_recovery_enabled = var.environment == "prod"
    }
  }

  deletion_protection = var.environment == "prod"
}
```

## Secret Manager

```hcl
resource "google_secret_manager_secret" "api_key" {
  secret_id = "${var.project_name}-api-key-${var.environment}"

  replication {
    auto {}
  }

  labels = local.labels
}
```
```

### Example 2.3: Testing Strategy

**Directory Structure:**
```
.claude/skills/testing-strategy/
├── SKILL.md
├── UNIT.md               # Unit testing patterns
├── INTEGRATION.md        # Integration testing
├── E2E.md                # End-to-end testing
├── FIXTURES.md           # Test data management
└── MOCKING.md            # Mocking strategies
```

**SKILL.md:**
```yaml
---
name: testing-strategy
description: Implement comprehensive testing strategies including unit, integration, and e2e tests with proper fixtures and mocking. Use when writing tests, setting up test infrastructure, debugging test failures, or when user mentions testing, TDD, test coverage, or pytest/jest/vitest.
---

# Testing Strategy

## Quick Navigation

| Test Type | Reference | When to Use |
|-----------|-----------|-------------|
| Unit | [UNIT.md](UNIT.md) | Individual functions/classes |
| Integration | [INTEGRATION.md](INTEGRATION.md) | Component interactions |
| E2E | [E2E.md](E2E.md) | Full user flows |
| Fixtures | [FIXTURES.md](FIXTURES.md) | Test data setup |
| Mocking | [MOCKING.md](MOCKING.md) | External dependencies |

## Testing Pyramid

```
        /\
       /E2E\        ← Few, slow, high confidence
      /------\
     /Integr- \     ← Some, medium speed
    /  ation   \
   /------------\
  /    Unit      \  ← Many, fast, focused
 /________________\
```

## Quick Commands

```bash
# Python
pytest tests/ -v                     # All tests
pytest tests/unit/ -v                # Unit only
pytest -x --tb=short                 # Stop on first failure
pytest --cov=src --cov-report=html   # Coverage

# TypeScript
npm test                             # All tests
npm test -- --coverage               # Coverage
npm test -- --watch                  # Watch mode
```

## Test Structure (AAA Pattern)

```python
def test_user_creation():
    # Arrange - Set up test data
    user_data = {"email": "test@example.com", "name": "Test"}

    # Act - Execute the code
    result = create_user(user_data)

    # Assert - Verify the outcome
    assert result.email == "test@example.com"
    assert result.id is not None
```
```

### Level 2 Best Practices

1. **SKILL.md is the entry point** - Keep it under 100 lines
2. **Use navigation tables** - Help Claude find the right file
3. **One topic per file** - Don't mix concerns
4. **Link, don't duplicate** - Reference other files instead of copying
5. **Include decision trees** - Guide Claude to the right resource

---

## Level 3: Skills with Scripts and Validation

### Characteristics

- **Executable scripts**: Python/Bash utilities that Claude runs
- **Validation before action**: Check before doing something risky
- **Automated feedback**: Scripts provide structured output
- **Error prevention**: Catch issues before they become problems

### Directory Structure

```
.claude/skills/
└── skill-name/
    ├── SKILL.md              # Main instructions
    ├── REFERENCE.md          # Detailed docs (optional)
    ├── scripts/
    │   ├── validate.py       # Pre-action validation
    │   ├── execute.py        # Main action
    │   ├── verify.py         # Post-action verification
    │   └── rollback.py       # Undo if needed
    └── templates/
        └── template.ext      # Templates for generated files
```

### Script Design Principles

1. **Scripts output structured feedback** - Claude reads and acts on it
2. **Non-zero exit = failure** - Claude knows something went wrong
3. **Validate → Execute → Verify** - Always this order
4. **Rollback capability** - For dangerous operations

### Example 3.1: Database Migration Workflow

**Directory Structure:**
```
.claude/skills/database-migration/
├── SKILL.md
├── ROLLBACK.md
├── scripts/
│   ├── validate_migration.py
│   ├── check_breaking_changes.py
│   └── test_migration.py
└── templates/
    └── migration_template.py
```

**SKILL.md:**
```yaml
---
name: database-migration-workflow
description: Create and manage database migrations with validation, rollback plans, and breaking change detection. Use when modifying database schema, creating migrations, altering tables, or when user mentions migrations, alembic, schema changes, or database updates.
---

# Database Migration Workflow

## ⚠️ Critical: Always Validate First

Before ANY migration:

```bash
python .claude/skills/database-migration/scripts/validate_migration.py
```

## Workflow Checklist

```markdown
## Migration: {description}

### Pre-Migration
- [ ] Run breaking change check: `python scripts/check_breaking_changes.py`
- [ ] Review output for warnings
- [ ] Create rollback plan (see [ROLLBACK.md](ROLLBACK.md))

### Create Migration
- [ ] Generate: `alembic revision --autogenerate -m "{description}"`
- [ ] Review generated file (NEVER trust autogenerate blindly)
- [ ] Add data migration if needed

### Validate
- [ ] Run validation: `python scripts/validate_migration.py`
- [ ] Test migration: `python scripts/test_migration.py`
- [ ] Check reversibility: `alembic downgrade -1` then `alembic upgrade head`

### Apply
- [ ] Apply to dev: `alembic upgrade head`
- [ ] Verify application state
- [ ] Document in PR
```

## Quick Reference

| Operation | Risk Level | Requires |
|-----------|------------|----------|
| Add column (nullable) | Low | None |
| Add column (NOT NULL) | Medium | Default value |
| Drop column | High | Data migration plan |
| Rename column | High | Application update first |
| Add index | Low | Check table size |
| Drop index | Medium | Query analysis |

## Rollback

See [ROLLBACK.md](ROLLBACK.md) for detailed procedures.

Quick rollback:
```bash
alembic downgrade -1           # Rollback last
alembic downgrade {revision}   # Rollback to specific
```
```

**scripts/validate_migration.py:**
```python
#!/usr/bin/env python3
"""
Validates migration files before execution.
Exit 0 = OK, Exit 1 = Issues found
"""

import sys
import re
from pathlib import Path
import subprocess

def validate_migration(migration_file: Path) -> dict:
    """Validate a migration file and return issues."""
    issues = {"errors": [], "warnings": []}
    content = migration_file.read_text()

    # Check for dangerous operations
    dangerous_patterns = [
        (r"op\.drop_table\(", "DROP TABLE detected - ensure backup exists"),
        (r"op\.drop_column\(", "DROP COLUMN detected - verify data migration"),
        (r"op\.execute\(['\"]DELETE", "Raw DELETE detected - verify WHERE clause"),
        (r"op\.execute\(['\"]TRUNCATE", "TRUNCATE detected - data will be lost"),
    ]

    for pattern, message in dangerous_patterns:
        if re.search(pattern, content):
            issues["warnings"].append(message)

    # Check for missing downgrade
    if "def downgrade():" in content:
        downgrade_section = content.split("def downgrade():")[1]
        if "pass" in downgrade_section.split("\n")[1]:
            issues["errors"].append("Empty downgrade - migration not reversible")

    # Check for NOT NULL without default
    if re.search(r"nullable=False", content) and not re.search(r"server_default=", content):
        if "add_column" in content:
            issues["warnings"].append("NOT NULL without server_default - will fail on existing rows")

    return issues

def main():
    migrations_dir = Path("migrations/versions")

    if not migrations_dir.exists():
        print("❌ migrations/versions directory not found")
        sys.exit(1)

    # Get latest migration
    migrations = sorted(
        migrations_dir.glob("*.py"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )

    if not migrations:
        print("No migrations found")
        sys.exit(0)

    latest = migrations[0]
    print(f"Validating: {latest.name}")

    issues = validate_migration(latest)

    if issues["errors"]:
        print("\n❌ ERRORS (must fix):")
        for error in issues["errors"]:
            print(f"  • {error}")

    if issues["warnings"]:
        print("\n⚠️  WARNINGS (review carefully):")
        for warning in issues["warnings"]:
            print(f"  • {warning}")

    if not issues["errors"] and not issues["warnings"]:
        print("✅ Migration validation passed")

    sys.exit(1 if issues["errors"] else 0)

if __name__ == "__main__":
    main()
```

**scripts/check_breaking_changes.py:**
```python
#!/usr/bin/env python3
"""
Analyzes migration for breaking changes requiring coordination.
"""

import sys
import re
from pathlib import Path
import json

def analyze_breaking_changes(migration_file: Path) -> dict:
    """Analyze migration for coordination needs."""
    content = migration_file.read_text()

    changes = {
        "breaking": [],
        "coordinated": [],
        "safe": []
    }

    # Breaking: definitely breaks running apps
    breaking_patterns = [
        (r"op\.drop_column\(['\"](\w+)['\"],\s*['\"](\w+)['\"]",
         "Column drop: {}.{} - App will fail if referencing"),
        (r"op\.drop_table\(['\"](\w+)['\"]",
         "Table drop: {} - All queries will fail"),
    ]

    # Coordinated: need app update first
    coordinated_patterns = [
        (r"op\.create_unique_constraint\(",
         "Unique constraint - Handle duplicates first"),
        (r"nullable=False",
         "NOT NULL - Ensure no NULL values exist"),
    ]

    for pattern, message in breaking_patterns:
        matches = re.findall(pattern, content)
        for match in matches:
            if isinstance(match, tuple):
                changes["breaking"].append(message.format(*match))
            else:
                changes["breaking"].append(message.format(match))

    for pattern, message in coordinated_patterns:
        if re.search(pattern, content):
            changes["coordinated"].append(message)

    return changes

def main():
    if len(sys.argv) < 2:
        migrations_dir = Path("migrations/versions")
        migrations = sorted(
            migrations_dir.glob("*.py"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        migration_file = migrations[0] if migrations else None
    else:
        migration_file = Path(sys.argv[1])

    if not migration_file or not migration_file.exists():
        print("No migration file found")
        sys.exit(1)

    print(f"Analyzing: {migration_file.name}\n")

    changes = analyze_breaking_changes(migration_file)

    if changes["breaking"]:
        print("🚨 BREAKING (require downtime):")
        for change in changes["breaking"]:
            print(f"  • {change}")

    if changes["coordinated"]:
        print("\n⚠️  COORDINATED (deploy app first):")
        for change in changes["coordinated"]:
            print(f"  • {change}")

    if not changes["breaking"] and not changes["coordinated"]:
        print("✅ No breaking changes detected")

    sys.exit(1 if changes["breaking"] else 0)

if __name__ == "__main__":
    main()
```

### Example 3.2: Debug Investigation

**Directory Structure:**
```
.claude/skills/debug-investigation/
├── SKILL.md
├── PATTERNS.md           # Common bug patterns
├── scripts/
│   ├── collect_context.py
│   ├── analyze_logs.py
│   └── generate_report.py
└── templates/
    └── bug_report.md
```

**SKILL.md:**
```yaml
---
name: debug-investigation
description: Systematically investigate and debug issues using structured analysis and log examination. Use when debugging errors, investigating bugs, analyzing stack traces, or when user mentions bug, error, crash, failure, or "not working".
---

# Debug Investigation Workflow

## Phase 1: Context Collection

```bash
python .claude/skills/debug-investigation/scripts/collect_context.py "{error_description}"
```

This collects:
- Recent git changes
- Related log entries
- Stack trace analysis
- Environment info

## Phase 2: Investigation Checklist

```markdown
## Bug: {title}

### 1. Reproduce
- [ ] Can reproduce locally?
- [ ] Steps documented
- [ ] Frequency: Always / Sometimes / Rare

### 2. Isolate
- [ ] Which commit introduced it?
- [ ] Which component affected?
- [ ] Environment-specific?

### 3. Analyze
- [ ] Run: `python scripts/analyze_logs.py`
- [ ] Review stack trace
- [ ] Check related code changes

### 4. Root Cause
- [ ] Identified root cause
- [ ] Documented

### 5. Fix
- [ ] Fix implemented
- [ ] Tests added
- [ ] Fix verified
```

## Quick Commands

```bash
# Analyze recent logs
python scripts/analyze_logs.py --since="1 hour ago"

# Generate investigation report
python scripts/generate_report.py --output=investigation.md
```

## Common Patterns

See [PATTERNS.md](PATTERNS.md) for:
- Race conditions
- Memory leaks
- Connection pool exhaustion
- N+1 query problems
```

**scripts/collect_context.py:**
```python
#!/usr/bin/env python3
"""Collects debugging context automatically."""

import subprocess
import sys
from pathlib import Path

def run_cmd(cmd: list[str]) -> str:
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.stdout
    except Exception as e:
        return f"Error: {e}"

def main():
    error_desc = sys.argv[1] if len(sys.argv) > 1 else "unknown error"

    print(f"🔍 Collecting context for: {error_desc}\n")
    print("=" * 60)

    # Git context
    print("\n📦 GIT CONTEXT")
    print("-" * 40)
    print("Recent commits:")
    print(run_cmd(["git", "log", "--oneline", "-10"]))
    print("Uncommitted changes:")
    print(run_cmd(["git", "status", "--short"]))

    # Environment
    print("\n🖥️  ENVIRONMENT")
    print("-" * 40)
    print(f"Python: {run_cmd(['python', '--version']).strip()}")
    print(f"Branch: {run_cmd(['git', 'branch', '--show-current']).strip()}")

    # Search for error in code
    print("\n📁 RELATED FILES")
    print("-" * 40)
    result = run_cmd([
        "grep", "-r", "-l", error_desc, ".",
        "--include=*.py", "--include=*.ts"
    ])
    print(result if result.strip() else "No source files mention this error")

    print("\n" + "=" * 60)
    print("Context collection complete.")

if __name__ == "__main__":
    main()
```

**scripts/analyze_logs.py:**
```python
#!/usr/bin/env python3
"""Analyzes log files for patterns and anomalies."""

import re
import sys
from collections import Counter
from pathlib import Path
import argparse

def analyze_log_file(log_path: Path) -> dict:
    """Analyze a single log file."""
    stats = {
        "total_lines": 0,
        "level_counts": Counter(),
        "error_patterns": Counter(),
    }

    level_pattern = re.compile(r'\b(ERROR|WARN|INFO|DEBUG)\b')

    with open(log_path) as f:
        for line in f:
            stats["total_lines"] += 1
            match = level_pattern.search(line)
            if match:
                level = match.group(1)
                stats["level_counts"][level] += 1

                if level == "ERROR":
                    # Extract error pattern
                    pattern = re.sub(r'\d+', 'N', line)[:50]
                    stats["error_patterns"][pattern] += 1

    return stats

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", default="logs", help="Log directory")
    parser.add_argument("--since", default="1 day ago", help="Time filter")
    args = parser.parse_args()

    log_path = Path(args.path)

    if not log_path.exists():
        print(f"Path not found: {log_path}")
        sys.exit(1)

    print(f"📊 Analyzing: {log_path}\n")

    all_stats = {"level_counts": Counter(), "error_patterns": Counter()}
    log_files = [log_path] if log_path.is_file() else list(log_path.glob("**/*.log"))

    for log_file in log_files:
        stats = analyze_log_file(log_file)
        all_stats["level_counts"] += stats["level_counts"]
        all_stats["error_patterns"] += stats["error_patterns"]

    print("📈 Log Level Distribution:")
    for level, count in all_stats["level_counts"].most_common():
        print(f"  {level}: {count}")

    if all_stats["error_patterns"]:
        print("\n🔥 Top Error Patterns:")
        for pattern, count in all_stats["error_patterns"].most_common(5):
            print(f"  [{count}x] {pattern}...")

if __name__ == "__main__":
    main()
```

### Example 3.3: API Documentation Generator

**Directory Structure:**
```
.claude/skills/api-docs-generator/
├── SKILL.md
├── scripts/
│   ├── extract_endpoints.py
│   ├── generate_openapi.py
│   └── validate_docs.py
└── templates/
    └── endpoint.md.j2
```

**SKILL.md:**
```yaml
---
name: api-documentation-generator
description: Generate API documentation including OpenAPI specs and endpoint docs. Use when documenting APIs, creating OpenAPI specs, or when user mentions API docs, swagger, OpenAPI.
---

# API Documentation Generator

## Workflow

```markdown
### 1. Extract
- [ ] Run: `python scripts/extract_endpoints.py app.main:app`
- [ ] Review extracted endpoints

### 2. Generate
- [ ] Generate OpenAPI: `python scripts/generate_openapi.py`
- [ ] Generate markdown: from templates

### 3. Validate
- [ ] Run: `python scripts/validate_docs.py`
- [ ] Fix any issues
```

## Quick Commands

```bash
# Full pipeline
python scripts/extract_endpoints.py app.main:app && \
python scripts/generate_openapi.py && \
python scripts/validate_docs.py
```

## Documentation Standards

Each endpoint must have:
1. **Summary**: One-line description
2. **Description**: Detailed explanation
3. **Parameters**: All params documented
4. **Responses**: All response codes
5. **Examples**: Request/response example
```

### Level 3 Best Practices

1. **Scripts return structured output** - JSON or clear text Claude can parse
2. **Non-zero exit on failure** - Claude knows to stop/retry
3. **Validate before execute** - Prevent mistakes
4. **Include rollback scripts** - For dangerous operations
5. **Keep scripts focused** - One script, one job

---

## Level 4: Self-Evolving Skills with Hooks

### Characteristics

- **Hook-enforced execution**: Guaranteed to run at specific events
- **Pattern detection**: Identifies reusable processes
- **Self-improvement**: Skills update based on experience
- **Cross-agent learning**: Knowledge sharing between agents
- **Feedback loops**: Capture what works and what doesn't

### Directory Structure

```
.claude/skills/
└── skill-name/
    ├── SKILL.md
    ├── PATTERNS.md           # Detected patterns
    ├── ANTI_PATTERNS.md      # Things that don't work
    ├── scripts/
    │   ├── detect_patterns.py
    │   ├── promote_pattern.py
    │   ├── record_failure.py
    │   └── session_reflection.py
    └── data/
        └── pattern_log.jsonl
```

### Hook Configuration

Add to `.claude/settings.json`:

```json
{
  "hooks": {
    "SubagentStop": [
      {
        "hooks": [{
          "type": "command",
          "command": "python .claude/skills/agent-learning/scripts/session_reflection.py"
        }]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python .claude/skills/skill-evolution/scripts/detect_patterns.py"
          },
          {
            "type": "command",
            "command": "python .claude/skills/agent-learning/scripts/cross_agent_sync.py"
          }
        ]
      }
    ]
  }
}
```

### Pattern Lifecycle

```
Observation → Candidate → Emerging → Established → Promoted
                                          ↓
                                    Anti-Pattern (if >60% failure)
```

| State | Threshold | Action |
|-------|-----------|--------|
| `candidate` | 1 occurrence | Recorded in PATTERNS.md |
| `emerging` | 2-3 occurrences | Tracked |
| `established` | 4+ successes | Ready for promotion |
| `proven` | Promoted to skill | Part of workflow |
| `deprecated` | >60% failure | Moved to ANTI_PATTERNS.md |

### Example 4.1: Skill Evolution System

**SKILL.md:**
```yaml
---
name: skill-evolution-system
description: Meta-skill for pattern detection and skill evolution. Automatically invoked at session end. Use when reviewing skill effectiveness or promoting patterns.
---

# Skill Evolution System

## How This Works

```
┌─────────────────────────────────────────────────────────┐
│                    Session Work                          │
│                         │                                │
│                         ▼                                │
│              Stop Hook Triggered                         │
│                         │                                │
│                         ▼                                │
│            detect_patterns.py runs                       │
│                         │                                │
│                         ▼                                │
│    ┌────────────────────┴────────────────────┐          │
│    │                                          │          │
│    ▼                                          ▼          │
│ New Pattern?                            Existing Pattern?│
│    │                                          │          │
│    ▼                                          ▼          │
│ Add to PATTERNS.md                   Update occurrence   │
│ as "candidate"                        count & success    │
│                                              │           │
│                                              ▼           │
│                                    Ready for promotion?  │
│                                       (4+ success, >80%) │
│                                              │           │
│                                              ▼           │
│                                    promote_pattern.py    │
│                                              │           │
│                                              ▼           │
│                                    Create/update SKILL   │
└─────────────────────────────────────────────────────────┘
```

## Commands

```bash
# Manually record a pattern
python scripts/detect_patterns.py

# Promote established pattern to skill
python scripts/promote_pattern.py --pattern="name" --target-skill="skill"

# Record pattern failure
python scripts/record_failure.py --pattern="name" --reason="why"
```

## Pattern Format in PATTERNS.md

```markdown
## Pattern: {name}
**State**: candidate | emerging | established
**Occurrences**: N
**Success Rate**: X%
**First Seen**: YYYY-MM-DD

### Steps
1. Step one
2. Step two

### Context
When this applies

### Results
- [YYYY-MM-DD] ✅ Success: note
- [YYYY-MM-DD] ❌ Failure: reason
```

## Promotion Criteria

- [ ] 4+ successful uses
- [ ] >80% success rate
- [ ] Clear trigger identified
- [ ] Steps are reproducible
```

**scripts/detect_patterns.py:**
```python
#!/usr/bin/env python3
"""
Runs at session end to prompt for pattern detection.
"""

from pathlib import Path
from datetime import datetime

PATTERNS_FILE = Path(".claude/skills/skill-evolution/PATTERNS.md")

def load_existing_patterns() -> list[str]:
    """Load names of existing patterns."""
    patterns = []
    if PATTERNS_FILE.exists():
        import re
        content = PATTERNS_FILE.read_text()
        patterns = re.findall(r'^## Pattern: (.+)$', content, re.MULTILINE)
    return patterns

def main():
    existing = load_existing_patterns()

    prompt = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SKILL EVOLUTION CHECK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 1. PATTERN DETECTION

Did you perform any multi-step process (3+ steps) that could be reused?

If YES:
- **Name**: (e.g., "debug-memory-leak")
- **Steps**: (numbered)
- **Trigger**: (when to use)
- **Outcome**: ✅ or ❌

## 2. EXISTING PATTERN MATCH

Existing patterns: {', '.join(existing) if existing else 'None'}

If match: Update PATTERNS.md with new occurrence

## 3. ACTION REQUIRED

Do ONE of:
A) Add new pattern → Edit PATTERNS.md
B) Update existing pattern occurrence
C) Promote pattern (if 4+ success, >80% rate) → Create SKILL.md
D) Explain why no patterns emerged

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    print(prompt)

if __name__ == "__main__":
    main()
```

**scripts/promote_pattern.py:**
```python
#!/usr/bin/env python3
"""Promotes an established pattern to a skill."""

import argparse
import re
from pathlib import Path
from datetime import datetime

PATTERNS_FILE = Path(".claude/skills/skill-evolution/PATTERNS.md")
SKILLS_DIR = Path(".claude/skills")

def extract_pattern(pattern_name: str) -> dict | None:
    """Extract pattern details from PATTERNS.md."""
    if not PATTERNS_FILE.exists():
        return None

    content = PATTERNS_FILE.read_text()
    pattern_regex = rf'## Pattern: {re.escape(pattern_name)}\n(.*?)(?=\n## Pattern:|\Z)'
    match = re.search(pattern_regex, content, re.DOTALL)

    if not match:
        return None

    section = match.group(1)

    return {
        "name": pattern_name,
        "steps": re.search(r'### Steps\n(.*?)(?=\n###|\Z)', section, re.DOTALL),
        "context": re.search(r'### Context\n(.*?)(?=\n###|\Z)', section, re.DOTALL),
    }

def generate_skill(pattern: dict, target_skill: str) -> str:
    """Generate SKILL.md from pattern."""
    name_words = pattern["name"].replace("-", " ").replace("_", " ")
    steps = pattern["steps"].group(1).strip() if pattern["steps"] else ""
    context = pattern["context"].group(1).strip() if pattern["context"] else ""

    return f"""---
name: {target_skill}
description: {name_words.title()}. {context[:200]}
---

# {name_words.title()}

## When to Use

{context}

## Workflow

{steps}

---

*Promoted from pattern on {datetime.now().strftime('%Y-%m-%d')}*
"""

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pattern", required=True)
    parser.add_argument("--target-skill", required=True)
    args = parser.parse_args()

    print(f"🚀 Promoting '{args.pattern}' to '{args.target_skill}'")

    pattern = extract_pattern(args.pattern)
    if not pattern:
        print(f"❌ Pattern not found")
        return

    skill_dir = SKILLS_DIR / args.target_skill
    skill_dir.mkdir(parents=True, exist_ok=True)

    skill_content = generate_skill(pattern, args.target_skill)
    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text(skill_content)

    print(f"✅ Created: {skill_file}")

    # Update pattern state
    content = PATTERNS_FILE.read_text()
    updated = re.sub(
        rf'(## Pattern: {re.escape(args.pattern)}\n\*\*State\*\*: )\w+',
        r'\1proven',
        content
    )
    PATTERNS_FILE.write_text(updated)
    print("✅ Pattern marked as proven")

if __name__ == "__main__":
    main()
```

### Example 4.2: Agent Learning System

**SKILL.md:**
```yaml
---
name: agent-learning-system
description: Enables agents to learn and share knowledge. Invoked via hooks at session end. Use when reviewing learnings or syncing knowledge.
---

# Agent Learning System

## Architecture

```
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  AI Engineer │  │   Frontend   │  │    DevOps    │
│    Agent     │  │   Engineer   │  │   Engineer   │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │
       ▼                 ▼                 ▼
┌─────────────────────────────────────────────────┐
│           SubagentStop Hook                      │
│      (session_reflection.py per agent)           │
└─────────────────────────────────────────────────┘
       │                 │                 │
       ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│Agent Memory  │  │Agent Memory  │  │Agent Memory  │
│ (individual) │  │ (individual) │  │ (individual) │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │
       └─────────────────┼─────────────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │ cross_agent_sync.py │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │  Shared Knowledge   │
              │(shared-context.json)│
              └─────────────────────┘
```

## Memory Format

Each agent memory file:

```markdown
## [YYYY-MM-DD HH:MM] Session: {task}

### What Worked
- Approach that succeeded

### What Didn't Work
- Failed approach because reason

### Patterns Discovered
- New reusable pattern

### Cross-Agent Notes
- @other-agent: Important message

### Blockers
- Unresolved issue
```

## Commands

```bash
# Manual reflection
python scripts/session_reflection.py --agent="ai-engineer"

# Sync across agents
python scripts/cross_agent_sync.py

# Weekly digest
python scripts/weekly_digest.py
```
```

**scripts/session_reflection.py:**
```python
#!/usr/bin/env python3
"""Runs at agent session end to prompt reflection."""

import os
from datetime import datetime

def main():
    agent_name = os.environ.get("CLAUDE_AGENT_NAME", "unknown")
    memory_path = f".claude/agents/{agent_name}/memory.md"

    prompt = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AGENT SESSION REFLECTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Agent: {agent_name}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Update Memory File: {memory_path}

```markdown
## [{datetime.now().strftime('%Y-%m-%d %H:%M')}] Session: {{task}}

### What Worked
- {{successful approach}}

### What Didn't Work
- {{failed approach}} because {{reason}}

### Patterns Discovered
- {{reusable pattern}}

### Cross-Agent Notes
- @{{agent}}: {{message if needed}}

### Blockers
- {{unresolved issues}}
```

You MUST edit the memory file before ending.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    print(prompt)

if __name__ == "__main__":
    main()
```

**scripts/cross_agent_sync.py:**
```python
#!/usr/bin/env python3
"""Syncs knowledge across agents."""

import re
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

AGENTS_DIR = Path(".claude/agents")
SHARED_CONTEXT = Path(".claude/context/shared-context.json")

def find_memories() -> dict[str, Path]:
    """Find all agent memory files."""
    memories = {}
    for agent_dir in AGENTS_DIR.iterdir():
        if agent_dir.is_dir():
            memory = agent_dir / "memory.md"
            if memory.exists():
                memories[agent_dir.name] = memory
    return memories

def extract_mentions(content: str) -> list[dict]:
    """Extract @agent: message mentions."""
    pattern = r'@([\w-]+):\s*(.+?)(?=\n|$)'
    return [
        {"target": m.group(1), "message": m.group(2).strip()}
        for m in re.finditer(pattern, content)
    ]

def main():
    print("🔄 Syncing agent knowledge...\n")

    memories = find_memories()
    print(f"Found {len(memories)} agents: {', '.join(memories.keys())}")

    messages = defaultdict(list)
    patterns = []

    for agent, path in memories.items():
        content = path.read_text()

        # Extract cross-agent mentions
        for mention in extract_mentions(content):
            if mention["target"] != agent:
                messages[mention["target"]].append({
                    "from": agent,
                    "message": mention["message"],
                    "time": datetime.now().isoformat()
                })

        # Extract patterns
        pattern_match = re.search(
            r'### Patterns Discovered\n(.*?)(?=\n###|\n##|\Z)',
            content, re.DOTALL
        )
        if pattern_match:
            for line in pattern_match.group(1).split('\n'):
                if line.strip().startswith('- '):
                    patterns.append({"agent": agent, "pattern": line[2:].strip()})

    # Deliver messages
    for target, msgs in messages.items():
        incoming = AGENTS_DIR / target / "incoming.md"
        if incoming.parent.exists():
            existing = incoming.read_text() if incoming.exists() else ""
            new = "\n".join([
                f"- [{m['time'][:10]}] @{m['from']}: {m['message']}"
                for m in msgs
            ])
            incoming.write_text(f"{existing}\n{new}\n")

    # Update shared context
    shared = json.loads(SHARED_CONTEXT.read_text()) if SHARED_CONTEXT.exists() else {}
    shared.setdefault("recent_learnings", [])

    for p in patterns:
        shared["recent_learnings"].append({
            "date": datetime.now().strftime("%Y-%m-%d"),
            "agent": p["agent"],
            "learning": p["pattern"][:200]
        })

    shared["recent_learnings"] = shared["recent_learnings"][-20:]

    SHARED_CONTEXT.parent.mkdir(parents=True, exist_ok=True)
    SHARED_CONTEXT.write_text(json.dumps(shared, indent=2))

    print(f"\n📊 Results:")
    print(f"   Messages delivered: {sum(len(m) for m in messages.values())}")
    print(f"   Patterns found: {len(patterns)}")
    print(f"✅ Shared context updated")

if __name__ == "__main__":
    main()
```

### Example 4.3: Complete Settings.json

```json
{
  "permissions": {
    "allow": [
      "Bash(python .claude/skills/**)",
      "Bash(pytest *)",
      "Bash(npm test *)",
      "Bash(git status)",
      "Bash(git diff *)",
      "Bash(git add *)",
      "Bash(git commit *)",
      "Bash(gh pr *)"
    ],
    "deny": [
      "Bash(rm -rf *)",
      "Bash(git push --force*)"
    ]
  },
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [{
          "type": "command",
          "command": "python .claude/scripts/auto-lint.py"
        }]
      }
    ],
    "SubagentStop": [
      {
        "hooks": [{
          "type": "command",
          "command": "python .claude/skills/agent-learning/scripts/session_reflection.py"
        }]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python .claude/skills/skill-evolution/scripts/detect_patterns.py"
          },
          {
            "type": "command",
            "command": "python .claude/skills/agent-learning/scripts/cross_agent_sync.py"
          }
        ]
      }
    ]
  }
}
```

### Level 4 Best Practices

1. **Hooks are mandatory** - Don't rely on Claude remembering to run scripts
2. **Pattern lifecycle is key** - Track progression from candidate to proven
3. **Cross-agent sync matters** - Knowledge shouldn't be siloed
4. **Anti-patterns are valuable** - Learn from failures
5. **Weekly reviews** - Human oversight of the evolution system

---

## Migration Path

### From Level 1 to Level 2

**When to migrate:**
- SKILL.md exceeds 200 lines
- Multiple distinct sub-topics
- Claude reads full file but only needs parts

**How:**
1. Identify distinct sections
2. Extract to separate .md files
3. Replace content with links
4. Keep SKILL.md as navigation

### From Level 2 to Level 3

**When to migrate:**
- Process needs validation before execution
- Manual steps could be automated
- Errors happen that scripts could catch

**How:**
1. Identify validation needs
2. Create scripts/ directory
3. Write validation scripts
4. Add script calls to workflow

### From Level 3 to Level 4

**When to migrate:**
- Skill should improve over time
- Team is learning patterns worth capturing
- Critical process needs guaranteed reflection

**How:**
1. Add hook configuration
2. Create pattern detection scripts
3. Establish PATTERNS.md structure
4. Set up cross-agent sync if using agents

---

## Anti-Patterns

### ❌ Wrong Level Selection

**Problem**: Using Level 4 for simple templates
```
.claude/skills/hello-world/
├── SKILL.md
├── scripts/
│   ├── detect.py
│   └── learn.py
└── data/
```

**Fix**: Use Level 1 for simple content

### ❌ Scripts Without Validation

**Problem**: Level 3 scripts that just execute without checking
```python
# Bad: Just does it
def deploy():
    run("terraform apply -auto-approve")
```

**Fix**: Always validate → execute → verify
```python
# Good: Validates first
def deploy():
    if not validate():
        return "Validation failed"
    run("terraform apply")
    verify()
```

### ❌ Hooks Without Prompts

**Problem**: Hook scripts that just log without prompting action
```python
# Bad: Just logs
print(f"Session ended at {time}")
```

**Fix**: Output actionable prompts
```python
# Good: Forces reflection
print("You MUST update the memory file before ending.")
```

### ❌ No Pattern Graduation

**Problem**: Patterns stay as candidates forever
```markdown
## Pattern: some-pattern
**State**: candidate  # Never changes
**Occurrences**: 47
```

**Fix**: Implement promotion criteria and automate

### ❌ Siloed Agent Learning

**Problem**: Agents learn independently, don't share
```
ai-engineer/memory.md      # Has learnings
frontend-engineer/memory.md # Doesn't know about them
```

**Fix**: Implement cross_agent_sync.py with @mentions

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│                    SKILL COMPLEXITY LEVELS                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  LEVEL 1: Single File                                        │
│  └── SKILL.md only                                           │
│      Best for: Templates, quick references, patterns         │
│                                                              │
│  LEVEL 2: Multi-File                                         │
│  ├── SKILL.md (entry point)                                  │
│  ├── TOPIC_A.md                                              │
│  └── TOPIC_B.md                                              │
│      Best for: Complex domains, progressive disclosure       │
│                                                              │
│  LEVEL 3: With Scripts                                       │
│  ├── SKILL.md                                                │
│  └── scripts/                                                │
│      ├── validate.py                                         │
│      └── execute.py                                          │
│      Best for: Workflows needing validation/automation       │
│                                                              │
│  LEVEL 4: Self-Evolving                                      │
│  ├── SKILL.md                                                │
│  ├── PATTERNS.md                                             │
│  ├── scripts/                                                │
│  │   ├── detect_patterns.py                                  │
│  │   └── cross_agent_sync.py                                 │
│  └── settings.json (hooks)                                   │
│      Best for: Learning systems, team knowledge              │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│  HOOK EVENTS:                                                │
│  • Stop - Main session ends                                  │
│  • SubagentStop - Agent completes                            │
│  • PostToolUse - After Write/Edit/etc                        │
│  • PreToolUse - Before tool execution                        │
└─────────────────────────────────────────────────────────────┘
```

---

## Next Steps

1. **Audit current skills** - What level are they?
2. **Identify upgrade candidates** - Which need more complexity?
3. **Start with Level 4 meta-skills** - skill-evolution, agent-learning
4. **Configure hooks** - In settings.json
5. **Test the flow** - Run sessions and verify learning capture
