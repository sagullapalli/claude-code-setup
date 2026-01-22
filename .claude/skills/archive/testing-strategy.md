# Testing Strategy Skill

This skill provides comprehensive testing strategies for building robust, reliable software.

## Usage

Use this skill when you need to:
- Design test strategies and plans
- Implement automated testing
- Choose appropriate testing tools
- Set up CI/CD testing pipelines
- Improve test coverage and quality

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

### Unit Tests (60%)
- Test individual functions/methods
- Fast execution (<1ms per test)
- No external dependencies
- Mock external services
- High code coverage

### Integration Tests (30%)
- Test component interactions
- Database, API, service integration
- Moderate execution time
- Use test databases
- Verify end-to-end flows

### E2E Tests (10%)
- Test complete user journeys
- Browser automation
- Slow execution
- Test critical user paths only
- Catch UI and integration issues

## Testing Strategies by Layer

### 1. Unit Testing

#### What to Test
- Business logic
- Data transformations
- Validation functions
- Utility functions
- Edge cases and error handling

#### Best Practices
```python
# Good: Single responsibility, descriptive name
def test_user_email_validation_rejects_invalid_format():
    user = User(email="invalid-email")
    assert not user.is_valid()
    assert "email" in user.errors

# Bad: Testing multiple things, vague name
def test_user():
    user = User(email="test@example.com", name="John")
    assert user.is_valid()
    assert user.save()
```

#### Patterns
- **AAA Pattern**: Arrange, Act, Assert
- **Given-When-Then**: BDD style
- **Test Fixtures**: Reusable test data
- **Mocking**: Isolate dependencies
- **Parameterized Tests**: Test multiple inputs

### 1.5. Frontend Component Testing

Component tests bridge the gap between unit tests and E2E tests. They test UI components in isolation with rendered DOM, focusing on user interactions and behavior rather than implementation details.

#### What to Test
- User interactions (clicks, typing, form submission)
- Conditional rendering based on props/state
- Component integration with hooks and context
- Error states and loading states
- Accessibility attributes

#### Best Practices

**Good: User-centric queries**
```typescript
// Good: Test from user's perspective
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

test('user can submit login form', async () => {
  // Arrange
  const handleSubmit = jest.fn();
  render(<LoginForm onSubmit={handleSubmit} />);

  // Act
  await userEvent.type(screen.getByLabelText(/email/i), 'test@example.com');
  await userEvent.type(screen.getByLabelText(/password/i), 'password123');
  await userEvent.click(screen.getByRole('button', { name: /sign in/i }));

  // Assert
  expect(handleSubmit).toHaveBeenCalledWith({
    email: 'test@example.com',
    password: 'password123'
  });
});
```

**Bad: Implementation-focused queries**
```typescript
// Bad: Relies on implementation details
test('user can submit login form', () => {
  const { container } = render(<LoginForm />);
  const emailInput = container.querySelector('.email-input');
  const submitBtn = container.querySelector('#submit-btn');

  // Brittle - breaks if CSS classes change
  fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
  fireEvent.click(submitBtn);
});
```

#### Query Priority (Use in this order)
1. **getByRole**: Accessibility-first (buttons, links, headings)
2. **getByLabelText**: Form inputs associated with labels
3. **getByPlaceholderText**: Inputs with placeholder text
4. **getByText**: Non-interactive text content
5. **getByTestId**: Last resort (avoid if possible)

#### Testing Async Behavior

```typescript
test('displays user data after loading', async () => {
  // Mock API call
  jest.spyOn(api, 'fetchUser').mockResolvedValue({
    id: 1,
    name: 'John Doe'
  });

  render(<UserProfile userId={1} />);

  // Loading state
  expect(screen.getByText(/loading/i)).toBeInTheDocument();

  // Wait for data to load
  expect(await screen.findByText('John Doe')).toBeInTheDocument();
  expect(screen.queryByText(/loading/i)).not.toBeInTheDocument();
});
```

#### Mocking Context and Hooks

```typescript
test('user can logout', async () => {
  const mockLogout = jest.fn();

  // Mock auth context
  render(
    <AuthContext.Provider value={{ user: { name: 'John' }, logout: mockLogout }}>
      <UserMenu />
    </AuthContext.Provider>
  );

  await userEvent.click(screen.getByRole('button', { name: /logout/i }));

  expect(mockLogout).toHaveBeenCalled();
});
```

#### Svelte Component Testing

```typescript
import { render, fireEvent } from '@testing-library/svelte';
import Counter from './Counter.svelte';

test('increments counter on button click', async () => {
  // Arrange
  const { getByText, getByRole } = render(Counter, { props: { initial: 0 } });

  // Act
  const button = getByRole('button', { name: /increment/i });
  await fireEvent.click(button);

  // Assert
  expect(getByText('Count: 1')).toBeInTheDocument();
});
```

#### When to Use Component Tests vs E2E Tests

**Component Tests** ✅
- Testing individual component behavior
- Form validation logic
- Conditional rendering
- User interactions within a component
- Fast feedback (runs in <100ms)

**E2E Tests** ✅
- Complete user journeys across pages
- Authentication flows
- Payment/checkout processes
- Critical business paths
- Cross-browser compatibility

### 2. Integration Testing

#### Database Integration Tests
```python
def test_user_repository_creates_and_retrieves_user():
    # Arrange
    repo = UserRepository(test_db)
    user_data = {"email": "test@example.com", "name": "John"}

    # Act
    created_user = repo.create(user_data)
    retrieved_user = repo.get_by_id(created_user.id)

    # Assert
    assert retrieved_user.email == user_data["email"]
    assert retrieved_user.name == user_data["name"]
```

#### API Integration Tests
```python
def test_create_user_endpoint():
    response = client.post("/api/users", json={
        "email": "test@example.com",
        "name": "John Doe"
    })

    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"

    # Verify in database
    user = db.query(User).filter_by(email="test@example.com").first()
    assert user is not None
```

### 3. End-to-End Testing

#### User Journey Tests
```javascript
// Playwright/Cypress example
test('user can sign up and create a post', async ({ page }) => {
  // Navigate to signup
  await page.goto('/signup');

  // Fill form
  await page.fill('input[name="email"]', 'test@example.com');
  await page.fill('input[name="password"]', 'password123');
  await page.click('button[type="submit"]');

  // Verify redirect to dashboard
  await expect(page).toHaveURL('/dashboard');

  // Create a post
  await page.click('text=New Post');
  await page.fill('textarea[name="content"]', 'My first post');
  await page.click('button:has-text("Publish")');

  // Verify post appears
  await expect(page.locator('text=My first post')).toBeVisible();
});
```

### 4. Accessibility Testing

Accessibility testing ensures your application is usable by everyone, including people with disabilities. Automated tools catch ~30-40% of accessibility issues; manual testing is essential for the rest.

#### Why A11y Testing Matters
- **Legal Compliance**: WCAG 2.1 AA is legally required in many jurisdictions
- **Better UX**: Accessible apps are easier for everyone to use
- **SEO Benefits**: Screen reader-friendly content is also search engine-friendly
- **Keyboard Navigation**: Essential for power users and accessibility

#### Automated A11y Testing (Component Level)

**Jest with jest-axe**
```typescript
import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';

expect.extend(toHaveNoViolations);

test('LoginForm has no accessibility violations', async () => {
  const { container } = render(<LoginForm />);

  // Run axe accessibility checks
  const results = await axe(container);

  expect(results).toHaveNoViolations();
});

test('form inputs have proper labels', () => {
  const { getByLabelText } = render(<LoginForm />);

  // These will fail if labels are missing or improperly associated
  expect(getByLabelText(/email/i)).toBeInTheDocument();
  expect(getByLabelText(/password/i)).toBeInTheDocument();
});
```

**Python/FastAPI Backend A11y**
```python
def test_api_returns_accessible_error_messages():
    """Error messages should be descriptive for screen readers"""
    response = client.post("/api/users", json={"email": "invalid"})

    assert response.status_code == 400
    error_data = response.json()

    # Should have human-readable error messages
    assert "detail" in error_data
    assert len(error_data["detail"]) > 10  # Descriptive, not just "Invalid"
    assert "email" in error_data["detail"].lower()
```

#### E2E Accessibility Testing (Playwright)

```typescript
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test('homepage should not have accessibility violations', async ({ page }) => {
  await page.goto('/');

  // Run axe on the page
  const accessibilityScanResults = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
    .analyze();

  expect(accessibilityScanResults.violations).toEqual([]);
});

test('keyboard navigation works on dashboard', async ({ page }) => {
  await page.goto('/dashboard');

  // Tab through interactive elements
  await page.keyboard.press('Tab');
  await expect(page.locator(':focus')).toHaveAttribute('role', 'button');

  // Enter key should activate
  await page.keyboard.press('Enter');
  await expect(page).toHaveURL(/\/new-post/);
});

test('skip to main content link is present', async ({ page }) => {
  await page.goto('/');

  // First tab should focus skip link
  await page.keyboard.press('Tab');
  const skipLink = page.locator('a:has-text("Skip to main content")');
  await expect(skipLink).toBeFocused();

  // Activating skip link should jump to main content
  await page.keyboard.press('Enter');
  await expect(page.locator('main')).toBeFocused();
});
```

#### Common A11y Issues to Test For

**Color Contrast**
```typescript
test('error messages have sufficient contrast', async ({ page }) => {
  await page.goto('/login');

  // Trigger error state
  await page.click('button[type="submit"]');

  // Check contrast ratio (axe will catch this)
  const results = await new AxeBuilder({ page }).analyze();
  const contrastIssues = results.violations.filter(
    v => v.id === 'color-contrast'
  );
  expect(contrastIssues).toHaveLength(0);
});
```

**ARIA Attributes**
```typescript
test('loading states are announced to screen readers', () => {
  const { container } = render(<DataTable isLoading={true} />);

  // Should have aria-busy or role="status"
  const loadingRegion = container.querySelector('[aria-busy="true"]') ||
                        container.querySelector('[role="status"]');

  expect(loadingRegion).toBeInTheDocument();
  expect(loadingRegion).toHaveTextContent(/loading/i);
});

test('form errors are associated with inputs', () => {
  const { getByLabelText, getByText } = render(
    <LoginForm errors={{ email: 'Invalid email' }} />
  );

  const emailInput = getByLabelText(/email/i);
  const errorMessage = getByText('Invalid email');

  // Input should reference error via aria-describedby
  expect(emailInput).toHaveAttribute(
    'aria-describedby',
    expect.stringContaining(errorMessage.id)
  );
  expect(emailInput).toHaveAttribute('aria-invalid', 'true');
});
```

**Keyboard Navigation**
```typescript
test('modal traps focus', async () => {
  const { getByRole } = render(<ConfirmDialog />);

  const modal = getByRole('dialog');
  const closeButton = getByRole('button', { name: /close/i });
  const confirmButton = getByRole('button', { name: /confirm/i });

  // Focus should start on first focusable element
  expect(confirmButton).toHaveFocus();

  // Tab should cycle within modal
  await userEvent.tab();
  expect(closeButton).toHaveFocus();

  await userEvent.tab();
  expect(confirmButton).toHaveFocus(); // Wrapped back

  // Escape should close modal
  await userEvent.keyboard('{Escape}');
  expect(modal).not.toBeInTheDocument();
});
```

#### Manual A11y Testing Checklist

Automated tools can't catch everything. Test manually for:

- [ ] **Screen Reader Testing**: Use NVDA (Windows) or VoiceOver (Mac)
  - Can users understand all content when read aloud?
  - Are interactive elements properly announced?
  - Do dynamic updates get announced?

- [ ] **Keyboard-Only Navigation**: Unplug your mouse
  - Can you reach all interactive elements with Tab?
  - Is the focus indicator always visible?
  - Can you activate all buttons/links with Enter/Space?
  - Can you close modals with Escape?

- [ ] **Zoom and Text Scaling**: Browser zoom to 200%
  - Does content still fit on screen?
  - Are horizontal scrollbars avoided?
  - Do text and buttons remain readable?

- [ ] **Color Blindness**: Use color blindness simulators
  - Is information conveyed without relying only on color?
  - Are error states indicated with icons or text, not just red?

#### A11y Best Practices for Testing

```typescript
// ✅ Good: Semantic HTML, proper labels
test('good form accessibility', () => {
  render(
    <form>
      <label htmlFor="email">Email Address</label>
      <input id="email" type="email" required aria-required="true" />

      <button type="submit">Sign In</button>
    </form>
  );

  // Will pass accessibility checks
});

// ❌ Bad: No labels, non-semantic elements
test('bad form accessibility - will fail', () => {
  render(
    <div>
      <div>Email</div>
      <div contentEditable>Type here</div>
      <div onClick={handleSubmit}>Submit</div>
    </div>
  );

  // Will have multiple violations
});
```

#### WCAG Levels to Target

- **WCAG 2.1 Level A**: Minimum (legal requirement in most places)
- **WCAG 2.1 Level AA**: Standard target (recommended)
- **WCAG 2.1 Level AAA**: Enhanced (gold standard, not always feasible)

**Common WCAG AA Requirements:**
- Color contrast ratio ≥ 4.5:1 for normal text
- Color contrast ratio ≥ 3:1 for large text (18pt+)
- All functionality available via keyboard
- Focus indicators visible
- Form inputs have labels
- Headings follow proper hierarchy (h1 → h2 → h3)

### 5. Security Testing

Security testing ensures your application is protected against common vulnerabilities and attacks. This section covers application-level security testing from a QA perspective.

**Note**: Infrastructure security (GCP IAM, VPC, Cloud SQL hardening), threat modeling, and penetration testing are covered in dedicated security and architecture documentation.

#### Why Security Testing Matters
- **Prevent Data Breaches**: Protect user data and business assets
- **Compliance**: Meet regulatory requirements (GDPR, HIPAA, etc.)
- **Trust**: Maintain user confidence
- **Cost**: Security bugs are expensive to fix in production

#### OWASP Top 10 Testing

Test for the most critical web application security risks:

**1. Injection Attacks (SQL, NoSQL, Command)**

❌ **Bad: Vulnerable to SQL injection**
```python
def get_user(email: str):
    # VULNERABLE - never do this!
    query = f"SELECT * FROM users WHERE email = '{email}'"
    return db.execute(query)

# Test that would exploit this:
def test_sql_injection_vulnerability():
    # This should NOT work if properly secured
    malicious_email = "'; DROP TABLE users; --"
    with pytest.raises(ValueError):  # Should raise, not execute SQL
        get_user(malicious_email)
```

✅ **Good: Protected with parameterized queries**
```python
def get_user(email: str):
    # Safe - uses parameterized query
    query = "SELECT * FROM users WHERE email = ?"
    return db.execute(query, (email,))

def test_sql_injection_prevention():
    malicious_email = "'; DROP TABLE users; --"
    result = get_user(malicious_email)

    # Should treat as literal string, not SQL
    assert result is None  # No user with that email

    # Verify users table still exists
    assert db.table_exists("users")
```

**2. Cross-Site Scripting (XSS)**

```python
def test_xss_prevention_in_api_response():
    """API should sanitize/escape user input"""
    response = client.post("/api/comments", json={
        "content": "<script>alert('XSS')</script>"
    })

    assert response.status_code == 201
    comment = response.json()

    # Should be escaped or sanitized
    assert "<script>" not in comment["content"]
    assert "alert" not in comment["content"]
```

```typescript
// Frontend XSS testing
test('prevents XSS in user-generated content', () => {
  const maliciousContent = '<img src=x onerror="alert(1)">';

  render(<Comment content={maliciousContent} />);

  // Should render as text, not execute script
  const element = screen.getByTestId('comment-content');
  expect(element.innerHTML).not.toContain('<img');
  expect(element.textContent).toContain('&lt;img'); // Escaped
});
```

**3. Authentication & Authorization**

```python
def test_unauthenticated_access_blocked():
    """Protected endpoints require authentication"""
    response = client.get("/api/users/me")
    assert response.status_code == 401
    assert "authentication required" in response.json()["detail"].lower()

def test_authorization_prevents_access_to_other_users():
    """Users can't access other users' data"""
    # Login as user1
    user1_token = login("user1@example.com", "password")

    # Try to access user2's data
    response = client.get(
        "/api/users/user2-id/private-data",
        headers={"Authorization": f"Bearer {user1_token}"}
    )

    assert response.status_code == 403  # Forbidden
    assert "not authorized" in response.json()["detail"].lower()

def test_jwt_token_expiration():
    """Expired tokens should be rejected"""
    expired_token = create_expired_jwt()

    response = client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {expired_token}"}
    )

    assert response.status_code == 401
    assert "expired" in response.json()["detail"].lower()
```

**4. Sensitive Data Exposure**

```python
def test_passwords_not_in_response():
    """User objects should never include password hashes"""
    response = client.get("/api/users/123")
    user = response.json()

    # Should NOT contain password fields
    assert "password" not in user
    assert "password_hash" not in user
    assert "hashed_password" not in user

def test_error_messages_dont_leak_info():
    """Error messages shouldn't reveal system details"""
    response = client.post("/api/auth/login", json={
        "email": "nonexistent@example.com",
        "password": "wrong"
    })

    assert response.status_code == 401
    # Generic message, doesn't reveal if email exists
    assert response.json()["detail"] == "Invalid credentials"
    # NOT: "Email not found" or "Wrong password"
```

**5. Security Headers**

```python
def test_security_headers_present():
    """Critical security headers should be set"""
    response = client.get("/")

    headers = response.headers

    # Prevent clickjacking
    assert "X-Frame-Options" in headers
    assert headers["X-Frame-Options"] in ["DENY", "SAMEORIGIN"]

    # Prevent MIME sniffing
    assert headers.get("X-Content-Type-Options") == "nosniff"

    # XSS protection (legacy but still useful)
    assert "X-XSS-Protection" in headers

    # HTTPS enforcement (if in production)
    if is_production():
        assert "Strict-Transport-Security" in headers
```

#### API Security Testing

**Rate Limiting**
```python
def test_rate_limiting_enforced():
    """API should enforce rate limits"""
    # Make requests beyond limit
    for i in range(101):  # Limit is 100/minute
        response = client.get("/api/users")

    # 101st request should be rate limited
    assert response.status_code == 429  # Too Many Requests
    assert "rate limit" in response.json()["detail"].lower()

    # Should include rate limit headers
    assert "X-RateLimit-Limit" in response.headers
    assert "X-RateLimit-Remaining" in response.headers
    assert "X-RateLimit-Reset" in response.headers

def test_rate_limit_varies_by_user():
    """Authenticated users should have separate rate limits"""
    user1_token = login("user1@example.com", "password")
    user2_token = login("user2@example.com", "password")

    # User1 hits rate limit
    for _ in range(100):
        client.get("/api/data", headers={"Authorization": f"Bearer {user1_token}"})

    # User2 should still be able to make requests
    response = client.get("/api/data", headers={"Authorization": f"Bearer {user2_token}"})
    assert response.status_code == 200
```

**CORS Configuration**
```python
def test_cors_headers_configured():
    """CORS should be properly configured"""
    response = client.options("/api/users")

    assert "Access-Control-Allow-Origin" in response.headers

    # Should NOT be wildcard in production
    if is_production():
        assert response.headers["Access-Control-Allow-Origin"] != "*"

def test_cors_blocks_unauthorized_origins():
    """Requests from unauthorized origins should be blocked"""
    response = client.get(
        "/api/users",
        headers={"Origin": "https://evil.com"}
    )

    # Should either block or not include CORS headers
    if "Access-Control-Allow-Origin" in response.headers:
        assert response.headers["Access-Control-Allow-Origin"] != "https://evil.com"
```

#### Dependency Vulnerability Scanning

**Python Dependencies**
```bash
# In CI/CD pipeline
pip install pip-audit
pip-audit --desc --require requirements.txt

# Or use Safety
pip install safety
safety check --json
```

```python
# pytest integration
def test_no_known_vulnerabilities():
    """Fail if dependencies have known vulnerabilities"""
    result = subprocess.run(
        ["pip-audit", "--desc", "--require", "requirements.txt"],
        capture_output=True
    )

    assert result.returncode == 0, f"Vulnerabilities found:\n{result.stdout.decode()}"
```

**JavaScript Dependencies**
```bash
# In CI/CD pipeline
npm audit --audit-level=high

# Or use Snyk
npx snyk test
```

```json
// package.json script
{
  "scripts": {
    "audit": "npm audit --audit-level=high",
    "audit:fix": "npm audit fix"
  }
}
```

#### Secrets Management Testing

**Prevent Secrets in Code**
```bash
# Install git-secrets (one-time setup)
git secrets --install
git secrets --register-aws

# Scan repository
git secrets --scan

# Or use TruffleHog
truffleHog filesystem . --json
```

**Test Secret Manager Integration**
```python
def test_secrets_loaded_from_secret_manager():
    """Secrets should come from GCP Secret Manager, not env vars"""
    from google.cloud import secretmanager

    # Should use Secret Manager
    secret_value = get_database_password()

    # Should NOT be in environment variables
    assert "DATABASE_PASSWORD" not in os.environ

    # Should be non-empty
    assert secret_value
    assert len(secret_value) > 10

def test_secrets_not_in_logs():
    """Secrets should never appear in logs"""
    with LogCapture() as logs:
        # Operation that uses secrets
        connect_to_database()

    log_output = logs.get_all()

    # Check logs don't contain common secret patterns
    assert "password=" not in log_output.lower()
    assert "api_key=" not in log_output.lower()
    assert "secret=" not in log_output.lower()
```

**Environment Variable Validation**
```python
def test_required_env_vars_set_in_production():
    """Production should use secure configuration"""
    if is_production():
        # Should use Secret Manager, not env vars for secrets
        assert "DATABASE_URL" not in os.environ
        assert "JWT_SECRET" not in os.environ

        # Should have proper configuration
        assert os.getenv("USE_SECRET_MANAGER") == "true"
        assert os.getenv("GCP_PROJECT_ID")
```

#### CI/CD Security Automation

**GitHub Actions Example**
```yaml
name: Security Checks

on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      # Secret scanning
      - name: TruffleHog scan
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./

      # Python dependency scanning
      - name: Python security check
        run: |
          pip install pip-audit safety
          pip-audit --desc
          safety check --json

      # JavaScript dependency scanning
      - name: npm audit
        run: npm audit --audit-level=high

      # SAST (Static Application Security Testing)
      - name: Bandit (Python SAST)
        run: |
          pip install bandit
          bandit -r src/ -ll  # Medium-low severity and up

      - name: ESLint security plugin
        run: |
          npm install eslint-plugin-security
          npx eslint --ext .js,.ts,.tsx src/

      # Fail on high/critical vulnerabilities
      - name: Check for high severity issues
        run: |
          if [ $? -ne 0 ]; then
            echo "Security vulnerabilities found!"
            exit 1
          fi
```

**SAST Tools**

**Python: Bandit**
```bash
# Install
pip install bandit

# Scan
bandit -r src/ -f json -o bandit-report.json

# In pytest
def test_no_security_issues_in_code():
    """Static security analysis should pass"""
    result = subprocess.run(
        ["bandit", "-r", "src/", "-ll"],
        capture_output=True
    )

    assert result.returncode == 0, f"Security issues found:\n{result.stdout.decode()}"
```

**JavaScript: ESLint Security Plugin**
```bash
npm install --save-dev eslint-plugin-security

# .eslintrc.json
{
  "plugins": ["security"],
  "extends": ["plugin:security/recommended"]
}
```

#### Security Testing Checklist

- [ ] **Injection Testing**: SQL, NoSQL, Command injection tests
- [ ] **Authentication**: Login, logout, session management tests
- [ ] **Authorization**: Role-based access control tests
- [ ] **XSS Prevention**: Input sanitization tests
- [ ] **CSRF Protection**: Token validation tests
- [ ] **Sensitive Data**: Ensure no passwords/secrets in responses
- [ ] **Security Headers**: X-Frame-Options, CSP, HSTS, etc.
- [ ] **Rate Limiting**: Enforce API rate limits
- [ ] **CORS**: Proper origin validation
- [ ] **HTTPS**: All traffic encrypted (production)
- [ ] **Dependency Scanning**: No known vulnerabilities (high/critical)
- [ ] **Secret Management**: Secrets from Secret Manager, not env vars
- [ ] **Error Handling**: No stack traces or internal details leaked
- [ ] **Logging**: Security events logged, secrets not logged
- [ ] **SAST**: Static analysis passes (Bandit, ESLint security)

#### Security Testing Best Practices

**Do:**
- ✅ Test negative cases (what should be blocked)
- ✅ Automate security scans in CI/CD
- ✅ Fail builds on high/critical vulnerabilities
- ✅ Test with realistic attack payloads
- ✅ Validate both frontend and backend security
- ✅ Keep dependencies updated
- ✅ Use parameterized queries always
- ✅ Sanitize user input on both client and server

**Don't:**
- ❌ Skip security tests because "we'll pen test later"
- ❌ Test only happy paths
- ❌ Commit secrets to version control
- ❌ Expose detailed error messages in production
- ❌ Use wildcard CORS in production
- ❌ Disable security features for "convenience"
- ❌ Trust client-side validation alone

#### Severity Levels

**Critical**: Fix immediately, block deployment
- Remote code execution
- SQL injection
- Authentication bypass
- Secrets in code

**High**: Fix before next release
- XSS vulnerabilities
- Missing authentication
- Broken authorization
- Known CVEs in dependencies (CVSS > 7.0)

**Medium**: Fix in current sprint
- Missing security headers
- Weak rate limiting
- Information disclosure
- Known CVEs (CVSS 4.0-6.9)

**Low**: Fix when convenient
- Missing CSRF tokens on non-critical forms
- Verbose error messages
- Known CVEs (CVSS < 4.0)

#### Reference Documentation

For comprehensive security testing patterns including advanced attack vectors, refer to:
- **`.claude/skills/security-best-practices.md`**: Complete security implementation patterns
- **OWASP Testing Guide**: https://owasp.org/www-project-web-security-testing-guide/
- **PortSwigger Academy**: Realistic attack payloads and techniques

### 6. Advanced Security Testing Patterns

This section provides comprehensive test patterns for advanced security vulnerabilities, organized by OWASP categories and common attack vectors.

#### Security Testing Core Principles

**Critical Testing Principles:**

1. **Test Negative Cases**: Always test what should be blocked, not just what should work
   - Test malicious inputs (SQL injection, XSS payloads)
   - Test unauthorized access attempts
   - Test invalid authentication tokens
   - Test boundary violations (file size, rate limits)

2. **Prevent TOCTOU (Time-of-Check-Time-of-Use)**:
   - Validate once, use validated value
   - **DNS rebinding**: Resolve DNS once, use IP in request (don't re-resolve)
   - File validation: Check file type once, process same file
   - Race conditions: Use transactions, locks, or atomic operations

3. **Defense in Depth**:
   - Validate on both client and server (never trust client)
   - Use whitelist validation over blacklist
   - Sanitize both input and output (prevent XSS)
   - Multiple layers of security (authentication + authorization + rate limiting)

4. **Use Realistic Attack Payloads**:
   - Use OWASP payloads, not simple test strings
   - Test polyglot attacks (works in multiple contexts)
   - Test encoded/obfuscated payloads
   - Reference PortSwigger Academy for realistic attack patterns

5. **Fail Securely**:
   - On error, deny access (don't default to allow)
   - Log security failures for monitoring
   - Return generic error messages (don't leak info)
   - Timeout operations to prevent resource exhaustion

6. **Automate Security Testing**:
   - Security scans in CI/CD pipeline
   - Fail builds on critical vulnerabilities
   - Continuous dependency scanning
   - Regular DAST scans against staging

**Test Both Positive and Negative:**
- ✅ Valid requests should succeed
- ❌ Invalid requests should fail gracefully
- ❌ Malicious requests should be blocked and logged

#### Security Test Organization

**Recommended directory structure:**
```
tests/
├── security/
│   ├── test_authentication.py      # Login, session, password reset
│   ├── test_authorization.py       # RBAC, permissions, access control
│   ├── test_injection.py           # SQL, NoSQL, Command, LDAP injection
│   ├── test_xss.py                 # Reflected, Stored, DOM XSS
│   ├── test_csrf.py                # CSRF token validation
│   ├── test_ssrf.py                # SSRF prevention, DNS rebinding
│   ├── test_security_headers.py    # CSP, HSTS, X-Frame-Options
│   ├── test_jwt_security.py        # Token validation, rotation
│   ├── test_rate_limiting.py       # API rate limits, brute force
│   ├── test_file_upload.py         # File type, size, malicious files
│   ├── test_sensitive_data.py      # PII exposure, password leaks
│   ├── test_session_security.py    # Session fixation, hijacking
│   └── test_cryptography.py        # Hashing, encryption, tokens
├── conftest.py                      # Shared security fixtures
└── pytest.ini
```

**pytest.ini marker:**
```ini
[pytest]
markers =
    security: Security-focused tests
    critical_security: Critical security tests (block deployment on failure)
```

#### Authentication & Authorization Tests

**JWT Token Validation**
```python
import jwt
import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

def test_expired_jwt_rejected():
    """Expired JWT tokens should be rejected"""
    # Create expired token
    expired_token = jwt.encode(
        {
            "sub": "user@example.com",
            "exp": datetime.utcnow() - timedelta(hours=1)  # Expired 1 hour ago
        },
        SECRET_KEY,
        algorithm="HS256"
    )

    response = client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {expired_token}"}
    )

    assert response.status_code == 401
    assert "expired" in response.json()["detail"].lower()

def test_invalid_jwt_signature_rejected():
    """JWT with invalid signature should be rejected"""
    # Create token with wrong secret
    invalid_token = jwt.encode(
        {"sub": "user@example.com", "exp": datetime.utcnow() + timedelta(hours=1)},
        "wrong-secret-key",
        algorithm="HS256"
    )

    response = client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {invalid_token}"}
    )

    assert response.status_code == 401
    assert "invalid" in response.json()["detail"].lower()

def test_jwt_missing_required_claims():
    """JWT without required claims should be rejected"""
    # Missing 'sub' claim
    token = jwt.encode(
        {"exp": datetime.utcnow() + timedelta(hours=1)},
        SECRET_KEY,
        algorithm="HS256"
    )

    response = client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 401

def test_jwt_token_not_in_response_body():
    """JWT tokens should never appear in API responses"""
    response = client.post("/api/auth/login", json={
        "email": "user@example.com",
        "password": "correct_password"
    })

    assert response.status_code == 200

    # Token should be in HttpOnly cookie, not response body
    response_body = json.dumps(response.json())
    assert "token" not in response_body.lower()
    assert "jwt" not in response_body.lower()

    # Should be in Set-Cookie header
    assert "Set-Cookie" in response.headers
    cookie = response.headers["Set-Cookie"]
    assert "HttpOnly" in cookie
    assert "Secure" in cookie  # Production only
    assert "SameSite" in cookie

def test_jwt_token_rotation():
    """Tokens should be rotated on privilege escalation"""
    # Login as regular user
    login_response = client.post("/api/auth/login", json={
        "email": "user@example.com",
        "password": "password"
    })
    old_token = login_response.cookies.get("access_token")

    # Upgrade to admin
    upgrade_response = client.post(
        "/api/users/me/upgrade-to-admin",
        cookies={"access_token": old_token}
    )

    new_token = upgrade_response.cookies.get("access_token")

    # Should have new token
    assert new_token != old_token

    # Old token should be invalidated
    response = client.get(
        "/api/admin/users",
        cookies={"access_token": old_token}
    )
    assert response.status_code == 401
```

**Session Management Security**
```python
def test_session_fixation_prevention():
    """Session ID should change after login"""
    # Get session ID before login
    response1 = client.get("/")
    session_id_before = response1.cookies.get("session_id")

    # Login
    login_response = client.post("/api/auth/login", json={
        "email": "user@example.com",
        "password": "password"
    }, cookies={"session_id": session_id_before})

    session_id_after = login_response.cookies.get("session_id")

    # Session ID should be different (prevents fixation)
    assert session_id_after != session_id_before

def test_session_hijacking_prevention():
    """Session should be invalidated on logout"""
    # Login
    login_response = client.post("/api/auth/login", json={
        "email": "user@example.com",
        "password": "password"
    })
    session_id = login_response.cookies.get("session_id")

    # Verify session works
    response = client.get("/api/users/me", cookies={"session_id": session_id})
    assert response.status_code == 200

    # Logout
    client.post("/api/auth/logout", cookies={"session_id": session_id})

    # Session should be invalid
    response = client.get("/api/users/me", cookies={"session_id": session_id})
    assert response.status_code == 401

def test_concurrent_session_limit():
    """User should have limited concurrent sessions"""
    # Login from device 1
    response1 = client.post("/api/auth/login", json={
        "email": "user@example.com",
        "password": "password"
    })
    session1 = response1.cookies.get("session_id")

    # Login from device 2
    response2 = client.post("/api/auth/login", json={
        "email": "user@example.com",
        "password": "password"
    })
    session2 = response2.cookies.get("session_id")

    # Login from device 3
    response3 = client.post("/api/auth/login", json={
        "email": "user@example.com",
        "password": "password"
    })
    session3 = response3.cookies.get("session_id")

    # Oldest session (session1) should be invalidated
    response = client.get("/api/users/me", cookies={"session_id": session1})
    assert response.status_code == 401

    # Newer sessions should still work
    response = client.get("/api/users/me", cookies={"session_id": session2})
    assert response.status_code == 200
```

**Login Security Tests**
```python
def test_login_rate_limiting():
    """Login endpoint should enforce rate limiting"""
    # Attempt 10 failed logins
    for i in range(10):
        response = client.post("/api/auth/login", json={
            "email": "user@example.com",
            "password": f"wrong_password_{i}"
        })

    # 11th attempt should be rate limited
    response = client.post("/api/auth/login", json={
        "email": "user@example.com",
        "password": "any_password"
    })

    assert response.status_code == 429
    assert "too many attempts" in response.json()["detail"].lower()

def test_account_lockout_after_failed_attempts():
    """Account should lock after N failed login attempts"""
    # 5 failed attempts
    for i in range(5):
        client.post("/api/auth/login", json={
            "email": "user@example.com",
            "password": "wrong_password"
        })

    # Even with correct password, account should be locked
    response = client.post("/api/auth/login", json={
        "email": "user@example.com",
        "password": "correct_password"
    })

    assert response.status_code == 403
    assert "account locked" in response.json()["detail"].lower()

def test_password_reset_flow_security():
    """Password reset should be secure"""
    # Request reset
    response = client.post("/api/auth/password-reset-request", json={
        "email": "user@example.com"
    })

    assert response.status_code == 200
    # Should not reveal if email exists
    assert response.json()["message"] == "If that email exists, you'll receive a reset link"

    # Reset token should expire
    expired_token = create_expired_reset_token("user@example.com")
    response = client.post("/api/auth/password-reset", json={
        "token": expired_token,
        "new_password": "NewPassword123!"
    })

    assert response.status_code == 400
    assert "expired" in response.json()["detail"].lower()

def test_password_reset_single_use_token():
    """Password reset tokens should be single-use"""
    # Get valid reset token
    reset_token = create_password_reset_token("user@example.com")

    # Use token once
    response1 = client.post("/api/auth/password-reset", json={
        "token": reset_token,
        "new_password": "NewPassword123!"
    })
    assert response1.status_code == 200

    # Try to reuse token
    response2 = client.post("/api/auth/password-reset", json={
        "token": reset_token,
        "new_password": "AnotherPassword123!"
    })

    assert response2.status_code == 400
    assert "invalid" in response2.json()["detail"].lower()
```

**Role-Based Access Control (RBAC)**
```python
@pytest.mark.parametrize("role,endpoint,expected_status", [
    ("admin", "/api/admin/users", 200),
    ("user", "/api/admin/users", 403),
    ("guest", "/api/admin/users", 403),
    ("admin", "/api/users/me", 200),
    ("user", "/api/users/me", 200),
    ("guest", "/api/users/me", 401),  # Not authenticated
])
def test_rbac_enforcement(role, endpoint, expected_status):
    """Role-based access control should be enforced"""
    if role == "guest":
        # No authentication
        response = client.get(endpoint)
    else:
        # Login with role
        token = login_as_role(role)
        response = client.get(
            endpoint,
            headers={"Authorization": f"Bearer {token}"}
        )

    assert response.status_code == expected_status

def test_horizontal_privilege_escalation_prevention():
    """Users should not access other users' resources"""
    # Login as user1
    user1_token = login("user1@example.com", "password")

    # Try to access user2's profile
    response = client.get(
        "/api/users/user2-id/profile",
        headers={"Authorization": f"Bearer {user1_token}"}
    )

    assert response.status_code == 403
    assert "not authorized" in response.json()["detail"].lower()

def test_vertical_privilege_escalation_prevention():
    """Regular users should not access admin endpoints"""
    user_token = login("user@example.com", "password")

    response = client.post(
        "/api/admin/delete-all-users",
        headers={"Authorization": f"Bearer {user_token}"}
    )

    assert response.status_code == 403

def test_permission_check_consistency():
    """Permission checks should be consistent across all endpoints"""
    user_token = login("user@example.com", "password")

    # Try multiple protected endpoints
    protected_endpoints = [
        "/api/admin/users",
        "/api/admin/settings",
        "/api/admin/logs"
    ]

    for endpoint in protected_endpoints:
        response = client.get(
            endpoint,
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 403, f"{endpoint} should block regular users"
```

#### Injection Attack Tests

**SQL Injection Prevention**
```python
@pytest.mark.parametrize("malicious_input", [
    "'; DROP TABLE users; --",
    "1' OR '1'='1",
    "1' UNION SELECT * FROM passwords--",
    "admin'--",
    "1'; DELETE FROM users WHERE '1'='1",
    "1' AND (SELECT COUNT(*) FROM users) > 0--",
])
def test_sql_injection_prevention(malicious_input):
    """API should prevent SQL injection attacks"""
    # Try SQL injection in search parameter
    response = client.get(f"/api/users/search?email={malicious_input}")

    # Should not execute SQL, should treat as literal string
    assert response.status_code in [200, 400, 404]

    # Verify database integrity
    users_count = db.query("SELECT COUNT(*) FROM users").scalar()
    assert users_count > 0  # Table still exists

def test_parameterized_queries_enforced():
    """All database queries should use parameterized statements"""
    # This test ensures ORM/query builder is used, not string concatenation
    import inspect
    from src.database import queries

    # Scan all query functions
    for name, obj in inspect.getmembers(queries):
        if callable(obj):
            source = inspect.getsource(obj)

            # Should not contain f-strings or .format() with SQL
            assert "f\"SELECT" not in source
            assert "f'SELECT" not in source
            assert ".format(" not in source or "SELECT" not in source

            # Should use parameterized syntax
            if "SELECT" in source:
                assert "?" in source or "%" in source  # Parameterized placeholders
```

**NoSQL Injection Prevention**
```python
@pytest.mark.parametrize("malicious_input", [
    {"$gt": ""},  # MongoDB operator injection
    {"$ne": None},
    {"$regex": ".*"},
    '{"$gt": ""}',  # JSON string that could be parsed
])
def test_nosql_injection_prevention(malicious_input):
    """Prevent NoSQL injection attacks"""
    response = client.post("/api/users/search", json={
        "email": malicious_input
    })

    # Should validate input type, not execute operators
    assert response.status_code == 400
    assert "invalid" in response.json()["detail"].lower()

def test_nosql_input_sanitization():
    """NoSQL queries should sanitize operator characters"""
    # Input with $ operator
    response = client.get("/api/users/search?name[$ne]=admin")

    # Should treat $ as literal character or reject
    assert response.status_code in [400, 404]
```

**Command Injection Prevention**
```python
@pytest.mark.parametrize("malicious_input", [
    "; ls -la",
    "| cat /etc/passwd",
    "&& rm -rf /",
    "$(cat /etc/passwd)",
    "`whoami`",
    "\n cat /etc/shadow",
])
def test_command_injection_prevention(malicious_input):
    """Prevent command injection in system calls"""
    # Endpoint that processes files (e.g., image conversion)
    response = client.post("/api/files/process", json={
        "filename": f"test{malicious_input}.txt"
    })

    # Should reject or sanitize input
    assert response.status_code in [400, 422]

def test_subprocess_safety():
    """Subprocess calls should use safe parameter passing"""
    import subprocess
    from src.utils import file_processor

    # Test that subprocess is called with list args (safe)
    # NOT with shell=True (unsafe)

    # Good pattern check
    source = inspect.getsource(file_processor.process_file)

    # Should NOT use shell=True
    assert "shell=True" not in source

    # Should use list arguments
    assert "subprocess.run([" in source or "subprocess.Popen([" in source
```

**LDAP Injection Prevention**
```python
@pytest.mark.parametrize("malicious_input", [
    "*)(uid=*",
    "admin)(&(password=*))",
    "*)(objectClass=*",
])
def test_ldap_injection_prevention(malicious_input):
    """Prevent LDAP injection in directory lookups"""
    response = client.get(f"/api/ldap/search?username={malicious_input}")

    assert response.status_code in [400, 404]
    # Should not return all users
    if response.status_code == 200:
        assert len(response.json()["users"]) < 100
```

#### XSS Prevention Tests

**Reflected XSS**
```python
@pytest.mark.parametrize("xss_payload", [
    "<script>alert('XSS')</script>",
    "<img src=x onerror='alert(1)'>",
    "<svg/onload=alert('XSS')>",
    "javascript:alert('XSS')",
    "<iframe src='javascript:alert(1)'>",
    "<body onload=alert('XSS')>",
    "'-alert(1)-'",
    "\"><script>alert(String.fromCharCode(88,83,83))</script>",
])
def test_reflected_xss_prevention(xss_payload):
    """API should prevent reflected XSS in query parameters"""
    response = client.get(f"/api/search?q={xss_payload}")

    # Response should escape or sanitize
    assert response.status_code == 200
    content = response.text

    # Should not contain unescaped script tags
    assert "<script>" not in content.lower()
    assert "onerror=" not in content.lower()
    assert "onload=" not in content.lower()

    # Should be HTML-escaped
    if xss_payload in content:
        assert "&lt;script&gt;" in content or xss_payload not in content

def test_url_parameter_sanitization():
    """URL parameters should be sanitized before rendering"""
    response = client.get("/api/redirect?url=javascript:alert('XSS')")

    # Should reject or sanitize javascript: protocol
    assert response.status_code in [400, 422]
    if response.status_code == 302:  # If redirect allowed
        location = response.headers.get("Location", "")
        assert not location.startswith("javascript:")
        assert not location.startswith("data:")
```

**Stored XSS**
```python
def test_stored_xss_prevention():
    """User input should be sanitized before storage and rendering"""
    # Store malicious content
    xss_content = "<script>alert('Stored XSS')</script>"

    response = client.post("/api/comments", json={
        "content": xss_content
    })

    assert response.status_code == 201
    comment_id = response.json()["id"]

    # Retrieve comment
    response = client.get(f"/api/comments/{comment_id}")
    stored_content = response.json()["content"]

    # Should be sanitized or escaped
    assert "<script>" not in stored_content.lower()

    # Either stripped or HTML-escaped
    assert (
        "alert" not in stored_content or
        "&lt;script&gt;" in stored_content
    )

def test_rich_text_xss_prevention():
    """Rich text fields should allow safe HTML only"""
    # Malicious rich text
    rich_text = """
    <p>Safe paragraph</p>
    <script>alert('XSS')</script>
    <img src=x onerror="alert(1)">
    <a href="javascript:alert(1)">Click me</a>
    """

    response = client.post("/api/posts", json={
        "content": rich_text
    })

    assert response.status_code == 201
    post_id = response.json()["id"]

    # Retrieve post
    response = client.get(f"/api/posts/{post_id}")
    sanitized_content = response.json()["content"]

    # Should keep safe tags
    assert "<p>" in sanitized_content

    # Should remove dangerous tags
    assert "<script>" not in sanitized_content.lower()
    assert "onerror=" not in sanitized_content.lower()
    assert "javascript:" not in sanitized_content.lower()
```

**DOM-Based XSS**
```typescript
// Frontend component test
test('prevents DOM-based XSS', () => {
  // User-controlled input
  const maliciousHash = "#<img src=x onerror='alert(1)'>";

  // Simulate URL hash
  window.location.hash = maliciousHash;

  render(<SearchResults />);

  // Component should not execute script
  const container = screen.getByTestId('search-container');

  // Should be text content, not HTML
  expect(container.innerHTML).not.toContain('<img');
  expect(container.textContent).toContain('&lt;img'); // Escaped
});

test('innerHTML usage is safe', () => {
  const userInput = "<script>alert('XSS')</script>";

  render(<UserProfile bio={userInput} />);

  const bioElement = screen.getByTestId('user-bio');

  // Should use textContent or dangerouslySetInnerHTML with sanitization
  expect(bioElement.innerHTML).not.toContain('<script>');
});
```

**JSON Response XSS**
```python
def test_json_response_xss_prevention():
    """JSON responses should not be exploitable when rendered"""
    response = client.post("/api/users", json={
        "name": "</script><script>alert('XSS')</script>"
    })

    assert response.status_code == 201
    user = response.json()

    # JSON should have proper Content-Type
    assert response.headers["Content-Type"] == "application/json"

    # Should not be exploitable if accidentally rendered as HTML
    assert "</script>" not in user["name"]
```

**CSV Injection (Formula Injection)**
```python
def test_csv_injection_prevention():
    """CSV exports should prevent formula injection"""
    # Create user with malicious name
    client.post("/api/users", json={
        "name": "=1+1+cmd|'/c calc'!A1",
        "email": "user@example.com"
    })

    # Export to CSV
    response = client.get("/api/users/export.csv")

    csv_content = response.text

    # Should escape formula characters
    assert not csv_content.startswith("=")
    assert not csv_content.startswith("+")
    assert not csv_content.startswith("-")
    assert not csv_content.startswith("@")

    # Should prefix with single quote or tab
    assert csv_content.startswith("'=") or csv_content.startswith("\t=")
```

#### CSRF Protection Tests

**CSRF Token Validation**
```python
def test_csrf_token_required_for_state_changing_operations():
    """POST/PUT/DELETE should require CSRF token"""
    # Get CSRF token
    response = client.get("/api/csrf-token")
    csrf_token = response.json()["token"]

    # Request without CSRF token
    response = client.post("/api/users", json={
        "email": "user@example.com",
        "name": "Test User"
    })

    assert response.status_code == 403
    assert "csrf" in response.json()["detail"].lower()

    # Request with valid CSRF token
    response = client.post(
        "/api/users",
        json={"email": "user@example.com", "name": "Test User"},
        headers={"X-CSRF-Token": csrf_token}
    )

    assert response.status_code == 201

def test_csrf_token_single_use():
    """CSRF tokens should be single-use (synchronizer token pattern)"""
    response = client.get("/api/csrf-token")
    csrf_token = response.json()["token"]

    # Use token once
    response1 = client.post(
        "/api/users",
        json={"email": "user1@example.com", "name": "User 1"},
        headers={"X-CSRF-Token": csrf_token}
    )
    assert response1.status_code == 201

    # Try to reuse token
    response2 = client.post(
        "/api/users",
        json={"email": "user2@example.com", "name": "User 2"},
        headers={"X-CSRF-Token": csrf_token}
    )

    assert response2.status_code == 403

def test_csrf_samesite_cookie():
    """Session cookies should have SameSite attribute"""
    response = client.post("/api/auth/login", json={
        "email": "user@example.com",
        "password": "password"
    })

    set_cookie = response.headers.get("Set-Cookie", "")

    assert "SameSite=Strict" in set_cookie or "SameSite=Lax" in set_cookie

def test_csrf_get_requests_safe():
    """GET requests should not change state (CSRF-safe)"""
    # GET should not create/update/delete
    response = client.get("/api/users/delete?id=123")

    # Should be 405 Method Not Allowed or no state change
    assert response.status_code in [405, 404]

def test_csrf_double_submit_cookie():
    """Double-submit cookie pattern should be enforced"""
    # Set CSRF cookie
    response = client.get("/")
    csrf_cookie = response.cookies.get("csrf_token")

    # Submit with matching CSRF header
    response = client.post(
        "/api/users",
        json={"email": "user@example.com", "name": "Test"},
        headers={"X-CSRF-Token": csrf_cookie},
        cookies={"csrf_token": csrf_cookie}
    )

    assert response.status_code == 201

    # Submit with mismatched CSRF token
    response = client.post(
        "/api/users",
        json={"email": "user2@example.com", "name": "Test 2"},
        headers={"X-CSRF-Token": "wrong-token"},
        cookies={"csrf_token": csrf_cookie}
    )

    assert response.status_code == 403
```

#### SSRF Prevention Tests

**DNS Rebinding Prevention (Critical)**
```python
import socket
from unittest.mock import patch

def test_ssrf_blocks_private_ips():
    """SSRF prevention should block private IP ranges"""
    private_ips = [
        "http://127.0.0.1/admin",
        "http://192.168.1.1/internal",
        "http://10.0.0.1/secret",
        "http://172.16.0.1/data",
        "http://localhost/admin",
        "http://[::1]/admin",  # IPv6 localhost
        "http://169.254.169.254/latest/meta-data/",  # AWS metadata
    ]

    for url in private_ips:
        response = client.post("/api/fetch-url", json={"url": url})

        assert response.status_code == 400
        assert "private" in response.json()["detail"].lower() or \
               "internal" in response.json()["detail"].lower()

def test_ssrf_dns_rebinding_prevention():
    """Prevent DNS rebinding attacks (TOCTOU vulnerability)"""
    # Mock DNS resolution to change between validation and request
    with patch('socket.getaddrinfo') as mock_dns:
        # First call: return safe IP (validation)
        # Second call: return private IP (actual request)
        mock_dns.side_effect = [
            [( socket.AF_INET, socket.SOCK_STREAM, 6, '', ('1.2.3.4', 80))],  # Safe
            [(socket.AF_INET, socket.SOCK_STREAM, 6, '', ('127.0.0.1', 80))]   # Private!
        ]

        response = client.post("/api/fetch-url", json={
            "url": "http://evil.com/redirect"
        })

        # Should still block because IP is resolved once and reused
        assert response.status_code == 400

def test_ssrf_url_scheme_validation():
    """Only allow http/https schemes"""
    dangerous_schemes = [
        "file:///etc/passwd",
        "ftp://internal-server/data",
        "gopher://internal:70",
        "dict://localhost:11211/stats",
        "sftp://internal-server/",
    ]

    for url in dangerous_schemes:
        response = client.post("/api/fetch-url", json={"url": url})

        assert response.status_code == 400
        assert "scheme" in response.json()["detail"].lower() or \
               "protocol" in response.json()["detail"].lower()

def test_ssrf_redirect_blocking():
    """SSRF should not follow redirects to private IPs"""
    # URL that redirects to private IP
    response = client.post("/api/fetch-url", json={
        "url": "http://example.com/redirect-to-localhost"
    })

    # Should either:
    # 1. Not follow redirects, OR
    # 2. Validate redirect target
    assert response.status_code in [400, 200]

    if response.status_code == 200:
        # Should not contain private data
        assert "internal" not in response.text.lower()

def test_ssrf_timeout_enforcement():
    """SSRF requests should have timeout"""
    import time

    start_time = time.time()

    # Request to slow server
    response = client.post("/api/fetch-url", json={
        "url": "http://httpbin.org/delay/30"  # 30 second delay
    })

    duration = time.time() - start_time

    # Should timeout before 30 seconds
    assert duration < 10
    assert response.status_code in [400, 408, 504]  # Timeout error
```

**Correct SSRF Prevention Implementation**
```python
# Example of secure SSRF prevention
import socket
import ipaddress
from urllib.parse import urlparse

def is_safe_url(url: str) -> bool:
    """Validate URL is not targeting private networks"""
    parsed = urlparse(url)

    # Only allow http/https
    if parsed.scheme not in ['http', 'https']:
        return False

    hostname = parsed.hostname
    if not hostname:
        return False

    # Resolve DNS ONCE
    try:
        addr_info = socket.getaddrinfo(hostname, None, socket.AF_INET)
        ip_str = addr_info[0][4][0]
    except socket.gaierror:
        return False

    # Check if IP is private
    ip = ipaddress.ip_address(ip_str)

    if ip.is_private or ip.is_loopback or ip.is_link_local:
        return False

    # Check for cloud metadata IPs
    if str(ip).startswith('169.254'):  # AWS/Azure metadata
        return False

    return True

@app.post("/api/fetch-url")
async def fetch_url(url: str):
    if not is_safe_url(url):
        raise HTTPException(400, "URL targets private network")

    # Use the resolved IP, not hostname (prevent DNS rebinding)
    parsed = urlparse(url)
    addr_info = socket.getaddrinfo(parsed.hostname, None, socket.AF_INET)
    ip = addr_info[0][4][0]

    # Build URL with IP instead of hostname
    safe_url = f"{parsed.scheme}://{ip}{parsed.path}"

    # Add original Host header
    headers = {"Host": parsed.hostname}

    async with httpx.AsyncClient(timeout=5.0, follow_redirects=False) as client:
        response = await client.get(safe_url, headers=headers)

    return response.json()
```

#### File Upload Security Tests

**File Type Validation**
```python
def test_file_upload_validates_mime_type():
    """File uploads should validate MIME type"""
    # Upload executable disguised as image
    malicious_file = io.BytesIO(b"MZ\x90\x00")  # PE header (Windows executable)
    malicious_file.name = "image.jpg"

    response = client.post("/api/upload", files={
        "file": ("image.jpg", malicious_file, "image/jpeg")
    })

    # Should detect real file type (magic bytes)
    assert response.status_code == 400
    assert "file type" in response.json()["detail"].lower()

def test_file_upload_magic_bytes_validation():
    """Validate file content, not just extension"""
    # Valid JPEG magic bytes
    jpeg_data = b"\xFF\xD8\xFF\xE0\x00\x10JFIF"

    # Test extension mismatch
    response = client.post("/api/upload", files={
        "file": ("file.txt", io.BytesIO(jpeg_data), "text/plain")
    })

    # Should validate against magic bytes
    assert response.status_code in [200, 400]

def test_file_upload_size_limit():
    """File uploads should enforce size limits"""
    # Create 11MB file (limit is 10MB)
    large_file = io.BytesIO(b"A" * (11 * 1024 * 1024))

    response = client.post("/api/upload", files={
        "file": ("large.jpg", large_file, "image/jpeg")
    })

    assert response.status_code == 413  # Payload Too Large

def test_file_upload_path_traversal_prevention():
    """File uploads should prevent path traversal"""
    malicious_filenames = [
        "../../../etc/passwd",
        "..\\..\\..\\windows\\system32\\config\\sam",
        "../../app/config.py",
    ]

    for filename in malicious_filenames:
        response = client.post("/api/upload", files={
            "file": (filename, io.BytesIO(b"data"), "text/plain")
        })

        assert response.status_code == 400

        # Verify file wasn't created outside upload directory
        assert not os.path.exists("/etc/passwd_uploaded")

def test_file_upload_malicious_content_detection():
    """Detect malicious file content"""
    # SVG with embedded JavaScript
    malicious_svg = b"""<svg xmlns="http://www.w3.org/2000/svg">
        <script>alert('XSS')</script>
    </svg>"""

    response = client.post("/api/upload", files={
        "file": ("image.svg", io.BytesIO(malicious_svg), "image/svg+xml")
    })

    # Should either reject SVG or sanitize
    assert response.status_code in [400, 201]

    if response.status_code == 201:
        # Verify sanitization
        file_id = response.json()["id"]
        stored_content = get_uploaded_file_content(file_id)
        assert b"<script>" not in stored_content
```

#### Cryptography Tests

**Password Hashing**
```python
def test_passwords_use_strong_hashing():
    """Passwords should use Argon2 or bcrypt"""
    from src.auth import hash_password

    hashed = hash_password("MyPassword123!")

    # Should use Argon2 (preferred) or bcrypt
    assert hashed.startswith("$argon2") or hashed.startswith("$2b$")

    # Should be sufficiently long
    assert len(hashed) > 50

def test_password_hashing_includes_salt():
    """Each password should have unique salt"""
    password = "SamePassword123!"

    hash1 = hash_password(password)
    hash2 = hash_password(password)

    # Different hashes due to unique salts
    assert hash1 != hash2

def test_token_generation_cryptographically_secure():
    """Tokens should be cryptographically random"""
    import secrets
    from src.auth import generate_token

    tokens = [generate_token() for _ in range(100)]

    # No duplicates
    assert len(tokens) == len(set(tokens))

    # Sufficient length
    for token in tokens:
        assert len(token) >= 32

def test_encryption_uses_authenticated_encryption():
    """Encryption should use AEAD (e.g., AES-GCM)"""
    from src.crypto import encrypt, decrypt

    plaintext = "Sensitive data"
    ciphertext = encrypt(plaintext)

    # Should be different each time (nonce/IV)
    ciphertext2 = encrypt(plaintext)
    assert ciphertext != ciphertext2

    # Should decrypt correctly
    assert decrypt(ciphertext) == plaintext

    # Tampering should be detected
    tampered = ciphertext[:-1] + b"X"
    with pytest.raises(Exception):  # Authentication failure
        decrypt(tampered)
```

#### Security Scanning Automation

**Static Application Security Testing (SAST)**
```python
def test_bandit_security_scan_passes():
    """Python code should pass Bandit security scan"""
    import subprocess

    result = subprocess.run(
        ["bandit", "-r", "src/", "-ll", "-f", "json"],
        capture_output=True
    )

    output = json.loads(result.stdout)

    # No high/medium severity issues
    high_severity = [i for i in output.get("results", []) if i["issue_severity"] == "HIGH"]
    medium_severity = [i for i in output.get("results", []) if i["issue_severity"] == "MEDIUM"]

    assert len(high_severity) == 0, f"High severity issues found: {high_severity}"
    assert len(medium_severity) == 0, f"Medium severity issues found: {medium_severity}"

def test_semgrep_security_rules():
    """Code should pass Semgrep security rules"""
    result = subprocess.run(
        ["semgrep", "--config=auto", "--json", "src/"],
        capture_output=True
    )

    output = json.loads(result.stdout)

    # Filter for security findings
    security_findings = [
        f for f in output.get("results", [])
        if "security" in f.get("extra", {}).get("metadata", {}).get("category", "").lower()
    ]

    assert len(security_findings) == 0, f"Security findings: {security_findings}"
```

**Dynamic Application Security Testing (DAST)**
```python
def test_owasp_zap_baseline_scan():
    """Run OWASP ZAP baseline scan"""
    import subprocess

    # Start app in test mode
    app_url = "http://localhost:8000"

    # Run ZAP baseline scan
    result = subprocess.run([
        "docker", "run", "--rm",
        "-v", f"{os.getcwd()}:/zap/wrk:rw",
        "owasp/zap2docker-stable",
        "zap-baseline.py",
        "-t", app_url,
        "-J", "zap-report.json"
    ], capture_output=True)

    # Load report
    with open("zap-report.json") as f:
        report = json.load(f)

    # Check for high-risk alerts
    high_risk = [a for a in report.get("site", [{}])[0].get("alerts", []) if a["riskcode"] == "3"]

    assert len(high_risk) == 0, f"High risk vulnerabilities found: {high_risk}"
```

**Dependency Scanning**
```bash
# CI/CD pipeline integration
# .github/workflows/security.yml

name: Security Scans

on: [push, pull_request]

jobs:
  dependency-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Python dependency scan
        run: |
          pip install pip-audit safety
          pip-audit --desc --require requirements.txt
          safety check --json --output safety-report.json

      - name: JavaScript dependency scan
        run: |
          npm audit --audit-level=high --json > npm-audit.json

      - name: Container scanning
        run: |
          docker build -t app:latest .
          docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
            aquasec/trivy image --severity HIGH,CRITICAL app:latest

  sast:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Bandit scan
        run: |
          pip install bandit
          bandit -r src/ -ll -f json -o bandit-report.json

      - name: Semgrep scan
        uses: returntocorp/semgrep-action@v1

  secrets-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: TruffleHog scan
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: ${{ github.event.repository.default_branch }}
          head: HEAD
```

#### Security Testing Best Practices Summary

**Critical Principles:**

1. **Test Negative Cases**: Test what should be blocked, not just what should work
2. **Prevent TOCTOU**: Resolve DNS once, validate once, use validated value
3. **Defense in Depth**: Validate on both client and server
4. **Realistic Payloads**: Use actual attack patterns from OWASP, PortSwigger
5. **Fail Secure**: On error, deny access (don't default to allow)
6. **Automate Everything**: Security scans in CI/CD, fail builds on critical issues

**Common Mistakes to Avoid:**

- ❌ Testing only happy paths
- ❌ Validating input but not output (XSS)
- ❌ Resolving hostnames multiple times (DNS rebinding)
- ❌ Trusting client-side validation alone
- ❌ Using blacklists instead of whitelists
- ❌ Logging sensitive data
- ❌ Rolling your own crypto
- ❌ Ignoring dependency vulnerabilities

**Security Test Coverage Targets:**

- **Authentication/Authorization**: 100% coverage
- **Input Validation**: 100% coverage
- **Injection Prevention**: 100% coverage
- **XSS Prevention**: 100% coverage
- **SSRF Prevention**: 100% coverage
- **File Upload Security**: 100% coverage
- **Session Management**: 100% coverage

## Testing AI/ML Systems

### 1. LLM Output Testing

**CRITICAL Principle: Never Assert Exact Strings**

LLM outputs are non-deterministic. Testing them requires semantic/structural assertions, not exact matches.

#### Semantic Assertion Patterns

```python
# ❌ BAD: Exact match (will fail due to non-determinism)
def test_llm_bad():
    response = llm.generate("What is the capital of France?")
    assert response == "The capital of France is Paris."  # Will fail!

# ✅ GOOD: Keyword presence
def test_llm_keyword():
    response = llm.generate("What is the capital of France?")
    assert "Paris" in response  # Flexible

# ✅ GOOD: Length bounds
def test_llm_length():
    response = llm.generate("Summarize this article...")
    assert 50 < len(response) < 200  # Reasonable length

# ✅ GOOD: Format check
def test_llm_format():
    response = llm.generate("What is the capital of France?")
    assert response.startswith("The capital")  # Structure check

# ✅ GOOD: JSON mode for deterministic structure
def test_llm_json():
    prompt = "Return JSON with capital of France. Use JSON mode."
    response = llm.generate(prompt, response_format="json")
    response_json = json.loads(response)

    assert "capital" in response_json
    assert response_json["capital"] == "Paris"  # Can check value in structured output
    assert "country" in response_json
```

**Evaluation Strategies:**

1. **Keyword Presence**: Check response contains expected keywords
   ```python
   assert all(keyword in response.lower() for keyword in ["paris", "france", "capital"])
   ```

2. **Length Bounds**: Min/max character count
   ```python
   assert 50 <= len(response) <= 500
   ```

3. **Format Validation**: JSON parses correctly, has required fields
   ```python
   data = json.loads(response)
   assert "result" in data
   assert isinstance(data["result"], str)
   ```

4. **Regex Matching**: Matches expected pattern
   ```python
   import re
   assert re.match(r"^The capital .* is \w+\.$", response)
   ```

5. **JSON Mode**: Force LLM to return JSON for structural testing
   ```python
   # Most reliable for deterministic testing
   response = llm.generate(prompt, response_format="json")
   data = json.loads(response)
   assert data["answer"] == "Paris"
   ```

**Advanced Evaluations (when needed):**

- **Embedding Similarity**: Compare response embedding to expected using cosine similarity
  ```python
  from sklearn.metrics.pairwise import cosine_similarity

  response_embedding = get_embedding(response)
  expected_embedding = get_embedding("Paris is the capital of France")
  similarity = cosine_similarity([response_embedding], [expected_embedding])[0][0]
  assert similarity > 0.85
  ```

- **LLM-as-Judge**: Use another LLM to evaluate output quality
  ```python
  judge_prompt = f"Rate this answer on a scale of 1-10: {response}"
  score = int(llm_judge.generate(judge_prompt))
  assert score >= 7
  ```

- **Golden Dataset**: Compare against known-good baseline responses
  ```python
  baseline = load_baseline("question_123")
  similarity = calculate_semantic_similarity(response, baseline)
  assert similarity > 0.8
  ```

**What NOT to Test:**

- ❌ **Exact output strings** (non-deterministic)
- ❌ **LLM quality** (that's OpenAI/Google's responsibility)
- ❌ **Hallucinations** (can't reliably test without ground truth)
- ❌ **Style/tone** (subjective, varies per run)

#### Golden Dataset Testing
```python
golden_tests = [
    {
        "prompt": "Summarize: The quick brown fox jumps over the lazy dog.",
        "expected_keywords": ["fox", "jumps", "dog"],
        "max_length": 50
    }
]

def test_llm_summarization():
    for test_case in golden_tests:
        result = llm.summarize(test_case["prompt"])

        # Check keywords present
        for keyword in test_case["expected_keywords"]:
            assert keyword.lower() in result.lower()

        # Check length constraint
        assert len(result) <= test_case["max_length"]
```

#### Regression Testing
```python
def test_llm_output_regression():
    # Store baseline outputs
    baseline = load_baseline_outputs()

    for test_case in test_cases:
        current_output = llm.generate(test_case.prompt)
        baseline_output = baseline[test_case.id]

        # Compare semantic similarity
        similarity = calculate_similarity(current_output, baseline_output)
        assert similarity > 0.8, f"Output diverged significantly: {similarity}"
```

### 2. Prompt Testing

```python
def test_prompt_variations():
    prompts = [
        "Summarize this text: {text}",
        "Provide a brief summary of: {text}",
        "TL;DR: {text}"
    ]

    text = "Long article content..."

    for prompt_template in prompts:
        prompt = prompt_template.format(text=text)
        result = llm.generate(prompt)

        assert len(result) < len(text)  # Should be shorter
        assert len(result) > 10  # Not too short
```

### 3. Cost and Performance Testing

```python
def test_llm_token_usage():
    with token_counter() as counter:
        result = llm.generate("Test prompt")

    assert counter.input_tokens < 100
    assert counter.output_tokens < 500
    assert counter.total_cost < 0.01  # Cost threshold
```

## Test Data Management

### 1. Test Fixtures

```python
# pytest fixtures
@pytest.fixture
def test_db():
    db = create_test_database()
    yield db
    db.cleanup()

@pytest.fixture
def sample_user():
    return User(
        email="test@example.com",
        name="Test User",
        role="admin"
    )
```

### 2. Factory Pattern

```python
class UserFactory:
    @staticmethod
    def create(**kwargs):
        defaults = {
            "email": "test@example.com",
            "name": "Test User",
            "role": "user"
        }
        defaults.update(kwargs)
        return User(**defaults)

# Usage
admin_user = UserFactory.create(role="admin")
```

### 3. Database Seeding

```python
def seed_test_data(db):
    users = [
        User(email=f"user{i}@example.com", name=f"User {i}")
        for i in range(10)
    ]
    db.add_all(users)
    db.commit()
```

## Mocking and Stubbing

### 1. External API Mocking

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

### 2. Database Mocking

```python
def test_user_repository_with_mock_db():
    mock_db = Mock()
    mock_db.query.return_value.filter_by.return_value.first.return_value = User(
        id=1, email="test@example.com"
    )

    repo = UserRepository(mock_db)
    user = repo.get_by_email("test@example.com")

    assert user.id == 1
```

## Performance Testing

### 1. Load Testing

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

### 2. Database Performance Testing

```python
import time

def test_query_performance():
    start = time.time()
    users = db.query(User).filter(User.role == "admin").all()
    duration = time.time() - start

    assert duration < 0.1  # Should complete in <100ms
    assert len(users) > 0
```

## Test Coverage

### Coverage Goals
- **Critical Paths**: 100% coverage
- **Business Logic**: 90-100% coverage
- **API Endpoints**: 80-90% coverage
- **Utility Functions**: 80-90% coverage
- **UI Components**: 70-80% coverage

### Measuring Coverage

```bash
# Python
pytest --cov=src --cov-report=html

# JavaScript
jest --coverage

# View report
open coverage/index.html
```

## CI/CD Integration

### GitHub Actions Example

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
        run: pytest --cov=src --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## Test Organization

### Directory Structure

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
└── conftest.py
```

## Best Practices Checklist

- [ ] Follow testing pyramid (more unit tests, fewer E2E tests)
- [ ] Write tests before or during development (TDD/BDD)
- [ ] Keep tests independent and isolated
- [ ] Use descriptive test names
- [ ] One assertion per test (when possible)
- [ ] Mock external dependencies
- [ ] Use test fixtures and factories
- [ ] Maintain high test coverage (>80%)
- [ ] Run tests in CI/CD pipeline
- [ ] Keep tests fast (<1s for unit tests)
- [ ] Test edge cases and error scenarios
- [ ] Clean up test data after tests
- [ ] Use consistent naming conventions
- [ ] Document complex test setups
- [ ] Review and refactor tests regularly

## Common Testing Pitfalls

- Testing implementation details instead of behavior
- Tests that depend on each other
- Slow tests that block development
- **Flaky tests that fail randomly** (see detailed section below)
- Mocking too much (losing confidence)
- Not testing error scenarios
- Ignoring test failures
- Poor test data management
- Not cleaning up after tests
- Over-complicated test setup

### Flaky Test Management (Critical)

**Flaky tests** are tests that sometimes pass and sometimes fail without code changes. They destroy confidence in your test suite and must be addressed immediately.

#### Identifying Flaky Tests

**Signs of flakiness:**
- ❌ Tests fail on CI but pass locally (or vice versa)
- ❌ Tests fail intermittently (~10-50% of runs)
- ❌ Tests fail with timing-related errors ("element not found", "timeout")
- ❌ Tests depend on external state (network, time, file system)

**How to detect:**
```bash
# Run tests multiple times to find flakiness
pytest tests/ --count=10  # pytest-repeat

# Run in parallel to expose race conditions
pytest tests/ -n 4  # pytest-xdist

# CI should track flaky test metrics
# GitHub Actions example: track test retries
```

#### Common Causes and Fixes

**1. Timing Issues (Most Common)**

❌ **Bad: Using sleep()**
```python
def test_data_loads():
    trigger_async_load()
    time.sleep(2)  # Flaky! Might be too short or too long
    assert data_is_loaded()
```

✅ **Good: Explicit waits with conditions**
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

✅ **Good: Playwright auto-waits**
```typescript
// ❌ Bad: Manual sleep
await page.click('button');
await page.waitForTimeout(1000); // Flaky!
expect(page.locator('.result')).toBeVisible();

// ✅ Good: Automatic waiting
await page.click('button');
await expect(page.locator('.result')).toBeVisible(); // Waits automatically
```

**2. Non-Deterministic Data**

❌ **Bad: Random or time-dependent data**
```python
def test_user_creation():
    user = create_user(
        email=f"test{random.randint(1000, 9999)}@example.com",
        created_at=datetime.now()  # Changes every run!
    )
    assert user.created_at == datetime.now()  # Flaky!
```

✅ **Good: Fixed test data with freezegun**
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

**3. Test Isolation Issues**

❌ **Bad: Tests depend on each other**
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

✅ **Good: Each test is independent**
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

**4. External Dependencies**

❌ **Bad: Real API calls**
```python
def test_fetch_user_profile():
    # Flaky! Network issues, rate limits, API changes
    response = requests.get("https://api.example.com/user/1")
    assert response.status_code == 200
```

✅ **Good: Mock external calls**
```python
@patch('requests.get')
def test_fetch_user_profile(mock_get):
    mock_get.return_value = Mock(status_code=200, json=lambda: {"id": 1})

    response = requests.get("https://api.example.com/user/1")
    assert response.status_code == 200
```

**5. Shared State / Global Variables**

❌ **Bad: Shared mutable state**
```python
# Global cache (shared across tests)
_cache = {}

def test_cache_set():
    _cache['key'] = 'value'
    assert _cache['key'] == 'value'

def test_cache_get():
    # Flaky! Depends on test execution order
    assert _cache.get('key') is None
```

✅ **Good: Isolated state per test**
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

#### Retry Strategies (Last Resort)

**⚠️ Warning**: Retrying flaky tests hides problems. Fix the root cause first!

If you must retry (e.g., external E2E tests):

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

#### CI/CD Flaky Test Handling

**GitHub Actions: Separate flaky tests**
```yaml
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

**Mark known flaky tests:**
```python
@pytest.mark.flaky
@pytest.mark.skip(reason="Flaky - tracked in issue #123")
def test_known_flaky():
    pass
```

#### Flaky Test Action Plan

When you encounter a flaky test:

1. **Reproduce it locally**: Run test 10-20 times
2. **Identify the root cause**: Review checklist above
3. **Fix immediately**: Don't let flaky tests accumulate
4. **If can't fix quickly**:
   - Mark as `@pytest.mark.skip` with issue number
   - Create tracking issue with reproduction steps
   - Set deadline to fix (within 1 sprint)
5. **Never ignore**: Flaky tests are bugs in your tests

#### Measuring Flakiness

Track these metrics:
- **Flaky test rate**: % of tests that are flaky
- **Flaky test age**: How long tests have been flaky
- **CI retry rate**: How often tests are retried

**Goal**: 0% flaky tests. Anything above 1% destroys confidence.
