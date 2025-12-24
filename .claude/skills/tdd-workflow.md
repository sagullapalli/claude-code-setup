# TDD Workflow - Test-Driven Development

**Last Updated**: 2025-12-04

This skill documents the Test-Driven Development (TDD) workflow for coordinating between Arc (Main Orchestrator), Kai (AI Engineer), and Vera (QA Tester).

---

## TDD Decision Matrix

```
                    TDD?          Why?
┌─────────────────────────────────────────────────────────────┐
│ API Endpoints      ✅ YES      Clear contract, testable      │
│ Service Logic      ✅ YES      Business rules, reproducible  │
│ Utilities          ✅ YES      Pure functions, fast tests    │
│ Bug Fixes          ✅ YES      Regression prevention         │
│ Data Layer         ✅ YES      Queries, ORM, cache logic     │
├─────────────────────────────────────────────────────────────┤
│ UI Components      ❌ NO       Visual feedback loop needed   │
│ AI/LLM Behavior    ❌ NO       Non-deterministic outputs     │
│ Infrastructure     ❌ NO       Validated by terraform plan   │
│ Exploratory Work   ❌ NO       Requirements unclear          │
│ Config Files       ❌ NO       Runtime validation sufficient │
└─────────────────────────────────────────────────────────────┘
```

---

## When to Use TDD

### ✅ USE TDD For:

**1. API Endpoints**
- New REST endpoints
- Endpoint modifications
- Request/response validation
- Error handling

**2. Service Logic**
- Business logic functions
- Data transformations
- State management
- Integration with external services

**3. Utilities & Helpers**
- Data validation functions
- Formatting utilities
- Calculation logic
- Parsers and serializers

**4. Bug Fixes**
- Write failing test that reproduces bug
- Fix the bug
- Verify test passes
- Prevents regression

**5. Data Layer**
- Database queries
- ORM operations
- Data access patterns
- Cache logic

### ❌ DON'T Use TDD For:

**1. UI/Frontend Components**
- Visual design iteration
- Layout adjustments
- CSS styling
- Interactive prototyping
- **Why**: UI requires visual feedback loop, not test-first

**2. AI/LLM Behavior**
- Agent prompts
- Tool descriptions
- Response formatting (non-deterministic)
- **Why**: LLM outputs are non-deterministic, require semantic testing

**3. Infrastructure as Code**
- Terraform configurations
- Deployment scripts
- Cloud resource definitions
- **Why**: IaC is declarative, validated by `terraform plan`, not unit tests

**4. Exploratory Work**
- Prototyping new ideas
- Spike solutions
- Research tasks
- **Why**: Requirements unclear, test-after is more efficient

**5. Configuration Files**
- JSON/YAML configs
- Environment variables
- **Why**: Validated at runtime, not via tests

---

## TDD Cycle: RED → GREEN → REFACTOR

### Phase 1: RED (Write Failing Test)

**Vera writes the test FIRST** (before any implementation exists).

⚠️ **CRITICAL: Import Error Handling**

When Vera writes a test importing code that doesn't exist yet (e.g., `from backend.app.api.routes import list_gtm_accounts`), pytest will crash with an `ImportError` or `Collection Error`. **This is a valid RED state** - do NOT try to fix the import. Kai will create the missing files in Phase 2.

**Valid RED States**:
1. ✅ `ImportError` - Module/function doesn't exist (Kai will create it)
2. ✅ `AssertionError` - Test runs but assertion fails (expected behavior)
3. ✅ `404 Not Found` - Endpoint doesn't exist (Kai will add route)

**Example**: New endpoint to list GTM accounts

```python
# backend/tests/integration/test_gtm_endpoints.py
import pytest
from fastapi.testclient import TestClient

@pytest.mark.integration
def test_list_gtm_accounts(test_client: TestClient):
    """Test listing GTM accounts for authenticated user."""
    # Arrange
    session_id = "test-session"

    # Act
    response = test_client.get(
        "/api/v1/gtm/accounts",
        cookies={"session_id": session_id}
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "accounts" in data
    assert isinstance(data["accounts"], list)
```

**Run test**: `pytest tests/integration/test_gtm_endpoints.py::test_list_gtm_accounts`

**Expected**: ❌ Test FAILS (endpoint doesn't exist yet - returns 404 or ImportError)

---

### Phase 2: GREEN (Minimal Implementation)

**Kai implements the MINIMAL code** to make the test pass.

**Step 2a: Create File Structure** (if ImportError in Phase 1)
```python
# backend/app/api/routes.py
from fastapi import APIRouter

router = APIRouter()

# File exists now - ImportError resolved
```

**Step 2b: Stub Implementation**
```python
# backend/app/api/routes.py
from fastapi import APIRouter, Cookie

router = APIRouter()

@router.get("/api/v1/gtm/accounts")
async def list_gtm_accounts(session_id: str = Cookie(None)):
    """List GTM accounts for authenticated user."""
    # Minimal implementation - just return empty list
    return {"accounts": []}
```

**Run test**: `pytest tests/integration/test_gtm_endpoints.py::test_list_gtm_accounts`

**Expected**: ✅ Test PASSES (with stub)

**Step 2c: Real Implementation**
```python
# backend/app/api/routes.py
from fastapi import APIRouter, Cookie, Depends
from backend.app.services.agent_service import AgentService, get_agent_service

router = APIRouter()

@router.get("/api/v1/gtm/accounts")
async def list_gtm_accounts(
    session_id: str = Cookie(None),
    agent_service: AgentService = Depends(get_agent_service)
):
    """List GTM accounts for authenticated user."""
    # Real implementation - fetch from GTM API
    accounts = await agent_service.list_gtm_accounts(session_id)
    return {"accounts": accounts}
```

**Run test**: `pytest tests/integration/test_gtm_endpoints.py::test_list_gtm_accounts`

**Expected**: ✅ Test STILL PASSES (with real implementation)

---

### Phase 3: REFACTOR (Cleanup & Edge Cases)

**Kai refactors** while keeping tests green. **Vera adds edge case tests**.

**Kai's Refactoring**:
- Add type hints
- Add docstrings
- Add error handling
- Improve code structure

**Vera's Edge Case Tests**:
```python
@pytest.mark.integration
def test_list_gtm_accounts_not_authenticated(test_client: TestClient):
    """Test listing accounts without authentication."""
    response = test_client.get("/api/v1/gtm/accounts")
    assert response.status_code == 401

@pytest.mark.integration
def test_list_gtm_accounts_api_error(test_client: TestClient, app):
    """Test handling GTM API errors using FastAPI dependency injection."""
    from backend.app.services.agent_service import get_agent_service

    # Define mock service that raises error
    class MockErrorService:
        async def list_gtm_accounts(self, session_id):
            raise Exception("GTM API unavailable")

    # Override dependency (preferred for FastAPI)
    app.dependency_overrides[get_agent_service] = lambda: MockErrorService()

    response = test_client.get("/api/v1/gtm/accounts", cookies={"session_id": "test"})
    assert response.status_code == 500

    # Clean up
    app.dependency_overrides = {}

# Alternative: Using mocker.patch (for non-FastAPI code)
@pytest.mark.integration
def test_list_gtm_accounts_api_error_with_patch(test_client: TestClient, mocker):
    """Test handling GTM API errors using mocker.patch."""
    mocker.patch(
        'backend.app.services.agent_service.AgentService.list_gtm_accounts',
        side_effect=Exception("GTM API unavailable")
    )
    response = test_client.get("/api/v1/gtm/accounts", cookies={"session_id": "test"})
    assert response.status_code == 500
```

**Note on FastAPI Testing**: For FastAPI endpoints, **prefer `app.dependency_overrides`** over `mocker.patch` because it's more reliable with async contexts and matches how FastAPI's dependency injection works.

---

## TDD Roles & Coordination

### Arc (Main Orchestrator)
**Responsibilities**:
1. Receive feature request from user
2. Break down into testable requirements
3. Coordinate TDD workflow between Vera and Kai
4. Review test coverage and implementation
5. Approve when feature is complete

**Template for TDD Delegation**:
```markdown
User requests: [Feature description]

DELEGATION:
1. @Vera - Write failing integration test for [feature]
   - Test should verify [expected behavior]
   - Use AAA pattern (Arrange-Act-Assert)
   - Mark with @pytest.mark.integration
   - Expected: Test FAILS (feature not implemented)

2. @Kai - Implement minimal code to pass test
   - Start with stub implementation
   - Run test to verify GREEN
   - Then add real logic (REFACTOR phase)
   - Ensure test stays GREEN

3. @Vera - Add edge case tests
   - Authentication failures
   - Invalid inputs
   - Error handling
   - Boundary conditions
```

---

### Vera (QA Tester)
**Responsibilities**:
1. **RED Phase**: Write failing test FIRST
   - Use AAA pattern (Arrange-Act-Assert)
   - Test expected behavior, not implementation
   - Add descriptive docstring
   - Run test to confirm it FAILS
2. **GREEN Phase**: Verify Kai's implementation passes test
3. **REFACTOR Phase**: Add edge case tests
   - Error handling
   - Boundary conditions
   - Invalid inputs
   - Authentication/authorization

**Vera's Checklist**:
- [ ] Test written with clear docstring
- [ ] Test uses AAA pattern
- [ ] Test run shows RED (failure)
- [ ] Test expectations are clear (no ambiguity)
- [ ] Edge cases identified for later

---

### Kai (AI Engineer)
**Responsibilities**:
1. **GREEN Phase**: Write MINIMAL code to pass test
   - Start with stub (return empty list, hardcoded value, etc.)
   - Run test to verify GREEN
   - Commit stub implementation
2. **REFACTOR Phase**: Replace stub with real logic
   - Add actual implementation
   - Run test after each change (keep it GREEN)
   - Add error handling
   - Add type hints and docstrings
   - Commit production implementation

**Kai's Checklist**:
- [ ] Test is RED before implementation
- [ ] Stub implementation makes test GREEN
- [ ] Real implementation keeps test GREEN
- [ ] Edge case tests all pass
- [ ] Type hints added
- [ ] Docstrings added
- [ ] Error handling added

---

## TDD Examples by Feature Type

### Example 1: Bug Fix

**Scenario**: Agent service crashes on empty message

**RED (Vera)**:
```python
@pytest.mark.unit
def test_chat_with_empty_message():
    """Test chat service rejects empty messages."""
    agent_service = AgentService()

    with pytest.raises(ValueError, match="Message cannot be empty"):
        await agent_service.chat(
            session_id="test",
            message=""  # Empty message
        )
```

**Run**: ❌ Test FAILS (no validation exists)

**GREEN (Kai)**:
```python
# backend/app/services/agent_service.py
async def chat(self, session_id: str, message: str) -> str:
    if not message or not message.strip():
        raise ValueError("Message cannot be empty")
    # ... rest of implementation
```

**Run**: ✅ Test PASSES

**REFACTOR (Kai)**: Add more validation (max length, sanitization)

---

### Example 2: New Utility Function

**Scenario**: Add function to format GTM container names

**RED (Vera)**:
```python
@pytest.mark.unit
def test_format_container_name():
    """Test formatting GTM container names."""
    from backend.app.utils.formatters import format_container_name

    assert format_container_name("My Container") == "my-container"
    assert format_container_name("Test_Container_123") == "test-container-123"
    assert format_container_name("UPPERCASE") == "uppercase"
```

**Run**: ❌ Test FAILS (function doesn't exist)

**GREEN (Kai)**:
```python
# backend/app/utils/formatters.py
def format_container_name(name: str) -> str:
    """Format container name to lowercase-hyphenated format."""
    return name.lower().replace("_", "-").replace(" ", "-")
```

**Run**: ✅ Test PASSES

**REFACTOR (Kai)**: Add edge case handling (empty string, special chars)

---

### Example 3: Service Logic

**Scenario**: Add method to filter expired sessions

**RED (Vera)**:
```python
@pytest.mark.unit
async def test_filter_expired_sessions():
    """Test filtering expired sessions."""
    from datetime import datetime, timedelta, timezone

    session_service = GcsSessionService()

    # Arrange
    now = datetime.now(timezone.utc)
    expired_session = {
        "session_id": "expired",
        "last_activity": (now - timedelta(hours=25)).isoformat()
    }
    active_session = {
        "session_id": "active",
        "last_activity": (now - timedelta(hours=1)).isoformat()
    }

    sessions = [expired_session, active_session]

    # Act
    result = session_service.filter_expired_sessions(sessions, max_age_hours=24)

    # Assert
    assert len(result) == 1
    assert result[0]["session_id"] == "active"
```

**Run**: ❌ Test FAILS (method doesn't exist)

**GREEN (Kai)**:
```python
# backend/app/services/gcs_session_service.py
def filter_expired_sessions(
    self,
    sessions: list[dict],
    max_age_hours: int = 24
) -> list[dict]:
    """Filter out sessions older than max_age_hours."""
    from datetime import datetime, timedelta, timezone

    cutoff = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)

    return [
        s for s in sessions
        if datetime.fromisoformat(s["last_activity"]) > cutoff
    ]
```

**Run**: ✅ Test PASSES

**REFACTOR (Kai)**: Add error handling for malformed timestamps

---

## Common TDD Mistakes

### ❌ Mistake 1: Writing Implementation First
**Wrong**:
```
1. Kai writes endpoint
2. Vera writes test for existing code
```

**Right**:
```
1. Vera writes failing test
2. Kai implements to pass test
```

**Why**: Test-after leads to tests that just verify what code does, not what it should do.

---

### ❌ Mistake 2: Testing Implementation Details
**Wrong**:
```python
def test_chat_calls_gemini_api():
    """Test that chat service calls Gemini API."""
    # Tests HOW it's implemented
    mock_gemini.assert_called_once()
```

**Right**:
```python
def test_chat_returns_valid_response():
    """Test that chat service returns valid response."""
    # Tests WHAT it returns
    response = agent_service.chat("Hello")
    assert isinstance(response, str)
    assert len(response) > 0
```

**Why**: Implementation details change, behavior contracts don't.

---

### ❌ Mistake 3: Skipping RED Phase
**Wrong**:
```
1. Vera writes test
2. Test passes immediately (stub exists)
3. Kai adds real implementation
```

**Right**:
```
1. Vera writes test
2. Test FAILS (no implementation)
3. Kai adds stub → GREEN
4. Kai adds real implementation → GREEN
```

**Why**: If test passes immediately, it might not be testing the right thing.

---

### ❌ Mistake 4: Testing Too Much at Once
**Wrong**:
```python
def test_complete_gtm_workflow():
    """Test entire GTM workflow end-to-end."""
    # 50 lines of test code
    # Tests authentication + listing + creating + deleting
```

**Right**:
```python
def test_list_gtm_accounts():
    """Test listing GTM accounts."""
    # 10 lines - one behavior

def test_create_gtm_container():
    """Test creating GTM container."""
    # 10 lines - one behavior
```

**Why**: Small, focused tests are easier to debug and maintain.

---

## TDD Workflow Checklist

### For New Features

- [ ] **Arc**: Break down feature into testable requirements
- [ ] **Vera**: Write failing integration test (RED) - *Expect ImportErrors if files don't exist*
- [ ] **Vera**: Confirm test FAILS (ImportError, 404, or AssertionError all valid)
- [ ] **Kai**: Create file structure/skeletons to resolve ImportErrors (if needed)
- [ ] **Kai**: Write minimal stub implementation (GREEN - interface)
- [ ] **Kai**: Confirm test PASSES with stub
- [ ] **Kai**: Add real implementation logic (GREEN - production code)
- [ ] **Kai**: Confirm test STILL PASSES with real implementation
- [ ] **Kai**: Refactor code (add type hints, docstrings, error handling)
- [ ] **Vera**: Add edge case tests (auth failures, invalid inputs, errors)
- [ ] **Kai**: Fix edge cases
- [ ] **Arc**: Review coverage and approve

### For Bug Fixes

- [ ] **Vera**: Write failing test that reproduces bug (RED)
- [ ] **Vera**: Confirm test FAILS with bug behavior
- [ ] **Kai**: Fix the bug (GREEN)
- [ ] **Kai**: Confirm test PASSES
- [ ] **Vera**: Add regression tests for related edge cases
- [ ] **Arc**: Approve fix

---

## Integration with Existing Testing Infrastructure

**Unit Tests** (`.../tests/unit/`)
- Test individual functions/methods
- Fast execution (<1s per test)
- Mock external dependencies
- Use TDD for service logic, utilities

**Integration Tests** (`.../tests/integration/`)
- Test API endpoints
- Use TestClient (no real HTTP)
- Mock external APIs (Gemini, GTM)
- Use TDD for API routes

**E2E Tests** (`.../tests/e2e/`)
- Test complete workflows
- Use real dependencies (or close proxies)
- Slower execution (>1s per test)
- DON'T use TDD (too slow for RED-GREEN cycle)

---

## When to Deviate from TDD

**Acceptable Deviations**:
1. **Prototyping**: Exploring uncertain requirements → Write code first, add tests after validation
2. **Emergency Hotfixes**: Production down → Fix first, test immediately after
3. **Refactoring Existing Code**: Tests already exist → Refactor, keep tests green
4. **UI Polish**: Visual iteration required → Build UI, add component tests after

**NOT Acceptable**:
1. "Tests slow me down" → Learn TDD better, tests prevent bugs
2. "I'll add tests later" → Later never comes, always add tests
3. "This code is too simple to test" → Simple code = easy to test

---

## Success Metrics

**TDD is working when**:
- [ ] 90%+ of new code has tests written BEFORE implementation
- [ ] Test failures caught during development, not in production
- [ ] Refactoring is safe (tests catch regressions)
- [ ] Bugs have regression tests (fix + test together)
- [ ] Coverage stays >70% without effort (tests come naturally)

**TDD is NOT working when**:
- [ ] Tests written after implementation (test-after, not TDD)
- [ ] Tests frequently break during refactoring (testing implementation)
- [ ] Bugs found in production (missing test coverage)
- [ ] Developers skip tests "to move faster" (indicates misunderstanding)

---

## Quick Reference

**TDD in 3 Phases**:
1. **RED**: Vera writes failing test (ImportError/404/AssertionError all valid)
2. **GREEN**: Kai creates files → stub → real implementation (test stays green)
3. **REFACTOR**: Kai adds types/docs/error handling, Vera adds edge case tests

**When to use**: APIs, services, utils, bug fixes
**When NOT to use**: UI, AI behavior, IaC, exploratory work

**Roles**:
- **Arc**: Coordinate workflow, review coverage
- **Vera**: Write tests (RED phase + edge cases in REFACTOR)
- **Kai**: Implement code (GREEN = stub + real logic, REFACTOR = cleanup)

**FastAPI Testing Best Practice**: Use `app.dependency_overrides` instead of `mocker.patch` for mocking dependencies in integration tests (more reliable with async contexts)

---

**Last Updated**: 2025-12-04 by Arc (Main Orchestrator)

**See Also**:
- [.claude/skills/testing-strategy/00-testing-troubleshooting.md](.claude/skills/testing-strategy/00-testing-troubleshooting.md) - Common testing issues
- [docs/TESTING_GUIDE.md](../../docs/TESTING_GUIDE.md) - pytest fundamentals
- [docs/PHASE_2_TODOS.md](../../docs/PHASE_2_TODOS.md) - TODO-KB1: Implement TDD workflow
