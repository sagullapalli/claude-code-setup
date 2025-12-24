# Frontend Development Skill

Comprehensive guide for building modern, accessible, performant frontend applications with simplicity and best practices.

## Scope

This skill covers **SPA (Single Page Application) development** for client-side apps that communicate with FastAPI backends. For server-side rendering needs, see the meta-framework section below.

## Framework Selection Guide

### Meta-Framework vs SPA Decision Tree

```
Need SEO or Server-Side Rendering?
├─ Yes → Meta-framework
│  ├─ React ecosystem → Next.js
│  └─ Svelte ecosystem → SvelteKit
└─ No → SPA (client-side only)
   └─ Need interactivity?
      ├─ No → Static HTML + CSS (+ Tailwind)
      └─ Yes
         └─ Complex state/interactions?
            ├─ No → HTMX + Tailwind (no build step)
            └─ Yes → Need framework
               └─ Team preference?
                  ├─ Simplicity → Svelte
                  ├─ Ecosystem → React
                  └─ Performance → Svelte or React
```

**This skill focuses on SPAs** (Vite + React/Svelte). For Next.js/SvelteKit, consult their official documentation.

### HTMX (Simplest)

**When to use:**
- Simple CRUD applications
- Server-rendered content
- Minimal JavaScript needed
- Progressive enhancement

**Pros:**
- No build step
- Very small size (~14KB)
- Works with any backend
- Easy to learn

**Cons:**
- Limited for complex SPAs
- Server-dependent
- Less community support

```html
<div hx-get="/api/users" hx-trigger="load">
  Loading...
</div>
```

### Svelte (Simple & Modern)

**When to use:**
- Small to medium applications
- Want simplicity and performance
- Team comfortable with new syntax

**Pros:**
- Minimal boilerplate
- Built-in state management
- Smaller bundles
- Great DX

**Cons:**
- Smaller ecosystem than React
- Less mature tooling
- Fewer jobs/resources

```svelte
<script lang="ts">
  let count = 0;
</script>

<button on:click={() => count++}>
  Count: {count}
</button>
```

### React (Most Popular)

**When to use:**
- Medium to large applications
- Need large ecosystem
- Team knows React
- Hiring consideration

**Pros:**
- Huge ecosystem
- Mature tooling
- Wide adoption
- Lots of resources

**Cons:**
- More boilerplate
- Bundle size larger
- Need extra libraries for state

```tsx
function Counter() {
  const [count, setCount] = useState(0);

  return (
    <button onClick={() => setCount(c => c + 1)}>
      Count: {count}
    </button>
  );
}
```

## Project Setup

### Vite + React + TypeScript

```bash
# Create project
npm create vite@latest my-app -- --template react-ts
cd my-app

# Install Tailwind
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# Install core dependencies
npm install react-router-dom @tanstack/react-query zod react-hook-form @hookform/resolvers

# Install UI library (for complex components)
npm install @radix-ui/react-dialog @radix-ui/react-dropdown-menu @radix-ui/react-select

# Install linting & formatting
npm install -D eslint prettier eslint-config-prettier eslint-plugin-react-hooks
npm install -D @typescript-eslint/parser @typescript-eslint/eslint-plugin

# Install testing
npm install -D vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event

# Install Playwright (E2E)
npm create playwright@latest

# Install pre-commit hooks
npm install -D husky lint-staged
npx husky init
```

**ESLint Configuration** (`.eslintrc.cjs`):
```javascript
module.exports = {
  root: true,
  env: { browser: true, es2020: true },
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:react-hooks/recommended',
    'prettier' // Must be last to override other configs
  ],
  ignorePatterns: ['dist', '.eslintrc.cjs'],
  parser: '@typescript-eslint/parser',
  plugins: ['react-refresh'],
  rules: {
    'react-refresh/only-export-components': [
      'warn',
      { allowConstantExport: true },
    ],
    '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
  },
}
```

**Prettier Configuration** (`.prettierrc`):
```json
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5",
  "printWidth": 100,
  "arrowParens": "avoid"
}
```

**Husky Pre-commit Hook** (`.husky/pre-commit`):
```bash
#!/usr/bin/env sh
. "$(dirname -- "$0")/_/husky.sh"

npx lint-staged
```

**Lint-staged Configuration** (`package.json`):
```json
{
  "lint-staged": {
    "*.{ts,tsx}": ["eslint --fix", "prettier --write"],
    "*.{json,md}": ["prettier --write"]
  }
}
```

### Vite + Svelte + TypeScript

```bash
# Create project
npm create vite@latest my-app -- --template svelte-ts
cd my-app

# Install Tailwind (same as React)
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

### Environment Variables

```bash
# .env.local
VITE_API_URL=http://localhost:8000
VITE_ENABLE_DEBUG=true
```

```ts
// src/config.ts
export const config = {
  apiUrl: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  enableDebug: import.meta.env.VITE_ENABLE_DEBUG === 'true'
};
```

### Folder Structure Guidelines

**Small Projects (<10 components):**
```
src/
├── components/
├── pages/
├── utils/
├── App.tsx
└── main.tsx
```

**Medium+ Projects (>10 components):**
```
src/
├── features/
│   ├── auth/
│   │   ├── components/
│   │   │   ├── LoginForm.tsx
│   │   │   └── SignupForm.tsx
│   │   ├── hooks/
│   │   │   └── useAuth.ts
│   │   ├── api/
│   │   │   └── authApi.ts
│   │   └── types.ts
│   ├── users/
│   │   ├── components/
│   │   ├── hooks/
│   │   └── api/
│   └── ...
├── components/      # Shared components
│   ├── ui/         # UI primitives (Button, Input, etc.)
│   └── layout/     # Layout components (Header, Sidebar)
├── lib/            # Utilities, helpers
│   ├── api.ts      # API client setup
│   ├── queryClient.ts  # TanStack Query setup
│   └── utils.ts
├── hooks/          # Shared hooks
├── types/          # Shared types
├── App.tsx
└── main.tsx
```

**Key Principles:**
- **Feature-based structure** for medium+ projects (collocate related code)
- **Flat structure** for small projects (less than 10 components)
- **Shared components** in `/components` (used across features)
- **Feature-specific components** in `/features/[feature]/components`

## Component Patterns

### Composition Over Props

```tsx
// Good: Composition
function Card({ children }: { children: React.ReactNode }) {
  return <div className="card">{children}</div>;
}

function CardHeader({ children }: { children: React.ReactNode }) {
  return <div className="card-header">{children}</div>;
}

// Usage
<Card>
  <CardHeader>Title</CardHeader>
  <p>Content</p>
</Card>

// Bad: Too many props
function Card({ title, subtitle, content, footer, showBorder, theme }: Props) {
  // Complex logic...
}
```

### Container/Presenter Pattern

**DEPRECATED: Don't use useEffect for data fetching.** Use TanStack Query instead (see next section).

```tsx
// Container (data fetching with TanStack Query)
import { useQuery } from '@tanstack/react-query';
import { fetchUsers } from '@/api/users';

function UserListContainer() {
  const { data: users = [], isLoading } = useQuery({
    queryKey: ['users'],
    queryFn: fetchUsers,
  });

  return <UserListPresenter users={users} loading={isLoading} />;
}

// Presenter (UI only)
interface Props {
  users: User[];
  loading: boolean;
}

function UserListPresenter({ users, loading }: Props) {
  if (loading) return <Spinner />;

  return (
    <ul>
      {users.map(u => <UserItem key={u.id} user={u} />)}
    </ul>
  );
}
```

### Data Fetching (TanStack Query)

**CRITICAL: Do NOT use useEffect for data fetching.** It has race conditions, no cleanup, and React 18 Strict Mode issues.

**Use TanStack Query (React Query) for all server state:**

```tsx
// Setup Query Client (src/lib/queryClient.ts)
import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      retry: 1,
    },
  },
});
```

```tsx
// App.tsx
import { QueryClientProvider } from '@tanstack/react-query';
import { queryClient } from './lib/queryClient';

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Routes />
    </QueryClientProvider>
  );
}
```

```tsx
// API functions (src/features/users/api/userApi.ts)
import { config } from '@/config';

export async function fetchUsers(): Promise<User[]> {
  const response = await fetch(`${config.apiUrl}/api/users`);
  if (!response.ok) throw new Error('Failed to fetch users');
  return response.json();
}

export async function createUser(user: CreateUser): Promise<User> {
  const response = await fetch(`${config.apiUrl}/api/users`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(user),
  });
  if (!response.ok) throw new Error('Failed to create user');
  return response.json();
}
```

```tsx
// Fetch data with useQuery
import { useQuery } from '@tanstack/react-query';
import { fetchUsers } from '@/features/users/api/userApi';

function UserList() {
  const { data: users, isLoading, error } = useQuery({
    queryKey: ['users'],
    queryFn: fetchUsers,
  });

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <ul>
      {users?.map(user => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  );
}
```

```tsx
// Mutate data with useMutation
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { createUser } from '@/features/users/api/userApi';

function CreateUserForm() {
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: createUser,
    onSuccess: () => {
      // Invalidate and refetch users query
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  });

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    mutation.mutate({
      name: formData.get('name') as string,
      email: formData.get('email') as string,
    });
  };

  return (
    <form onSubmit={handleSubmit}>
      <input name="name" required />
      <input name="email" type="email" required />
      <button type="submit" disabled={mutation.isPending}>
        {mutation.isPending ? 'Creating...' : 'Create User'}
      </button>
      {mutation.error && <p>Error: {mutation.error.message}</p>}
    </form>
  );
}
```

**Benefits of TanStack Query:**
- ✅ Automatic caching and background refetching
- ✅ No race conditions or memory leaks
- ✅ Loading/error states built-in
- ✅ Optimistic updates support
- ✅ Query invalidation and refetching
- ✅ React 18 Strict Mode compatible

### Custom Hooks (For Non-Server State)

```tsx
// useLocalStorage.ts
export function useLocalStorage<T>(key: string, initialValue: T) {
  const [value, setValue] = useState<T>(() => {
    const item = localStorage.getItem(key);
    return item ? JSON.parse(item) : initialValue;
  });

  const setStoredValue = (newValue: T) => {
    setValue(newValue);
    localStorage.setItem(key, JSON.stringify(newValue));
  };

  return [value, setStoredValue] as const;
}

// Usage
function ThemeToggle() {
  const [theme, setTheme] = useLocalStorage('theme', 'light');
  // ...
}
```

## State Management

### When to Use What

**Local State (useState):**
- Component-specific data
- Form inputs
- UI state (modals, tabs)

**Lifted State:**
- Shared between siblings
- Parent-child communication
- 2-3 levels deep

**Context:**
- Theme, locale, auth
- Deeply nested components
- Avoid prop drilling

**External Library (Zustand, Redux):**
- Complex global state
- Time-travel debugging needed
- Very large applications

### Session-Specific UI States

**Problem**: When managing multiple sessions (e.g., chat sessions, tabs), UI loading states can incorrectly persist when switching between sessions if they're tied to global mutation state.

**Pattern**: Track which session has an active operation and only show loading UI when the current session matches the active session.

```tsx
// BAD: Global mutation state shows in all sessions
function App() {
  const [currentSessionId, setCurrentSessionId] = useState('session-1');
  const chatMutation = useMutation({ mutationFn: sendMessage });

  // PROBLEM: isLoading is true for ALL sessions when mutation runs
  return <PipelinePane isLoading={chatMutation.isPending} />;
}

// GOOD: Track which session has the active mutation
function App() {
  const [currentSessionId, setCurrentSessionId] = useState('session-1');
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);

  const chatMutation = useMutation({
    mutationFn: sendMessage,
    onMutate: () => {
      // Mark which session started the mutation
      setActiveSessionId(currentSessionId);
    },
    onSuccess: () => {
      // Clear on completion
      setActiveSessionId(null);
    },
    onError: () => {
      // Clear on error
      setActiveSessionId(null);
    },
  });

  const handleSessionSwitch = (newSessionId: string) => {
    setCurrentSessionId(newSessionId);
    // Clear active session to stop loading in the new session
    setActiveSessionId(null);
  };

  // Only show loading when current session matches the active session
  return (
    <PipelinePane
      isLoading={chatMutation.isPending && activeSessionId === currentSessionId}
    />
  );
}
```

**Key Principles**:
1. **Track Active Context**: Store which session/tab/context has the active mutation
2. **Conditional Loading**: `isLoading={mutation.isPending && activeId === currentId}`
3. **Let Mutation Lifecycle Manage State**: Do NOT clear `activeId` on session switch
4. **Clear on Complete**: Reset in `onSuccess`, `onError`, and `onSettled` callbacks

**Real-World Example**: Chat app with multiple sessions
- User sends message in Session A → mutation starts → `activeSessionId = 'session-a'`
- User switches to Session B → `activeSessionId` STAYS 'session-a' → no loading shown (condition fails)
- User switches back to Session A → loading DOES show (condition passes)
- Mutation completes → `activeSessionId = null` → loading disappears

### Common Mistake: Over-clearing State

**WRONG: Clearing activeSessionId on session switch**
```tsx
const handleSessionSwitch = (newSessionId: string) => {
  setCurrentSessionId(newSessionId);
  setActiveSessionId(null); // ❌ WRONG: Breaks loading when switching back
};
```

**WHY THIS IS WRONG**:
- When switching to Session B, the condition `activeSessionId === currentSessionId` already prevents loading from showing
- Clearing `activeSessionId` loses track of which session has the active mutation
- When switching BACK to Session A, loading won't show even if mutation is still running
- This breaks the user experience - they can't see loading progress anymore

**CORRECT: Let the mutation lifecycle manage its own state**
```tsx
const handleSessionSwitch = (newSessionId: string) => {
  setCurrentSessionId(newSessionId);
  // DON'T clear activeSessionId - the condition handles showing/hiding
};

const mutation = useMutation({
  onMutate: () => setActiveSessionId(currentSessionId), // Set on start
  onSuccess: () => setActiveSessionId(null), // Clear on success
  onError: () => setActiveSessionId(null), // Clear on error
});
```

**PRINCIPLE**: The conditional check `activeSessionId === currentSessionId` handles showing/hiding the loading state automatically. You only need to set `activeSessionId` when mutation starts and clear it when mutation completes. Don't clear it on session switches.

### Optimistic Updates with Session-Specific State

**Problem**: When using optimistic updates in a multi-session app (chat sessions, tabs, workspaces), switching sessions during an active mutation can destroy optimistic updates because query refetches overwrite local state.

**Root Cause**:
1. User sends message in Session A → Optimistically added to local state
2. Mutation starts → Backend processing begins
3. User switches to Session B → Messages query refetches for Session B
4. `useEffect` calls `setMessages(messagesData.messages)` → **Replaces ALL local state** with Session B data
5. User switches back to Session A → Messages query refetches
6. **Race condition**: If mutation still pending, query returns old messages (without optimistic update)
7. Result: Optimistic update lost, user message disappears until mutation completes

**Anti-Pattern** ❌:
```tsx
// WRONG: Single messages array + query overwriting optimistic updates
function App() {
  const [currentSessionId, setCurrentSessionId] = useState('session-1');
  const [messages, setMessages] = useState<ChatMessage[]>([]); // ❌ Single array for all sessions

  const { data: messagesData } = useQuery({
    queryKey: ['messages', currentSessionId],
    queryFn: () => fetchMessages(currentSessionId),
  });

  // ❌ PROBLEM: Unconditionally overwrites local state, destroying optimistic updates
  useEffect(() => {
    if (messagesData?.messages) {
      setMessages(messagesData.messages); // ❌ Replaces everything!
    }
  }, [messagesData]);

  const chatMutation = useMutation({
    mutationFn: sendMessage,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['messages', currentSessionId] });
    },
  });

  const handleSendMessage = () => {
    // Optimistic update to single array
    setMessages((prev) => [...prev, userMessage]); // ❌ Will be lost on session switch
    chatMutation.mutate({ session_id: currentSessionId, message: inputMessage });
  };

  const handleSessionSwitch = (newSessionId: string) => {
    setCurrentSessionId(newSessionId); // ❌ Triggers query refetch → overwrites local state
  };
}
```

**Correct Pattern** ✅:
```tsx
// CORRECT: Session-specific message state using Map
function App() {
  const [currentSessionId, setCurrentSessionId] = useState('session-1');
  // ✅ Use Map to store messages per session
  const [sessionMessages, setSessionMessages] = useState<Map<string, ChatMessage[]>>(new Map());

  // ✅ Derived state for current session
  const messages = sessionMessages.get(currentSessionId) || [];

  const { data: messagesData } = useQuery({
    queryKey: ['messages', currentSessionId],
    queryFn: () => fetchMessages(currentSessionId),
  });

  // ✅ Update only the specific session's messages
  useEffect(() => {
    if (messagesData?.messages) {
      setSessionMessages((prev) => {
        const newMap = new Map(prev);
        newMap.set(currentSessionId, messagesData.messages);
        return newMap;
      });
    }
  }, [messagesData, currentSessionId]);

  const chatMutation = useMutation({
    mutationFn: sendMessage,
    onMutate: () => {
      setActiveSessionId(currentSessionId); // Track which session has mutation
    },
    onSuccess: () => {
      setActiveSessionId(null);
      queryClient.invalidateQueries({ queryKey: ['messages', currentSessionId] });
    },
    onError: () => {
      // ✅ Rollback optimistic update on error
      setSessionMessages((prev) => {
        const newMap = new Map(prev);
        const sessionMsgs = newMap.get(currentSessionId) || [];
        newMap.set(currentSessionId, sessionMsgs.slice(0, -1)); // Remove last message
        return newMap;
      });
      setActiveSessionId(null);
    },
  });

  const handleSendMessage = () => {
    // ✅ Optimistic update to session-specific state
    setSessionMessages((prev) => {
      const newMap = new Map(prev);
      const sessionMsgs = newMap.get(currentSessionId) || [];
      newMap.set(currentSessionId, [...sessionMsgs, userMessage]);
      return newMap;
    });
    chatMutation.mutate({ session_id: currentSessionId, message: inputMessage });
  };

  const handleSessionSwitch = (newSessionId: string) => {
    setCurrentSessionId(newSessionId); // ✅ Safe - only updates derived state
    // Messages for each session are preserved in the Map
  };
}
```

**Key Benefits**:
1. ✅ **Optimistic updates preserved** when switching sessions during mutation
2. ✅ **No cross-contamination** - Session A data never overwrites Session B data
3. ✅ **Clean rollback** - Easy to remove failed optimistic updates per session
4. ✅ **Predictable state** - Each session has independent message history

**When to Use This Pattern**:
- Multi-session/tab apps (chat apps, workspaces, documents)
- Apps where users frequently switch contexts during async operations
- Optimistic updates needed for good UX
- Query data that varies by context (session ID, tab ID, workspace ID)

**Pattern Verified**: 2025-12-07 (Phase 2B - User message disappearing bug fix)

### Context API (React)

```tsx
// AuthContext.tsx
interface AuthContext {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContext | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);

  const login = async (email: string, password: string) => {
    const user = await loginAPI(email, password);
    setUser(user);
  };

  const logout = () => setUser(null);

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
}

// Usage
function App() {
  return (
    <AuthProvider>
      <Routes />
    </AuthProvider>
  );
}

function Header() {
  const { user, logout } = useAuth();
  return <div>{user?.name} <button onClick={logout}>Logout</button></div>;
}
```

### Svelte Stores

```ts
// stores/auth.ts
import { writable } from 'svelte/store';

interface User {
  id: number;
  name: string;
  email: string;
}

function createAuthStore() {
  const { subscribe, set, update } = writable<User | null>(null);

  return {
    subscribe,
    login: async (email: string, password: string) => {
      const user = await loginAPI(email, password);
      set(user);
    },
    logout: () => set(null)
  };
}

export const auth = createAuthStore();
```

```svelte
<!-- Usage in Svelte component -->
<script lang="ts">
  import { auth } from './stores/auth';
</script>

{#if $auth}
  <p>Welcome, {$auth.name}!</p>
  <button on:click={() => auth.logout()}>Logout</button>
{:else}
  <LoginForm />
{/if}
```

## Forms & Validation

### Type-Safe Validation with Zod

**Use Zod for schema validation** - type-safe, runtime validation for forms and API responses.

```tsx
// Schema definition (src/features/users/schemas/userSchema.ts)
import { z } from 'zod';

export const createUserSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Invalid email address'),
  age: z.number().min(18, 'Must be 18 or older').optional(),
});

export type CreateUserInput = z.infer<typeof createUserSchema>;
```

### Simple Form (Controlled Components + Zod)

```tsx
// React
import { useState } from 'react';
import { createUserSchema, type CreateUserInput } from './schemas/userSchema';

function UserForm() {
  const [formData, setFormData] = useState({ name: '', email: '' });
  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validate with Zod
    const result = createUserSchema.safeParse(formData);

    if (!result.success) {
      const fieldErrors: Record<string, string> = {};
      result.error.errors.forEach(err => {
        if (err.path[0]) {
          fieldErrors[err.path[0].toString()] = err.message;
        }
      });
      setErrors(fieldErrors);
      return;
    }

    // Data is now type-safe and validated
    await createUser(result.data);
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label htmlFor="email">Email</label>
        <input
          id="email"
          type="email"
          value={formData.email}
          onChange={e => setFormData({ ...formData, email: e.target.value })}
          aria-invalid={!!errors.email}
        />
        {errors.email && <p className="error">{errors.email}</p>}
      </div>

      <div>
        <label htmlFor="name">Name</label>
        <input
          id="name"
          type="text"
          value={formData.name}
          onChange={e => setFormData({ ...formData, name: e.target.value })}
          aria-invalid={!!errors.name}
        />
        {errors.name && <p className="error">{errors.name}</p>}
      </div>

      <button type="submit">Create User</button>
    </form>
  );
}
```

### React Hook Form + Zod (Best for Complex Forms)

```tsx
// react-hook-form + zod (minimal re-renders + type-safe validation)
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { createUserSchema, type CreateUserInput } from './schemas/userSchema';

function UserForm() {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<CreateUserInput>({
    resolver: zodResolver(createUserSchema),
  });

  const onSubmit = async (data: CreateUserInput) => {
    // Data is validated and type-safe
    await createUser(data);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <div>
        <label htmlFor="email">Email</label>
        <input
          id="email"
          type="email"
          {...register('email')}
          aria-invalid={!!errors.email}
        />
        {errors.email && <p className="error">{errors.email.message}</p>}
      </div>

      <div>
        <label htmlFor="name">Name</label>
        <input
          id="name"
          {...register('name')}
          aria-invalid={!!errors.name}
        />
        {errors.name && <p className="error">{errors.name.message}</p>}
      </div>

      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Creating...' : 'Create User'}
      </button>
    </form>
  );
}
```

### API Response Validation with Zod

```tsx
// Validate API responses at runtime
import { z } from 'zod';

const userSchema = z.object({
  id: z.number(),
  name: z.string(),
  email: z.string().email(),
  createdAt: z.string().datetime(),
});

export async function fetchUser(id: number): Promise<z.infer<typeof userSchema>> {
  const response = await fetch(`/api/users/${id}`);
  const data = await response.json();

  // Validate response matches expected schema
  return userSchema.parse(data); // Throws if invalid
}

// Or use safeParse for graceful handling
export async function fetchUserSafe(id: number) {
  const response = await fetch(`/api/users/${id}`);
  const data = await response.json();

  const result = userSchema.safeParse(data);
  if (!result.success) {
    console.error('Invalid API response:', result.error);
    throw new Error('Invalid API response');
  }

  return result.data;
}
```

## Error Handling

### Error Boundaries (React)

```tsx
// ErrorBoundary.tsx
import { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
    // Send to error tracking service
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div className="error-container">
          <h2>Something went wrong</h2>
          <p>{this.state.error?.message}</p>
          <button onClick={() => this.setState({ hasError: false })}>
            Try again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

// Usage
<ErrorBoundary>
  <App />
</ErrorBoundary>
```

### API Error Handling

```tsx
// api.ts
export class APIError extends Error {
  constructor(
    message: string,
    public status: number,
    public response?: any
  ) {
    super(message);
    this.name = 'APIError';
  }
}

async function fetchAPI<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, options);

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new APIError(
      error.detail || `Request failed: ${response.statusText}`,
      response.status,
      error
    );
  }

  return response.json();
}

// Usage
try {
  const users = await fetchAPI<User[]>('/api/users');
} catch (error) {
  if (error instanceof APIError) {
    if (error.status === 401) {
      // Handle unauthorized
    } else if (error.status === 404) {
      // Handle not found
    }
  }
}
```

## Performance Optimization

### React.memo & useMemo

```tsx
// Only re-render if props change
const UserCard = memo(function UserCard({ user }: { user: User }) {
  return <div>{user.name}</div>;
});

// Memoize expensive calculations
function UserList({ users }: { users: User[] }) {
  const sortedUsers = useMemo(() => {
    return users.sort((a, b) => a.name.localeCompare(b.name));
  }, [users]);

  return <>{sortedUsers.map(u => <UserCard key={u.id} user={u} />)}</>;
}
```

### Code Splitting

```tsx
// Route-based splitting
import { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';

const Home = lazy(() => import('./pages/Home'));
const Users = lazy(() => import('./pages/Users'));
const Settings = lazy(() => import('./pages/Settings'));

function App() {
  return (
    <BrowserRouter>
      <Suspense fallback={<div>Loading...</div>}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/users" element={<Users />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}
```

### Virtual Scrolling (Large Lists)

```tsx
// Use react-window for large lists
import { FixedSizeList } from 'react-window';

function UserList({ users }: { users: User[] }) {
  return (
    <FixedSizeList
      height={600}
      itemCount={users.length}
      itemSize={50}
      width="100%"
    >
      {({ index, style }) => (
        <div style={style}>
          {users[index].name}
        </div>
      )}
    </FixedSizeList>
  );
}
```

## Accessibility Best Practices

### Semantic HTML
```tsx
// Good
<nav>
  <ul>
    <li><a href="/">Home</a></li>
    <li><a href="/about">About</a></li>
  </ul>
</nav>

<main>
  <article>
    <h1>Title</h1>
    <p>Content</p>
  </article>
</main>

<footer>
  <p>&copy; 2024</p>
</footer>

// Bad
<div className="nav">
  <div onClick={() => navigate('/')}>Home</div>
</div>
```

### ARIA Attributes
```tsx
// Button with icon
<button
  onClick={handleDelete}
  aria-label="Delete user John Doe"
>
  <TrashIcon />
</button>

// Form validation
<input
  type="email"
  aria-invalid={!!error}
  aria-describedby="email-error"
/>
{error && (
  <p id="email-error" role="alert">
    {error}
  </p>
)}

// Modal
<div
  role="dialog"
  aria-modal="true"
  aria-labelledby="modal-title"
>
  <h2 id="modal-title">Confirm Delete</h2>
</div>
```

### Keyboard Navigation
```tsx
// Keyboard support for custom components
function TabList({ tabs }: { tabs: Tab[] }) {
  const [activeIndex, setActiveIndex] = useState(0);

  const handleKeyDown = (e: React.KeyboardEvent, index: number) => {
    if (e.key === 'ArrowRight') {
      setActiveIndex((index + 1) % tabs.length);
    } else if (e.key === 'ArrowLeft') {
      setActiveIndex((index - 1 + tabs.length) % tabs.length);
    }
  };

  return (
    <div role="tablist">
      {tabs.map((tab, i) => (
        <button
          key={tab.id}
          role="tab"
          aria-selected={i === activeIndex}
          tabIndex={i === activeIndex ? 0 : -1}
          onKeyDown={e => handleKeyDown(e, i)}
          onClick={() => setActiveIndex(i)}
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
}
```

### Complex Accessible Components (Radix UI)

**For complex interactive components, use Radix UI to avoid accessibility bugs:**

Radix UI provides unstyled, accessible primitives for:
- **Modals/Dialogs**: Focus trap, escape key, click outside
- **Dropdowns/Menus**: Keyboard navigation, ARIA roles
- **Select/Combobox**: Search, keyboard selection, screen reader support
- **Tooltips**: Hover/focus behavior, accessible descriptions
- **Tabs**: Keyboard navigation, ARIA attributes

**When to use:**
- ✅ Modals, dropdowns, combobox, tooltips, tabs, accordions
- ✅ Complex keyboard interactions needed
- ✅ Screen reader support critical
- ❌ Simple buttons, inputs, cards (build yourself)
- ❌ Basic layout components

```tsx
// Example: Accessible Modal with Radix UI
import * as Dialog from '@radix-ui/react-dialog';

function DeleteUserModal({ user, open, onOpenChange }: Props) {
  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/50" />
        <Dialog.Content className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-white p-6 rounded-lg">
          <Dialog.Title className="text-xl font-bold">
            Delete {user.name}?
          </Dialog.Title>
          <Dialog.Description className="mt-2 text-gray-600">
            This action cannot be undone. This will permanently delete the user.
          </Dialog.Description>

          <div className="mt-4 flex gap-2">
            <Dialog.Close asChild>
              <button className="px-4 py-2 bg-gray-200 rounded">Cancel</button>
            </Dialog.Close>
            <button className="px-4 py-2 bg-red-600 text-white rounded">
              Delete
            </button>
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
```

**Benefits:**
- ✅ Automatic focus management
- ✅ Correct ARIA attributes
- ✅ Keyboard navigation built-in
- ✅ Screen reader tested
- ✅ Unstyled (use Tailwind freely)

**Installation:**
```bash
# Install only what you need
npm install @radix-ui/react-dialog
npm install @radix-ui/react-dropdown-menu
npm install @radix-ui/react-select
```

## Testing Strategies

### Component Testing (Vitest + Testing Library)

```tsx
// UserCard.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { UserCard } from './UserCard';

describe('UserCard', () => {
  const mockUser = {
    id: 1,
    name: 'John Doe',
    email: 'john@example.com'
  };

  it('renders user information', () => {
    render(<UserCard user={mockUser} onDelete={vi.fn()} />);

    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('john@example.com')).toBeInTheDocument();
  });

  it('calls onDelete when button clicked', () => {
    const handleDelete = vi.fn();
    render(<UserCard user={mockUser} onDelete={handleDelete} />);

    fireEvent.click(screen.getByRole('button', { name: /delete/i }));
    expect(handleDelete).toHaveBeenCalledWith(mockUser.id);
  });

  it('is accessible', () => {
    const { container } = render(<UserCard user={mockUser} onDelete={vi.fn()} />);

    // Check for proper heading
    expect(screen.getByRole('heading', { name: 'John Doe' })).toBeInTheDocument();

    // Check for delete button with aria-label
    expect(screen.getByRole('button', { name: /delete.*john doe/i })).toBeInTheDocument();
  });
});
```

### E2E Testing (Playwright)

```typescript
// e2e/users.spec.ts
import { test, expect } from '@playwright/test';

test.describe('User Management', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:5173');
  });

  test('can create a new user', async ({ page }) => {
    // Fill form
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="name"]', 'Test User');

    // Submit
    await page.click('button[type="submit"]');

    // Verify user appears
    await expect(page.locator('text=Test User')).toBeVisible();
    await expect(page.locator('text=test@example.com')).toBeVisible();
  });

  test('shows validation errors', async ({ page }) => {
    // Submit empty form
    await page.click('button[type="submit"]');

    // Verify errors
    await expect(page.locator('text=Email is required')).toBeVisible();
    await expect(page.locator('text=Name is required')).toBeVisible();
  });

  test('can delete a user', async ({ page }) => {
    // Create user first
    await page.fill('input[name="email"]', 'delete@example.com');
    await page.fill('input[name="name"]', 'Delete Me');
    await page.click('button[type="submit"]');

    // Delete user
    await page.click('button[aria-label*="Delete"]');

    // Verify user removed
    await expect(page.locator('text=Delete Me')).not.toBeVisible();
  });
});
```

## Build & Deployment

### Optimize Build

```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          // Split vendor code
          vendor: ['react', 'react-dom'],
          router: ['react-router-dom']
        }
      }
    },
    // Optimize chunk size
    chunkSizeWarningLimit: 500,
    // Minify
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true, // Remove console.logs in production
      }
    }
  }
});
```

### Environment-Specific Builds

```json
// package.json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "build:staging": "vite build --mode staging",
    "build:production": "vite build --mode production",
    "preview": "vite preview"
  }
}
```

```bash
# .env.production
VITE_API_URL=https://api.production.com

# .env.staging
VITE_API_URL=https://api.staging.com
```

## Best Practices Summary

### Do
- ✅ Use TypeScript
- ✅ Keep components small
- ✅ Test accessibility
- ✅ Handle errors gracefully
- ✅ Optimize performance
- ✅ Use semantic HTML
- ✅ Lazy load routes
- ✅ Minimize dependencies

### Don't
- ❌ Over-engineer state
- ❌ Ignore accessibility
- ❌ Skip error handling
- ❌ Use div for everything
- ❌ Premature optimization
- ❌ Large bundle sizes
- ❌ Hardcode values
- ❌ Skip testing
