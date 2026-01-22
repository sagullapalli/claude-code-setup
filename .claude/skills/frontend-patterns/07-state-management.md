# React State Management Patterns

**Purpose**: Comprehensive patterns for choosing and implementing state management in React + TypeScript applications

**When to use**: Deciding between useState, Context, Zustand, Jotai, TanStack Query for client and server state

**Last Updated**: 2025-12-09

**Key Principle**: The best state management solution is the simplest one that works. ~90% of state management problems disappear when you properly separate server state from client state.

---

## Table of Contents

1. [Decision Framework](#decision-framework)
2. [State Colocation](#state-colocation)
3. [Server State vs Client State](#server-state-vs-client-state)
4. [React Context Patterns](#react-context-patterns)
5. [Zustand Patterns](#zustand-patterns)
6. [Jotai Patterns](#jotai-patterns)
7. [State Persistence](#state-persistence)
8. [Immer Integration](#immer-integration)
9. [DevTools Integration](#devtools-integration)
10. [Migration Patterns](#migration-patterns)
11. [Comparison Table](#comparison-table)

---

## Decision Framework

### The State Management Decision Tree

```
START
  │
  ├─ Is this data from the server (API)?
  │    └─ YES → Use TanStack Query
  │         └─ STOP (server state handled)
  │
  └─ NO → It's client state
       │
       ├─ Is it local to a single component?
       │    └─ YES → Use useState/useReducer
       │         └─ STOP (local state)
       │
       └─ NO → It's shared state
            │
            ├─ Is it simple, low-frequency (theme/auth)?
            │    └─ YES → Use Context API
            │         └─ STOP (simple global state)
            │
            └─ NO → High-frequency or complex updates
                 │
                 ├─ Small/medium app, need simplicity?
                 │    └─ YES → Use Zustand
                 │         └─ STOP (versatile middle ground)
                 │
                 ├─ Complex interdependent state?
                 │    └─ YES → Use Jotai
                 │         └─ STOP (atomic state)
                 │
                 └─ Enterprise app, strict patterns?
                      └─ YES → Use Redux Toolkit
                           └─ STOP (enterprise control)
```

### When to Use What

#### useState/useReducer
**Use for**:
- Local component state
- A few independent values
- Form inputs within a component
- UI state (modals, dropdowns, toggles)

**When to upgrade**: State needs to be shared with siblings or distant components

```typescript
// ✅ CORRECT: Local state
function LoginForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  // Form state stays local
}
```

#### Context API
**Use for**:
- Low-frequency updates (theme, locale, auth status)
- Small to medium apps
- Simple global state without complex logic
- Avoiding prop drilling for non-performance-critical data

**When to upgrade**: High-frequency updates causing performance issues

```typescript
// ✅ CORRECT: Context for theme
const ThemeContext = createContext<Theme>('light');

function App() {
  const [theme, setTheme] = useState<Theme>('light');

  return (
    <ThemeContext.Provider value={theme}>
      {children}
    </ThemeContext.Provider>
  );
}
```

#### TanStack Query
**Use for**:
- **ALL server state** (data from APIs)
- Caching, refetching, pagination
- Optimistic updates for mutations
- Background sync, stale-while-revalidate

**When NOT to use**: Client-only state (UI toggles, form drafts)

```typescript
// ✅ CORRECT: Server state
const { data: sessions } = useQuery({
  queryKey: ['sessions', userId],
  queryFn: () => fetchSessions(userId)
});
```

#### Zustand
**Use for**:
- Medium to large apps
- High-frequency client state updates
- Need for simplicity + performance
- Global UI state (sidebar open, selected items)
- When Context causes too many re-renders

**When to upgrade**: Need fine-grained reactivity for complex dependencies

```typescript
// ✅ CORRECT: Global UI state
const useUIStore = create<UIState>((set) => ({
  sidebarOpen: true,
  selectedItems: [],
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen }))
}));
```

#### Jotai
**Use for**:
- Complex interdependent state
- Fine-grained reactivity needed
- Derived state from multiple sources
- Apps needing atomic state updates

**When to upgrade**: Team requires stricter patterns (Redux)

```typescript
// ✅ CORRECT: Interdependent atoms
const userAtom = atom({ name: 'John', age: 30 });
const greetingAtom = atom((get) => {
  const user = get(userAtom);
  return `Hello, ${user.name}!`;
});
```

#### Redux Toolkit
**Use for**:
- Enterprise applications
- Multi-team projects
- Need for strict patterns and predictability
- Complex state with many interdependencies
- Time-travel debugging critical

**When NOT to use**: Small/medium apps (overkill, too much boilerplate)

---

## State Colocation

### Pattern: Keep State Close to Usage

**Principle**: State should live as close as possible to where it's used. Only lift state when multiple components need it.

```typescript
// ❌ WRONG: Lifting state unnecessarily
function App() {
  const [searchTerm, setSearchTerm] = useState(''); // Used only in SearchBar

  return (
    <div>
      <SearchBar value={searchTerm} onChange={setSearchTerm} />
      <OtherComponent /> {/* Doesn't need searchTerm */}
    </div>
  );
}

// ✅ CORRECT: Colocate state
function App() {
  return (
    <div>
      <SearchBar /> {/* searchTerm state lives here */}
      <OtherComponent />
    </div>
  );
}

function SearchBar() {
  const [searchTerm, setSearchTerm] = useState('');
  // State stays local
}
```

**Benefits**:
- Easier to maintain
- Better performance (fewer re-renders)
- Clearer data flow
- Easier to delete components

---

### Pattern: Lift State Only When Needed

**When to lift**:
- Two+ siblings need the same state
- Parent needs to coordinate children
- Multiple components need shared data

```typescript
// ✅ CORRECT: Lifting state for siblings
function ProductPage() {
  const [selectedSize, setSelectedSize] = useState('M'); // Shared

  return (
    <div>
      <SizeSelector value={selectedSize} onChange={setSelectedSize} />
      <AddToCartButton size={selectedSize} />
    </div>
  );
}
```

---

### Anti-Pattern: Global State for Everything

```typescript
// ❌ WRONG: Everything in global store
const useStore = create((set) => ({
  modalOpen: false, // Only used in one component
  searchTerm: '', // Only used in SearchBar
  tooltipText: '', // Only used in Tooltip
  // ... 50 more UI states
}));

// ✅ CORRECT: Keep local state local
function Modal() {
  const [isOpen, setIsOpen] = useState(false); // Local
}

function SearchBar() {
  const [searchTerm, setSearchTerm] = useState(''); // Local
}
```

**Rule**: If only one component needs it → useState. If 2-3 need it → lift to common parent. If many need it → global state.

---

## Server State vs Client State

### Pattern: Separate Server and Client State

**The 90% Rule**: Most state management problems disappear when you properly separate server state (TanStack Query) from client state (Zustand/Jotai/Context).

```typescript
// ✅ CORRECT: Server state in TanStack Query, client state in Zustand

// Server state (TanStack Query)
const { data: user } = useQuery({
  queryKey: ['user', userId],
  queryFn: () => fetchUser(userId)
});

// Client state (Zustand)
const { sidebarOpen, toggleSidebar } = useUIStore();
```

---

### Pattern: Don't Mix Server State in Client Stores

```typescript
// ❌ WRONG: Server data in Zustand
const useStore = create((set) => ({
  user: null,
  sessions: [],
  loadUser: async (id) => {
    const user = await fetchUser(id);
    set({ user }); // Manually managing cache
  }
}));

// ✅ CORRECT: Server state in TanStack Query
const { data: user } = useQuery({
  queryKey: ['user', userId],
  queryFn: () => fetchUser(userId),
  staleTime: 5 * 60 * 1000 // Automatic caching
});
```

**Why TanStack Query wins for server state**:
- Automatic caching, refetching, deduplication
- Stale-while-revalidate
- Optimistic updates
- Background sync
- Pagination, infinite queries
- Much less code than manual implementation

---

### Pattern: Combining Zustand + TanStack Query

**Best Practice**: Zustand owns client state, TanStack Query owns server state

```typescript
// Client state (Zustand)
interface UIState {
  sidebarOpen: boolean;
  selectedTheme: 'light' | 'dark';
  selectedItems: string[];
  toggleSidebar: () => void;
}

const useUIStore = create<UIState>((set) => ({
  sidebarOpen: true,
  selectedTheme: 'light',
  selectedItems: [],
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen }))
}));

// Server state (TanStack Query)
function Dashboard() {
  const { data: sessions } = useQuery({
    queryKey: ['sessions'],
    queryFn: fetchSessions
  });

  const { sidebarOpen, selectedTheme } = useUIStore();

  // Clean separation
}
```

**Result**: 90% of Redux's power at a fraction of code, bundle size, and cognitive load.

---

## React Context Patterns

### Pattern: Split Contexts by Domain and Update Frequency

**Problem**: Single context causes all consumers to re-render on any update

**Solution**: Separate contexts for different concerns

```typescript
// ❌ WRONG: Mega-context
const AppContext = createContext({
  user: null,
  theme: 'light',
  locale: 'en',
  sidebarOpen: true,
  notifications: [],
  // ... 20 more values
});

// ✅ CORRECT: Split contexts
const UserContext = createContext(null); // Low-frequency
const ThemeContext = createContext('light'); // Low-frequency
const UIContext = createContext({ sidebarOpen: true }); // High-frequency
```

**Rule**: One context per domain or update frequency

---

### Pattern: Separate State and Dispatch

**Problem**: Components re-render when actions are updated (even if stable)

**Solution**: Split state and dispatch into separate contexts

```typescript
// ✅ CORRECT: Separate state and dispatch
const StateContext = createContext<State | null>(null);
const DispatchContext = createContext<Dispatch | null>(null);

function Provider({ children }) {
  const [state, dispatch] = useReducer(reducer, initialState);

  return (
    <DispatchContext.Provider value={dispatch}>
      <StateContext.Provider value={state}>
        {children}
      </StateContext.Provider>
    </DispatchContext.Provider>
  );
}

// Components only using dispatch don't re-render on state changes
function ActionButton() {
  const dispatch = useContext(DispatchContext); // Stable reference
  return <button onClick={() => dispatch({ type: 'RESET' })}>Reset</button>;
}
```

---

### Pattern: Memoize Context Values

**Problem**: Context value object re-created on every render → all consumers re-render

**Solution**: Use `useMemo` for context value objects

```typescript
// ❌ WRONG: New object every render
function Provider({ children }) {
  const [count, setCount] = useState(0);

  return (
    <Context.Provider value={{ count, setCount }}> {/* New object! */}
      {children}
    </Context.Provider>
  );
}

// ✅ CORRECT: Memoized value
function Provider({ children }) {
  const [count, setCount] = useState(0);

  const value = useMemo(() => ({ count, setCount }), [count]);

  return (
    <Context.Provider value={value}>
      {children}
    </Context.Provider>
  );
}
```

---

### Pattern: Selector Pattern with Context

**Problem**: Components re-render even when their slice of context hasn't changed

**Solution**: Use selectors to extract specific data

```typescript
// ✅ CORRECT: Selector pattern
function createContextSelector<T>() {
  const Context = createContext<T | null>(null);

  function useSelector<R>(selector: (state: T) => R): R {
    const state = useContext(Context);
    if (!state) throw new Error('Missing provider');

    return useMemo(() => selector(state), [state, selector]);
  }

  return { Context, useSelector };
}

// Usage
const { Context, useSelector } = createContextSelector<AppState>();

function UserName() {
  // Only re-renders when user.name changes
  const name = useSelector((state) => state.user.name);
  return <div>{name}</div>;
}
```

---

### Pattern: Compound Components with Context

**Use for**: Related components sharing implicit state (Accordion, Tabs, Menu)

```typescript
// ✅ CORRECT: Compound components
const AccordionContext = createContext<AccordionContext | null>(null);

function Accordion({ children }: { children: React.ReactNode }) {
  const [openItem, setOpenItem] = useState<string | null>(null);

  const value = useMemo(() => ({ openItem, setOpenItem }), [openItem]);

  return (
    <AccordionContext.Provider value={value}>
      <div>{children}</div>
    </AccordionContext.Provider>
  );
}

function AccordionItem({ id, title, children }: AccordionItemProps) {
  const { openItem, setOpenItem } = useContext(AccordionContext)!;
  const isOpen = openItem === id;

  return (
    <div>
      <button onClick={() => setOpenItem(isOpen ? null : id)}>
        {title}
      </button>
      {isOpen && <div>{children}</div>}
    </div>
  );
}

// Usage: Clean, declarative API
<Accordion>
  <AccordionItem id="1" title="Section 1">Content 1</AccordionItem>
  <AccordionItem id="2" title="Section 2">Content 2</AccordionItem>
</Accordion>
```

---

### When to Use Context vs Libraries

**Use Context when**:
- Low-frequency updates (theme, auth, locale)
- Small to medium app
- Avoiding prop drilling 2-3 levels deep
- Simple state without complex logic

**Upgrade to Zustand/Jotai when**:
- High-frequency updates causing performance issues
- Context optimization becoming verbose
- Need devtools, time-travel debugging
- Managing complex derived state

---

## Zustand Patterns

### Pattern: Basic Store Setup with TypeScript

```typescript
import { create } from 'zustand';

// Define state + actions interface
interface BearState {
  // State
  bears: number;

  // Actions
  increasePopulation: () => void;
  removeAllBears: () => void;
  updateBears: (newBears: number) => void;
}

// ✅ CORRECT: TypeScript store
const useBearStore = create<BearState>((set) => ({
  bears: 0,
  increasePopulation: () => set((state) => ({ bears: state.bears + 1 })),
  removeAllBears: () => set({ bears: 0 }),
  updateBears: (newBears) => set({ bears: newBears })
}));

// Usage
function BearCounter() {
  const bears = useBearStore((state) => state.bears); // Selector
  return <div>{bears} bears</div>;
}

function Controls() {
  const increasePopulation = useBearStore((state) => state.increasePopulation);
  return <button onClick={increasePopulation}>Add Bear</button>;
}
```

**Key**: Use selectors to pick specific state → only re-renders when selected data changes

---

### Pattern: Slices Pattern (Modular Stores)

**For large stores**: Split into focused slices

```typescript
import { create, StateCreator } from 'zustand';

// Define combined store type
interface BoundState {
  user: UserSlice;
  ui: UISlice;
}

// User slice
interface UserSlice {
  name: string;
  age: number;
  setName: (name: string) => void;
}

const createUserSlice: StateCreator<BoundState, [], [], UserSlice> = (set) => ({
  name: 'John',
  age: 30,
  setName: (name) => set((state) => ({ user: { ...state.user, name } }))
});

// UI slice
interface UISlice {
  sidebarOpen: boolean;
  toggleSidebar: () => void;
}

const createUISlice: StateCreator<BoundState, [], [], UISlice> = (set) => ({
  sidebarOpen: true,
  toggleSidebar: () => set((state) => ({ ui: { ...state.ui, sidebarOpen: !state.ui.sidebarOpen } }))
});

// ✅ CORRECT: Combine slices
const useStore = create<BoundState>()((...a) => ({
  user: createUserSlice(...a),
  ui: createUISlice(...a)
}));

// Usage
function UserProfile() {
  const name = useStore((state) => state.user.name);
  const setName = useStore((state) => state.user.setName);
}
```

**Benefits**:
- Each slice in separate file
- Easier to maintain
- Testable in isolation
- Clear domain boundaries

---

### Pattern: Middleware (Persist + DevTools + Immer)

```typescript
import { create } from 'zustand';
import { devtools, persist, createJSONStorage } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';

interface StoreState {
  user: { name: string; age: number };
  updateUser: (updates: Partial<{ name: string; age: number }>) => void;
}

// ✅ CORRECT: Middleware composition
const useStore = create<StoreState>()(
  devtools(
    persist(
      immer((set) => ({
        user: { name: 'John', age: 30 },

        // Immer: mutate draft directly
        updateUser: (updates) => set((state) => {
          state.user = { ...state.user, ...updates }; // "Mutable" style
        })
      })),
      {
        name: 'user-storage', // localStorage key
        storage: createJSONStorage(() => localStorage)
      }
    ),
    { name: 'UserStore' } // DevTools name
  )
);
```

**Middleware order**:
1. `devtools` (outermost)
2. `persist`
3. `immer` (innermost)

**Important**: Apply middleware in combined store, NOT inside slices

---

### Pattern: Async Actions

```typescript
interface StoreState {
  user: User | null;
  loading: boolean;
  error: string | null;

  fetchUser: (id: string) => Promise<void>;
}

// ✅ CORRECT: Async actions
const useStore = create<StoreState>((set) => ({
  user: null,
  loading: false,
  error: null,

  fetchUser: async (id) => {
    set({ loading: true, error: null });

    try {
      const user = await fetchUserAPI(id);
      set({ user, loading: false });
    } catch (error) {
      set({ error: error.message, loading: false });
    }
  }
}));

// Usage
function UserProfile({ userId }: { userId: string }) {
  const { user, loading, error, fetchUser } = useStore();

  useEffect(() => {
    fetchUser(userId);
  }, [userId, fetchUser]);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return <div>{user?.name}</div>;
}
```

**Note**: For server data, prefer TanStack Query over manual async in Zustand

---

### Pattern: Selectors for Performance

```typescript
// ❌ WRONG: No selector → re-renders on ANY state change
function BearCounter() {
  const store = useBearStore(); // Entire store
  return <div>{store.bears}</div>; // Re-renders even if other fields change
}

// ✅ CORRECT: Selector → re-renders only when bears changes
function BearCounter() {
  const bears = useBearStore((state) => state.bears);
  return <div>{bears}</div>;
}

// ✅ CORRECT: Multiple selectors
function BearInfo() {
  const bears = useBearStore((state) => state.bears);
  const name = useBearStore((state) => state.name);

  // Re-renders only when bears OR name changes
}
```

**Advanced**: Use `shallow` for object equality

```typescript
import { shallow } from 'zustand/shallow';

// ✅ CORRECT: Shallow comparison for objects
const { bears, name } = useBearStore(
  (state) => ({ bears: state.bears, name: state.name }),
  shallow // Compare by key, not reference
);
```

---

### Pattern: SSR Compatibility (Next.js)

**Critical**: Don't use Zustand stores as global variables in Next.js (causes shared state across requests)

```typescript
// ❌ WRONG: Global store (shared across requests)
const useStore = create(() => ({ count: 0 }));

// ✅ CORRECT: Store factory + Context
import { createContext, useContext, useRef } from 'react';

const StoreContext = createContext(null);

export function StoreProvider({ children }) {
  const storeRef = useRef(null);

  if (!storeRef.current) {
    storeRef.current = create((set) => ({ count: 0 }));
  }

  return (
    <StoreContext.Provider value={storeRef.current}>
      {children}
    </StoreContext.Provider>
  );
}

export function useStore() {
  const store = useContext(StoreContext);
  if (!store) throw new Error('Missing StoreProvider');
  return store;
}
```

**Zustand + Next.js App Router**: Initialize stores at component level, not globally

---

## Jotai Patterns

### Pattern: Primitive Atoms

```typescript
import { atom, useAtom } from 'jotai';

// ✅ CORRECT: Primitive atoms
const countAtom = atom(0);
const nameAtom = atom('John');

function Counter() {
  const [count, setCount] = useAtom(countAtom);

  return (
    <div>
      <div>Count: {count}</div>
      <button onClick={() => setCount(count + 1)}>Increment</button>
    </div>
  );
}

function NameInput() {
  const [name, setName] = useAtom(nameAtom);

  return <input value={name} onChange={(e) => setName(e.target.value)} />;
}
```

**Benefits**:
- Minimal boilerplate
- Automatic fine-grained updates
- Components only re-render when their atoms change

---

### Pattern: Derived (Read-Only) Atoms

```typescript
import { atom, useAtomValue } from 'jotai';

const firstNameAtom = atom('John');
const lastNameAtom = atom('Doe');

// ✅ CORRECT: Derived atom
const fullNameAtom = atom((get) => {
  const first = get(firstNameAtom);
  const last = get(lastNameAtom);
  return `${first} ${last}`;
});

function FullName() {
  const fullName = useAtomValue(fullNameAtom); // Read-only
  return <div>{fullName}</div>;
}
```

**Pattern**: Derived atoms automatically update when dependencies change

---

### Pattern: Async Atoms

```typescript
import { atom, useAtom } from 'jotai';

// ✅ CORRECT: Async atom
const userAtom = atom(async (get) => {
  const userId = get(userIdAtom);
  const response = await fetch(`/api/users/${userId}`);
  return response.json();
});

function UserProfile() {
  const [user] = useAtom(userAtom);

  // Jotai + Suspense handles loading
  return <div>{user.name}</div>;
}

// Wrap with Suspense
function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <UserProfile />
    </Suspense>
  );
}
```

**Requirement**: Wrap components using async atoms in `<Suspense>`

---

### Pattern: Async Atoms with Error Boundaries

```typescript
import { Suspense } from 'react';
import { ErrorBoundary } from 'react-error-boundary';

// ✅ CORRECT: Suspense + Error Boundary
function App() {
  return (
    <ErrorBoundary fallback={<div>Error loading user</div>}>
      <Suspense fallback={<div>Loading...</div>}>
        <UserProfile />
      </Suspense>
    </ErrorBoundary>
  );
}
```

**Placement**: `ErrorBoundary -> Provider -> Suspense -> Component` (avoid loops)

---

### Pattern: Loadable API (Avoid Suspense)

**For manual loading/error handling** (without Suspense):

```typescript
import { atom } from 'jotai';
import { loadable } from 'jotai/utils';

const userAtom = atom(async () => {
  const response = await fetch('/api/user');
  return response.json();
});

const loadableUserAtom = loadable(userAtom);

// ✅ CORRECT: Manual state handling
function UserProfile() {
  const userLoadable = useAtomValue(loadableUserAtom);

  if (userLoadable.state === 'loading') return <div>Loading...</div>;
  if (userLoadable.state === 'hasError') return <div>Error: {userLoadable.error.message}</div>;

  // hasData
  return <div>{userLoadable.data.name}</div>;
}
```

**Returns**: `{ state: 'loading' | 'hasData' | 'hasError', data?, error? }`

---

### Pattern: atomWithStorage (Persistence)

```typescript
import { atomWithStorage } from 'jotai/utils';

// ✅ CORRECT: Persisted atom
const themeAtom = atomWithStorage<'light' | 'dark'>('theme', 'light');

function ThemeToggle() {
  const [theme, setTheme] = useAtom(themeAtom);

  // Automatically syncs to localStorage with key 'theme'
  return (
    <button onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}>
      Toggle Theme
    </button>
  );
}
```

**Default storage**: `localStorage` (can override with `sessionStorage` or custom)

---

### Pattern: atomFamily (Dynamic Atoms)

**For dynamic collections** (e.g., user profiles by ID):

```typescript
import { atomFamily } from 'jotai/utils';

// ✅ CORRECT: Atom family
const userAtomFamily = atomFamily((userId: string) =>
  atom(async () => {
    const response = await fetch(`/api/users/${userId}`);
    return response.json();
  })
);

function UserProfile({ userId }: { userId: string }) {
  const userAtom = userAtomFamily(userId); // Get/create atom for this ID
  const [user] = useAtom(userAtom);

  return <div>{user.name}</div>;
}
```

**Caching**: `atomFamily` caches atoms by param → same ID = same atom

**Memory management**: Explicitly remove unused atoms with `atomFamily.remove(param)`

---

### Pattern: TypeScript with Jotai

```typescript
import { atom, PrimitiveAtom, WritableAtom } from 'jotai';

// Explicit types for atoms
const countAtom: PrimitiveAtom<number> = atom(0);

const doubleCountAtom: WritableAtom<number, [number], void> = atom(
  (get) => get(countAtom) * 2,
  (get, set, newValue: number) => {
    set(countAtom, newValue / 2);
  }
);

// Generic atom family
interface User {
  id: string;
  name: string;
}

const userFamily = atomFamily<string, User>((userId) =>
  atom(async () => {
    const response = await fetch(`/api/users/${userId}`);
    return response.json();
  })
);
```

**TypeScript signature**: `atomFamily<Param, Value, Update>`

---

### Pattern: DevTools Integration

```typescript
import { useAtomDevtools } from 'jotai-devtools';

const countAtom = atom(0);

function Counter() {
  const [count, setCount] = useAtom(countAtom);

  // ✅ Enable devtools for this atom
  useAtomDevtools(countAtom, { name: 'count' });

  return <div>{count}</div>;
}
```

**Features**: Time-travel debugging, atom inspection, value dispatching

---

## State Persistence

### Pattern: localStorage with TypeScript

```typescript
// ✅ CORRECT: Type-safe localStorage utility
function useLocalStorage<T>(key: string, initialValue: T) {
  const [storedValue, setStoredValue] = useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error(`Error loading ${key}:`, error);
      return initialValue;
    }
  });

  const setValue = (value: T | ((val: T) => T)) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      window.localStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.error(`Error saving ${key}:`, error);
    }
  };

  return [storedValue, setValue] as const;
}

// Usage
function ThemeToggle() {
  const [theme, setTheme] = useLocalStorage<'light' | 'dark'>('theme', 'light');
}
```

---

### Pattern: Cross-Tab Synchronization

```typescript
// ✅ CORRECT: Sync state across tabs
function useLocalStorage<T>(key: string, initialValue: T) {
  const [storedValue, setStoredValue] = useState<T>(initialValue);

  // Listen to storage events (other tabs)
  useEffect(() => {
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === key && e.newValue) {
        setStoredValue(JSON.parse(e.newValue));
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, [key]);

  const setValue = (value: T) => {
    setStoredValue(value);
    window.localStorage.setItem(key, JSON.stringify(value));
  };

  return [storedValue, setValue] as const;
}
```

**Note**: `storage` event only fires in OTHER tabs, not the current one

---

### Pattern: useSyncExternalStore for localStorage

**Modern React approach** (React 18+):

```typescript
import { useSyncExternalStore } from 'react';

// ✅ CORRECT: useSyncExternalStore for localStorage
function useLocalStorage<T>(key: string, initialValue: T) {
  const subscribe = (callback: () => void) => {
    window.addEventListener('storage', callback);
    return () => window.removeEventListener('storage', callback);
  };

  const getSnapshot = () => {
    const item = window.localStorage.getItem(key);
    return item ? JSON.parse(item) : initialValue;
  };

  const value = useSyncExternalStore(subscribe, getSnapshot, getSnapshot);

  const setValue = (newValue: T) => {
    window.localStorage.setItem(key, JSON.stringify(newValue));
    window.dispatchEvent(new Event('storage')); // Trigger sync
  };

  return [value, setValue] as const;
}
```

**Benefits**: Automatic sync, server-safe (SSR), React 18 concurrent features

---

### Pattern: sessionStorage vs localStorage vs IndexedDB

**When to use what**:

| Storage | Capacity | Use Case | Sync |
|---------|----------|----------|------|
| `localStorage` | ~5MB | User preferences, theme, auth tokens | ✅ Cross-tab (storage event) |
| `sessionStorage` | ~5MB | Temporary data (wizard state, tab-specific) | ❌ Tab-isolated |
| `IndexedDB` | 50MB+ | Large datasets, offline data, images | ✅ BroadcastChannel |

```typescript
// ✅ CORRECT: sessionStorage for tab-specific state
const [wizardStep, setWizardStep] = useSessionStorage('wizardStep', 1);

// ✅ CORRECT: localStorage for user preferences
const [theme, setTheme] = useLocalStorage('theme', 'light');

// ✅ CORRECT: IndexedDB for large data
import { openDB } from 'idb';

const db = await openDB('myDB', 1, {
  upgrade(db) {
    db.createObjectStore('sessions');
  }
});

await db.put('sessions', sessionData, sessionId);
const session = await db.get('sessions', sessionId);
```

---

### Pattern: Zustand Persist Middleware

```typescript
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

// ✅ CORRECT: Zustand persist
const useStore = create(
  persist(
    (set) => ({
      theme: 'light',
      setTheme: (theme) => set({ theme })
    }),
    {
      name: 'app-storage', // localStorage key
      storage: createJSONStorage(() => localStorage), // or sessionStorage

      // Optional: Only persist specific keys
      partialize: (state) => ({ theme: state.theme })
    }
  )
);
```

---

### Pattern: Jotai atomWithStorage

```typescript
import { atomWithStorage } from 'jotai/utils';

// ✅ CORRECT: Jotai persist
const themeAtom = atomWithStorage<'light' | 'dark'>('theme', 'light');

// Custom storage (sessionStorage)
const sessionAtom = atomWithStorage(
  'sessionData',
  initialData,
  {
    getItem: (key) => sessionStorage.getItem(key),
    setItem: (key, value) => sessionStorage.setItem(key, value),
    removeItem: (key) => sessionStorage.removeItem(key)
  }
);
```

---

## Immer Integration

### Pattern: Immer with Zustand

**Problem**: Immutable updates are verbose for nested state

**Solution**: Use Immer middleware for "mutable" style

```typescript
import { create } from 'zustand';
import { immer } from 'zustand/middleware/immer';

interface State {
  user: {
    profile: {
      name: string;
      address: {
        city: string;
        zip: string;
      };
    };
  };
  updateCity: (city: string) => void;
}

// ❌ WRONG: Manual immutable updates (verbose)
const useStore = create<State>((set) => ({
  user: { profile: { name: 'John', address: { city: 'NYC', zip: '10001' } } },

  updateCity: (city) => set((state) => ({
    user: {
      ...state.user,
      profile: {
        ...state.user.profile,
        address: {
          ...state.user.profile.address,
          city // So much spreading!
        }
      }
    }
  }))
}));

// ✅ CORRECT: Immer middleware (mutable style)
const useStore = create<State>()(
  immer((set) => ({
    user: { profile: { name: 'John', address: { city: 'NYC', zip: '10001' } } },

    updateCity: (city) => set((state) => {
      state.user.profile.address.city = city; // "Mutate" draft directly
    })
  }))
);
```

**Benefits**:
- Cleaner syntax for nested updates
- Less boilerplate
- Same immutability guarantees

---

### Pattern: Immer Performance Tips

```typescript
// ✅ CORRECT: Large datasets
import { freeze } from 'immer';

const largeDataset = freeze(hugeArray); // Pre-freeze for faster Immer processing

set((state) => {
  state.data = largeDataset; // Immer skips frozen data
});
```

**When to use Immer**:
- Deeply nested state structures
- Complex updates across multiple levels
- When manual spreading becomes unreadable

**When NOT to use Immer**:
- Flat state structures (useState is fine)
- Performance-critical tight loops (Immer has overhead)

---

## DevTools Integration

### Pattern: Redux DevTools with Zustand

```typescript
import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

// ✅ CORRECT: DevTools middleware
const useStore = create<State>()(
  devtools(
    (set) => ({
      count: 0,
      increment: () => set((state) => ({ count: state.count + 1 }), false, 'increment')
    }),
    {
      name: 'MyStore', // DevTools connection name
      enabled: process.env.NODE_ENV === 'development' // Only in dev
    }
  )
);
```

**Features**:
- Time-travel debugging
- Action history
- State inspection

---

### Pattern: Filter Actions from DevTools

```typescript
// ✅ CORRECT: Filter noisy actions
devtools(
  (set) => ({ /* store */ }),
  {
    name: 'MyStore',
    actionsDenylist: ['updateMouse', 'tick'] // Exclude these actions
  }
)
```

---

### Pattern: Jotai DevTools

```typescript
import { useAtomDevtools, useAtomsDevtools } from 'jotai-devtools';

const countAtom = atom(0);

function Counter() {
  const [count, setCount] = useAtom(countAtom);

  // ✅ Single atom devtools
  useAtomDevtools(countAtom, { name: 'count' });

  return <div>{count}</div>;
}

// ✅ All atoms devtools
function App() {
  useAtomsDevtools('MyApp'); // Track all atoms

  return <div>{/* app */}</div>;
}
```

**Features**: Atom inspection, time-travel, value dispatching

---

## Migration Patterns

### Pattern: When to Migrate (Decision Framework)

**DON'T migrate if**:
- Current solution works fine
- No performance issues
- No developer complaints
- No state-related bugs

**Consider migration when**:
- State updates lag user interactions
- Components re-render excessively
- State logic duplicated across components
- Frequent state-related bugs
- Context optimization becoming verbose

---

### Pattern: Migrating from Context to Zustand

```typescript
// BEFORE: Context
const UserContext = createContext(null);

function UserProvider({ children }) {
  const [user, setUser] = useState(null);

  const value = useMemo(() => ({ user, setUser }), [user]);

  return <UserContext.Provider value={value}>{children}</UserContext.Provider>;
}

function useUser() {
  return useContext(UserContext);
}

// AFTER: Zustand
import { create } from 'zustand';

const useUserStore = create<UserState>((set) => ({
  user: null,
  setUser: (user) => set({ user })
}));

// ✅ Remove provider, direct import
function UserProfile() {
  const user = useUserStore((state) => state.user);
}
```

**Benefits**: No provider, better performance, less boilerplate

---

### Pattern: Migrating from Redux to Zustand

```typescript
// BEFORE: Redux
const userSlice = createSlice({
  name: 'user',
  initialState: { user: null },
  reducers: {
    setUser: (state, action) => {
      state.user = action.payload;
    }
  }
});

// AFTER: Zustand (90% less code)
const useUserStore = create<UserState>((set) => ({
  user: null,
  setUser: (user) => set({ user })
}));
```

**Steps**:
1. Identify Redux slices → convert to Zustand stores/slices
2. Replace `useSelector` → Zustand selectors
3. Replace `useDispatch` → direct action calls
4. Remove Redux boilerplate (actions, reducers, store setup)
5. Test incrementally (migrate one slice at a time)

---

### Pattern: When NOT to Migrate

**Keep Redux if**:
- Enterprise app with strict patterns required
- Multi-team project needing predictability
- Existing Redux setup works well
- Team familiar with Redux, not willing to learn new tool

**Keep Context if**:
- Small app with simple state
- Low-frequency updates only
- No performance issues
- Avoiding dependencies

**Rule**: Don't migrate for the sake of migrating. Only upgrade when current solution has problems.

---

## Comparison Table

### Features Comparison

| Feature | Context | Zustand | Jotai | Redux Toolkit | TanStack Query |
|---------|---------|---------|-------|---------------|----------------|
| **Bundle Size** | 0 (built-in) | ~1KB | ~1.2KB | ~15KB | ~13KB |
| **Boilerplate** | Low | Minimal | Minimal | High | Low |
| **TypeScript** | Manual | Good | Excellent | Excellent | Excellent |
| **DevTools** | ❌ | ✅ Redux DevTools | ✅ Jotai DevTools | ✅ Redux DevTools | ✅ React Query DevTools |
| **Persist** | Manual | ✅ Middleware | ✅ atomWithStorage | ✅ redux-persist | ✅ Built-in |
| **SSR/SSG** | ✅ | ⚠️ (needs setup) | ✅ | ⚠️ (needs setup) | ✅ |
| **Async** | Manual | Manual | ✅ Built-in | ✅ Thunks | ✅ Built-in |
| **Suspense** | Manual | Manual | ✅ | ❌ | ✅ |
| **Learning Curve** | Low | Low | Medium | High | Medium |
| **Performance** | ⚠️ Can re-render | ✅ Excellent | ✅ Excellent | ✅ Good | ✅ Excellent |

---

### Use Cases Comparison

| Use Case | Recommended Solution | Why |
|----------|---------------------|-----|
| Local component state | `useState` | Simplest, built-in |
| Form state | `useState` + React Hook Form | Specialized for forms |
| Theme, locale, auth status | Context API | Low-frequency, small app |
| Server data (API) | TanStack Query | Built for caching, refetching |
| Global UI state (medium app) | Zustand | Versatile, minimal boilerplate |
| Complex interdependent state | Jotai | Fine-grained reactivity |
| Enterprise app (multi-team) | Redux Toolkit | Strict patterns, predictability |
| Offline-first app | IndexedDB + TanStack Query | Large data, background sync |

---

## Summary

### Key Patterns

1. **Separate server state from client state**
   - TanStack Query for server data
   - Zustand/Jotai/Context for client UI state

2. **Colocate state as close to usage as possible**
   - Only lift when multiple components need it
   - Avoid global state for local concerns

3. **Start simple, scale when needed**
   - useState → Context → Zustand/Jotai → Redux
   - Don't prematurely optimize

4. **Use selectors for performance**
   - Zustand: `useStore((state) => state.value)`
   - Jotai: Atomic updates by default

5. **Leverage middleware/utilities**
   - Persist: Zustand/Jotai storage middleware
   - DevTools: Redux DevTools for debugging
   - Immer: Clean nested updates

---

### Common Mistakes

❌ **Using global state for everything**
→ ✅ Colocate state, lift only when needed

❌ **Mixing server state in client stores**
→ ✅ Use TanStack Query for all API data

❌ **Premature optimization**
→ ✅ Start simple, upgrade when problems appear

❌ **Context without memoization**
→ ✅ Memoize values, split contexts by domain

❌ **Not using selectors in Zustand**
→ ✅ Always select specific state to minimize re-renders

❌ **Forgetting Suspense with async Jotai atoms**
→ ✅ Wrap in `<Suspense>` or use `loadable`

❌ **Global Zustand stores in Next.js SSR**
→ ✅ Use store factory + Context for per-request stores

---

### Quick Reference

**Decision Tree**:
```
Server data? → TanStack Query
Local component? → useState
Low-frequency global (theme)? → Context
High-frequency global? → Zustand (simple) or Jotai (complex)
Enterprise patterns? → Redux Toolkit
```

**Performance**:
- Context: Memoize values, split contexts, selectors
- Zustand: Use selectors, shallow comparison
- Jotai: Atomic updates (built-in optimization)

**Persistence**:
- Zustand: `persist` middleware
- Jotai: `atomWithStorage`
- Manual: `useLocalStorage` hook + `useSyncExternalStore`

**Async**:
- Server state: TanStack Query (preferred)
- Client async: Jotai async atoms + Suspense
- Zustand: Manual async actions (loading/error states)

---

## Related Skills

- **[04-tanstack-query.md](04-tanstack-query.md)** - Server state management with TanStack Query
- **[03-react-performance.md](03-react-performance.md)** - Performance optimization patterns
- **[05-form-handling.md](05-form-handling.md)** - Form state management with React Hook Form
- **[06-react-router-patterns.md](06-react-router-patterns.md)** - Router state and navigation

---

## Sources

- [Do You Need State Management in 2025? React Context vs Zustand vs Jotai vs Redux](https://dev.to/saswatapal/do-you-need-state-management-in-2025-react-context-vs-zustand-vs-jotai-vs-redux-1ho)
- [State Management Trends in React 2025: When to Use Zustand, Jotai, XState, or Something Else](https://makersden.io/blog/react-state-management-in-2025)
- [State Management in 2025: When to Use Context, Redux, Zustand, or Jotai](https://dev.to/hijazi313/state-management-in-2025-when-to-use-context-redux-zustand-or-jotai-2d2k)
- [React State Management in 2025: What You Actually Need](https://www.developerway.com/posts/react-state-management-2025)
- [Zustand Official Documentation - Slices Pattern](https://zustand.docs.pmnd.rs/guides/slices-pattern)
- [Zustand Official Documentation - DevTools](https://zustand.docs.pmnd.rs/middlewares/devtools)
- [Zustand Official Documentation - Persist](https://zustand.docs.pmnd.rs/middlewares/persist)
- [Zustand Official Documentation - Immer](https://zustand.docs.pmnd.rs/middlewares/immer)
- [Zustand Official Documentation - Setup with Next.js](https://zustand.docs.pmnd.rs/guides/nextjs)
- [Jotai Official Documentation - Atom](https://jotai.org/docs/core/atom)
- [Jotai Official Documentation - Async](https://jotai.org/docs/guides/async)
- [Jotai Official Documentation - Family](https://jotai.org/docs/utilities/family)
- [Jotai Official Documentation - DevTools](https://jotai.org/docs/tools/devtools)
- [Optimizing React Context for Performance](https://www.tenxdeveloper.com/blog/optimizing-react-context-performance)
- [How to optimize your context value](https://kentcdodds.com/blog/how-to-optimize-your-context-value)
- [How to write performant React apps with Context](https://www.developerway.com/posts/how-to-write-performant-react-apps-with-context)
- [State Colocation will make your React app faster](https://kentcdodds.com/blog/state-colocation-will-make-your-react-app-faster)
- [Separating Concerns with Zustand and TanStack Query](https://volodymyrrudyi.com/blog/separating-concerns-with-zustand-and-tanstack-query/)
- [Does TanStack Query replace Redux, MobX or other global state managers?](https://tanstack.com/query/v5/docs/framework/react/guides/does-this-replace-client-state)
- [Redux vs TanStack Query & Zustand: The 2025 Verdict](https://www.bugragulculer.com/blog/good-bye-redux-how-react-query-and-zustand-re-wired-state-management-in-25)
- [How to Manage State Across Multiple Tabs and Windows](https://blog.pixelfreestudio.com/how-to-manage-state-across-multiple-tabs-and-windows/)
- [Sync Local Storage state across tabs in React using useSyncExternalStore](https://oakhtar147.medium.com/sync-local-storage-state-across-tabs-in-react-using-usesyncexternalstore-613d2c22819e)
- [Master Browser Storage in 2025: The Ultimate Guide for Front-End Developers](https://medium.com/@osamajavaid/master-browser-storage-in-2025-the-ultimate-guide-for-front-end-developers-7b2735b4cc13)
- [Immer Official Documentation - React & Immer](https://immerjs.github.io/immer/example-setstate/)
- [Immer Official Documentation - Performance](https://immerjs.github.io/immer/performance/)
- [Zustand vs. Redux Toolkit vs. Jotai](https://betterstack.com/community/guides/scaling-nodejs/zustand-vs-redux-toolkit-vs-jotai/)
- [Zustand Official Comparison](https://zustand.docs.pmnd.rs/getting-started/comparison)
- [Jotai Official Comparison](https://jotai.org/docs/basics/comparison)
- [Compound Pattern](https://www.patterns.dev/react/compound-pattern/)
- [Mastering the Compound Pattern in React with TypeScript](https://pasquale-favella.github.io/blog/28)
- [React Compound component with Typescript](https://medium.com/@win.le/react-compound-component-with-typescript-d7944ac0d1d6)
- [Moving away from Redux to SWR + Zustand](https://medium.com/@riyalh1997/moving-away-from-redux-to-swr-zustand-cd5217471867)
