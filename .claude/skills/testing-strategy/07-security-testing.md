# Security Testing

**When to use**: Preventing vulnerabilities, OWASP Top 10, protecting user data.

**CRITICAL**: Test negative cases - what should be blocked!

**Full details**: See `.claude/skills/security-best-practices.md` for comprehensive patterns.

---

## OWASP Top 10 Testing

### 1. SQL Injection Prevention

```python
@pytest.mark.parametrize("malicious_input", [
    "'; DROP TABLE users; --",
    "1' OR '1'='1",
    "1' UNION SELECT * FROM passwords--",
])
def test_sql_injection_prevention(malicious_input):
    response = client.get(f"/api/users/search?email={malicious_input}")
    
    # Should not execute SQL
    assert response.status_code in [200, 400, 404]
    
    # Verify database integrity
    users_count = db.query("SELECT COUNT(*) FROM users").scalar()
    assert users_count > 0  # Table still exists
```

### 2. XSS Prevention

```python
@pytest.mark.parametrize("xss_payload", [
    "<script>alert('XSS')</script>",
    "<img src=x onerror='alert(1)'>",
    "javascript:alert('XSS')",
])
def test_xss_prevention(xss_payload):
    response = client.post("/api/comments", json={"content": xss_payload})
    
    assert response.status_code == 201
    content = response.json()["content"]
    
    # Should be escaped or sanitized
    assert "<script>" not in content.lower()
```

### 3. Authentication Testing

```python
def test_unauthenticated_access_blocked():
    response = client.get("/api/users/me")
    assert response.status_code == 401

def test_authorization_prevents_access_to_other_users():
    user1_token = login("user1@example.com", "password")
    
    response = client.get(
        "/api/users/user2-id/private-data",
        headers={"Authorization": f"Bearer {user1_token}"}
    )
    
    assert response.status_code == 403
```

---

## CSRF Protection

```python
def test_csrf_token_required_for_state_changing_operations():
    # Request without CSRF token
    response = client.post("/api/users", json={"email": "test@example.com"})
    assert response.status_code == 403
    
    # Request with valid CSRF token
    csrf_token = client.get("/api/csrf-token").json()["token"]
    response = client.post(
        "/api/users",
        json={"email": "test@example.com"},
        headers={"X-CSRF-Token": csrf_token}
    )
    assert response.status_code == 201
```

---

## Security Headers

```python
def test_security_headers_present():
    response = client.get("/")
    
    assert "X-Frame-Options" in response.headers
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    
    if is_production():
        assert "Strict-Transport-Security" in response.headers
```

---

## Dependency Scanning

```bash
# Python
pip install pip-audit
pip-audit --desc --require requirements.txt

# JavaScript
npm audit --audit-level=high
```

---

## SAST (Static Analysis)

```bash
# Python: Bandit
bandit -r src/ -ll -f json

# JavaScript: ESLint security plugin
npm install --save-dev eslint-plugin-security
npx eslint --ext .js,.ts src/
```

---

## Summary

### Key Points

1. **Test negative cases** (what should be blocked)
2. **OWASP Top 10** (SQL injection, XSS, auth, CSRF)
3. **Automate scans** (pip-audit, bandit, npm audit)
4. **Security headers** required
5. **Rate limiting** on sensitive endpoints

### Checklist

- [ ] SQL injection tests
- [ ] XSS prevention tests
- [ ] Authentication/authorization tests
- [ ] CSRF protection tests
- [ ] Security headers validated
- [ ] Dependency scanning automated
- [ ] SAST in CI/CD

---

## Cross-References

- **Comprehensive security**: See `.claude/skills/security-best-practices.md`
- **API security**: See `.claude/skills/api-design.md` (Section 5)
- **Integration testing**: [03-integration-testing.md](03-integration-testing.md)
- **CI/CD setup**: [11-ci-cd-integration.md](11-ci-cd-integration.md)
