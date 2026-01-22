# E2E (End-to-End) Testing

**When to use**: Testing complete user journeys across pages, critical business paths.

**Focus**: Real browser automation, cross-browser compatibility, user flows.

**WARNING**: E2E tests should be 10% of your test suite (testing pyramid).

---

## What to Test (E2E Level)

### ✅ Test These

- **Critical user journeys**: Signup, login, checkout
- **Multi-step workflows**: Create account → verify email → complete profile
- **Cross-browser compatibility**: Chrome, Firefox, Safari
- **Authentication flows**: Login, logout, password reset
- **Payment flows**: Add to cart → checkout → payment

### ❌ Don't Test These (covered elsewhere)

- **Component behavior** → Component tests (Module 4)
- **Business logic** → Unit tests (Module 2)
- **API validation** → Integration tests (Module 3)

**Rule**: Only test critical paths with E2E (they're slow and brittle).

---

## Playwright Patterns

### Basic User Journey

```javascript
import { test, expect } from '@playwright/test';

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

### Auto-Waits (Built-in)

```javascript
// ✅ GOOD: Playwright auto-waits (no manual sleep needed)
test('user can submit form', async ({ page }) => {
  await page.goto('/form');
  await page.click('button'); // Waits for button to be clickable
  await expect(page.locator('.result')).toBeVisible(); // Waits for element
});

// ❌ BAD: Manual sleep (flaky!)
test('user can submit form', async ({ page }) => {
  await page.goto('/form');
  await page.click('button');
  await page.waitForTimeout(1000); // Flaky! Might be too short or too long
  expect(await page.locator('.result').isVisible()).toBe(true);
});
```

### Page Object Model (POM)

**Good for reducing duplication:**

```javascript
// pages/LoginPage.js
class LoginPage {
  constructor(page) {
    this.page = page;
    this.emailInput = page.locator('input[name="email"]');
    this.passwordInput = page.locator('input[name="password"]');
    this.submitButton = page.locator('button[type="submit"]');
  }

  async login(email, password) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }
}

// tests/login.spec.js
import { LoginPage } from '../pages/LoginPage';

test('user can login', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await page.goto('/login');
  await loginPage.login('test@example.com', 'password123');

  await expect(page).toHaveURL('/dashboard');
});
```

---

## Best Practices

### ✅ Do

- **Use Playwright auto-waits** (don't use sleep)
- **Test critical paths only** (10% of test suite)
- **Run in CI, not locally** (too slow for dev workflow)
- **Use Page Object Model** for common flows
- **Run in parallel** to speed up execution
- **Use headless mode** in CI

### ❌ Don't

- **Test every feature** with E2E (use component tests)
- **Use sleep()** (use auto-waits)
- **Run locally** on every save (too slow)
- **Test implementation details** (CSS classes)

---

## Playwright Configuration

### playwright.config.ts

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true, // Run tests in parallel
  forbidOnly: !!process.env.CI, // Fail if .only in CI
  retries: process.env.CI ? 2 : 0, // Retry flaky tests in CI
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',

  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry', // Capture trace on failures
  },

  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } },
  ],

  webServer: {
    command: 'npm run start',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
```

---

## Running E2E Tests

```bash
# Run all tests
npx playwright test

# Run specific test
npx playwright test tests/e2e/login.spec.ts

# Run in headed mode (see browser)
npx playwright test --headed

# Debug mode
npx playwright test --debug

# Run in specific browser
npx playwright test --project=firefox

# Generate code (record interactions)
npx playwright codegen http://localhost:3000
```

---

## Summary

### Key Points

1. **E2E tests are 10% of test suite** (testing pyramid)
2. **Test critical paths only** (signup, login, checkout)
3. **Use Playwright auto-waits** (never sleep)
4. **Run in CI, not locally** (too slow)
5. **Use Page Object Model** for common flows

### Checklist

- [ ] Only critical paths tested
- [ ] Auto-waits used (no sleep)
- [ ] Page Object Model for common flows
- [ ] Cross-browser testing configured
- [ ] Run in CI pipeline
- [ ] Headless mode in CI

---

## Cross-References

- **Testing philosophy**: [01-testing-philosophy.md](01-testing-philosophy.md)
- **Component testing**: [04-frontend-component-testing.md](04-frontend-component-testing.md)
- **Accessibility testing**: [06-accessibility-testing.md](06-accessibility-testing.md)
- **Flaky test fixes**: [10-flaky-test-management.md](10-flaky-test-management.md)
- **CI/CD setup**: [11-ci-cd-integration.md](11-ci-cd-integration.md)
