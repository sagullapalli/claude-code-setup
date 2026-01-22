# Testing Philosophy

**When to use**: Planning test strategy, understanding testing approach, setting coverage targets.

---

## The Testing Pyramid

```
        /\
       /  \  E2E Tests (10%)
      /----\
     /      \  Integration Tests (30%)
    /--------\
   /          \  Unit Tests (60%)
  /--------------\
```

### Principle
**More unit tests (fast, isolated), fewer E2E tests (slow, brittle).**

### Why This Matters
- **Unit tests**: Fast feedback (<1s), pinpoint failures, easy to maintain
- **Integration tests**: Verify components work together, catch interface bugs
- **E2E tests**: Validate user journeys, catch UI/UX issues

**Anti-pattern**: Inverted pyramid (mostly E2E tests) → slow suite, flaky tests, hard to debug.

---

## Coverage Targets

| Layer | Target Coverage | Why |
|-------|----------------|-----|
| **Critical Paths** | 100% | Payment, auth, data loss scenarios |
| **Business Logic** | 90-100% | Core features, algorithms, validation |
| **API Endpoints** | 80-90% | All routes, status codes, error handling |
| **Utility Functions** | 80-90% | Reusable helpers, transformations |
| **UI Components** | 70-80% | User interactions, conditional rendering |

**Measure Coverage:**
```bash
# Python
pytest --cov=src --cov-report=html --cov-report=term

# JavaScript
jest --coverage

# View report
open coverage/index.html
```

---

## What to Test

### ✅ DO Test

**Business Logic:**
- Data transformations
- Validation functions
- Algorithms
- State transitions

**API Endpoints:**
- All routes (GET, POST, PUT, DELETE)
- HTTP status codes (200, 201, 400, 401, 403, 404, 500)
- Request validation
- Response structure
- Error handling

**Database Operations:**
- CRUD operations
- Transactions
- Constraint violations
- Query correctness

**Error Handling:**
- Edge cases (null, empty, very large inputs)
- Failure scenarios (network errors, timeouts)
- Error messages are clear and actionable

**Security:**
- Authentication and authorization
- Input validation (SQL injection, XSS)
- CSRF protection
- Rate limiting

**User Journeys (E2E):**
- Critical paths (signup, login, checkout)
- Multi-step workflows
- Cross-browser compatibility

---

## What NOT to Test

### ❌ DON'T Test

**Implementation Details:**
- Private methods
- Internal variable names
- Code structure (if refactoring breaks tests, you're testing implementation)

**Third-Party Libraries:**
- Don't test pytest, FastAPI, React
- Trust mature libraries (they have their own tests)

**Framework Internals:**
- Don't test FastAPI routing
- Don't test React rendering
- Don't test SQLAlchemy ORM

**Trivial Code:**
- Simple getters/setters
- Pass-through functions
- Constants

**Example:**
```python
# ❌ DON'T test this
class User:
    def __init__(self, name):
        self._name = name

    def get_name(self):
        return self._name  # Trivial, don't test

# ✅ DO test this
class User:
    def is_valid_email(self):
        # Complex validation logic
        return re.match(r'^[a-z0-9]+@[a-z]+\.[a-z]+$', self.email) is not None
```

---

## Testing Patterns

### AAA Pattern (Arrange, Act, Assert)

**Standard pattern for all tests:**

```python
def test_user_email_validation():
    # Arrange: Set up test data
    user = User(email="invalid-email")

    # Act: Perform action
    result = user.is_valid()

    # Assert: Verify outcome
    assert result is False
    assert "email" in user.errors
```

### Given-When-Then (BDD Style)

**Alternative pattern for behavior-driven tests:**

```python
def test_user_email_validation():
    # Given a user with an invalid email
    user = User(email="invalid-email")

    # When we validate the user
    result = user.is_valid()

    # Then validation should fail
    assert result is False
    assert "email" in user.errors
```

---

## Test Naming Conventions

### Descriptive Names

**Pattern**: `test_<unit>_<scenario>_<expected_outcome>`

**Good Examples:**
```python
def test_user_email_validation_rejects_invalid_format()
def test_api_create_user_returns_201_with_valid_data()
def test_database_transaction_rolls_back_on_error()
```

**Bad Examples:**
```python
def test_user()  # Too vague
def test_1()  # Meaningless
def test_email()  # What about email?
```

---

## Test Independence

### Critical Rule: Tests Must Be Independent

**Each test should:**
- Run in any order
- Not depend on other tests
- Clean up after itself
- Use fresh fixtures

**Example:**

```python
# ❌ BAD: Tests depend on each other
def test_create_user():
    user = User.create(email="test@example.com")
    assert user.id == 1

def test_update_user():
    user = User.get(id=1)  # Depends on test_create_user!
    user.update(name="Updated")

# ✅ GOOD: Each test is independent
@pytest.fixture
def test_user(db):
    user = User.create(email="test@example.com")
    yield user
    db.rollback()  # Clean up

def test_create_user(db):
    user = User.create(email="test@example.com")
    assert user.id is not None

def test_update_user(test_user):
    test_user.update(name="Updated")
    assert test_user.name == "Updated"
```

---

## Test Speed

### Unit Tests: <1s Each
- No database calls (use mocks)
- No API calls (use mocks)
- No file I/O (use in-memory)

### Integration Tests: <5s Each
- Use test database
- Minimize network calls
- Parallelize when possible

### E2E Tests: <30s Each
- Only for critical paths
- Run on CI, not locally
- Use headless browsers

**If tests are slow, developers won't run them.**

---

## When to Write Tests

### TDD (Test-Driven Development)
1. Write failing test
2. Write minimal code to pass
3. Refactor

**Benefits**: Better design, full coverage, confidence in refactoring.

### BDD (Behavior-Driven Development)
1. Define behavior in Given-When-Then
2. Write tests for behavior
3. Implement feature

**Benefits**: Clear requirements, testable specs, stakeholder alignment.

### Test-After (Acceptable)
1. Implement feature
2. Write tests immediately after
3. Verify coverage >80%

**Warning**: Easy to skip tests. Enforce coverage in CI/CD.

---

## Testing Anti-Patterns

### ❌ Testing Implementation Details

**Problem**: Tests break on refactoring, not on behavior changes.

```python
# ❌ BAD: Testing internal variable
def test_user_sets_internal_variable():
    user = User(name="John")
    assert user._name == "John"  # Don't test private vars!

# ✅ GOOD: Testing behavior
def test_user_returns_name():
    user = User(name="John")
    assert user.get_name() == "John"
```

### ❌ Flaky Tests

**Problem**: Tests fail randomly without code changes.

**Common causes**:
- Using `time.sleep()` instead of explicit waits
- Non-deterministic data (random, timestamps)
- Shared state between tests

**Fix**: See [10-flaky-test-management.md](10-flaky-test-management.md)

### ❌ One Test Doing Too Much

**Problem**: Hard to debug, unclear what failed.

```python
# ❌ BAD: Multiple assertions, unclear failure
def test_user():
    user = User(email="test@example.com", name="John")
    assert user.is_valid()
    assert user.save()
    assert user.id is not None
    assert user.created_at is not None

# ✅ GOOD: Focused tests
def test_user_validation_succeeds_with_valid_data():
    user = User(email="test@example.com", name="John")
    assert user.is_valid()

def test_user_save_assigns_id():
    user = User(email="test@example.com", name="John")
    user.save()
    assert user.id is not None
```

### ❌ Ignoring Test Failures

**Problem**: "It's just a flaky test" → Test suite loses credibility.

**Solution**: Fix or skip with tracking issue. **Never ignore.**

---

## Test Organization

### Recommended Directory Structure

```
tests/
├── unit/
│   ├── test_models.py
│   ├── test_services.py
│   └── test_utils.py
├── integration/
│   ├── test_api.py
│   ├── test_database.py
│   └── test_external_services.py
├── e2e/
│   ├── test_user_journey.py
│   └── test_checkout_flow.py
├── fixtures/
│   ├── users.py
│   └── products.py
├── conftest.py  # Shared fixtures
└── pytest.ini   # pytest configuration
```

---

## Quality Gates

### Before Merging to Main

- [ ] All tests pass
- [ ] Coverage >80% (critical paths 100%)
- [ ] No flaky tests
- [ ] No skipped tests without tracking issue
- [ ] Security tests pass

### CI/CD Pipeline

```yaml
# .github/workflows/test.yml
- name: Run tests
  run: pytest --cov=src --cov-fail-under=80

- name: Check for flaky tests
  run: pytest --count=3  # Run 3 times

- name: Security scan
  run: bandit -r src/ -ll
```

---

## Summary

### Key Principles

1. **Follow the pyramid**: 60% unit, 30% integration, 10% E2E
2. **Test behavior, not implementation**
3. **Keep tests independent** (no shared state)
4. **Keep tests fast** (<1s for unit tests)
5. **Maintain high coverage** (>80%, critical paths 100%)
6. **Fix flaky tests immediately** (don't let them accumulate)

### Quick Checklist

- [ ] Tests follow AAA pattern
- [ ] Tests are independent (run in any order)
- [ ] Test names are descriptive
- [ ] Coverage >80% on new code
- [ ] No flaky tests
- [ ] Tests run in <5 minutes total

---

## Cross-References

- **Unit testing patterns**: [02-unit-testing.md](02-unit-testing.md)
- **Integration testing**: [03-integration-testing.md](03-integration-testing.md)
- **E2E testing**: [05-e2e-testing.md](05-e2e-testing.md)
- **Flaky test fixes**: [10-flaky-test-management.md](10-flaky-test-management.md)
- **CI/CD setup**: [11-ci-cd-integration.md](11-ci-cd-integration.md)
