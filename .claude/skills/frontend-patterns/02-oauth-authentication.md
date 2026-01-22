# OAuth Frontend Patterns

**Purpose**: Reusable OAuth 2.0 authentication patterns for React frontends

**When to use**: Implementing OAuth login flows, auth state management, callback handling in React apps

**Last Updated**: 2025-12-08

---

## Table of Contents

1. [User-Scoped vs Session-Scoped Auth](#user-scoped-vs-session-scoped-auth)
2. [OAuth Callback Handling](#oauth-callback-handling)
3. [Auth State Management](#auth-state-management)
4. [Error Handling](#error-handling)
5. [Auth Flow Mismatch Patterns](#auth-flow-mismatch-patterns)

---

## User-Scoped vs Session-Scoped Auth

### The Problem

**Backend**: Auth tokens stored per `session_id` (SESSION-scoped)
**Frontend**: User expects to stay logged in across sessions (USER-scoped)

**Impact**:
- Creating new session → Backend has no tokens for new `session_id` → 401 error
- Switching sessions → Same issue
- User forced to re-authenticate on every session change

---

### Solution: User-Scoped Auth in Frontend

**Store auth status at user level** (localStorage), not session level:

#### localStorage Utilities

**`src/utils/session.ts`**:
```typescript
// User-level authentication (not session-specific)
export function getAuthStatus(): boolean {
  try {
    const status = localStorage.getItem('app_auth_status');
    return status === 'authenticated';
  } catch {
    return false;
  }
}

export function setAuthStatus(authenticated: boolean): void {
  try {
    localStorage.setItem('app_auth_status', authenticated ? 'authenticated' : 'not_authenticated');
  } catch (e) {
    console.error('Failed to set auth status:', e);
  }
}

export function clearAuthStatus(): void {
  try {
    localStorage.removeItem('app_auth_status');
    localStorage.removeItem('app_user_id');
    localStorage.removeItem('app_user_name');
    localStorage.removeItem('app_user_email');
  } catch (e) {
    console.error('Failed to clear auth status:', e);
  }
}

// User metadata
export function getUserId(): string {
  return localStorage.getItem('app_user_id') || '';
}

export function setUserId(userId: string): void {
  localStorage.setItem('app_user_id', userId);
}

export function getUserName(): string {
  return localStorage.getItem('app_user_name') || '';
}

export function setUserName(userName: string): void {
  localStorage.setItem('app_user_name', userName);
}

export function getUserEmail(): string {
  return localStorage.getItem('app_user_email') || '';
}

export function setUserEmail(userEmail: string): void {
  localStorage.setItem('app_user_email', userEmail);
}
```

---

### Pattern: Initialize Auth from localStorage

```typescript
import { getAuthStatus, setAuthStatus, clearAuthStatus } from './utils/session';

function App() {
  // ✅ Initialize from localStorage (user-level auth)
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(getAuthStatus());
  const [isCheckingAuth, setIsCheckingAuth] = useState(true);

  useEffect(() => {
    // Check localStorage first (user-level)
    const storedAuthStatus = getAuthStatus();
    if (storedAuthStatus) {
      setIsAuthenticated(true);
      setIsCheckingAuth(false);
      return; // Early return - already authenticated
    }

    // If not authenticated in localStorage, check backend
    const sessionId = getSessionId();
    if (!sessionId) {
      setIsAuthenticated(false);
      setIsCheckingAuth(false);
      return;
    }

    // Timeout guard (5 seconds)
    const timeoutId = setTimeout(() => {
      setIsAuthenticated(false);
      setIsCheckingAuth(false);
    }, 5000);

    authApi.getAuthStatus(sessionId)
      .then((status) => {
        clearTimeout(timeoutId);
        setIsAuthenticated(status.authenticated);
        setAuthStatus(status.authenticated); // Store in localStorage
      })
      .catch(() => {
        clearTimeout(timeoutId);
        setIsAuthenticated(false);
      })
      .finally(() => setIsCheckingAuth(false));
  }, []); // ✅ Empty deps - only run on mount, NOT on session changes
}
```

**Key Points**:
- ✅ Check localStorage FIRST (fast, no network request)
- ✅ Early return if authenticated (skip backend check)
- ✅ Empty dependency array (`[]`) - run only on mount
- ✅ Store auth status in localStorage after backend check

---

### Pattern: Logout Clears User-Level Auth

```typescript
const handleLogout = async () => {
  try {
    await authApi.logout(sessionId);
    clearAuthStatus(); // ✅ Clear user-level auth + metadata
    setIsAuthenticated(false);
    navigate('/');
  } catch (error) {
    console.error('Logout failed:', error);
  }
};
```

---

## OAuth Callback Handling

### Pattern: URL Parameter Extraction

**OAuth providers redirect back** with user data in URL params:

**`/callback?user_id=123&user_name=John&user_email=john@example.com`**

```typescript
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { setUserId, setUserName, setUserEmail, setAuthStatus } from '../utils/session';

function CallbackPage() {
  const navigate = useNavigate();

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const userId = params.get('user_id');
    const userName = params.get('user_name');
    const userEmail = params.get('user_email');

    console.log('[OAuth Callback] Received');
    console.log('[OAuth Callback] User ID:', userId);
    console.log('[OAuth Callback] User Name:', userName);
    // Mask email for PII protection in logs
    console.log('[OAuth Callback] User Email:', userEmail ? `${userEmail.substring(0, 3)}***@${userEmail.split('@')[1]}` : 'none');

    if (userId && userName && userEmail) {
      // Store user metadata
      setUserId(userId);
      setUserName(userName);
      setUserEmail(userEmail);

      console.log('[OAuth Callback] User metadata stored');

      // Poll auth status (backend processes token exchange)
      pollAuthStatus(userId);
    } else {
      console.error('[OAuth Callback] Missing user metadata in URL params');
      alert('OAuth callback missing user information. Please try again.');
      navigate('/');
    }
  }, [navigate]);

  return (
    <div className="flex items-center justify-center h-screen">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
        <p className="mt-4 text-gray-600">Completing sign in...</p>
      </div>
    </div>
  );
}
```

---

### Pattern: Auth Status Polling

**After OAuth redirect**, backend needs time to process token exchange:

```typescript
function pollAuthStatus(userId: string) {
  let attempts = 0;
  const maxAttempts = 10;

  const intervalId = setInterval(async () => {
    attempts++;
    console.log(`[OAuth Callback] Polling auth status (attempt ${attempts}/${maxAttempts})`);

    try {
      const sessionId = getSessionId(); // Or create new session
      const status = await authApi.getAuthStatus(sessionId);

      if (status.authenticated) {
        console.log('[OAuth Callback] Authentication successful');
        clearInterval(intervalId);
        setAuthStatus(true); // Store user-level auth
        navigate('/');
      } else if (attempts >= maxAttempts) {
        console.error('[OAuth Callback] Auth check timed out');
        clearInterval(intervalId);
        alert('Authentication timed out. Please try again.');
        navigate('/');
      }
    } catch (error) {
      console.error('[OAuth Callback] Auth status check failed:', error);

      if (attempts >= maxAttempts) {
        clearInterval(intervalId);
        alert('Failed to verify authentication. Please try again.');
        navigate('/');
      }
    }
  }, 1000); // Poll every 1 second

  // Cleanup on unmount
  return () => clearInterval(intervalId);
}
```

**Key Points**:
- ✅ Poll every 1 second (reasonable interval)
- ✅ Max attempts (10 = 10 seconds total)
- ✅ Clear interval on success or timeout
- ✅ User-friendly error messages

---

### Pattern: Alternative - WebSocket for Auth Completion

**For real-time notification** instead of polling:

```typescript
useEffect(() => {
  const userId = params.get('user_id');

  if (userId) {
    const ws = new WebSocket(`wss://api.example.com/auth/ws?user_id=${userId}`);

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === 'auth_complete' && data.authenticated) {
        setAuthStatus(true);
        navigate('/');
        ws.close();
      }
    };

    ws.onerror = () => {
      alert('Real-time auth failed. Please refresh.');
    };

    return () => ws.close();
  }
}, [navigate]);
```

---

## Auth State Management

### Pattern: Auth Check with Timeout

**Prevent infinite loading** when backend is unreachable:

```typescript
useEffect(() => {
  // Early return if no session (show login immediately)
  const sessionId = getSessionId();
  if (!sessionId) {
    setIsAuthenticated(false);
    setIsCheckingAuth(false);
    return;
  }

  // 5-second timeout guard
  const timeoutId = setTimeout(() => {
    console.warn('Auth check timed out - showing login');
    setIsAuthenticated(false);
    setIsCheckingAuth(false);
  }, 5000);

  authApi.getAuthStatus(sessionId)
    .then((status) => {
      clearTimeout(timeoutId);
      setIsAuthenticated(status.authenticated);
    })
    .catch(() => {
      clearTimeout(timeoutId);
      setIsAuthenticated(false);
    })
    .finally(() => setIsCheckingAuth(false));
}, []);
```

---

### Pattern: Conditional Rendering

**Show different UI** based on auth state:

```typescript
if (isCheckingAuth) {
  return (
    <div className="flex items-center justify-center h-screen">
      <Spinner />
      <p className="ml-4">Checking authentication...</p>
    </div>
  );
}

if (!isAuthenticated) {
  return (
    <div className="flex items-center justify-center h-screen">
      <div className="text-center">
        <h1 className="text-2xl font-bold mb-4">Welcome</h1>
        <button onClick={handleLogin} className="btn-primary">
          Sign In with OAuth
        </button>
      </div>
    </div>
  );
}

return <MainApp />; // Authenticated UI
```

---

### Pattern: Protected Routes (React Router)

```typescript
import { Navigate } from 'react-router-dom';
import { getAuthStatus } from './utils/session';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = getAuthStatus();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}

// In routes:
<Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
<Route path="/login" element={<LoginPage />} />
<Route path="/callback" element={<CallbackPage />} />
```

---

## Error Handling

### Pattern: 401 Error Detection and Auth Clearing

**Detect auth failures** in API responses and clear auth status:

```typescript
const chatMutation = useMutation({
  mutationFn: sendMessage,

  onError: (error: any) => {
    console.error('[Chat Mutation] Error:', error);

    // Check if error is auth-related
    if (
      error?.response?.status === 401 ||
      error?.message?.includes('not authenticated') ||
      error?.message?.includes('unauthorized')
    ) {
      console.warn('[Chat Mutation] Auth error detected - clearing auth status');

      // Clear user-level auth
      clearAuthStatus();
      setIsAuthenticated(false);

      // User-friendly message
      alert('Your session has expired. Please sign in again.');
    } else {
      alert('Failed to send message. Please try again.');
    }
  }
});
```

**Key Points**:
- ✅ Check multiple error patterns (status code, message)
- ✅ Clear auth status on auth errors
- ✅ Show user-friendly message
- ✅ Don't auto-retry (could cause loop)

---

### Pattern: Axios Interceptor for Global Auth Error Handling

```typescript
import axios from 'axios';
import { clearAuthStatus } from './utils/session';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
});

// Response interceptor for global error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle 401 globally
    if (error.response?.status === 401) {
      console.warn('[API] 401 Unauthorized - clearing auth');
      clearAuthStatus();
      window.location.href = '/login'; // Redirect to login
    }

    return Promise.reject(error);
  }
);

export default api;
```

---

### Pattern: Retry with Auth Refresh

**For refresh token pattern**:

```typescript
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If 401 and haven't retried yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // Attempt token refresh
        const newToken = await refreshAccessToken();
        localStorage.setItem('access_token', newToken);

        // Retry original request with new token
        originalRequest.headers['Authorization'] = `Bearer ${newToken}`;
        return api(originalRequest);
      } catch (refreshError) {
        // Refresh failed - logout
        clearAuthStatus();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);
```

---

## Auth Flow Mismatch Patterns

### Problem: Frontend vs Backend Scoping Mismatch

**Scenario**:
- Frontend creates new sessions client-side (`session-${userId}-${timestamp}`)
- Backend stores tokens per `session_id`
- New session ID → No tokens → 401 error

---

### Solution 1: Immediate Error Handling (Quick Fix)

**Handle 401 errors** and prompt user to re-authenticate:

```typescript
const chatMutation = useMutation({
  mutationFn: sendMessage,

  onError: (error) => {
    if (error?.response?.status === 401) {
      clearAuthStatus();
      setIsAuthenticated(false);
      alert('Session not authenticated. Please sign in again.');
    }
  }
});
```

**Pro**: Quick fix, prevents app from breaking
**Con**: User must re-auth on every new session

---

### Solution 2: Backend Token Sharing (Permanent Fix)

**Backend changes** to store tokens by `user_id` instead of `session_id`:

**Backend (`oauth_service.py`)**:
```python
# Store tokens by user_id (not session_id)
def save_tokens(user_id: str, tokens: dict):
    # Store in database or cache by user_id
    token_cache[user_id] = tokens

def get_tokens(user_id: str) -> dict:
    return token_cache.get(user_id)

# Session creation endpoint
@app.post("/api/v1/sessions")
async def create_session(user_id: str):
    session_id = f"session-{user_id}-{int(time.time())}"

    # Copy user tokens to new session
    user_tokens = get_tokens(user_id)
    if user_tokens:
        session_tokens[session_id] = user_tokens

    return {"session_id": session_id}
```

**Frontend**: Call session creation endpoint before using new session

```typescript
const handleNewSession = async () => {
  const userId = getUserId();

  // Create session on backend (with token copy)
  const response = await api.post('/api/v1/sessions', { user_id: userId });
  const newSessionId = response.data.session_id;

  setCurrentSessionId(newSessionId);
};
```

---

### Solution 3: Session Creation with Token Propagation

**Frontend creates session**, backend propagates tokens:

```typescript
const createSessionWithAuth = async () => {
  const userId = getUserId();
  const currentSessionId = getSessionId();

  // Backend endpoint that creates new session and copies tokens
  const response = await api.post('/api/v1/sessions/create', {
    user_id: userId,
    source_session_id: currentSessionId // Copy tokens from this session
  });

  return response.data.session_id;
};
```

---

## Summary

**Key Patterns**:

1. **User-Scoped Auth**:
   - Store auth status in localStorage (user-level)
   - Check localStorage first (skip backend if authenticated)
   - Run auth check ONLY on mount (empty deps)

2. **OAuth Callback**:
   - Extract user data from URL params
   - Store user metadata (id, name, email)
   - Poll auth status or use WebSocket
   - Mask PII in logs

3. **Auth State**:
   - Timeout guards (5s) for auth checks
   - Conditional rendering based on auth state
   - Protected routes with Navigate redirect

4. **Error Handling**:
   - Detect 401 errors globally
   - Clear auth status on auth failures
   - Show user-friendly messages
   - Don't auto-retry auth errors

5. **Flow Mismatch**:
   - Quick fix: Handle 401, prompt re-auth
   - Permanent fix: Backend stores tokens by user_id
   - Alternative: Session creation endpoint with token propagation

**Common Mistakes**:

- ❌ Running auth check on every session change (use empty deps `[]`)
- ❌ No timeout guards (infinite loading)
- ❌ Auto-retrying 401 errors (causes loops)
- ❌ Not storing auth status (re-auth on page refresh)
- ❌ Not masking PII in logs (security risk)

**Quick Reference**:

| Use Case | Pattern |
|----------|---------|
| Initial auth check | localStorage first, then backend |
| OAuth callback | URL params + polling |
| 401 error | Clear auth, redirect to login |
| Session mismatch | Backend stores tokens by user_id |
| Protected routes | `<ProtectedRoute>` wrapper |

---

**Related Skills**:
- `frontend-patterns/01-troubleshooting.md` - CORS, network debugging
- `frontend-patterns/04-tanstack-query.md` - Query error handling
- `frontend-patterns/03-react-performance.md` - State optimization
