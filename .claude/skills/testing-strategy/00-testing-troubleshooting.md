# Testing Troubleshooting & Common Fixes

**Last Updated**: 2025-12-04

This skill captures common testing issues and their fixes to prevent re-discovery.

---

## Common pytest Issues

### Issue 1: Pydantic ValidationError on Import

**Error**:
```
pydantic_core._pydantic_core.ValidationError: 3 validation errors for Settings
oauth_client_id
  Field required [type=missing, input_value={}, input_type=dict]
```

**Root Cause**: `conftest.py` imports Settings before environment variables are set.

**Fix**: Set environment variables at module level BEFORE imports in `conftest.py`:

```python
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# ⚠️ SET ENV VARS BEFORE IMPORTING SETTINGS
os.environ.setdefault("GCP_PROJECT", "test-project")
os.environ.setdefault("OAUTH_CLIENT_ID", "test-client-id")
os.environ.setdefault("OAUTH_CLIENT_SECRET", "test-secret")
# ... all required env vars

# NOW safe to import Settings
from backend.app.core.config import Settings
```

**Pattern**: Always set env vars before Pydantic Settings import.

---

### Issue 2: Missing `@pytest.mark.asyncio` Decorator

**Error**:
```
async def functions are not natively supported.
You need to install a suitable plugin for your async framework...
```

**Root Cause**: Async test functions missing `@pytest.mark.asyncio` decorator.

**Fix**: Add decorator to ALL async test functions:

```python
@pytest.mark.asyncio
async def test_my_async_function():
    result = await my_async_function()
    assert result == expected
```

**Pattern**: Every `async def test_*` needs `@pytest.mark.asyncio`.

**Script to Fix Automatically**:
```python
import re

def add_asyncio_marker(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    new_lines = []
    for i, line in enumerate(lines):
        # Check if this line defines an async test
        if re.match(r'\s+async def test_', line):
            # Check if previous line already has decorator
            if i > 0 and '@pytest.mark.asyncio' not in lines[i-1]:
                indent = len(line) - len(line.lstrip())
                new_lines.append(' ' * indent + '@pytest.mark.asyncio\n')
        new_lines.append(line)

    with open(file_path, 'w') as f:
        f.writelines(new_lines)
```

---

### Issue 3: Mock Attribute Errors (Lazy Imports)

**Error**:
```
AttributeError: <module 'backend.app.api.routes'> does not have the attribute 'get_oauth_service'
```

**Root Cause**: Code uses **lazy imports** (import inside function), but tests try to mock at module level.

**Example - Code Structure**:
```python
# backend/app/api/routes.py
def my_endpoint():
    from backend.app.services.oauth_service import get_oauth_service  # Lazy import!
    oauth = get_oauth_service()
    ...
```

**Wrong Mock Path** (FAILS):
```python
@patch('backend.app.api.routes.get_oauth_service')  # ❌ Doesn't exist at module level!
def test_my_endpoint(mock_oauth):
    ...
```

**Correct Mock Path** (WORKS):
```python
@patch('backend.app.services.oauth_service.get_oauth_service')  # ✅ Mock at source!
def test_my_endpoint(mock_oauth):
    ...
```

**Pattern**: Always mock at the **source module** where function is defined, not where it's imported.

**How to Find Correct Path**:
1. Grep for the function in the codebase:
   ```bash
   grep -rn "get_oauth_service" backend/
   ```
2. Find the `def get_oauth_service():` definition (not the import)
3. Use that module path for mocking

---

## Mock Gotchas

### Gotcha 1: Mock Makes `hasattr()` Always Return True

**Problem**:
```python
mock_obj = Mock()
hasattr(mock_obj, 'anything')  # ❌ Always True!
```

**Impact**: Code like `if hasattr(event, 'tool_use'):` will incorrectly return True.

**Fix**: Use `Mock(spec=[...])` to whitelist attributes:
```python
mock_obj = Mock(spec=['attr1', 'attr2'])
hasattr(mock_obj, 'attr1')  # ✅ True
hasattr(mock_obj, 'attr3')  # ✅ False
```

**Pattern**: Always use `spec` parameter when mocking objects with `hasattr()` checks.

---

### Gotcha 2: Mock Objects Are Not Iterable

**Problem**:
```python
mock_list = Mock()
for item in mock_list:  # ❌ TypeError: 'Mock' object is not iterable
    ...
```

**Fix**: Use actual objects or simple classes, not Mocks:
```python
# Option 1: Use actual object
from backend.app.models import Content
mock_content = Content(parts=[...])

# Option 2: Simple class
class FakeContent:
    def __init__(self, parts):
        self.parts = parts

mock_content = FakeContent(parts=[...])
```

**Pattern**: Don't mock complex iterables - use real objects or simple classes.

---

### Gotcha 3: Async Generators Require `yield`

**Problem**:
```python
async def mock_run_with_error():
    raise Exception("Error")

mock_runner.run_async = mock_run_with_error

# ❌ TypeError: 'async for' requires __aiter__ method
async for event in mock_runner.run_async():
    ...
```

**Fix**: Add unreachable `yield` to make it an async generator:
```python
async def mock_run_with_error():
    raise Exception("Error")
    yield  # ✅ Never reached, but makes it async generator

mock_runner.run_async = mock_run_with_error
```

**Pattern**: Async functions used in `async for` must have `yield` (even if unreachable).

---

### Gotcha 4: Partial State Matching

**Problem**: Production code adds extra fields, exact dict comparison fails:
```python
# Code adds extra fields
create_session(state={'oauth_token': 'abc', 'subject': 'Auto', 'last_activity': '...'})

# Test expects exact match
mock.create_session.assert_called_once_with(
    state={'oauth_token': 'abc'}  # ❌ FAILS! Missing subject, last_activity
)
```

**Fix**: Use partial matching with `call_args`:
```python
call_kwargs = mock.create_session.call_args.kwargs
assert call_kwargs['state']['oauth_token'] == 'abc'
# ✅ Don't check auto-generated fields
```

**Pattern**: Only assert keys you control, not auto-generated fields.

---

## Test Isolation Issues

### Issue: GCS Test Data Leakage

**Problem**: Integration tests share real GCS bucket, data from previous runs persists.

**Symptoms**:
- `test_list_sessions` expects 1 session, gets 92 (91 leftover from previous runs)
- Tests pass in clean environment, fail in dirty environment

**Root Cause**: No cleanup between test runs.

**Fix Option 1: Mock GCS** (recommended for integration tests):
```python
@pytest.fixture
def mock_gcs_bucket():
    bucket = Mock(spec=storage.Bucket)
    bucket._blobs = {}  # In-memory storage
    # ... mock upload/download logic
    return bucket
```

**Fix Option 2: Separate Test Bucket + Cleanup**:
```python
@pytest.fixture(scope="session", autouse=True)
def cleanup_test_bucket():
    yield
    # Cleanup after all tests
    bucket = storage_client.bucket("test-bucket")
    for blob in bucket.list_blobs():
        blob.delete()
```

**Pattern**: Integration tests should either mock external services OR use separate test infrastructure with cleanup.

---

## LLM/AI Testing Issues

### Issue: Non-Deterministic LLM Responses

**Problem**: LLM responses vary, exact string assertions fail:
```python
response = agent.chat("Hello")
assert response == "Hello! I'm the GTM Assistant."  # ❌ Fails (response varies)
```

**Fix**: Use semantic assertions:
```python
# ✅ Keyword presence
assert "GTM" in response
assert "Assistant" in response

# ✅ Length bounds
assert 10 < len(response) < 200

# ✅ Structure checks
assert response.startswith("Hello")
assert "?" in response or "." in response
```

**Pattern**: Never assert exact LLM output strings - use semantic matching.

**Full Guide**: See `.claude/skills/testing-strategy/08-ai-llm-testing.md`

---

## Quick Reference

| Error | Root Cause | Fix |
|-------|------------|-----|
| Pydantic ValidationError on import | Env vars not set before Settings import | Set `os.environ` at module level in conftest.py |
| `async def functions are not natively supported` | Missing `@pytest.mark.asyncio` | Add decorator to async tests |
| `AttributeError: ... does not have the attribute` | Mocking lazy imports at wrong path | Mock at source module, not where imported |
| `hasattr()` always True on Mock | Mock allows any attribute | Use `Mock(spec=[...])` |
| `'Mock' object is not iterable` | Mocking complex objects | Use real objects or simple classes |
| `TypeError: 'async for' requires __aiter__` | Async mock not a generator | Add unreachable `yield` |
| Exact dict assertions fail | Production adds extra fields | Use partial matching with `call_args.kwargs` |
| Test data leakage | Shared GCS bucket | Mock GCS or use separate test bucket with cleanup |
| LLM exact string fails | Non-deterministic responses | Use semantic assertions (keywords, length) |

---

## When to Update This Skill

**Add new patterns when**:
- You discover a pytest issue that took >30 minutes to debug
- You find a fix that's not obvious from pytest docs
- You encounter a mock pattern that's tricky to get right
- You discover a testing gotcha specific to this codebase

**Keep it actionable**: Include error message, root cause, fix, and pattern (not just the fix).

---

**Last Updated**: 2025-12-04 by Arc (Main Orchestrator)
