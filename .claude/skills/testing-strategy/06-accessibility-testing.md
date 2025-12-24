# Accessibility Testing

**When to use**: Ensuring application is usable by everyone, including people with disabilities.

**Target**: WCAG 2.1 Level AA compliance

---

## Why A11y Testing Matters

- **Legal Compliance**: WCAG 2.1 AA legally required in many jurisdictions
- **Better UX**: Accessible apps easier for everyone
- **SEO Benefits**: Screen reader-friendly = search engine-friendly
- **Keyboard Navigation**: Essential for power users

**Note**: Automated tools catch ~30-40% of issues; manual testing essential.

---

## Automated A11y Testing

### Component Level (jest-axe)

```typescript
import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';

expect.extend(toHaveNoViolations);

test('LoginForm has no accessibility violations', async () => {
  const { container } = render(<LoginForm />);
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});

test('form inputs have proper labels', () => {
  const { getByLabelText } = render(<LoginForm />);
  expect(getByLabelText(/email/i)).toBeInTheDocument();
  expect(getByLabelText(/password/i)).toBeInTheDocument();
});
```

### E2E Level (Playwright + axe)

```typescript
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test('homepage should not have accessibility violations', async ({ page }) => {
  await page.goto('/');

  const accessibilityScanResults = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
    .analyze();

  expect(accessibilityScanResults.violations).toEqual([]);
});
```

---

## Keyboard Navigation Testing

```typescript
test('keyboard navigation works on dashboard', async ({ page }) => {
  await page.goto('/dashboard');

  // Tab through interactive elements
  await page.keyboard.press('Tab');
  await expect(page.locator(':focus')).toHaveAttribute('role', 'button');

  // Enter key should activate
  await page.keyboard.press('Enter');
  await expect(page).toHaveURL(/\/new-post/);
});

test('modal traps focus', async () => {
  const { getByRole } = render(<ConfirmDialog />);

  const confirmButton = getByRole('button', { name: /confirm/i });
  const closeButton = getByRole('button', { name: /close/i });

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

---

## ARIA Attributes Testing

```typescript
test('loading states are announced to screen readers', () => {
  const { container } = render(<DataTable isLoading={true} />);

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

  expect(emailInput).toHaveAttribute('aria-describedby', expect.stringContaining(errorMessage.id));
  expect(emailInput).toHaveAttribute('aria-invalid', 'true');
});
```

---

## Manual A11y Testing Checklist

- [ ] **Screen Reader Testing**: Use NVDA (Windows) or VoiceOver (Mac)
- [ ] **Keyboard-Only Navigation**: Can reach all elements with Tab?
- [ ] **Zoom to 200%**: Content still fits on screen?
- [ ] **Color Blindness**: Information conveyed without relying only on color?
- [ ] **Focus indicators**: Always visible?

---

## WCAG Levels

- **WCAG 2.1 Level A**: Minimum (legal requirement)
- **WCAG 2.1 Level AA**: Standard target (recommended) ← **Use this**
- **WCAG 2.1 Level AAA**: Enhanced (gold standard)

**WCAG AA Requirements:**
- Color contrast ≥ 4.5:1 for normal text
- Color contrast ≥ 3:1 for large text (18pt+)
- All functionality via keyboard
- Focus indicators visible
- Form inputs have labels
- Headings follow hierarchy (h1 → h2 → h3)

---

## Summary

### Key Points

1. **Automated tools catch 30-40%** - manual testing essential
2. **Target WCAG 2.1 Level AA**
3. **Test keyboard navigation** (Tab, Enter, Escape)
4. **Test screen readers** (NVDA, VoiceOver)
5. **Use semantic HTML** (reduces violations)

### Checklist

- [ ] Automated a11y tests (jest-axe, Playwright axe)
- [ ] Keyboard navigation tested
- [ ] ARIA attributes validated
- [ ] Color contrast checked
- [ ] Manual testing performed

---

## Cross-References

- **Component testing**: [04-frontend-component-testing.md](04-frontend-component-testing.md)
- **E2E testing**: [05-e2e-testing.md](05-e2e-testing.md)
- **Security testing**: [07-security-testing.md](07-security-testing.md)
