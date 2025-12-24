# TanStack Query Patterns

**Purpose**: Best practices for TanStack Query (React Query) in React applications

**When to use**: Implementing data fetching, caching, mutations, and optimistic updates with TanStack Query

**Last Updated**: 2025-12-08

**Version**: TanStack Query v5

---

## Table of Contents

1. [Cache Invalidation vs Refetch](#cache-invalidation-vs-refetch)
2. [Mutation Lifecycle](#mutation-lifecycle)
3. [Optimistic Updates](#optimistic-updates)
4. [Query Configuration](#query-configuration)
5. [Session-Specific State](#session-specific-state)
6. [useEffect Dependencies](#useeffect-dependencies)
7. [Common Patterns](#common-patterns)

---

## Cache Invalidation vs Refetch

### invalidateQueries (Async, Lazy)

**Use when**: You want to mark queries as stale and refetch **when next observed**

```typescript
// Marks queries as stale, refetches when component renders
queryClient.invalidateQueries({ queryKey: ['sessions', userId] });
```

**Behavior**:
- Marks matching queries as stale
- Refetch happens when query is next observed (component renders)
- Non-blocking (doesn't wait for refetch)
- Can cause race conditions if timing matters

---

### refetchQueries (Sync with await)

**Use when**: You need **immediate, synchronous refetch** (timing matters)

```typescript
// Forces immediate refetch, waits for completion
await queryClient.refetchQueries({
  queryKey: ['sessions', userId],
  type: 'active' // Only refetch active (mounted) queries
});
```

**Behavior**:
- Forces immediate refetch of matching queries
- Returns promise you can `await`
- Prevents race conditions
- Use when subsequent code depends on fresh data

---

### Pattern: Session Switch with Race Condition Fix

**Problem**: Sessions list not updating immediately on switch (messages query refetched before sessions query)

**Solution**: Use `await refetchQueries` to ensure synchronous update

```typescript
const handleSessionClick = async (sessionId: string) => {
  console.log('[Session] Switching to:', sessionId);
  setCurrentSessionId(sessionId);

  // ✅ CORRECT: Force immediate refetch with await
  await queryClient.refetchQueries({
    queryKey: ['sessions', getUserId()],
    type: 'active'
  });

  console.log('[Session] Sessions query refetched');
};
```

**Anti-Pattern**:
```typescript
// ❌ WRONG: Race condition (may refetch after messages query)
const handleSessionClick = (sessionId: string) => {
  setCurrentSessionId(sessionId);
  queryClient.invalidateQueries({ queryKey: ['sessions', userId] }); // No await
};
```

---

### Pattern: Multiple Related Queries

**Invalidate multiple related queries** after a mutation:

```typescript
const chatMutation = useMutation({
  mutationFn: sendMessage,
  onSuccess: async (data) => {
    // Invalidate multiple queries
    await Promise.all([
      queryClient.refetchQueries({ queryKey: ['messages', sessionId] }),
      queryClient.refetchQueries({ queryKey: ['sessions', userId] }),
      queryClient.invalidateQueries({ queryKey: ['stats'] }) // Less critical
    ]);
  }
});
```

---

## Mutation Lifecycle

### Complete Lifecycle Hooks

```typescript
const mutation = useMutation({
  mutationFn: async (variables) => {
    return await api.sendMessage(variables);
  },

  // 1. Called BEFORE mutation function
  onMutate: async (variables) => {
    console.log('[Mutation] Starting with:', variables);

    // Cancel outgoing queries (avoid overwriting optimistic update)
    await queryClient.cancelQueries({ queryKey: ['messages'] });

    // Snapshot current data (for rollback)
    const previousMessages = queryClient.getQueryData(['messages', sessionId]);

    // Optimistic update
    queryClient.setQueryData(['messages', sessionId], (old) => [
      ...old,
      { role: 'user', content: variables.message }
    ]);

    // Return context for rollback
    return { previousMessages };
  },

  // 2. Called on SUCCESS
  onSuccess: (data, variables, context) => {
    console.log('[Mutation] Success:', data);

    // Update with real server response
    queryClient.setQueryData(['messages', sessionId], (old) => [
      ...old,
      { role: 'assistant', content: data.response }
    ]);

    // Refetch related queries
    await queryClient.refetchQueries({ queryKey: ['sessions', userId] });
  },

  // 3. Called on ERROR
  onError: (error, variables, context) => {
    console.error('[Mutation] Error:', error);

    // Rollback optimistic update
    if (context?.previousMessages) {
      queryClient.setQueryData(['messages', sessionId], context.previousMessages);
    }

    // Show user-friendly error
    alert('Failed to send message. Please try again.');
  },

  // 4. Called ALWAYS (success or error)
  onSettled: (data, error, variables, context) => {
    console.log('[Mutation] Settled');

    // Cleanup, logging, analytics, etc.
  }
});
```

**Execution Order**:
1. `onMutate` → Before request
2. `mutationFn` → Actual request
3. `onSuccess` OR `onError` → After request
4. `onSettled` → Always runs

---

### Pattern: Optimistic Updates with Rollback

**Use optimistic updates** for instant UI feedback:

```typescript
const sendMessageMutation = useMutation({
  mutationFn: chatApi.sendMessage,

  onMutate: async (variables) => {
    // Cancel queries to avoid race
    await queryClient.cancelQueries({ queryKey: ['messages', sessionId] });

    // Snapshot for rollback
    const previous = queryClient.getQueryData(['messages', sessionId]);

    // Optimistic update (show user message immediately)
    queryClient.setQueryData(['messages', sessionId], (old) => [
      ...old,
      { role: 'user', content: variables.message, timestamp: new Date().toISOString() }
    ]);

    return { previous };
  },

  onError: (err, variables, context) => {
    // Rollback on error
    queryClient.setQueryData(['messages', sessionId], context.previous);
  },

  onSuccess: (data) => {
    // Replace optimistic update with server response
    queryClient.setQueryData(['messages', sessionId], (old) => {
      const withoutOptimistic = old.slice(0, -1); // Remove optimistic user message
      return [
        ...withoutOptimistic,
        { role: 'user', content: data.user_message },
        { role: 'assistant', content: data.response }
      ];
    });
  }
});
```

---

## Optimistic Updates

### State Accumulation Pattern

**Problem**: Tool calls disappearing on mutation

**Cause**: Replacing state instead of accumulating

**Solution**: Use spread operator to accumulate

```typescript
// ❌ WRONG: Replaces all tool calls with latest
setAllToolCalls(data.tool_calls);

// ✅ CORRECT: Accumulates tool calls across all messages
setAllToolCalls((prev) => [...prev, ...(data.tool_calls || [])]);
```

**TypeScript Safety**:
```typescript
// Always provide fallback for optional arrays
...(data.tool_calls || []) // Prevents "Type must have [Symbol.iterator]" error
```

---

### Pattern: Clear State on New Message

**Correct pattern**: Clear optimistic state when starting new mutation

```typescript
const chatMutation = useMutation({
  mutationFn: sendMessage,

  onMutate: async (variables) => {
    // ✅ Clear tool calls for NEW message (not accumulated from previous)
    setAllToolCalls([]);

    // Optimistic update for user message
    setMessages((prev) => [
      ...prev,
      { role: 'user', content: variables.message }
    ]);
  },

  onSuccess: (data) => {
    // ✅ ACCUMULATE tool calls for THIS message
    setAllToolCalls((prev) => [...prev, ...(data.tool_calls || [])]);

    // Add assistant response
    setMessages((prev) => [
      ...prev,
      { role: 'assistant', content: data.response }
    ]);
  }
});
```

**Key Insight**: Clear on `onMutate`, accumulate on `onSuccess`

---

## Query Configuration

### Default Configuration

**Configure QueryClient** for optimal behavior:

```typescript
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes (reasonable for chat apps)
      retry: 1, // Only retry once (don't hammer backend)
      refetchOnWindowFocus: false, // Chat messages don't change on tab switch
      refetchOnMount: true, // Refresh on component mount
      refetchOnReconnect: true, // Refresh on network reconnect
    },
    mutations: {
      retry: 0, // Don't retry mutations (could duplicate actions)
    }
  }
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      {/* Your app */}
    </QueryClientProvider>
  );
}
```

---

### Per-Query Configuration

**Override defaults** for specific queries:

```typescript
// Frequently-changing data → shorter staleTime
const { data: stats } = useQuery({
  queryKey: ['stats'],
  queryFn: fetchStats,
  staleTime: 30 * 1000, // 30 seconds
  refetchInterval: 30 * 1000, // Poll every 30s
});

// Rarely-changing data → longer staleTime
const { data: config } = useQuery({
  queryKey: ['config'],
  queryFn: fetchConfig,
  staleTime: 60 * 60 * 1000, // 1 hour
  refetchOnMount: false,
});

// Conditional fetching
const { data: messages } = useQuery({
  queryKey: ['messages', sessionId],
  queryFn: () => fetchMessages(sessionId),
  enabled: !!sessionId && isAuthenticated, // Only fetch when ready
});
```

---

## Session-Specific State

### Pattern: Track Active Mutation by Session/Context

**Problem**: Loading state shows in ALL sessions when one session has active mutation

**Solution**: Track which session has the active mutation

```typescript
const [activeSessionId, setActiveSessionId] = useState<string | null>(null);

const chatMutation = useMutation({
  mutationFn: sendMessage,

  onMutate: async (variables) => {
    // Track which session has active mutation
    setActiveSessionId(currentSessionId);
  },

  onSuccess: () => {
    // Clear active session
    setActiveSessionId(null);
  },

  onError: () => {
    // Clear active session
    setActiveSessionId(null);
  }
});

// In component:
<PipelinePane
  toolCalls={allToolCalls}
  isLoading={chatMutation.isPending && activeSessionId === currentSessionId}
/>
```

**Key Insight**: Only show loading when `currentId === activeId`

---

### Pattern: Session-Specific Query Data with Map

**Use Map** to store query data per session:

```typescript
const [messagesMap, setMessagesMap] = useState<Map<string, Message[]>>(new Map());

// Query for current session
const { data: messagesData } = useQuery({
  queryKey: ['messages', currentSessionId],
  queryFn: () => fetchMessages(currentSessionId),
  enabled: !!currentSessionId
});

// Update Map when query data changes
useEffect(() => {
  // Capture sessionId in closure (important!)
  const sessionIdForThisData = currentSessionId;

  if (messagesData?.messages) {
    setMessagesMap((prevMap) => {
      const newMap = new Map(prevMap);
      newMap.set(sessionIdForThisData, messagesData.messages);
      return newMap;
    });
  }
}, [messagesData]); // ✅ Only depend on messagesData, NOT currentSessionId

// Display messages for current session
const currentMessages = messagesMap.get(currentSessionId) || [];
```

**Critical**: Use closure pattern to avoid stale session ID

---

### Common Mistake: Over-Clearing State

**Problem**: Clearing `activeSessionId` on session switch breaks loading state

```typescript
// ❌ WRONG: Breaks loading when switching back to active session
const handleSessionClick = (sessionId: string) => {
  setCurrentSessionId(sessionId);
  setActiveSessionId(null); // DON'T DO THIS
};
```

**Solution**: Let mutation lifecycle manage state

```typescript
// ✅ CORRECT: Only mutation clears activeSessionId
const handleSessionClick = (sessionId: string) => {
  setCurrentSessionId(sessionId);
  // activeSessionId managed by onMutate/onSuccess/onError
};

// Conditional check handles show/hide automatically
{chatMutation.isPending && activeSessionId === currentSessionId && <Spinner />}
```

---

## useEffect Dependencies

### Pattern: Avoid Duplicating Query Reactivity

**Problem**: TanStack Query already refetches when `queryKey` changes, adding that value to `useEffect` deps causes double-processing

```typescript
// ❌ WRONG: Double reactivity (query refetches + useEffect runs)
useEffect(() => {
  if (messagesData?.messages) {
    setMessagesMap((prevMap) => {
      const newMap = new Map(prevMap);
      newMap.set(currentSessionId, messagesData.messages); // Stale sessionId!
      return newMap;
    });
  }
}, [messagesData, currentSessionId]); // ← currentSessionId causes double processing
```

**Solution**: Use closure pattern, remove state from deps if query tracks it

```typescript
// ✅ CORRECT: Single reactivity source
useEffect(() => {
  // Capture currentSessionId in closure
  const sessionIdForThisData = currentSessionId;

  if (messagesData?.messages) {
    setMessagesMap((prevMap) => {
      const newMap = new Map(prevMap);
      newMap.set(sessionIdForThisData, messagesData.messages);
      return newMap;
    });
  }
}, [messagesData]); // ✅ Only depend on messagesData
```

**Why this works**:
- Query refetches when `currentSessionId` changes (it's in `queryKey`)
- This triggers `useEffect` via `messagesData` change
- Closure captures correct `sessionId` for each effect run
- No double-processing, no stale closures

---

### Pattern: Closure Capture for Async Operations

**Capture values in closure** for async operations:

```typescript
useEffect(() => {
  // Capture values that may change during async operation
  const sessionIdForThisRequest = currentSessionId;
  const userIdForThisRequest = userId;

  async function loadData() {
    const data = await fetchData(sessionIdForThisRequest, userIdForThisRequest);

    // Use captured values, not current state
    setDataMap((prev) => {
      const newMap = new Map(prev);
      newMap.set(sessionIdForThisRequest, data);
      return newMap;
    });
  }

  loadData();
}, [/* dependencies */]);
```

---

## Common Patterns

### Pattern: Polling with refetchInterval

```typescript
const { data } = useQuery({
  queryKey: ['status'],
  queryFn: fetchStatus,
  refetchInterval: 5000, // Poll every 5 seconds
  refetchIntervalInBackground: false, // Stop polling when tab hidden
});
```

---

### Pattern: Dependent Queries

```typescript
// Only fetch messages after user is authenticated
const { data: user } = useQuery({
  queryKey: ['user'],
  queryFn: fetchUser
});

const { data: messages } = useQuery({
  queryKey: ['messages'],
  queryFn: fetchMessages,
  enabled: !!user?.id, // Only run when user exists
});
```

---

### Pattern: Parallel Queries

```typescript
// Fetch multiple queries in parallel
function Dashboard() {
  const { data: sessions } = useQuery({ queryKey: ['sessions'], queryFn: fetchSessions });
  const { data: stats } = useQuery({ queryKey: ['stats'], queryFn: fetchStats });
  const { data: config } = useQuery({ queryKey: ['config'], queryFn: fetchConfig });

  // All queries run in parallel automatically
}
```

---

### Pattern: Query Cancellation

```typescript
const { data, refetch, cancel } = useQuery({
  queryKey: ['search', searchTerm],
  queryFn: ({ signal }) => fetchSearch(searchTerm, { signal }), // Pass AbortSignal
  enabled: searchTerm.length >= 3
});

// Cancel on unmount or new search
useEffect(() => {
  return () => cancel(); // Cleanup
}, [cancel]);
```

---

## Summary

**Key Patterns**:

1. **Cache Management**:
   - Use `invalidateQueries` for lazy refetch
   - Use `await refetchQueries` when timing matters

2. **Mutations**:
   - Use all lifecycle hooks (`onMutate`, `onSuccess`, `onError`, `onSettled`)
   - Implement optimistic updates with rollback
   - Clear state on `onMutate`, accumulate on `onSuccess`

3. **State Management**:
   - Use Map for session-specific data
   - Track active context (session, tab) for loading states
   - Don't over-clear state (let mutation lifecycle manage it)

4. **useEffect**:
   - Don't duplicate query reactivity in deps
   - Use closure pattern to capture values
   - Only depend on query data, not state in `queryKey`

5. **Configuration**:
   - Set reasonable `staleTime` (5 minutes for chat apps)
   - Disable `refetchOnWindowFocus` for chat/static data
   - Retry once for queries, zero for mutations

**Common Mistakes**:

- ❌ Using `invalidateQueries` when timing matters (use `refetchQueries`)
- ❌ Replacing state instead of accumulating (`setState(new)` vs `setState(prev => [...prev, new])`)
- ❌ Including `queryKey` values in `useEffect` deps (double reactivity)
- ❌ Over-clearing state (e.g., clearing `activeSessionId` on session switch)
- ❌ Not using TypeScript fallbacks (`...(data || [])` prevents errors)

**Quick Reference**:

| Use Case | Pattern |
|----------|---------|
| Immediate update needed | `await refetchQueries()` |
| Lazy update OK | `invalidateQueries()` |
| Optimistic UI | `onMutate` + `onError` rollback |
| Session-specific loading | Track `activeSessionId` |
| Accumulate data | `setState(prev => [...prev, ...new])` |
| Query depends on state | Use `enabled` prop |

---

**Related Skills**:
- `frontend-patterns/01-troubleshooting.md` - Network debugging
- `frontend-patterns/02-oauth-authentication.md` - Auth-specific query patterns
- `frontend-patterns/03-react-performance.md` - Query optimization
