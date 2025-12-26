---
name: frontend-patterns
description: React, TypeScript, Vite patterns for web applications. Use when building UI components, forms, routing, state management, or animations.
---

# Frontend Patterns

**Purpose**: Comprehensive React + TypeScript + Vite patterns for building modern, performant web applications

**Stack**: React 18, TypeScript, Vite, TanStack Query v5, React Router, Tailwind CSS

---

## Pattern Index

### Core Patterns (Existing)

| # | Pattern | Focus Area | When to Use |
|---|---------|------------|-------------|
| **01** | [Troubleshooting](01-troubleshooting.md) | CORS, Loading States, Network Debugging | Debugging frontend connectivity, timeouts, environment issues |
| **02** | [OAuth Authentication](02-oauth-authentication.md) | User Auth, OAuth Flows, Error Handling | Implementing OAuth login, auth state, callback handling |
| **03** | [React Performance](03-react-performance.md) | Bundle Size, Query Optimization, State | Optimizing bundle, state management, component rendering |
| **04** | [TanStack Query](04-tanstack-query.md) | Cache, Mutations, Optimistic Updates | Data fetching, caching, invalidation, session-specific state |

### Extended Patterns (New)

| # | Pattern | Focus Area | When to Use |
|---|---------|------------|-------------|
| **05** | [Form Handling](05-form-handling.md) | Validation, Submission, Complex Forms | Building forms with validation, file uploads, multi-step flows |
| **06** | [React Router Patterns](06-react-router-patterns.md) | Navigation, Guards, Layouts | React Router patterns, protected routes, nested routing |
| **07** | [State Management](07-state-management.md) | Context, Zustand, Jotai, Decision Tree | Choosing state solutions (useState/Context/Zustand/Jotai), migration patterns |
| **08** | [Animations](08-animations.md) | CSS, Framer Motion, View Transitions, GSAP | Adding animations, transitions, gestures, scroll effects |

---

## Quick Navigation by Use Case

### Development & Debugging
- **CORS errors**: [01-troubleshooting.md#cors-debugging](01-troubleshooting.md#cors-debugging)
- **Loading states hang**: [01-troubleshooting.md#loading-state-issues](01-troubleshooting.md#loading-state-issues)
- **Network debugging**: [01-troubleshooting.md#network-debugging](01-troubleshooting.md#network-debugging)
- **Environment setup**: [01-troubleshooting.md#environment-setup-verification](01-troubleshooting.md#environment-setup-verification)

### Authentication
- **User-scoped auth**: [02-oauth-authentication.md#user-scoped-vs-session-scoped-auth](02-oauth-authentication.md#user-scoped-vs-session-scoped-auth)
- **OAuth callback**: [02-oauth-authentication.md#oauth-callback-handling](02-oauth-authentication.md#oauth-callback-handling)
- **Auth error handling**: [02-oauth-authentication.md#error-handling](02-oauth-authentication.md#error-handling)
- **Protected routes**: [02-oauth-authentication.md#pattern-protected-routes-react-router](02-oauth-authentication.md#pattern-protected-routes-react-router)

### Performance
- **Bundle optimization**: [03-react-performance.md#bundle-optimization](03-react-performance.md#bundle-optimization)
- **Code splitting**: [03-react-performance.md#pattern-dynamic-imports-for-route-based-code-splitting](03-react-performance.md#pattern-dynamic-imports-for-route-based-code-splitting)
- **State patterns**: [03-react-performance.md#state-management-patterns](03-react-performance.md#state-management-patterns)
- **Asset optimization**: [03-react-performance.md#asset-optimization](03-react-performance.md#asset-optimization)

### Data Fetching
- **Cache invalidation**: [04-tanstack-query.md#cache-invalidation-vs-refetch](04-tanstack-query.md#cache-invalidation-vs-refetch)
- **Mutations**: [04-tanstack-query.md#mutation-lifecycle](04-tanstack-query.md#mutation-lifecycle)
- **Optimistic updates**: [04-tanstack-query.md#optimistic-updates](04-tanstack-query.md#optimistic-updates)
- **Session-specific state**: [04-tanstack-query.md#session-specific-state](04-tanstack-query.md#session-specific-state)

### Forms
- **Form validation**: [05-form-handling.md#3-validation-patterns](05-form-handling.md#3-validation-patterns)
- **File uploads**: [05-form-handling.md#5-file-upload-patterns](05-form-handling.md#5-file-upload-patterns)
- **Multi-step forms**: [05-form-handling.md#6-multi-step-forms](05-form-handling.md#6-multi-step-forms)
- **Async validation**: [05-form-handling.md#8-async-validation](05-form-handling.md#8-async-validation)
- **Auto-save drafts**: [05-form-handling.md#10-auto-save-drafts](05-form-handling.md#10-auto-save-drafts)

### Routing
- **React Router setup**: [06-react-router-patterns.md#1-react-router-v6-setup](06-react-router-patterns.md#1-react-router-v6-setup)
- **Route guards**: [06-react-router-patterns.md#2-route-guards--protection](06-react-router-patterns.md#2-route-guards--protection)
- **Nested routes**: [06-react-router-patterns.md#3-nested-routes--layouts](06-react-router-patterns.md#3-nested-routes--layouts)
- **Lazy loading**: [06-react-router-patterns.md#6-lazy-loading-routes](06-react-router-patterns.md#6-lazy-loading-routes)
- **URL state**: [06-react-router-patterns.md#10-url-state-management](06-react-router-patterns.md#10-url-state-management)

### State Management
- **Decision framework**: [07-state-management.md#decision-framework](07-state-management.md#decision-framework)
- **Server vs client state**: [07-state-management.md#server-state-vs-client-state](07-state-management.md#server-state-vs-client-state)
- **Context patterns**: [07-state-management.md#react-context-patterns](07-state-management.md#react-context-patterns)
- **Zustand patterns**: [07-state-management.md#zustand-patterns](07-state-management.md#zustand-patterns)
- **Jotai atoms**: [07-state-management.md#jotai-patterns](07-state-management.md#jotai-patterns)
- **State persistence**: [07-state-management.md#state-persistence](07-state-management.md#state-persistence)
- **Migration patterns**: [07-state-management.md#migration-patterns](07-state-management.md#migration-patterns)

### Animations
- **Decision framework**: [08-animations.md#decision-framework](08-animations.md#decision-framework)
- **Library comparison**: [08-animations.md#library-comparison](08-animations.md#library-comparison)
- **CSS transitions**: [08-animations.md#css-transitions--animations](08-animations.md#css-transitions--animations)
- **Framer Motion**: [08-animations.md#framer-motion-patterns](08-animations.md#framer-motion-patterns)
- **View Transitions API**: [08-animations.md#view-transitions-api](08-animations.md#view-transitions-api)
- **React Spring**: [08-animations.md#react-spring-patterns](08-animations.md#react-spring-patterns)
- **GSAP**: [08-animations.md#gsap-patterns](08-animations.md#gsap-patterns)
- **Common patterns**: [08-animations.md#common-animation-patterns](08-animations.md#common-animation-patterns)
- **Accessibility**: [08-animations.md#accessibility](08-animations.md#accessibility)
- **Performance**: [08-animations.md#performance-optimization](08-animations.md#performance-optimization)

---

## Common Patterns Across Files

### State Accumulation vs Replacement
- **Accumulate** (lists/history): `setState(prev => [...prev, newItem])`
- **Replace** (single values): `setState(newValue)`
- **Details**: [04-tanstack-query.md#state-accumulation-pattern](04-tanstack-query.md#state-accumulation-pattern)

### Timeout Guards
- Always add timeout guards for initial loading states (5-10s)
- Use `AbortController` for fetch requests
- **Details**: [01-troubleshooting.md#loading-state-issues](01-troubleshooting.md#loading-state-issues)

### Error Handling
- Detect auth errors (401) globally
- Clear auth state on failures
- Show user-friendly messages
- **Details**: [02-oauth-authentication.md#error-handling](02-oauth-authentication.md#error-handling)

### Query Configuration
- Set `staleTime` appropriately (5min for chat apps)
- Use `enabled` prop for conditional fetching
- Don't retry mutations (could duplicate actions)
- **Details**: [04-tanstack-query.md#query-configuration](04-tanstack-query.md#query-configuration)

---

## Technology Stack Reference

### Core Libraries
- **React**: 18.x (Concurrent features, Suspense)
- **TypeScript**: 5.x (Strict mode recommended)
- **Vite**: 5.x (Fast bundler, HMR)
- **TanStack Query**: 5.x (Data fetching, caching)
- **React Router**: 6.x (Routing, navigation)
- **Tailwind CSS**: 3.x (Utility-first styling)

### State Management Options
- **useState/useReducer**: Local component state
- **TanStack Query**: Server state (async data)
- **Zustand**: Global client state (lightweight)
- **Jotai**: Atomic state management
- **See**: [07-state-management.md](07-state-management.md) for decision guide

### Form Libraries
- **React Hook Form**: Performant, minimal re-renders
- **Zod**: Schema validation (TypeScript-first)
- **Formik**: Feature-rich (heavier)
- **See**: [05-form-handling.md](05-form-handling.md) for patterns

### Animation Libraries
- **CSS Transitions/Animations**: Native, performant
- **Framer Motion**: Declarative, gesture support
- **React Spring**: Physics-based animations
- **See**: [08-animations.md](08-animations.md) for comparisons

---

## Pattern Development Workflow

### 1. Check Existing Patterns
Before implementing a feature, check relevant pattern files:
```bash
# Search across all patterns
grep -r "pattern-keyword" .claude/skills/frontend-patterns/
```

### 2. Use Documented Patterns
If a pattern exists:
- Follow the documented approach
- Reference the pattern in code comments
- Don't reinvent the wheel

### 3. Document New Patterns
If you discover a new pattern:
1. Implement and verify it works
2. Add to appropriate pattern file
3. Use STAR format for lessons learned
4. Update this SKILL.md if it's a new category

### 4. Update Cross-References
When adding patterns:
- Add to "Quick Navigation by Use Case" section
- Update "Related Skills" in other pattern files
- Add to relevant agent memory files

---

## Contributing Guidelines

### Pattern File Structure
Each pattern file should follow this structure:

```markdown
# Pattern Name

**Purpose**: One-sentence description
**When to use**: Use cases
**Last Updated**: YYYY-MM-DD

## Table of Contents
1. [Pattern Category 1](#pattern-category-1)
2. [Pattern Category 2](#pattern-category-2)

## Pattern Category 1

### Pattern: Specific Pattern Name
**Problem**: What problem does this solve?
**Solution**: How to solve it
**Implementation**: Code examples

---

## Summary
- Key patterns list
- Common mistakes
- Quick reference table
- Related skills
```

### Code Examples
- Show both WRONG and CORRECT examples
- Include TypeScript types
- Add inline comments for clarity
- Keep examples focused and minimal

### Pattern Categories
- **Problem**: Describe the issue
- **Solution**: High-level approach
- **Implementation**: Code examples
- **Anti-Pattern**: Common mistakes
- **Key Points**: Bullet list of gotchas

---

## Maintenance

### When to Update
- New framework version released
- Discovered better pattern
- Common bug/issue encountered
- User feedback suggests improvement

### Review Cycle
- Review patterns quarterly
- Archive outdated patterns to `.claude/skills/archive/`
- Update "Last Updated" dates
- Maintain backward compatibility references

---

## Related Resources

### Internal
- **General Frontend**: [../frontend-development.md](../frontend-development.md)
- **Testing Patterns**: [../testing-strategy/04-frontend-component-testing.md](../testing-strategy/04-frontend-component-testing.md)
- **Security**: [../security-best-practices.md](../security-best-practices.md)
- **API Design**: [../api-design.md](../api-design.md)

### External (Official Docs)
- **React**: https://react.dev
- **Vite**: https://vitejs.dev
- **TanStack Query**: https://tanstack.com/query
- **React Router**: https://reactrouter.com
- **Tailwind CSS**: https://tailwindcss.com

---

**Last Updated**: 2025-12-09
