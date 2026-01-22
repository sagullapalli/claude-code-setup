# Integration Testing

**When to use**: Testing component interactions, API endpoints, database operations.

**Focus**: Verify components work together, catch interface bugs.

---

## What to Test (Integration Level)

### ✅ Test These

- **API endpoints**: All routes, status codes, validation
- **Database operations**: CRUD, transactions, constraints
- **Service integration**: Multiple components working together
- **External API integration**: Third-party services (mocked or sandboxed)

### ❌ Don't Test These (covered elsewhere)

- **Business logic** in isolation → Unit tests (Module 2)
- **Complete user journeys** → E2E tests (Module 5)

---

## API Integration Tests (FastAPI)

### FastAPI TestClient Pattern

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_user_endpoint():
    response = client.post("/api/users", json={
        "email": "test@example.com",
        "name": "John Doe"
    })

    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"

def test_get_user_endpoint():
    response = client.get("/api/users/1")

    assert response.status_code == 200
    assert "email" in response.json()

def test_update_user_endpoint():
    response = client.put("/api/users/1", json={
        "name": "Jane Doe"
    })

    assert response.status_code == 200
    assert response.json()["name"] == "Jane Doe"

def test_delete_user_endpoint():
    response = client.delete("/api/users/1")

    assert response.status_code == 204
```

### Testing HTTP Status Codes

```python
def test_create_user_returns_400_with_invalid_email():
    response = client.post("/api/users", json={
        "email": "invalid-email",
        "name": "Test"
    })

    assert response.status_code == 400
    assert "email" in response.json()["detail"].lower()

def test_get_user_returns_404_when_not_found():
    response = client.get("/api/users/99999")

    assert response.status_code == 404

def test_unauthorized_access_returns_401():
    response = client.get("/api/users/me")

    assert response.status_code == 401
```

### Testing Request Validation

```python
@pytest.mark.parametrize("invalid_data,expected_field", [
    ({"email": "invalid", "name": "Test"}, "email"),
    ({"email": "test@example.com", "name": ""}, "name"),
    ({"email": "", "name": "Test"}, "email"),
    ({}, "email"),  # Missing required field
])
def test_create_user_validates_input(invalid_data, expected_field):
    response = client.post("/api/users", json=invalid_data)

    assert response.status_code in [400, 422]
    assert expected_field in str(response.json())
```

---

## Database Integration Tests

### Test Database Setup

**conftest.py:**
```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.main import app, get_db

# Use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="function")
def test_db():
    # Create test database
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()

    # Override dependency
    def override_get_db():
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    yield db

    # Cleanup
    db.close()
    Base.metadata.drop_all(bind=engine)
```

### CRUD Tests

```python
def test_user_repository_creates_user(test_db):
    # Arrange
    repo = UserRepository(test_db)
    user_data = {"email": "test@example.com", "name": "John"}

    # Act
    created_user = repo.create(user_data)

    # Assert
    assert created_user.id is not None
    assert created_user.email == user_data["email"]

def test_user_repository_retrieves_user(test_db):
    # Arrange
    repo = UserRepository(test_db)
    user = repo.create({"email": "test@example.com", "name": "John"})

    # Act
    retrieved_user = repo.get_by_id(user.id)

    # Assert
    assert retrieved_user.id == user.id
    assert retrieved_user.email == user.email

def test_user_repository_updates_user(test_db):
    # Arrange
    repo = UserRepository(test_db)
    user = repo.create({"email": "test@example.com", "name": "John"})

    # Act
    updated_user = repo.update(user.id, {"name": "Jane"})

    # Assert
    assert updated_user.name == "Jane"

def test_user_repository_deletes_user(test_db):
    # Arrange
    repo = UserRepository(test_db)
    user = repo.create({"email": "test@example.com", "name": "John"})

    # Act
    repo.delete(user.id)

    # Assert
    assert repo.get_by_id(user.id) is None
```

### Transaction Tests

```python
def test_transaction_commits_on_success(test_db):
    repo = UserRepository(test_db)

    with test_db.begin():
        user = repo.create({"email": "test@example.com", "name": "John"})

    # Verify data persisted
    retrieved_user = repo.get_by_id(user.id)
    assert retrieved_user is not None

def test_transaction_rolls_back_on_error(test_db):
    repo = UserRepository(test_db)

    try:
        with test_db.begin():
            user = repo.create({"email": "test@example.com", "name": "John"})
            raise Exception("Simulated error")
    except:
        pass

    # Verify data not persisted
    users = repo.get_all()
    assert len(users) == 0
```

### Constraint Tests

```python
def test_unique_constraint_prevents_duplicate_email(test_db):
    repo = UserRepository(test_db)

    # Create first user
    repo.create({"email": "test@example.com", "name": "John"})

    # Try to create duplicate
    with pytest.raises(IntegrityError):
        repo.create({"email": "test@example.com", "name": "Jane"})

def test_foreign_key_constraint_enforced(test_db):
    # Try to create post with non-existent user_id
    with pytest.raises(IntegrityError):
        Post.create(user_id=99999, content="Test post")
```

---

## API + Database Integration

### End-to-End API Tests

```python
def test_create_user_endpoint_persists_to_database(test_db):
    # Create user via API
    response = client.post("/api/users", json={
        "email": "test@example.com",
        "name": "John Doe"
    })

    assert response.status_code == 201
    user_id = response.json()["id"]

    # Verify in database
    user = test_db.query(User).filter_by(id=user_id).first()
    assert user is not None
    assert user.email == "test@example.com"

def test_update_user_endpoint_modifies_database(test_db):
    # Create user
    user = User(email="test@example.com", name="John")
    test_db.add(user)
    test_db.commit()

    # Update via API
    response = client.put(f"/api/users/{user.id}", json={
        "name": "Jane Doe"
    })

    assert response.status_code == 200

    # Verify in database
    test_db.refresh(user)
    assert user.name == "Jane Doe"
```

---

## Test Data Management

### Fixtures for Common Data

```python
@pytest.fixture
def sample_users(test_db):
    users = [
        User(email=f"user{i}@example.com", name=f"User {i}")
        for i in range(10)
    ]
    test_db.add_all(users)
    test_db.commit()
    return users

def test_list_users_returns_all_users(sample_users):
    response = client.get("/api/users")

    assert response.status_code == 200
    assert len(response.json()) == 10
```

### Factory Pattern

```python
class UserFactory:
    def __init__(self, db):
        self.db = db

    def create(self, **kwargs):
        defaults = {
            "email": f"test{random.randint(1000, 9999)}@example.com",
            "name": "Test User"
        }
        defaults.update(kwargs)
        user = User(**defaults)
        self.db.add(user)
        self.db.commit()
        return user

@pytest.fixture
def user_factory(test_db):
    return UserFactory(test_db)

def test_user_creation(user_factory):
    user = user_factory.create(name="Custom Name")
    assert user.name == "Custom Name"
```

---

## Mocking External Services

### Mock Third-Party APIs

```python
@patch('requests.get')
def test_fetch_external_user_data(mock_get, test_db):
    # Setup mock
    mock_get.return_value = Mock(
        status_code=200,
        json=lambda: {"id": 1, "name": "External User"}
    )

    # Call endpoint that fetches from external API
    response = client.get("/api/users/external/1")

    assert response.status_code == 200
    assert response.json()["name"] == "External User"
```

---

## Performance Testing (Integration Level)

### Query Performance

```python
import time

def test_list_users_query_performance(sample_users):
    start = time.time()

    response = client.get("/api/users")

    duration = time.time() - start

    assert response.status_code == 200
    assert duration < 0.5  # Should complete in <500ms
```

---

## Best Practices

### ✅ Do

- **Use test database** (in-memory SQLite or separate test instance)
- **Clean up after tests** (fixtures with teardown)
- **Test all HTTP methods** (GET, POST, PUT, DELETE)
- **Test all status codes** (200, 201, 400, 401, 404, 500)
- **Verify database state** after API calls
- **Mock external APIs** (don't hit real endpoints)

### ❌ Don't

- **Use production database** (ever!)
- **Leave test data** in database
- **Test business logic** here (use unit tests)
- **Test complete user journeys** (use E2E tests)

---

## Summary

### Key Points

1. **Integration tests verify components work together**
2. **Use test database** (in-memory or separate instance)
3. **Test all API endpoints** (routes, status codes, validation)
4. **Verify database operations** (CRUD, transactions, constraints)
5. **Mock external services** (third-party APIs)

### Checklist

- [ ] Test database setup with fixtures
- [ ] All API endpoints tested
- [ ] HTTP status codes verified
- [ ] Database operations tested (CRUD)
- [ ] Transactions tested (commit/rollback)
- [ ] Constraints tested (unique, foreign key)
- [ ] External services mocked
- [ ] Test data cleaned up

---

## Cross-References

- **Testing philosophy**: [01-testing-philosophy.md](01-testing-philosophy.md)
- **Unit testing**: [02-unit-testing.md](02-unit-testing.md)
- **E2E testing**: [05-e2e-testing.md](05-e2e-testing.md)
- **Security testing**: [07-security-testing.md](07-security-testing.md)
- **CI/CD setup**: [11-ci-cd-integration.md](11-ci-cd-integration.md)
