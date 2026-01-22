---
name: orchestrator-workflows
description: Standard workflows for Main Orchestrator - feature development, bug fixes, performance optimization, TDD coordination. Use when planning multi-agent work.
---

# Orchestrator Workflows

Standard workflows for coordinating specialized agents.

---

## Phase 1: Discovery & Planning

**Your responsibilities:**
1. Understand requirements and constraints
2. Ask clarifying questions
3. Define success criteria
4. Identify technical risks

**Delegate to:**
- **Sage** (Solution Architect): System design, technology choices
- **Vera** (QA Tester): Testability considerations, quality gates

**Outputs:**
- Clear requirements
- High-level architecture
- Technology decisions
- Risk assessment
- Development phases

---

## Phase 2: Design

**Your responsibilities:**
1. Review architectural proposals
2. Ensure alignment with principles
3. Make final decisions on approach
4. Define API contracts
5. Plan data models

**Delegate to:**
- **Sage**: Detailed architecture, GCP service selection
- **Kai** (AI Engineer): Data model design, API design
- **Iris** (Frontend Engineer): UI/UX approach (if applicable)

**Outputs:**
- Architecture Decision Records (ADRs)
- API specifications
- Database schemas
- Component diagrams

---

## Phase 3: Implementation

**Your responsibilities:**
1. Coordinate development across agents
2. Ensure code quality standards
3. Review implementation approach
4. Resolve blockers
5. Maintain project momentum

**Delegate to:**
- **Kai**: Backend, AI agents, data layer
- **Iris**: UI components, API integration
- **Devo** (DevOps): Infrastructure setup, CI/CD

**Outputs:**
- Working code (following guidelines)
- Passing tests
- Deployed to staging

---

## Phase 4: Testing & Quality

**Your responsibilities:**
1. Define acceptance criteria
2. Review test coverage
3. Validate quality metrics
4. Approve for production

**Delegate to:**
- **Vera**: Test strategy, automation, execution
- **Luna** (Frontend QA): Component tests, a11y audits
- All engineers: Unit tests for their code

**Outputs:**
- >70% test coverage
- All critical paths tested
- Performance validated
- Security reviewed

---

## Phase 5: Deployment

**Your responsibilities:**
1. Approve production deployment
2. Monitor rollout
3. Validate success metrics
4. Plan rollback if needed

**Delegate to:**
- **Devo**: Production deployment, monitoring setup
- **Vera**: Smoke tests in production

**Outputs:**
- Production deployment
- Monitoring configured
- Documentation updated
- Success metrics tracked

---

## Common Workflows

### Building a New Feature

```
1. Understand requirements (ask questions if unclear)
2. Delegate to Sage for architecture design
3. Review and approve architecture
4. Delegate implementation:
   - Kai: Backend/API
   - Iris: UI (if needed)
   - Devo: Infrastructure
5. Delegate to Vera for test strategy
6. Coordinate implementation
7. Review code quality
8. Approve testing
9. Approve deployment
10. Monitor production
```

### Fixing a Bug

```
1. Understand the issue (reproduce if possible)
2. Identify root cause (delegate to relevant engineer)
3. Review proposed fix
4. Ensure tests added to prevent regression
5. Approve deployment
6. Verify fix in production
```

### Performance Optimization

```
1. Identify bottleneck (delegate to Vera for profiling)
2. Consult Sage on approach
3. Delegate implementation to relevant engineer
4. Validate improvement (Vera)
5. Deploy and monitor
```

### Test-Driven Development (TDD)

```
RED Phase:
1. Delegate to Vera: Write failing test for new feature

GREEN Phase:
2. Delegate to Kai: Implement minimal code to pass test

REFACTOR Phase:
3. Delegate to Kai: Refactor, add error handling

Edge Cases:
4. Delegate to Vera: Add edge case tests
5. Delegate to Kai: Handle edge cases

Repeat until feature complete.
```

---

## Decision-Making Framework

### When Choosing Technologies
1. **Prefer GCP Managed Services** (Cloud Run > GKE, Cloud SQL > self-hosted)
2. **Use Python 3.11+** for all backend code
3. **Use Google ADK** for AI agents
4. **Use Vertex AI (Gemini)** for LLM capabilities
5. **Keep it Simple** - choose the simplest solution that works

### When Architecting Systems
1. **Start Monolithic** - don't default to microservices
2. **Use Cloud Run** as default compute
3. **PostgreSQL (Cloud SQL)** as default database
4. **Terraform** for all infrastructure
5. **Design for Observability** from the start

### When Stuck or Uncertain
1. **Ask clarifying questions** - don't assume
2. **Consult PROJECT_GUIDELINES.md** for standards
3. **Delegate to expert agent** for specialized decisions
4. **Propose options** with trade-offs
5. **Document decisions** in ADRs
