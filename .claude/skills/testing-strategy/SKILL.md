---
name: testing-strategy
description: Comprehensive testing patterns - unit, integration, E2E, accessibility, security. Use when writing tests, setting up test infrastructure, or TDD.
---

# Testing Strategy - Quick Reference

**Purpose**: Comprehensive testing strategies for robust, reliable software across all layers.

**When to use**: Designing test plans, implementing automated tests, setting up CI/CD, improving coverage.

---

## Modules

### 1. Testing Philosophy → [01-testing-philosophy.md](01-testing-philosophy.md)
- **Test pyramid** (60% unit, 30% integration, 10% E2E)
- **Coverage targets** (critical paths 100%, business logic 90%+)
- **What to test** vs. what NOT to test
- **Best practices** and common pitfalls

### 2. Unit Testing → [02-unit-testing.md](02-unit-testing.md)
- **pytest patterns** (AAA, fixtures, parametrization)
- **Mocking** (external APIs, databases)
- **Test isolation** and independence
- **Example patterns** with code

### 3. Integration Testing → [03-integration-testing.md](03-integration-testing.md)
- **API integration tests** (FastAPI TestClient)
- **Database integration** (test databases, transactions)
- **Service integration** (multi-component testing)
- **Test data management**

### 4. Frontend Component Testing → [04-frontend-component-testing.md](04-frontend-component-testing.md)
- **React Testing Library** (user-centric queries)
- **Svelte component tests**
- **Async behavior** (loading states, API calls)
- **Mocking context** and hooks

### 5. E2E Testing → [05-e2e-testing.md](05-e2e-testing.md)
- **Playwright patterns** (user journeys)
- **Browser automation**
- **Critical path testing**
- **When to use** E2E vs component tests

### 6. Accessibility Testing → [06-accessibility-testing.md](06-accessibility-testing.md)
- **WCAG 2.1 compliance** (Level AA target)
- **Automated A11y** (jest-axe, Playwright AxeBuilder)
- **Keyboard navigation** testing
- **Manual testing** checklist

### 7. Security Testing → [07-security-testing.md](07-security-testing.md)
- **OWASP Top 10** (injection, XSS, auth, CSRF)
- **API security** (rate limiting, CORS)
- **SSRF prevention** (DNS rebinding, TOCTOU)
- **Dependency scanning** (pip-audit, npm audit)
- **SAST/DAST** integration

### 8. AI/LLM Testing → [08-ai-llm-testing.md](08-ai-llm-testing.md)
- **Semantic assertions** (never exact strings!)
- **JSON mode** for deterministic testing
- **Prompt testing** and variations
- **Cost/performance** tracking

### 9. Performance Testing → [09-performance-testing.md](09-performance-testing.md)
- **Load testing** (Locust patterns)
- **Database performance** (query timing)
- **Profiling** and optimization

### 10. Flaky Test Management → [10-flaky-test-management.md](10-flaky-test-management.md)
- **Identifying flaky tests** (timing, non-determinism)
- **Common causes** and fixes (sleep(), shared state)
- **Retry strategies** (last resort!)
- **CI/CD handling** (separate flaky tests)

### 11. CI/CD Integration → [11-ci-cd-integration.md](11-ci-cd-integration.md)
- **GitHub Actions** patterns
- **Coverage reporting** (codecov)
- **Test organization** (unit/integration/e2e)
- **Quality gates**

---

## Quick Lookup

**Common Tasks:**

| Task | Module |
|------|--------|
| Writing pytest unit tests? | [02-unit-testing.md](02-unit-testing.md) |
| Testing FastAPI endpoints? | [03-integration-testing.md](03-integration-testing.md) |
| Testing React components? | [04-frontend-component-testing.md](04-frontend-component-testing.md) |
| Testing user flows? | [05-e2e-testing.md](05-e2e-testing.md) |
| Ensuring accessibility? | [06-accessibility-testing.md](06-accessibility-testing.md) |
| Security testing? | [07-security-testing.md](07-security-testing.md) |
| Testing AI agents/LLMs? | [08-ai-llm-testing.md](08-ai-llm-testing.md) |
| Load/performance testing? | [09-performance-testing.md](09-performance-testing.md) |
| Fixing flaky tests? | [10-flaky-test-management.md](10-flaky-test-management.md) |
| Setting up CI/CD? | [11-ci-cd-integration.md](11-ci-cd-integration.md) |

---

## Testing Pyramid

```
        /\
       /  \  E2E Tests (10%)
      /----\
     /      \  Integration Tests (30%)
    /--------\
   /          \  Unit Tests (60%)
  /--------------\
```

**Rule**: More unit tests (fast, isolated), fewer E2E tests (slow, brittle).

---

## Coverage Targets

| Layer | Target Coverage |
|-------|----------------|
| **Critical Paths** | 100% |
| **Business Logic** | 90-100% |
| **API Endpoints** | 80-90% |
| **Utility Functions** | 80-90% |
| **UI Components** | 70-80% |

**Measure**: `pytest --cov=src --cov-report=html`

---

## Anti-Patterns

### Testing Implementation Details
**Problem**: Tests break when refactoring, not when behavior changes.
**Fix**: Test behavior, not code structure. See [01-testing-philosophy.md](01-testing-philosophy.md)

### Flaky Tests
**Problem**: Tests fail randomly, destroying confidence.
**Fix**: See [10-flaky-test-management.md](10-flaky-test-management.md) for systematic fixes.

### Exact LLM Output Assertions
**Problem**: LLMs are non-deterministic, exact strings fail.
**Fix**: Use semantic assertions. See [08-ai-llm-testing.md](08-ai-llm-testing.md)

### No Test Isolation
**Problem**: Tests depend on each other, fail in isolation.
**Fix**: Use fixtures, clean up after tests. See [02-unit-testing.md](02-unit-testing.md)

### Skipping Security Tests
**Problem**: Vulnerabilities ship to production.
**Fix**: Automate security scans. See [07-security-testing.md](07-security-testing.md)

### Too Many E2E Tests
**Problem**: Slow test suite, brittle tests.
**Fix**: Follow testing pyramid. See [01-testing-philosophy.md](01-testing-philosophy.md)

---

## When to Use Which Module

### Planning test strategy?
→ **Module 1** (Philosophy) - Understand pyramid, coverage, best practices

### Writing backend tests?
→ **Module 2** (Unit) + **Module 3** (Integration)

### Testing UI?
→ **Module 4** (Component) for React/Svelte, **Module 5** (E2E) for flows

### Ensuring accessibility?
→ **Module 6** (Accessibility) - WCAG compliance, keyboard nav

### Testing security?
→ **Module 7** (Security) - OWASP Top 10, injection, auth

### Testing AI agents?
→ **Module 8** (AI/LLM) - Semantic assertions, prompt testing

### Performance issues?
→ **Module 9** (Performance) - Load testing, profiling

### Tests failing randomly?
→ **Module 10** (Flaky Tests) - Identify and fix root causes

### Setting up CI/CD?
→ **Module 11** (CI/CD) - GitHub Actions, coverage, automation

---

## Critical Reminders

### LLM Testing (CRITICAL)
**Never assert exact strings** - LLMs are non-deterministic!
- Use keyword presence: `assert "Paris" in response`
- Use JSON mode: `response_format="json"` for structure
- Use length bounds: `assert 50 < len(response) < 200`
- Never: `assert response == "Exact string"`

See [08-ai-llm-testing.md](08-ai-llm-testing.md) for complete patterns.

### Security Testing (CRITICAL)
**Test negative cases** - what should be blocked!
- Test SQL injection payloads: `"'; DROP TABLE users; --"`
- Test XSS: `"<script>alert('XSS')</script>"`
- Test SSRF: Block private IPs (`127.0.0.1`, `169.254.169.254`)
- Automate scans: `pip-audit`, `bandit`, `npm audit`

See [07-security-testing.md](07-security-testing.md) for complete OWASP coverage.

### Flaky Tests (CRITICAL)
**Fix immediately** - don't accumulate flaky tests!
- Never use `sleep()` - use explicit waits
- Never share state - use fixtures for isolation
- Never depend on test order - each test independent
- Goal: **0% flaky tests**

See [10-flaky-test-management.md](10-flaky-test-management.md) for systematic fixes.

---

## Best Practices Checklist

- [ ] Follow testing pyramid (more unit, fewer E2E)
- [ ] Write tests during development (TDD/BDD)
- [ ] Keep tests independent and isolated
- [ ] Use descriptive test names (`test_user_email_validation_rejects_invalid_format`)
- [ ] Mock external dependencies (APIs, databases in unit tests)
- [ ] Use test fixtures and factories
- [ ] Maintain >80% coverage (critical paths 100%)
- [ ] Run tests in CI/CD pipeline
- [ ] Keep unit tests fast (<1s each)
- [ ] Test edge cases and error scenarios
- [ ] Clean up test data after tests
- [ ] **Never ignore flaky tests** - fix or skip with tracking issue
- [ ] **Never assert exact LLM strings** - use semantic assertions
- [ ] **Always test security** - OWASP Top 10, negative cases

---

## Module Organization

Each module follows this structure:
1. **Introduction**: When to use this testing approach
2. **Patterns**: Code examples and best practices
3. **Anti-patterns**: Common mistakes to avoid
4. **Checklist**: Verification steps
5. **Cross-references**: Links to related modules

**Navigation**: Always load SKILL.md first for quick reference, then specific module for implementation details.
