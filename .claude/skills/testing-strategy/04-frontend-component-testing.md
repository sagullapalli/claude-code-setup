# Frontend Component Testing

**When to use**: Testing React/Svelte components in isolation with rendered DOM.

**Focus**: User interactions, conditional rendering, behavior (not implementation details).

---

## What to Test

### ✅ Test These

- **User interactions**: Clicks, typing, form submission
- **Conditional rendering**: Based on props/state
- **Component integration**: Hooks, context, stores
- **Error states**: Error messages, validation
- **Loading states**: Spinners, skeleton screens
- **Accessibility**: ARIA attributes, labels

### ❌ Don't Test These

- **Implementation details**: CSS classes, internal state variables
- **Third-party libraries**: Trust React, Svelte, UI libraries
- **Complete user journeys**: Use E2E tests (Module 5)

---

## React Testing Library Patterns

### User-Centric Queries (Priority Order)

**1. getByRole** (Accessibility-first):
```typescript
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

test('user can submit login form', async () => {
  const handleSubmit = jest.fn();
  render(<LoginForm onSubmit={handleSubmit} />);

  // Act - use roles for accessibility
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

**2. getByLabelText** (Form inputs):
```typescript
test('form inputs have proper labels', () => {
  render(<LoginForm />);

  // These will fail if labels are missing or improperly associated
  expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
  expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
});
```

**3. getByPlaceholderText**, **getByText** (Less preferred):
```typescript
test('displays welcome message', () => {
  render(<Dashboard username="John" />);

  expect(screen.getByText(/welcome, john/i)).toBeInTheDocument();
});
```

**4. getByTestId** (Last resort):
```typescript
// Only when no semantic query works
test('displays specific data', () => {
  render(<UserProfile />);

  expect(screen.getByTestId('user-bio')).toBeInTheDocument();
});
```

### ❌ Anti-Pattern: Implementation-Focused Queries

```typescript
// ❌ BAD: Relies on implementation details
test('user can submit login form', () => {
  const { container } = render(<LoginForm />);
  const emailInput = container.querySelector('.email-input'); // Brittle!
  const submitBtn = container.querySelector('#submit-btn'); // Brittle!

  fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
  fireEvent.click(submitBtn);
});

// ✅ GOOD: User-centric queries
test('user can submit login form', async () => {
  render(<LoginForm />);

  await userEvent.type(screen.getByLabelText(/email/i), 'test@example.com');
  await userEvent.click(screen.getByRole('button', { name: /sign in/i }));
});
```

---

## Testing Async Behavior

### Loading States

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

### Error States

```typescript
test('displays error message on API failure', async () => {
  jest.spyOn(api, 'fetchUser').mockRejectedValue(new Error('Network error'));

  render(<UserProfile userId={1} />);

  // Wait for error message
  expect(await screen.findByText(/error loading user/i)).toBeInTheDocument();
});
```

---

## Mocking Context and Hooks

### Mock React Context

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

### Mock Custom Hooks

```typescript
jest.mock('../hooks/useAuth', () => ({
  useAuth: () => ({
    user: { id: 1, name: 'John' },
    isAuthenticated: true
  })
}));

test('displays user name when authenticated', () => {
  render(<UserProfile />);

  expect(screen.getByText('John')).toBeInTheDocument();
});
```

---

## Svelte Component Testing

### Basic Svelte Test

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

### Testing Svelte Stores

```typescript
import { render } from '@testing-library/svelte';
import { get } from 'svelte/store';
import UserList from './UserList.svelte';
import { usersStore } from '../stores/users';

test('displays users from store', () => {
  // Set store data
  usersStore.set([
    { id: 1, name: 'John' },
    { id: 2, name: 'Jane' }
  ]);

  const { getByText } = render(UserList);

  expect(getByText('John')).toBeInTheDocument();
  expect(getByText('Jane')).toBeInTheDocument();
});
```

---

## When to Use Component Tests vs E2E Tests

### ✅ Component Tests

- Testing individual component behavior
- Form validation logic
- Conditional rendering
- User interactions within a component
- Fast feedback (runs in <100ms)
- **80% of UI tests should be component tests**

### ✅ E2E Tests

- Complete user journeys across pages
- Authentication flows
- Payment/checkout processes
- Critical business paths
- Cross-browser compatibility
- **20% of UI tests should be E2E** (see Module 5)

---

## Best Practices

### ✅ Do

- **Use user-centric queries** (getByRole, getByLabelText)
- **Test behavior, not implementation** (avoid CSS selectors)
- **Use userEvent over fireEvent** (more realistic)
- **Wait for async updates** (findBy, waitFor)
- **Mock external dependencies** (API calls, context)
- **Test accessibility** (ARIA roles, labels)

### ❌ Don't

- **Query by CSS classes or IDs** (brittle, implementation details)
- **Test internal component state** (test public API/behavior)
- **Use snapshot tests** for everything (hard to maintain)
- **Test third-party components** (trust the library)

---

## Summary

### Key Points

1. **Test from user's perspective** (roles, labels, text)
2. **Avoid implementation details** (CSS classes, IDs)
3. **Use userEvent** for realistic interactions
4. **Wait for async updates** (findBy, waitFor)
5. **Mock context and hooks** for isolation

### Checklist

- [ ] User-centric queries (getByRole, getByLabelText)
- [ ] Async behavior tested (loading, error states)
- [ ] Context/hooks mocked when needed
- [ ] Tests are fast (<100ms)
- [ ] No CSS selectors or test IDs (unless necessary)
- [ ] Accessibility considered (ARIA, labels)

---

## Cross-References

- **Testing philosophy**: [01-testing-philosophy.md](01-testing-philosophy.md)
- **E2E testing**: [05-e2e-testing.md](05-e2e-testing.md)
- **Accessibility testing**: [06-accessibility-testing.md](06-accessibility-testing.md)
- **Flaky test fixes**: [10-flaky-test-management.md](10-flaky-test-management.md)
