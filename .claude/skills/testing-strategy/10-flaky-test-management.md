# Flaky Test Management

**When to use**: Tests failing randomly without code changes.

**CRITICAL**: Flaky tests destroy confidence in your test suite - fix immediately!

---

## What are Flaky Tests?

**Definition**: Tests that sometimes pass and sometimes fail without code changes.

**Impact**:
- ❌ Destroy team confidence in test suite
- ❌ Developers ignore test failures ("it's just flaky")
- ❌ Hard to debug (can't reproduce reliably)
- ❌ Slow down CI/CD (retries, wasted time)

**Goal**: **0% flaky tests** (anything above 1% is unacceptable)

---

## Identifying Flaky Tests

### Signs of Flakiness

- ❌ Tests fail on CI but pass locally (or vice versa)
- ❌ Tests fail intermittently (~10-50% of runs)
- ❌ Timing-related errors ("element not found", "timeout")
- ❌ Tests depend on external state (network, time, file system)

### How to Detect

```bash
# Run tests multiple times to find flakiness
pytest tests/ --count=10  # pytest-repeat

# Run in parallel to expose race conditions
pytest tests/ -n 4  # pytest-xdist

# CI should track flaky test metrics
# GitHub Actions: track test retries
```

---

## Common Causes and Fixes

### 1. Timing Issues (MOST COMMON)

**❌ BAD: Using sleep()**
```python
def test_data_loads():
    trigger_async_load()
    time.sleep(2)  # FLAKY! Might be too short or too long
    assert data_is_loaded()
```

**✅ GOOD: Explicit waits with conditions**
```python
def test_data_loads():
    trigger_async_load()

    # Wait up to 5 seconds for condition
    wait_for(lambda: data_is_loaded(), timeout=5)
    assert data_is_loaded()

# Helper function
def wait_for(condition, timeout=10, interval=0.1):
    start = time.time()
    while time.time() - start < timeout:
        if condition():
            return True
        time.sleep(interval)
    raise TimeoutError(f"Condition not met within {timeout}s")
```

**✅ GOOD: Playwright auto-waits**
```typescript
// ❌ Bad: Manual sleep
await page.click('button');
await page.waitForTimeout(1000); // Flaky!

// ✅ Good: Automatic waiting
await page.click('button');
await expect(page.locator('.result')).toBeVisible(); // Waits automatically
```

### 2. Non-Deterministic Data

**❌ BAD: Random or time-dependent data**
```python
def test_user_creation():
    user = create_user(
        email=f"test{random.randint(1000, 9999)}@example.com",
        created_at=datetime.now()  # Changes every run!
    )
    assert user.created_at == datetime.now()  # FLAKY!
```

**✅ GOOD: Fixed test data with freezegun**
```python
from freezegun import freeze_time

@freeze_time("2024-01-15 10:00:00")
def test_user_creation():
    user = create_user(
        email="test@example.com",  # Deterministic
        created_at=datetime.now()  # Frozen to 2024-01-15
    )
    assert user.created_at == datetime(2024, 1, 15, 10, 0, 0)
```

### 3. Test Isolation Issues

**❌ BAD: Tests depend on each other**
```python
# Test 1 creates data
def test_create_user():
    user = User.create(email="test@example.com")
    assert user.id == 1

# Test 2 depends on Test 1 (FLAKY!)
def test_update_user():
    user = User.get(id=1)  # Fails if test_create_user didn't run
    user.update(name="Updated")
```

**✅ GOOD: Each test is independent**
```python
@pytest.fixture
def test_user(db):
    user = User.create(email="test@example.com")
    yield user
    db.rollback()  # Clean up

def test_update_user(test_user):
    test_user.update(name="Updated")
    assert test_user.name == "Updated"
```

### 4. External Dependencies

**❌ BAD: Real API calls**
```python
def test_fetch_user_profile():
    # FLAKY! Network issues, rate limits, API changes
    response = requests.get("https://api.example.com/user/1")
    assert response.status_code == 200
```

**✅ GOOD: Mock external calls**
```python
@patch('requests.get')
def test_fetch_user_profile(mock_get):
    mock_get.return_value = Mock(status_code=200, json=lambda: {"id": 1})

    response = requests.get("https://api.example.com/user/1")
    assert response.status_code == 200
```

### 5. Shared State / Global Variables

**❌ BAD: Shared mutable state**
```python
# Global cache (shared across tests)
_cache = {}

def test_cache_set():
    _cache['key'] = 'value'
    assert _cache['key'] == 'value'

def test_cache_get():
    # FLAKY! Depends on test execution order
    assert _cache.get('key') is None
```

**✅ GOOD: Isolated state per test**
```python
@pytest.fixture
def cache():
    return {}  # Fresh cache for each test

def test_cache_set(cache):
    cache['key'] = 'value'
    assert cache['key'] == 'value'

def test_cache_get(cache):
    assert cache.get('key') is None  # Always true
```

---

## Retry Strategies (LAST RESORT)

**⚠️ Warning**: Retrying flaky tests hides problems. Fix the root cause first!

**If you must retry** (e.g., external E2E tests):

```python
# pytest-rerunfailures
@pytest.mark.flaky(reruns=3, reruns_delay=2)
def test_external_integration():
    # Only use for truly external dependencies
    pass

# Playwright auto-retry
test.describe.configure({ retries: 2 });  // Max 2 retries
```

**Never retry:**
- Unit tests (they should never be flaky)
- Integration tests with mocked dependencies
- Tests failing due to actual bugs

---

## CI/CD Flaky Test Handling

### Separate Flaky Tests

```yaml
# GitHub Actions
- name: Run stable tests
  run: pytest tests/ -m "not flaky"

- name: Run flaky tests (allowed to fail)
  run: pytest tests/ -m flaky
  continue-on-error: true  # Don't block CI

- name: Report flaky test failures
  if: failure()
  run: |
    echo "Flaky tests failed - investigate immediately"
    # Post to Slack, create GitHub issue, etc.
```

### Mark Known Flaky Tests

```python
@pytest.mark.flaky
@pytest.mark.skip(reason="Flaky - tracked in issue #123")
def test_known_flaky():
    pass
```

---

## Flaky Test Action Plan

**When you encounter a flaky test:**

1. **Reproduce it locally**: Run test 10-20 times
2. **Identify the root cause**: Review checklist above
3. **Fix immediately**: Don't let flaky tests accumulate
4. **If can't fix quickly**:
   - Mark as `@pytest.mark.skip` with issue number
   - Create tracking issue with reproduction steps
   - Set deadline to fix (within 1 sprint)
5. **Never ignore**: Flaky tests are bugs in your tests

---

## Measuring Flakiness

**Track these metrics:**
- **Flaky test rate**: % of tests that are flaky
- **Flaky test age**: How long tests have been flaky
- **CI retry rate**: How often tests are retried

**Goal**: 0% flaky tests. Anything above 1% destroys confidence.

---

## Summary

### Key Points

1. **Flaky tests destroy confidence** - fix immediately
2. **Never use sleep()** - use explicit waits
3. **Never share state** - use fixtures for isolation
4. **Never depend on test order** - each test independent
5. **Goal: 0% flaky tests**

### Checklist

- [ ] No sleep() calls (use wait_for)
- [ ] No shared state (use fixtures)
- [ ] No external dependencies (use mocks)
- [ ] No random data (use fixed data or freeze time)
- [ ] Tests run in any order
- [ ] CI tracks flaky test metrics

---

## Cross-References

- **Testing philosophy**: [01-testing-philosophy.md](01-testing-philosophy.md)
- **Unit testing**: [02-unit-testing.md](02-unit-testing.md)
- **E2E testing**: [05-e2e-testing.md](05-e2e-testing.md)
- **CI/CD setup**: [11-ci-cd-integration.md](11-ci-cd-integration.md)
