---
name: deployment
description: GCP deployment patterns for Cloud Run, Cloud Build, Terraform, OAuth. Use when deploying services, setting up CI/CD, or troubleshooting deployment issues.
---

# Deployment Skills

**Last Updated**: 2025-12-11

This folder contains focused deployment skills for Google Cloud Platform, refactored from the original `gcp-deployment.md` (1,945 lines) into 6 specialized files.

---

## Skills Overview

| Skill | Lines | Description | When to Use |
|-------|-------|-------------|-------------|
| **[cloud-run.md](cloud-run.md)** | 597 | Cloud Run deployment patterns | Deploying services, traffic management, secrets, IAM |
| **[cloud-build.md](cloud-build.md)** | 566 | Cloud Build CI/CD patterns | Setting up CI/CD, cloudbuild.yaml, triggers |
| **[terraform.md](terraform.md)** | 616 | Infrastructure as Code patterns | Managing infrastructure, state, lifecycle blocks |
| **[oauth-deployment.md](oauth-deployment.md)** | 400 | OAuth-specific deployment | OAuth client setup, redirect URIs, secret management |
| **[validation.md](validation.md)** | 637 | Pre/post deployment validation | Validating Docker builds, IAM permissions, health checks |
| **[troubleshooting.md](troubleshooting.md)** | 542 | Common deployment errors | Debugging IAM issues, Docker failures, Cloud Build errors |

**Total**: 3,358 lines (was 2,610 lines across 2 files)

---

## Quick Reference

### For DevOps Engineers (Devo)

**Before any deployment**:
1. Read [validation.md](validation.md) - Complete pre-deployment checklist
2. Validate Docker builds locally (15 min investment saves 1.5 hours)
3. Wait 90 seconds after `terraform apply` before using new IAM bindings
4. Check [troubleshooting.md](troubleshooting.md) for common issues

**Auto-Discovery Keywords** (triggers skill loading):
- Cloud Run: `cloud run`, `gcloud run deploy`, `container deployment`
- Cloud Build: `cloudbuild.yaml`, `CI/CD pipeline`, `build trigger`
- Terraform: `terraform apply`, `infrastructure as code`, `tf state`
- OAuth: `oauth deployment`, `redirect uri`, `client credentials`
- Validation: `deployment validation`, `health check`, `pre-deployment`
- Troubleshooting: `deployment error`, `IAM issue`, `docker failure`

---

## Design Philosophy

These skills follow the design philosophy from [SKILLS_AND_AGENTS_GUIDE.md](../../../SKILLS_AND_AGENTS_GUIDE.md):

1. **Focused Skills**: One skill = one domain (Cloud Run, Terraform, OAuth, etc.)
2. **Folder Structure**: Related skills grouped in `deployment/` folder (like `google-adk-patterns/`)
3. **Manageable Size**: 300-600 lines per file (searchable, easy to navigate)
4. **Single Source of Truth**: No duplication between files (use cross-references)
5. **Examples-Heavy**: Good vs. bad patterns, real-world examples

---

## Refactoring History

**Date**: 2025-12-11
**Rationale**: Original `gcp-deployment.md` grew to 1,945 lines, making it difficult to navigate and search. `deployment-validation.md` (665 lines) had duplicate content.

**Changes**:
- Split into 6 focused files
- Removed duplicates (IAM propagation, Docker troubleshooting)
- Added cross-references between related skills
- Updated `.claude/config.json` with new skill registrations
- Updated `.claude/agents/devops-engineer.md` with new skill references

**Result**: Better organization, no content lost, easier to maintain.

---

## Cross-References

Each skill file references related skills:

- **cloud-run.md** → cloud-build.md, terraform.md, validation.md, troubleshooting.md
- **cloud-build.md** → cloud-run.md, terraform.md, validation.md, troubleshooting.md
- **terraform.md** → cloud-run.md, cloud-build.md, troubleshooting.md
- **oauth-deployment.md** → cloud-run.md, terraform.md, troubleshooting.md
- **validation.md** → cloud-build.md, cloud-run.md, terraform.md, troubleshooting.md
- **troubleshooting.md** → validation.md, cloud-run.md, cloud-build.md, terraform.md, oauth-deployment.md

---

**Remember**: These skills are single sources of truth for GCP deployment patterns. Update them when technology changes or new patterns are discovered.
