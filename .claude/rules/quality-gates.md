---
paths: backend/**/*.py, frontend/**/*.tsx, frontend/**/*.ts, **/*.tf
---

# Quality Gates (Standards)

**Apply when reviewing or approving code changes.**

## Code Quality

Before approving:
- [ ] Type hints on all functions (Python)
- [ ] TypeScript strict mode (Frontend)
- [ ] Docstrings on public functions
- [ ] PEP 8 / ESLint formatted
- [ ] No unused code
- [ ] Simple, readable implementation
- [ ] No hardcoded secrets

## Architecture

Before approving:
- [ ] Follows GCP best practices
- [ ] Uses managed services (Cloud Run > GKE, Cloud SQL > self-hosted)
- [ ] Simple, not over-engineered
- [ ] Documented (ADRs for key decisions)
- [ ] Scalable and maintainable

## Testing

Before approving:
- [ ] Unit tests written (70%+ coverage target)
- [ ] Integration tests for APIs
- [ ] E2E tests for critical paths
- [ ] All tests passing
- [ ] Performance acceptable

## Deployment

Before approving:
- [ ] Infrastructure as Code (Terraform)
- [ ] CI/CD configured
- [ ] Health checks implemented
- [ ] Monitoring and alerts configured
- [ ] Rollback plan defined

---

## Red Flags - REJECT These

### Over-Engineering
- Premature microservices
- Unnecessary abstractions
- Complex ORMs for simple queries
- Custom solutions for common problems

### Poor Code Quality
- No type hints
- Missing tests
- Hardcoded secrets
- Clever/unreadable code

### Wrong Technologies
- Non-GCP cloud services (without justification)
- Non-Python backend
- Not using Google ADK for agents
- Complex state management when simple works

### Bad Practices
- Manual deployments
- No error handling
- Skipping documentation
- Ignoring accessibility

---

## Idea Validation Gate

Before implementing user requests, verify:

- [ ] Challenged assumptions explicitly
- [ ] Considered simpler alternatives
- [ ] Checked alignment with Core Principles
- [ ] Stated confidence level on approach

**If doubts exist**: Discuss with user before proceeding, don't implement blindly.

---

## Success Metrics

Track and optimize for:
- **Velocity**: Features delivered per sprint
- **Quality**: Bug count, test coverage, uptime
- **Performance**: Response times, resource usage
- **Cost**: GCP spend efficiency
- **Developer Experience**: Time to onboard, deploy, debug
- **User Experience**: Load times, accessibility, usability
