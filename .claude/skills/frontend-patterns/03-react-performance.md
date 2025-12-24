# React Performance Patterns

**Purpose**: Performance optimization patterns for React + TypeScript + Vite applications

**When to use**: Optimizing bundle size, state management, query performance, and component rendering

**Last Updated**: 2025-12-08

---

## Table of Contents

1. [Bundle Optimization](#bundle-optimization)
2. [Query Optimization](#query-optimization)
3. [State Management Patterns](#state-management-patterns)
4. [Component Patterns](#component-patterns)
5. [Asset Optimization](#asset-optimization)

---

## Bundle Optimization

### Pattern: Manual Chunk Splitting

**Configure Vite** to split code into optimal chunks:

**`vite.config.ts`**:
```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          // Vendor chunk (React + React DOM)
          vendor: ['react', 'react-dom'],

          // Router chunk
          router: ['react-router-dom'],

          // Query chunk (TanStack Query)
          query: ['@tanstack/react-query'],

          // UI library chunk (if using one)
          // ui: ['@radix-ui/react-dropdown-menu', '@radix-ui/react-dialog'],
        }
      }
    },
    chunkSizeWarningLimit: 500 // Warn if chunk > 500KB
  }
});
```

**Benefits**:
- ✅ Vendor code cached separately (rarely changes)
- ✅ Better long-term caching
- ✅ Parallel chunk loading
- ✅ Smaller initial bundle

---

### Pattern: Dynamic Imports for Route-Based Code Splitting

**Split routes** into separate chunks:

```typescript
import { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';

// ✅ Lazy load route components
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Settings = lazy(() => import('./pages/Settings'));
const Profile = lazy(() => import('./pages/Profile'));

function App() {
  return (
    <BrowserRouter>
      <Suspense fallback={<LoadingSpinner />}>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/profile" element={<Profile />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}
```

**Result**: Each route loaded only when needed (not upfront)

---

### Pattern: Component-Level Code Splitting

**Split heavy components**:

```typescript
import { lazy, Suspense } from 'react';

// Heavy component (e.g., chart library, rich text editor)
const ChartComponent = lazy(() => import('./components/Chart'));

function Dashboard() {
  const [showChart, setShowChart] = useState(false);

  return (
    <div>
      <button onClick={() => setShowChart(true)}>Show Chart</button>

      {showChart && (
        <Suspense fallback={<div>Loading chart...</div>}>
          <ChartComponent data={chartData} />
        </Suspense>
      )}
    </div>
  );
}
```

**Use when**: Component uses heavy libraries (charts, editors, 3D rendering)

---

### Pattern: Bundle Analysis

**Analyze bundle size**:

```bash
# Install bundle analyzer
npm install -D rollup-plugin-visualizer

# Add to vite.config.ts
import { visualizer } from 'rollup-plugin-visualizer';

export default defineConfig({
  plugins: [
    react(),
    visualizer({ open: true }) // Opens report after build
  ]
});

# Build and analyze
npm run build
```

**Look for**:
- Large dependencies (can you use lighter alternatives?)
- Duplicate dependencies (check package versions)
- Unused code (tree-shaking opportunities)

---

## Query Optimization

### Pattern: Query Configuration for Performance

**Configure TanStack Query** for optimal performance:

```typescript
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Cache data for 5 minutes (reduce refetch frequency)
      staleTime: 5 * 60 * 1000,

      // Only retry once (don't hammer backend)
      retry: 1,

      // Don't refetch on window focus for static data
      refetchOnWindowFocus: false,

      // Refetch on mount (get fresh data)
      refetchOnMount: true,

      // Refetch on network reconnect
      refetchOnReconnect: true,

      // Keep unused data in cache for 5 minutes
      gcTime: 5 * 60 * 1000, // Previously cacheTime
    },
    mutations: {
      // Don't retry mutations (could duplicate actions)
      retry: 0,
    }
  }
});
```

---

### Pattern: Selective Query Disabling

**Don't fetch** until ready:

```typescript
// ❌ BAD: Fetches immediately even if sessionId is undefined
const { data } = useQuery({
  queryKey: ['messages', sessionId],
  queryFn: () => fetchMessages(sessionId)
});

// ✅ GOOD: Only fetches when sessionId exists and user is authenticated
const { data } = useQuery({
  queryKey: ['messages', sessionId],
  queryFn: () => fetchMessages(sessionId),
  enabled: !!sessionId && isAuthenticated
});
```

---

### Pattern: Query Data Normalization

**Normalize data** to reduce memory and improve lookups:

```typescript
// ❌ BAD: Duplicate data in memory
const sessions = [
  { id: '1', userId: 'user1', messages: [...100 messages] },
  { id: '2', userId: 'user1', messages: [...100 messages] },
];

// ✅ GOOD: Separate queries, normalized data
const { data: sessions } = useQuery({
  queryKey: ['sessions', userId],
  queryFn: fetchSessions,
  select: (data) => data.map(s => ({ id: s.id, subject: s.subject, lastActivity: s.lastActivity }))
});

const { data: messages } = useQuery({
  queryKey: ['messages', currentSessionId],
  queryFn: () => fetchMessages(currentSessionId),
  enabled: !!currentSessionId
});
```

**Benefits**:
- ✅ Less memory usage
- ✅ Faster lookups
- ✅ Independent invalidation

---

## State Management Patterns

### Pattern: Accumulation vs Replacement

**Understand when to accumulate vs replace**:

```typescript
// REPLACEMENT Pattern (single value)
const [currentUser, setCurrentUser] = useState<User | null>(null);

// User logs in
setCurrentUser(newUser); // ✅ Replace

// ACCUMULATION Pattern (list/history)
const [messages, setMessages] = useState<Message[]>([]);

// New message arrives
setMessages(prev => [...prev, newMessage]); // ✅ Accumulate

// ❌ WRONG: Replace (loses history)
setMessages([newMessage]);
```

**When to accumulate**:
- Chat messages
- Tool call history
- Notification queue
- Event logs

**When to replace**:
- Current user
- Active session
- Selected item
- Form values

---

### Pattern: Lazy Initial State

**Expensive initial state** computation:

```typescript
// ❌ BAD: Runs on every render
const [state, setState] = useState(expensiveComputation());

// ✅ GOOD: Runs only once (lazy initialization)
const [state, setState] = useState(() => expensiveComputation());
```

**Example**:
```typescript
const [messagesMap, setMessagesMap] = useState(() => {
  // Load from localStorage only once
  const stored = localStorage.getItem('messagesMap');
  return stored ? new Map(JSON.parse(stored)) : new Map();
});
```

---

### Pattern: Derived State (Don't Store What You Can Calculate)

```typescript
// ❌ BAD: Storing derived state (can get out of sync)
const [messages, setMessages] = useState<Message[]>([]);
const [messageCount, setMessageCount] = useState(0);

// When adding message, must update both
setMessages(prev => [...prev, newMessage]);
setMessageCount(prev => prev + 1); // Easy to forget!

// ✅ GOOD: Calculate derived state
const [messages, setMessages] = useState<Message[]>([]);
const messageCount = messages.length; // Always in sync
```

**Rule**: If you can calculate it from existing state, don't store it

---

### Pattern: State Colocation

**Keep state close** to where it's used:

```typescript
// ❌ BAD: Global state for local concern
function App() {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false); // Used only in Header
  return <Header isOpen={isDropdownOpen} setIsOpen={setIsDropdownOpen} />;
}

// ✅ GOOD: Local state in component
function Header() {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false); // Local to Header
  return <Dropdown open={isDropdownOpen} onToggle={setIsDropdownOpen} />;
}
```

**Benefits**:
- ✅ Easier to understand
- ✅ Less re-renders
- ✅ Better encapsulation

---

## Component Patterns

### Pattern: Composition Over Props

**Use composition** for flexible UIs:

```typescript
// ❌ BAD: Too many boolean props
function Card({ showHeader, showFooter, headerContent, footerContent, children }) {
  return (
    <div className="card">
      {showHeader && <div className="header">{headerContent}</div>}
      <div className="body">{children}</div>
      {showFooter && <div className="footer">{footerContent}</div>}
    </div>
  );
}

// ✅ GOOD: Composition with slots
function Card({ header, footer, children }) {
  return (
    <div className="card">
      {header && <div className="header">{header}</div>}
      <div className="body">{children}</div>}
      {footer && <div className="footer">{footer}</div>}
    </div>
  );
}

// Usage
<Card
  header={<h2>Title</h2>}
  footer={<button>Action</button>}
>
  Content here
</Card>
```

---

### Pattern: Native HTML for Accessibility

**Use native HTML** instead of custom components:

```typescript
// ❌ BAD: Custom accordion (complex, needs keyboard support)
function Accordion({ items }) {
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  return (
    <div>
      {items.map((item, i) => (
        <div key={i}>
          <button onClick={() => setOpenIndex(i === openIndex ? null : i)}>
            {item.title}
          </button>
          {openIndex === i && <div>{item.content}</div>}
        </div>
      ))}
    </div>
  );
}

// ✅ GOOD: Native <details> (keyboard support built-in)
function Accordion({ items }) {
  return (
    <div>
      {items.map((item, i) => (
        <details key={i}>
          <summary>{item.title}</summary>
          <div>{item.content}</div>
        </details>
      ))}
    </div>
  );
}
```

**Native HTML elements with built-in features**:
- `<details>` / `<summary>` - Accordion
- `<dialog>` - Modal
- `<input type="date">` - Date picker
- `<select>` - Dropdown

---

### Pattern: Memoization (use sparingly)

**Use `React.memo`** only for expensive components:

```typescript
// ✅ Good use case: Expensive list item component
const ExpensiveListItem = React.memo(function ListItem({ data }: { data: Item }) {
  // Heavy computation or rendering
  const processedData = useMemo(() => expensiveCalculation(data), [data]);

  return <div>{processedData.display}</div>;
});

// Usage
function List({ items }) {
  return (
    <div>
      {items.map(item => (
        <ExpensiveListItem key={item.id} data={item} />
      ))}
    </div>
  );
}
```

**Don't over-optimize**:
```typescript
// ❌ NOT needed: Simple component (premature optimization)
const SimpleButton = React.memo(function Button({ onClick, label }) {
  return <button onClick={onClick}>{label}</button>;
});
```

**Rule**: Profile first, optimize second

---

## Asset Optimization

### Pattern: Image Optimization

**Optimize images**:

```typescript
// ✅ Responsive images with srcset
function ProductImage({ src, alt }: { src: string; alt: string }) {
  return (
    <img
      src={src}
      srcSet={`${src}?w=400 400w, ${src}?w=800 800w, ${src}?w=1200 1200w`}
      sizes="(max-width: 640px) 400px, (max-width: 1024px) 800px, 1200px"
      alt={alt}
      loading="lazy" // Lazy load images below fold
    />
  );
}

// ✅ WebP with fallback
function OptimizedImage({ src, alt }: { src: string; alt: string }) {
  return (
    <picture>
      <source srcSet={src.replace('.jpg', '.webp')} type="image/webp" />
      <img src={src} alt={alt} loading="lazy" />
    </picture>
  );
}
```

---

### Pattern: Font Optimization

**Optimize web fonts**:

```html
<!-- In index.html -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
```

```css
/* In CSS */
@font-face {
  font-family: 'Inter';
  src: url('/fonts/inter-var.woff2') format('woff2');
  font-display: swap; /* Show fallback font immediately */
  font-weight: 100 900;
}
```

---

### Pattern: Tree-Shaking

**Import only what you need**:

```typescript
// ❌ BAD: Imports entire library
import _ from 'lodash';
const result = _.debounce(fn, 300);

// ✅ GOOD: Import specific function
import debounce from 'lodash/debounce';
const result = debounce(fn, 300);

// ✅ BETTER: Use native alternative
const debounce = (fn, delay) => {
  let timeoutId;
  return (...args) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn(...args), delay);
  };
};
```

---

## Summary

**Key Patterns**:

1. **Bundle Optimization**:
   - Manual chunk splitting (vendor, router, query)
   - Route-based code splitting with lazy()
   - Bundle analysis with visualizer

2. **Query Optimization**:
   - Configure staleTime, retry, refetchOnWindowFocus
   - Use `enabled` prop to prevent unnecessary fetches
   - Normalize data to reduce memory

3. **State Management**:
   - Accumulate for lists, replace for single values
   - Lazy initial state for expensive computations
   - Derive state instead of storing it
   - Colocate state close to usage

4. **Component Patterns**:
   - Composition over props
   - Native HTML for accessibility
   - Memoization only for expensive components
   - Profile before optimizing

5. **Asset Optimization**:
   - Responsive images with srcset
   - Lazy loading images
   - Font optimization with preconnect
   - Tree-shaking with specific imports

**Common Mistakes**:

- ❌ Premature optimization (memoizing simple components)
- ❌ Not using `enabled` on queries (unnecessary fetches)
- ❌ Storing derived state (can get out of sync)
- ❌ Global state for local concerns (causes re-renders)
- ❌ Importing entire libraries (large bundles)

**Quick Reference**:

| Use Case | Pattern | Tool |
|----------|---------|------|
| Large bundle | Code splitting | `lazy()`, dynamic import |
| Slow queries | Configure staleTime | TanStack Query config |
| Expensive computation | Lazy initial state | `useState(() => ...)` |
| Flexible UI | Composition | Children props, slots |
| Heavy images | Lazy loading | `loading="lazy"` |
| Analyze bundle | Bundle analyzer | `rollup-plugin-visualizer` |

---

**Measurement Tools**:

```bash
# Bundle size
npm run build
ls -lh dist/assets/*.js

# Lighthouse (performance score)
npm run build
npm run preview
# Open Chrome DevTools → Lighthouse

# Bundle analyzer
npm install -D rollup-plugin-visualizer
npm run build
```

---

**Related Skills**:
- `frontend-patterns/04-tanstack-query.md` - Query optimization details
- `frontend-development.md` - Component patterns
- `frontend-patterns/01-troubleshooting.md` - Performance debugging
