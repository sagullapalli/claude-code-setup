# Performance Testing

**When to use**: Load testing, profiling, identifying bottlenecks.

---

## Load Testing (Locust)

```python
from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def view_users(self):
        self.client.get("/api/users")
    
    @task(1)
    def create_user(self):
        self.client.post("/api/users", json={
            "email": "test@example.com",
            "name": "Test User"
        })
```

**Run**:
```bash
locust -f locustfile.py --host http://localhost:8000
# Open http://localhost:8089 to configure load test
```

---

## Database Performance

```python
import time

def test_query_performance():
    start = time.time()
    users = db.query(User).filter(User.role == "admin").all()
    duration = time.time() - start
    
    assert duration < 0.1  # <100ms
    assert len(users) > 0
```

---

## Summary

### Key Points

1. **Load test critical endpoints** (Locust)
2. **Profile slow queries** (<100ms target)
3. **Test under realistic load** (100+ concurrent users)

### Checklist

- [ ] Load tests for critical endpoints
- [ ] Database query performance tested
- [ ] Profiling done for slow operations

---

## Cross-References

- **Integration testing**: [03-integration-testing.md](03-integration-testing.md)
- **CI/CD setup**: [11-ci-cd-integration.md](11-ci-cd-integration.md)
