# Frontend Troubleshooting Patterns

**Purpose**: Reusable debugging patterns for React/Vite frontend applications

**When to use**: Debugging frontend connectivity issues, CORS errors, loading states, environment setup

**Last Updated**: 2025-12-08

---

## Table of Contents

1. [CORS Debugging](#cors-debugging)
2. [Loading State Issues](#loading-state-issues)
3. [Environment Setup Verification](#environment-setup-verification)
4. [Network Debugging](#network-debugging)
5. [Backend Connectivity](#backend-connectivity)

---

## CORS Debugging

### Pattern: Vite Proxy for Local Development

**Problem**: "Failed to fetch" errors when calling backend API from frontend

**Root Cause**: Absolute URLs bypass Vite proxy → direct cross-origin request → CORS error

**Solution**: Always use relative URLs in development

#### Configuration

**`vite.config.ts`**:
```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/auth': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
});
```

**`src/lib/config.ts`**:
```typescript
// ✅ CORRECT: Empty string for development (uses relative URLs)
export const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || '';

// Development: '' → relative URLs → proxy to backend
// Production: 'https://api.example.com' → absolute URLs → CORS headers
```

**`.env`** (for development):
```bash
# ❌ DO NOT SET in development (bypasses proxy)
# VITE_API_BASE_URL=http://localhost:8000

# ✅ Leave commented for dev, set for production build
# VITE_API_BASE_URL=https://api.your-domain.com
```

#### Testing

```bash
# Test that API calls use relative URLs
curl http://localhost:5173/api/v1/auth/status?session_id=test

# Should proxy to backend:
# → http://localhost:8000/api/v1/auth/status?session_id=test
```

**Anti-Pattern**:
```typescript
// ❌ WRONG: Absolute URL bypasses proxy
const apiBaseUrl = 'http://localhost:8000';
fetch(`${apiBaseUrl}/api/v1/endpoint`); // CORS error!

// ✅ CORRECT: Relative URL uses proxy
const apiBaseUrl = '';
fetch(`${apiBaseUrl}/api/v1/endpoint`); // → Proxied to backend
```

---

### Pattern: Vanilla JS Frontend (No Bundler)

**Same CORS fix applies to vanilla JavaScript projects**:

**`js/config.js`**:
```javascript
// ❌ WRONG: Absolute URL
const API_BASE = 'http://localhost:8000/api/v1';

// ✅ CORRECT: Relative URL
const API_BASE = '/api/v1';
```

**Key Insight**: Relative URLs (`/api/v1/...`) are same-origin → no CORS issues

---

### Pattern: CORS Verification (Backend)

**Check if backend CORS is configured correctly**:

```bash
# Test preflight request
curl -H "Origin: http://localhost:5173" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS \
     http://localhost:8000/api/v1/auth/login \
     -v 2>&1 | grep -i access-control

# Expected headers:
# access-control-allow-origin: http://localhost:5173
# access-control-allow-credentials: true
# access-control-allow-methods: GET, POST, PUT, DELETE, OPTIONS
# access-control-allow-headers: Content-Type, Authorization
```

**Common Issue**: Backend running with stale config

```bash
# Kill all backend processes
ps aux | grep uvicorn | grep -v grep
kill <PID1> <PID2>

# Restart backend (loads latest .env)
cd backend
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Pattern**: Backend config changes (`.env`, CORS origins) require process restart

---

## Loading State Issues

### Pattern: Timeout Guards for Initial Auth Checks

**Problem**: Infinite loading animation when backend is unreachable

**Solution**: Always add timeout guards to prevent hanging

#### Implementation

```typescript
// ✅ Auth check with timeout guard
useEffect(() => {
  // Early return if no session (show login immediately)
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
}, [sessionId]);
```

**Key Points**:
- ✅ Early return if no data needed (prevent unnecessary requests)
- ✅ Timeout after 5-10 seconds
- ✅ Always clear timeout in success/error handlers
- ✅ Gracefully degrade to showing login page

---

### Pattern: AbortController for Fetch Timeouts

**Problem**: Fetch requests hang indefinitely when backend is down

**Solution**: Use `AbortController` with timeout

#### Implementation

```typescript
async function fetchAPI(url: string, options?: RequestInit) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 10000); // 10s timeout

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: 'Unknown error' }));
      throw error;
    }

    return await response.json();
  } catch (error) {
    clearTimeout(timeoutId);

    if (error.name === 'AbortError') {
      throw new Error('Request timed out. Backend may be unreachable.');
    }

    throw error;
  }
}
```

**Anti-Pattern**:
```typescript
// ❌ WRONG: No timeout (hangs forever)
const response = await fetch(url);

// ✅ CORRECT: Timeout with AbortController
const controller = new AbortController();
setTimeout(() => controller.abort(), 10000);
const response = await fetch(url, { signal: controller.signal });
```

---

### Pattern: Comprehensive Error Logging

**Problem**: Silent failures hide root causes

**Solution**: Add logging at every layer

```typescript
// API Layer
async function fetchAPI(url: string, options?: RequestInit) {
  console.log(`[API] ${options?.method || 'GET'} ${url}`);

  try {
    const response = await fetch(url, options);
    console.log(`[API] Response status: ${response.status}`);

    const data = await response.json();
    console.log(`[API] Response data:`, data);

    return data;
  } catch (error) {
    console.error(`[API Error] ${url}:`, error);
    throw error;
  }
}

// Component Layer
const handleLogin = async () => {
  console.log('[Auth] Login button clicked');

  try {
    const response = await authApi.getLoginUrl(sessionId);
    console.log('[Auth] Login URL response:', response);

    if (response.auth_url) {
      console.log('[Auth] Redirecting to:', response.auth_url);
      window.location.href = response.auth_url;
    }
  } catch (error) {
    console.error('[Auth Error] Login failed:', error);
    alert('Failed to start login. Please try again.');
  }
};
```

**Pattern**: Prefix logs with component/layer name for easy filtering

---

## Environment Setup Verification

### Checklist: Frontend + Backend Startup

**When debugging "app not loading" issues, verify both layers**:

#### Backend Verification

```bash
# 1. Check if .env file exists
ls -la .env
# If missing, create from example:
cp .env.example .env

# 2. Verify required environment variables
cat .env | grep -E "OAUTH_CLIENT_ID|OAUTH_CLIENT_SECRET|GCS_BUCKET_NAME"

# 3. Check if backend is running
ps aux | grep uvicorn | grep -v grep

# 4. Check backend port
lsof -i :8000
# Or: netstat -an | grep 8000

# 5. Test backend API
curl http://localhost:8000/api/v1/auth/status?session_id=test

# 6. Start backend if not running
cd backend
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Verification

```bash
# 1. Check if dev server is running
ps aux | grep vite | grep -v grep

# 2. Check frontend port
lsof -i :5173
# Vite auto-increments if 5173 is occupied

# 3. Test frontend
curl http://localhost:5173/

# 4. Start frontend if not running
cd frontend-v2
npm run dev
```

#### Common Issues

**Issue**: Backend crashes at startup with Pydantic validation error

**Cause**: Missing required environment variables in `.env`

**Fix**: Create `.env` file with all required vars

---

**Issue**: Frontend shows "Failed to fetch" despite backend running

**Cause**: Absolute URLs in config bypassing Vite proxy

**Fix**: Use relative URLs (empty string for `apiBaseUrl`)

---

**Issue**: Changes to `.env` not taking effect

**Cause**: Backend process running with stale config (Pydantic loads at import time)

**Fix**: Kill ALL backend processes and restart

```bash
pkill -f uvicorn
cd backend && python3 -m uvicorn app.main:app --reload
```

---

## Network Debugging

### Browser DevTools

**Open Network Tab** (Chrome DevTools → Network):

1. **Check request URL**:
   - ✅ Should be relative: `/api/v1/auth/status`
   - ❌ NOT absolute: `http://localhost:8000/api/v1/auth/status`

2. **Check request headers**:
   - Origin: `http://localhost:5173`
   - Content-Type: `application/json`

3. **Check response headers**:
   - `access-control-allow-origin`: `http://localhost:5173`
   - `access-control-allow-credentials`: `true`

4. **Check response status**:
   - 200 OK → Success
   - 401 Unauthorized → Auth issue
   - 404 Not Found → Wrong endpoint
   - 500 Internal Server Error → Backend crash
   - (failed) → CORS or network issue

5. **Check response body**:
   - JSON data returned
   - Error messages
   - Stack traces (if backend in debug mode)

---

### curl Debugging

**Test backend directly** (bypassing frontend):

```bash
# Test GET request
curl http://localhost:8000/api/v1/auth/status?session_id=test

# Test POST request
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "session_id": "test"}'

# Test CORS preflight
curl -H "Origin: http://localhost:5173" \
     -H "Access-Control-Request-Method: POST" \
     -X OPTIONS \
     http://localhost:8000/api/v1/chat \
     -v

# Test with verbose output
curl -v http://localhost:8000/api/v1/auth/status?session_id=test
```

**Expected Output**:
```
< HTTP/1.1 200 OK
< content-type: application/json
< access-control-allow-origin: http://localhost:5173
< access-control-allow-credentials: true

{"authenticated": false, "session_id": "test"}
```

---

## Backend Connectivity

### Pattern: Health Check Endpoint

**Add a health check endpoint** for quick verification:

**Backend (`main.py`)**:
```python
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}
```

**Frontend (startup script)**:
```typescript
async function checkBackendHealth() {
  try {
    const response = await fetch('/health');
    const data = await response.json();
    console.log('[Health Check] Backend is healthy:', data);
    return true;
  } catch (error) {
    console.error('[Health Check] Backend unreachable:', error);
    return false;
  }
}

// Call on app startup
checkBackendHealth();
```

---

### Pattern: Graceful Degradation

**Show user-friendly errors** when backend is down:

```typescript
const [backendAvailable, setBackendAvailable] = useState(true);

useEffect(() => {
  const checkBackend = async () => {
    try {
      await fetch('/health');
      setBackendAvailable(true);
    } catch {
      setBackendAvailable(false);
    }
  };

  checkBackend();
  const interval = setInterval(checkBackend, 30000); // Check every 30s
  return () => clearInterval(interval);
}, []);

// In render:
{!backendAvailable && (
  <div className="bg-yellow-100 border-l-4 border-yellow-500 p-4">
    <p className="text-yellow-700">
      ⚠️ Backend is currently unavailable. Please check if the server is running.
    </p>
  </div>
)}
```

---

## Summary

**Key Patterns**:

1. **CORS**: Always use relative URLs in development (Vite proxy)
2. **Timeouts**: Add timeout guards to all initial loading checks (5-10s)
3. **AbortController**: Use for fetch requests (10s timeout)
4. **Logging**: Add comprehensive logging at every layer
5. **Environment**: Verify `.env` exists and backend restarts on changes
6. **Network**: Use Browser DevTools and curl for debugging
7. **Health Checks**: Add health endpoint for quick backend verification
8. **Graceful Degradation**: Show user-friendly errors when backend is down

**Common Mistakes**:

- ❌ Using absolute URLs in development (bypasses proxy)
- ❌ No timeout guards (infinite loading)
- ❌ Silent error handling (swallowing errors)
- ❌ Missing `.env` file (backend crashes)
- ❌ Not restarting backend after config changes

**Quick Diagnosis**:

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| "Failed to fetch" | CORS / Proxy | Use relative URLs |
| Infinite loading | Backend down / No timeout | Add timeout guards |
| Auth not working | Missing .env / Stale config | Restart backend |
| Changes not taking effect | Backend not restarted | Kill processes, restart |
| 404 errors | Wrong endpoint URL | Check API route |

---

**Related Skills**:
- `frontend-patterns/04-tanstack-query.md` - Query error handling
- `frontend-patterns/02-oauth-authentication.md` - Auth-specific debugging
- `frontend-development.md` - General React patterns
