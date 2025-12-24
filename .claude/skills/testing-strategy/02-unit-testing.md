# Unit Testing

**When to use**: Testing individual functions/methods in isolation, business logic, utilities.

**Focus**: Fast (<1ms), isolated, no external dependencies.

---

## What to Test (Unit Level)

### ✅ Test These

- **Business logic**: Algorithms, transformations, calculations
- **Data validation**: Email, phone, custom rules
- **Utility functions**: Formatters, parsers, helpers
- **Edge cases**: Null, empty, boundary values
- **Error handling**: Exceptions, error messages

### ❌ Don't Test These

- **Trivial code**: Getters/setters, pass-through functions
- **Third-party libraries**: Trust pytest, pydantic, etc.
- **Database operations**: That's integration testing (Module 3)
- **API calls**: That's integration testing (Module 3)

---

## pytest Patterns

### Basic Test Structure (AAA)

```python
def test_user_email_validation_rejects_invalid_format():
    # Arrange
    user = User(email="invalid-email")

    # Act
    result = user.is_valid()

    # Assert
    assert not result
    assert "email" in user.errors
```

### Fixtures (Reusable Test Data)

**Basic Fixture:**
```python
import pytest

@pytest.fixture
def sample_user():
    return User(
        email="test@example.com",
        name="Test User",
        role="admin"
    )

def test_user_has_email(sample_user):
    assert sample_user.email == "test@example.com"
```

**Fixture with Setup/Teardown:**
```python
@pytest.fixture
def temp_file():
    # Setup
    file = open("test.txt", "w")
    file.write("test data")
    file.close()

    yield "test.txt"

    # Teardown
    os.remove("test.txt")

def test_file_exists(temp_file):
    assert os.path.exists(temp_file)
```

**Fixture Scopes:**
```python
@pytest.fixture(scope="function")  # Default: New for each test
def user():
    return User()

@pytest.fixture(scope="module")  # Once per module
def database():
    db = create_database()
    yield db
    db.close()

@pytest.fixture(scope="session")  # Once per test session
def app_config():
    return load_config()
```

### Parametrized Tests

**Test Multiple Inputs:**
```python
@pytest.mark.parametrize("email,expected", [
    ("test@example.com", True),
    ("invalid-email", False),
    ("", False),
    ("test@", False),
    ("@example.com", False),
])
def test_email_validation(email, expected):
    user = User(email=email)
    assert user.is_valid() == expected
```

**Multiple Parameters:**
```python
@pytest.mark.parametrize("input_data,expected_output", [
    ({"name": "John", "age": 30}, "John is 30"),
    ({"name": "Jane", "age": 25}, "Jane is 25"),
])
def test_user_description(input_data, expected_output):
    user = User(**input_data)
    assert user.description() == expected_output
```

---

## Mocking External Dependencies

### Why Mock?
- **Speed**: No network/database calls (unit tests must be <1ms)
- **Isolation**: Test one function, not entire system
- **Reliability**: No flaky tests from external failures

### Critical Mock Gotchas (MUST READ)

**1. Mock objects make `hasattr()` always return True**

```python
# ❌ BAD: hasattr() always returns True for Mock objects
event = Mock()
event.tool_call = None  # Set to None
hasattr(event, 'tool_call')  # Returns True! (causes bugs)

# ✅ GOOD: Use spec to limit attributes
event = Mock(spec=['text', 'content'])  # Only these attributes exist
hasattr(event, 'tool_call')  # Returns False (correct)
```

**Why this matters**: Code that checks `hasattr(obj, 'attr')` will pass for Mock objects even when the attribute is None, causing logic bugs in tests.

**2. Mock objects are not iterable**

```python
# ❌ BAD: Mock parts can't be iterated
event = Mock()
event.content = Mock()
event.content.parts = Mock()  # Can't iterate!
for part in event.content.parts:  # TypeError: 'Mock' object is not iterable
    print(part.text)

# ✅ GOOD: Use actual objects or create simple class
from google.genai import types

class EventWithParts:
    text = None
    content = types.Content(
        role="model",
        parts=[types.Part(text="First"), types.Part(text="Second")]
    )

event = EventWithParts()
for part in event.content.parts:  # Works!
    print(part.text)
```

**3. Async generators require `yield`**

```python
# ❌ BAD: Not an async generator (fails with 'async for')
async def mock_run_async(*args, **kwargs):
    raise Exception("Error")  # No yield!

# Code: async for event in runner.run_async()  # TypeError!

# ✅ GOOD: Add yield to make it async generator
async def mock_run_async(*args, **kwargs):
    raise Exception("Error")
    yield  # Never reached, but makes this async generator

# Code: async for event in runner.run_async()  # Works!
```

**4. Partial matching for state/dict assertions**

```python
# ❌ BAD: Exact match fails when code adds extra fields
mock_service.create_session.assert_called_once_with(
    state={"token": "abc"}  # Fails if code adds 'subject', 'last_activity', etc.
)

# ✅ GOOD: Partial match using call_args
mock_service.create_session.assert_called_once()
kwargs = mock_service.create_session.call_args.kwargs
assert "token" in kwargs["state"]
assert kwargs["state"]["token"] == "abc"
# Don't check auto-generated fields
```

### unittest.mock Patterns

**Mock a Function:**
```python
from unittest.mock import Mock, patch

@patch('requests.get')
def test_fetch_user_data(mock_get):
    # Setup mock
    mock_get.return_value = Mock(
        status_code=200,
        json=lambda: {"id": 1, "name": "John"}
    )

    # Test
    result = fetch_user_data(user_id=1)

    # Verify
    assert result["name"] == "John"
    mock_get.assert_called_once_with("https://api.example.com/users/1")
```

**Mock a Class:**
```python
@patch('myapp.database.Database')
def test_user_repository(mock_database_class):
    # Setup
    mock_db_instance = Mock()
    mock_database_class.return_value = mock_db_instance
    mock_db_instance.query.return_value = [User(id=1, name="John")]

    # Test
    repo = UserRepository()
    users = repo.get_all()

    # Verify
    assert len(users) == 1
    assert users[0].name == "John"
```

**Mock Side Effects:**
```python
@patch('requests.get')
def test_api_retry_on_failure(mock_get):
    # First call fails, second succeeds
    mock_get.side_effect = [
        Exception("Network error"),
        Mock(status_code=200, json=lambda: {"data": "success"})
    ]

    # Test
    result = fetch_with_retry("https://api.example.com")

    # Verify retry logic
    assert result == {"data": "success"}
    assert mock_get.call_count == 2
```

**Mock Environment Variables:**
```python
@patch.dict(os.environ, {"API_KEY": "test-key-123"})
def test_api_uses_env_var():
    api = APIClient()
    assert api.api_key == "test-key-123"
```

---

## Testing Exceptions

### Verifying Exceptions are Raised

```python
def test_user_creation_fails_with_invalid_email():
    with pytest.raises(ValueError) as exc_info:
        User(email="invalid")

    # Verify exception message
    assert "Invalid email format" in str(exc_info.value)
```

**Multiple Exception Types:**
```python
@pytest.mark.parametrize("invalid_input,expected_exception", [
    ("", ValueError),
    (None, TypeError),
    (123, TypeError),
])
def test_invalid_inputs_raise_exceptions(invalid_input, expected_exception):
    with pytest.raises(expected_exception):
        process_input(invalid_input)
```

---

## Test Organization

### Naming Conventions

**Pattern**: `test_<function>_<scenario>_<expected_outcome>`

```python
# Good names
def test_user_email_validation_succeeds_with_valid_email()
def test_user_email_validation_fails_with_invalid_format()
def test_user_save_raises_error_when_email_duplicate()

# Bad names
def test_user()
def test_email()
def test_1()
```

### Grouping with Classes

```python
class TestUserValidation:
    def test_email_validation_succeeds(self):
        user = User(email="test@example.com")
        assert user.is_valid()

    def test_email_validation_fails_invalid_format(self):
        user = User(email="invalid")
        assert not user.is_valid()

    @pytest.fixture
    def valid_user(self):
        return User(email="test@example.com", name="Test")
```

---

## Test Isolation

### Critical Rule: No Shared State

**❌ BAD: Shared mutable state**
```python
# Global cache (shared across tests)
_cache = {}

def test_cache_set():
    _cache['key'] = 'value'
    assert _cache['key'] == 'value'

def test_cache_get():
    # FLAKY! Depends on test order
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

## Edge Cases and Boundary Testing

### Common Edge Cases

```python
@pytest.mark.parametrize("input_value", [
    None,           # Null
    "",             # Empty string
    " ",            # Whitespace
    "a" * 1000,     # Very long string
    -1,             # Negative number
    0,              # Zero
    sys.maxsize,    # Very large number
])
def test_input_validation_handles_edge_cases(input_value):
    # Verify function handles edge cases gracefully
    result = validate_input(input_value)
    assert isinstance(result, bool)
```

---

## Test Data Factories

### Factory Pattern for Test Data

```python
class UserFactory:
    @staticmethod
    def create(**kwargs):
        defaults = {
            "email": "test@example.com",
            "name": "Test User",
            "role": "user",
            "created_at": datetime(2024, 1, 1)
        }
        defaults.update(kwargs)
        return User(**defaults)

# Usage
def test_admin_user():
    admin = UserFactory.create(role="admin")
    assert admin.is_admin()

def test_user_with_custom_email():
    user = UserFactory.create(email="custom@example.com")
    assert user.email == "custom@example.com"
```

---

## Performance Constraints

### Keep Unit Tests Fast

**Target**: <1ms per test

```python
import time

def test_function_executes_quickly():
    start = time.time()

    result = my_function()

    duration = time.time() - start
    assert duration < 0.001  # <1ms
```

**If test is slow, you're testing integration (use Module 3).**

---

## Best Practices

### ✅ Do

- **Test one thing per test**
- **Use descriptive names** (`test_user_email_validation_rejects_invalid_format`)
- **Arrange, Act, Assert** (AAA pattern)
- **Mock external dependencies** (APIs, databases)
- **Test edge cases** (null, empty, boundary values)
- **Keep tests fast** (<1ms)
- **Use fixtures** for reusable test data
- **Parametrize** for multiple inputs

### ❌ Don't

- **Test implementation details** (private methods, internal state)
- **Share state between tests** (global variables, class attributes)
- **Sleep in tests** (use mocks, not time-based waits)
- **Test third-party libraries** (trust them)
- **Make tests depend on each other** (run in any order)

---

## Common Mistakes

### ❌ Testing Private Methods

```python
# BAD: Don't test private methods
def test_user_internal_method():
    user = User()
    assert user._validate_internal() is True  # Don't do this!

# GOOD: Test public behavior
def test_user_validation():
    user = User(email="test@example.com")
    assert user.is_valid()
```

### ❌ Not Cleaning Up

```python
# BAD: Leaves files behind
def test_file_creation():
    create_file("test.txt")
    assert os.path.exists("test.txt")
    # File not deleted!

# GOOD: Cleanup with fixture
@pytest.fixture
def temp_file():
    filename = "test.txt"
    yield filename
    if os.path.exists(filename):
        os.remove(filename)

def test_file_creation(temp_file):
    create_file(temp_file)
    assert os.path.exists(temp_file)
    # Fixture cleans up
```

---

## pytest Configuration

### pytest.ini

```ini
[pytest]
# Test discovery
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Options
addopts = -v --strict-markers --cov=src --cov-report=term --cov-report=html

# Markers
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    unit: marks tests as unit tests
    integration: marks tests as integration tests

# Minimum coverage
[coverage:report]
fail_under = 80
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific file
pytest tests/unit/test_models.py

# Run specific test
pytest tests/unit/test_models.py::test_user_validation

# Run with coverage
pytest --cov=src --cov-report=html

# Run only unit tests
pytest -m unit

# Exclude slow tests
pytest -m "not slow"

# Run in parallel
pytest -n 4  # 4 workers (requires pytest-xdist)

# Verbose output
pytest -v

# Stop on first failure
pytest -x
```

---

## Summary

### Key Points

1. **Unit tests are fast** (<1ms), isolated, no external dependencies
2. **Mock everything external** (APIs, databases, file I/O)
3. **Use fixtures** for reusable test data
4. **Parametrize** to test multiple inputs
5. **Test edge cases** (null, empty, boundary values)
6. **Keep tests independent** (no shared state)

### Checklist

- [ ] Tests follow AAA pattern
- [ ] External dependencies mocked
- [ ] Tests run in <1ms each
- [ ] Edge cases tested
- [ ] Tests are independent (run in any order)
- [ ] Fixtures used for reusable data
- [ ] Coverage >80%

---

## Cross-References

- **Testing philosophy**: [01-testing-philosophy.md](01-testing-philosophy.md)
- **Integration testing**: [03-integration-testing.md](03-integration-testing.md)
- **Mocking databases**: [03-integration-testing.md](03-integration-testing.md)
- **Flaky test fixes**: [10-flaky-test-management.md](10-flaky-test-management.md)
- **CI/CD setup**: [11-ci-cd-integration.md](11-ci-cd-integration.md)
