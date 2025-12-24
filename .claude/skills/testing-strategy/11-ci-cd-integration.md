# CI/CD Integration

**When to use**: Automating tests in pipelines, coverage reporting, quality gates.

---

## GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run tests
        run: pytest --cov=src --cov-report=xml --cov-fail-under=80
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## Quality Gates

```yaml
- name: Check coverage
  run: pytest --cov=src --cov-fail-under=80

- name: Security scan
  run: |
    pip install bandit pip-audit
    bandit -r src/ -ll
    pip-audit --desc

- name: Lint
  run: |
    pip install black ruff
    black --check src/
    ruff check src/
```

---

## Test Organization

```
tests/
├── unit/          # Fast, isolated
├── integration/   # API + DB
├── e2e/           # Playwright
├── security/      # OWASP scans
├── conftest.py
└── pytest.ini
```

---

## Summary

### Key Points

1. **Run tests on every push**
2. **Coverage >80% required**
3. **Security scans automated**
4. **Quality gates block bad code**

### Checklist

- [ ] Tests run in CI/CD
- [ ] Coverage reported (Codecov)
- [ ] Security scans automated
- [ ] Quality gates enforced

---

## Cross-References

- **Testing philosophy**: [01-testing-philosophy.md](01-testing-philosophy.md)
- **Unit testing**: [02-unit-testing.md](02-unit-testing.md)
- **Security testing**: [07-security-testing.md](07-security-testing.md)
