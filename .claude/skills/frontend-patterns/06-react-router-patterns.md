# React Router v6+ Routing Patterns

## Purpose

This skill provides comprehensive patterns for building robust, accessible, and performant routing in React + TypeScript applications using React Router v6+.

**Use this skill when:**
- Setting up routing with React Router v6+ (createBrowserRouter, RouterProvider)
- Implementing protected routes, authentication guards, and role-based access
- Building nested routes, shared layouts, and breadcrumb navigation
- Managing route parameters, search params, and URL state
- Implementing lazy loading, error boundaries, and 404 pages
- Handling navigation guards (unsaved changes warnings)
- Building accessible route transitions and focus management

**Last Updated:** 2025-12-09

---

## Table of Contents

1. [React Router v6 Setup](#1-react-router-v6-setup)
2. [Route Guards & Protection](#2-route-guards--protection)
3. [Nested Routes & Layouts](#3-nested-routes--layouts)
4. [Navigation Patterns](#4-navigation-patterns)
5. [Route Parameters & Search Params](#5-route-parameters--search-params)
6. [Lazy Loading Routes](#6-lazy-loading-routes)
7. [Error Boundaries](#7-error-boundaries)
8. [Navigation Guards](#8-navigation-guards)
9. [Route Transitions](#9-route-transitions)
10. [URL State Management](#10-url-state-management)
11. [Modal Routes](#11-modal-routes)
12. [Accessibility](#12-accessibility)
13. [Common Anti-Patterns](#13-common-anti-patterns)
14. [Summary](#summary)

---

## 1. React Router v6 Setup

### Problem
Need modern, type-safe routing setup with data APIs (loaders, actions) and optimal performance.

### Solution
Use **createBrowserRouter** with **RouterProvider** for React Router v6.4+ data APIs.

### Implementation

**Step 1: Install Dependencies**
```bash
npm install react-router-dom
# TypeScript types are included by default
```

**Step 2: Basic Setup with createBrowserRouter**
```tsx
// src/main.tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import Root from './routes/Root';
import Home from './routes/Home';
import About from './routes/About';
import ErrorPage from './routes/ErrorPage';

const router = createBrowserRouter([
  {
    path: '/',
    element: <Root />,
    errorElement: <ErrorPage />,
    children: [
      {
        index: true, // Default child route
        element: <Home />,
      },
      {
        path: 'about',
        element: <About />,
      },
    ],
  },
]);

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
);
```

**Step 3: Root Layout Component**
```tsx
// src/routes/Root.tsx
import { Outlet, Link } from 'react-router-dom';

export default function Root() {
  return (
    <div className="app">
      <nav>
        <Link to="/">Home</Link>
        <Link to="/about">About</Link>
      </nav>

      <main>
        {/* Child routes render here */}
        <Outlet />
      </main>
    </div>
  );
}
```

**Alternative: Using createRoutesFromElements (JSX Syntax)**
```tsx
import { createBrowserRouter, createRoutesFromElements, Route } from 'react-router-dom';

const router = createBrowserRouter(
  createRoutesFromElements(
    <Route path="/" element={<Root />} errorElement={<ErrorPage />}>
      <Route index element={<Home />} />
      <Route path="about" element={<About />} />
      <Route path="users/:id" element={<User />} />
    </Route>
  )
);
```

**TypeScript-First Route Configuration**
```tsx
// src/router/routes.ts
import { RouteObject } from 'react-router-dom';
import Root from '../routes/Root';
import Home from '../routes/Home';

export const routes: RouteObject[] = [
  {
    path: '/',
    element: <Root />,
    errorElement: <ErrorPage />,
    children: [
      {
        index: true,
        element: <Home />,
      },
      {
        path: 'users',
        children: [
          {
            index: true,
            element: <UserList />,
          },
          {
            path: ':id',
            element: <UserDetail />,
            loader: userLoader, // Data loading API
          },
        ],
      },
    ],
  },
];

// src/main.tsx
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import { routes } from './router/routes';

const router = createBrowserRouter(routes);
```

### Anti-Pattern

❌ **WRONG: Using BrowserRouter (legacy approach)**
```tsx
// Missing v6.4+ data APIs (loaders, actions, etc.)
<BrowserRouter>
  <Routes>
    <Route path="/" element={<Home />} />
  </Routes>
</BrowserRouter>
```

✅ **CORRECT: Using createBrowserRouter**
```tsx
const router = createBrowserRouter([
  { path: '/', element: <Home /> },
]);
<RouterProvider router={router} />
// Unlocks loaders, actions, deferred data, etc.
```

---

## 2. Route Guards & Protection

### Problem
Restrict routes based on authentication status or user roles.

### Solution
Create protected route wrappers using **Outlet** pattern or component wrappers.

### Implementation

**Pattern 1: Protected Outlet (Recommended for Multiple Routes)**
```tsx
// src/components/ProtectedRoute.tsx
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

export function ProtectedRoute() {
  const { isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
      </div>
    );
  }

  if (!isAuthenticated) {
    // Redirect to login, save attempted location
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <Outlet />;
}
```

**Usage in Router Configuration**
```tsx
const router = createBrowserRouter([
  {
    path: '/',
    element: <Root />,
    children: [
      {
        path: 'login',
        element: <Login />,
      },
      {
        // Protected routes wrapped under single outlet
        element: <ProtectedRoute />,
        children: [
          {
            path: 'dashboard',
            element: <Dashboard />,
          },
          {
            path: 'profile',
            element: <Profile />,
          },
          {
            path: 'settings',
            element: <Settings />,
          },
        ],
      },
    ],
  },
]);
```

**Pattern 2: Role-Based Access Control**
```tsx
// src/components/RoleGuard.tsx
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

interface RoleGuardProps {
  allowedRoles: string[];
}

export function RoleGuard({ allowedRoles }: RoleGuardProps) {
  const { user, isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  const hasRequiredRole = user?.roles?.some((role) =>
    allowedRoles.includes(role)
  );

  if (!hasRequiredRole) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-red-600 mb-2">Access Denied</h1>
          <p className="text-gray-600">You don't have permission to view this page.</p>
        </div>
      </div>
    );
  }

  return <Outlet />;
}
```

**Usage with Roles**
```tsx
const router = createBrowserRouter([
  {
    path: '/',
    element: <Root />,
    children: [
      {
        element: <ProtectedRoute />,
        children: [
          {
            path: 'dashboard',
            element: <Dashboard />, // All authenticated users
          },
          {
            // Admin-only routes
            element: <RoleGuard allowedRoles={['admin']} />,
            children: [
              {
                path: 'admin',
                element: <AdminPanel />,
              },
              {
                path: 'users',
                element: <UserManagement />,
              },
            ],
          },
        ],
      },
    ],
  },
]);
```

**Pattern 3: Redirect After Login**
```tsx
// src/routes/Login.tsx
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

export default function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();

  // Get the page user tried to access
  const from = location.state?.from?.pathname || '/dashboard';

  const handleLogin = async (credentials: Credentials) => {
    try {
      await login(credentials);
      // Redirect back to attempted page
      navigate(from, { replace: true });
    } catch (error) {
      toast.error('Login failed');
    }
  };

  return (
    <form onSubmit={handleSubmit(handleLogin)}>
      {/* Login form fields */}
    </form>
  );
}
```

**Pattern 4: Public-Only Routes (Login, Signup)**
```tsx
// src/components/PublicRoute.tsx
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

export function PublicRoute() {
  const { isAuthenticated } = useAuth();

  if (isAuthenticated) {
    // Already logged in, redirect to dashboard
    return <Navigate to="/dashboard" replace />;
  }

  return <Outlet />;
}
```

**Usage**
```tsx
const router = createBrowserRouter([
  {
    path: '/',
    element: <Root />,
    children: [
      {
        // Public-only routes (redirect if authenticated)
        element: <PublicRoute />,
        children: [
          {
            path: 'login',
            element: <Login />,
          },
          {
            path: 'signup',
            element: <Signup />,
          },
        ],
      },
      {
        // Protected routes
        element: <ProtectedRoute />,
        children: [
          {
            path: 'dashboard',
            element: <Dashboard />,
          },
        ],
      },
    ],
  },
]);
```

### Anti-Pattern

❌ **WRONG: Wrapping each route individually**
```tsx
<Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
<Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
<Route path="/settings" element={<ProtectedRoute><Settings /></ProtectedRoute>} />
// Repetitive, hard to maintain
```

✅ **CORRECT: Nested protected routes**
```tsx
{
  element: <ProtectedRoute />,
  children: [
    { path: 'dashboard', element: <Dashboard /> },
    { path: 'profile', element: <Profile /> },
    { path: 'settings', element: <Settings /> },
  ]
}
```

---

## 3. Nested Routes & Layouts

### Problem
Share layouts (header, sidebar) across multiple routes without duplicating code.

### Solution
Use **nested routes** with **Outlet** to render shared layouts and child routes.

### Implementation

**Pattern 1: Shared Layout with Outlet**
```tsx
// src/routes/DashboardLayout.tsx
import { Outlet, NavLink } from 'react-router-dom';

export default function DashboardLayout() {
  return (
    <div className="flex h-screen">
      {/* Sidebar */}
      <aside className="w-64 bg-gray-800 text-white">
        <nav className="p-4 space-y-2">
          <NavLink
            to="/dashboard"
            end // Only active on exact match
            className={({ isActive }) =>
              isActive
                ? 'block px-4 py-2 bg-blue-600 rounded'
                : 'block px-4 py-2 hover:bg-gray-700 rounded'
            }
          >
            Overview
          </NavLink>
          <NavLink
            to="/dashboard/analytics"
            className={({ isActive }) =>
              isActive
                ? 'block px-4 py-2 bg-blue-600 rounded'
                : 'block px-4 py-2 hover:bg-gray-700 rounded'
            }
          >
            Analytics
          </NavLink>
          <NavLink
            to="/dashboard/settings"
            className={({ isActive }) =>
              isActive
                ? 'block px-4 py-2 bg-blue-600 rounded'
                : 'block px-4 py-2 hover:bg-gray-700 rounded'
            }
          >
            Settings
          </NavLink>
        </nav>
      </aside>

      {/* Main content area */}
      <main className="flex-1 overflow-auto p-8">
        {/* Child routes render here */}
        <Outlet />
      </main>
    </div>
  );
}
```

**Router Configuration**
```tsx
const router = createBrowserRouter([
  {
    path: '/',
    element: <Root />,
    children: [
      {
        path: 'dashboard',
        element: <DashboardLayout />, // Shared layout
        children: [
          {
            index: true, // /dashboard
            element: <DashboardOverview />,
          },
          {
            path: 'analytics', // /dashboard/analytics
            element: <Analytics />,
          },
          {
            path: 'settings', // /dashboard/settings
            element: <Settings />,
          },
        ],
      },
    ],
  },
]);
```

**Pattern 2: Passing Context to Child Routes**
```tsx
// src/routes/DashboardLayout.tsx
import { Outlet } from 'react-router-dom';
import { useState } from 'react';

export default function DashboardLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  return (
    <div className="flex h-screen">
      <aside className={sidebarOpen ? 'w-64' : 'w-16'}>
        {/* Sidebar content */}
      </aside>

      <main className="flex-1">
        {/* Pass context to child routes */}
        <Outlet context={{ sidebarOpen, setSidebarOpen }} />
      </main>
    </div>
  );
}

// Child route accessing context
// src/routes/DashboardOverview.tsx
import { useOutletContext } from 'react-router-dom';

interface DashboardContext {
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
}

export default function DashboardOverview() {
  const { sidebarOpen, setSidebarOpen } = useOutletContext<DashboardContext>();

  return (
    <div>
      <button onClick={() => setSidebarOpen(!sidebarOpen)}>
        Toggle Sidebar
      </button>
    </div>
  );
}
```

**Pattern 3: Breadcrumb Navigation**
```tsx
// src/components/Breadcrumbs.tsx
import { Link, useMatches } from 'react-router-dom';

interface RouteHandle {
  crumb?: (data: any) => React.ReactNode;
}

export function Breadcrumbs() {
  const matches = useMatches();

  const crumbs = matches
    .filter((match) => Boolean((match.handle as RouteHandle)?.crumb))
    .map((match) => (match.handle as RouteHandle).crumb!(match.data));

  return (
    <nav aria-label="Breadcrumb" className="flex items-center space-x-2 text-sm">
      {crumbs.map((crumb, index) => (
        <div key={index} className="flex items-center">
          {index > 0 && <span className="mx-2 text-gray-400">/</span>}
          {crumb}
        </div>
      ))}
    </nav>
  );
}
```

**Router Configuration with Breadcrumbs**
```tsx
const router = createBrowserRouter([
  {
    path: '/',
    element: <Root />,
    handle: {
      crumb: () => <Link to="/">Home</Link>,
    },
    children: [
      {
        path: 'users',
        element: <UserList />,
        handle: {
          crumb: () => <Link to="/users">Users</Link>,
        },
        children: [
          {
            path: ':id',
            element: <UserDetail />,
            loader: userLoader,
            handle: {
              crumb: (data) => <span>{data.user.name}</span>,
            },
          },
        ],
      },
    ],
  },
]);
```

**Pattern 4: Layout Routes (No Path)**
```tsx
const router = createBrowserRouter([
  {
    path: '/',
    element: <Root />,
    children: [
      {
        // Layout route (no path, just groups children)
        element: <TwoColumnLayout />,
        children: [
          {
            path: 'products',
            element: <ProductList />,
          },
          {
            path: 'services',
            element: <ServiceList />,
          },
        ],
      },
      {
        // Different layout for other routes
        element: <SingleColumnLayout />,
        children: [
          {
            path: 'about',
            element: <About />,
          },
          {
            path: 'contact',
            element: <Contact />,
          },
        ],
      },
    ],
  },
]);
```

### Anti-Pattern

❌ **WRONG: Duplicating layout code**
```tsx
<Route path="/dashboard" element={
  <DashboardLayout>
    <DashboardOverview />
  </DashboardLayout>
} />
<Route path="/dashboard/analytics" element={
  <DashboardLayout>
    <Analytics />
  </DashboardLayout>
} />
// Layout code duplicated in every route
```

✅ **CORRECT: Nested routes with Outlet**
```tsx
{
  path: 'dashboard',
  element: <DashboardLayout />,
  children: [
    { index: true, element: <DashboardOverview /> },
    { path: 'analytics', element: <Analytics /> },
  ]
}
```

---

## 4. Navigation Patterns

### Problem
Navigate between routes declaratively (links) and programmatically (after actions).

### Solution
Use **Link** for declarative navigation, **NavLink** for active states, and **useNavigate** for programmatic navigation.

### Implementation

**Pattern 1: Link Component (Basic Navigation)**
```tsx
import { Link } from 'react-router-dom';

function Navigation() {
  return (
    <nav>
      {/* Basic link */}
      <Link to="/">Home</Link>

      {/* Link with search params */}
      <Link to="/products?category=electronics">Electronics</Link>

      {/* Link with state */}
      <Link
        to="/products/123"
        state={{ from: 'search-results' }}
      >
        Product 123
      </Link>

      {/* Relative link (from current route) */}
      <Link to="../about">About</Link>

      {/* Replace current history entry */}
      <Link to="/login" replace>
        Login
      </Link>
    </nav>
  );
}
```

**Pattern 2: NavLink (Active State)**
```tsx
import { NavLink } from 'react-router-dom';

function Sidebar() {
  return (
    <nav>
      {/* className as function */}
      <NavLink
        to="/dashboard"
        className={({ isActive, isPending }) =>
          isPending
            ? 'pending'
            : isActive
            ? 'active bg-blue-600 text-white'
            : 'text-gray-600 hover:bg-gray-100'
        }
      >
        Dashboard
      </NavLink>

      {/* style as function */}
      <NavLink
        to="/settings"
        style={({ isActive }) => ({
          color: isActive ? '#fff' : '#666',
          backgroundColor: isActive ? '#007bff' : 'transparent',
        })}
      >
        Settings
      </NavLink>

      {/* children as function */}
      <NavLink to="/profile">
        {({ isActive }) => (
          <div className={isActive ? 'flex items-center font-bold' : 'flex items-center'}>
            <UserIcon className={isActive ? 'text-blue-600' : 'text-gray-400'} />
            <span className="ml-2">Profile</span>
          </div>
        )}
      </NavLink>

      {/* end prop for exact matching */}
      <NavLink
        to="/dashboard"
        end // Only active on /dashboard, not /dashboard/analytics
        className={({ isActive }) => isActive ? 'active' : ''}
      >
        Dashboard Home
      </NavLink>
    </nav>
  );
}
```

**Pattern 3: useNavigate (Programmatic Navigation)**
```tsx
import { useNavigate } from 'react-router-dom';

function ProductForm() {
  const navigate = useNavigate();

  const handleSubmit = async (data: ProductData) => {
    try {
      const product = await api.createProduct(data);

      // Navigate to product detail
      navigate(`/products/${product.id}`);

      // Navigate with state
      navigate('/products', {
        state: { message: 'Product created!' },
      });

      // Replace current entry in history
      navigate('/login', { replace: true });

      // Navigate with search params
      navigate({
        pathname: '/products',
        search: '?category=electronics&sort=price',
      });
    } catch (error) {
      toast.error('Failed to create product');
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      {/* Form fields */}
      <button type="button" onClick={() => navigate(-1)}>
        Go Back
      </button>
      <button type="submit">Create Product</button>
    </form>
  );
}
```

**Pattern 4: Relative Navigation**
```tsx
import { useNavigate } from 'react-router-dom';

function UserSettings() {
  const navigate = useNavigate();

  return (
    <div>
      {/* Navigate relative to current route */}
      <button onClick={() => navigate('..')}>
        Back to User List
      </button>

      <button onClick={() => navigate('../other-user')}>
        View Other User
      </button>

      {/* Absolute navigation */}
      <button onClick={() => navigate('/dashboard')}>
        Go to Dashboard
      </button>

      {/* Navigate with delta */}
      <button onClick={() => navigate(-1)}>Back</button>
      <button onClick={() => navigate(1)}>Forward</button>
    </div>
  );
}
```

**Pattern 5: Accessing Location State**
```tsx
import { useLocation, useNavigate } from 'react-router-dom';
import { useEffect } from 'react';

function ProductList() {
  const location = useLocation();
  const message = location.state?.message;

  useEffect(() => {
    if (message) {
      toast.success(message);
      // Clear state so toast doesn't show on refresh
      window.history.replaceState({}, document.title);
    }
  }, [message]);

  return <div>{/* Product list */}</div>;
}
```

**Pattern 6: Prevent Navigation on Unsaved Changes**
```tsx
import { useNavigate, useBlocker } from 'react-router-dom';
import { useEffect, useState } from 'react';

function EditForm() {
  const [isDirty, setIsDirty] = useState(false);

  // Block navigation if form has unsaved changes
  const blocker = useBlocker(
    ({ currentLocation, nextLocation }) =>
      isDirty && currentLocation.pathname !== nextLocation.pathname
  );

  useEffect(() => {
    if (blocker.state === 'blocked') {
      const shouldProceed = window.confirm(
        'You have unsaved changes. Are you sure you want to leave?'
      );

      if (shouldProceed) {
        blocker.proceed();
      } else {
        blocker.reset();
      }
    }
  }, [blocker]);

  return (
    <form onChange={() => setIsDirty(true)}>
      {/* Form fields */}
    </form>
  );
}
```

### Anti-Pattern

❌ **WRONG: Using anchor tags**
```tsx
<a href="/about">About</a>
// Causes full page reload, loses app state
```

✅ **CORRECT: Using Link component**
```tsx
<Link to="/about">About</Link>
// Client-side navigation, preserves state
```

---

## 5. Route Parameters & Search Params

### Problem
Access dynamic route parameters and query strings in a type-safe way.

### Solution
Use **useParams** for route parameters and **useSearchParams** for query strings.

### Implementation

**Pattern 1: Route Parameters with useParams**
```tsx
import { useParams } from 'react-router-dom';

// Route configuration
// { path: 'users/:id' }

interface UserParams {
  id: string;
}

function UserDetail() {
  const { id } = useParams<UserParams>();
  // TypeScript knows id is string | undefined

  if (!id) {
    return <div>Invalid user ID</div>;
  }

  return <div>User ID: {id}</div>;
}
```

**Pattern 2: Multiple Route Parameters**
```tsx
// Route configuration
// { path: 'posts/:postId/comments/:commentId' }

interface PostCommentParams {
  postId: string;
  commentId: string;
}

function CommentDetail() {
  const { postId, commentId } = useParams<PostCommentParams>();

  return (
    <div>
      Post: {postId}, Comment: {commentId}
    </div>
  );
}
```

**Pattern 3: Search Params with useSearchParams**
```tsx
import { useSearchParams } from 'react-router-dom';

function ProductList() {
  const [searchParams, setSearchParams] = useSearchParams();

  // Read search params
  const category = searchParams.get('category'); // 'electronics' or null
  const sort = searchParams.get('sort') ?? 'name'; // Default to 'name'
  const page = parseInt(searchParams.get('page') ?? '1', 10);

  // Update search params
  const handleCategoryChange = (newCategory: string) => {
    setSearchParams({
      category: newCategory,
      sort, // Preserve sort
      page: '1', // Reset to page 1
    });
  };

  const handleSortChange = (newSort: string) => {
    setSearchParams((prev) => {
      prev.set('sort', newSort);
      return prev;
    });
  };

  // Remove a param
  const clearCategory = () => {
    setSearchParams((prev) => {
      prev.delete('category');
      return prev;
    });
  };

  return (
    <div>
      <select value={category ?? ''} onChange={(e) => handleCategoryChange(e.target.value)}>
        <option value="">All Categories</option>
        <option value="electronics">Electronics</option>
        <option value="books">Books</option>
      </select>

      <select value={sort} onChange={(e) => handleSortChange(e.target.value)}>
        <option value="name">Name</option>
        <option value="price">Price</option>
      </select>
    </div>
  );
}
```

**Pattern 4: Type-Safe Search Params Helper**
```tsx
// src/hooks/useTypedSearchParams.ts
import { useSearchParams } from 'react-router-dom';
import { z } from 'zod';

export function useTypedSearchParams<T extends z.ZodTypeAny>(schema: T) {
  const [searchParams, setSearchParams] = useSearchParams();

  const params = Object.fromEntries(searchParams.entries());
  const parsed = schema.safeParse(params);

  const typedParams = parsed.success ? parsed.data : schema.parse({});

  const updateParams = (updates: Partial<z.infer<T>>) => {
    const newParams = { ...typedParams, ...updates };
    setSearchParams(newParams as Record<string, string>);
  };

  return [typedParams, updateParams] as const;
}

// Usage
const productFiltersSchema = z.object({
  category: z.string().optional(),
  minPrice: z.coerce.number().optional(),
  maxPrice: z.coerce.number().optional(),
  page: z.coerce.number().default(1),
  sort: z.enum(['name', 'price', 'date']).default('name'),
});

function ProductList() {
  const [filters, setFilters] = useTypedSearchParams(productFiltersSchema);
  // filters is fully typed!

  return (
    <div>
      <input
        type="number"
        value={filters.minPrice ?? ''}
        onChange={(e) => setFilters({ minPrice: parseInt(e.target.value) })}
      />
    </div>
  );
}
```

**Pattern 5: Persisting Complex State in URL**
```tsx
import { useSearchParams } from 'react-router-dom';
import { useMemo } from 'react';

interface Filters {
  categories: string[];
  priceRange: [number, number];
  inStock: boolean;
}

function ProductSearch() {
  const [searchParams, setSearchParams] = useSearchParams();

  // Parse filters from URL
  const filters = useMemo<Filters>(() => {
    const categoriesParam = searchParams.get('categories');
    const minPrice = searchParams.get('minPrice');
    const maxPrice = searchParams.get('maxPrice');
    const inStock = searchParams.get('inStock');

    return {
      categories: categoriesParam ? categoriesParam.split(',') : [],
      priceRange: [
        minPrice ? parseInt(minPrice) : 0,
        maxPrice ? parseInt(maxPrice) : 10000,
      ],
      inStock: inStock === 'true',
    };
  }, [searchParams]);

  // Update filters in URL
  const updateFilters = (newFilters: Partial<Filters>) => {
    const updated = { ...filters, ...newFilters };

    setSearchParams({
      categories: updated.categories.join(','),
      minPrice: updated.priceRange[0].toString(),
      maxPrice: updated.priceRange[1].toString(),
      inStock: updated.inStock.toString(),
    });
  };

  return (
    <div>
      <MultiSelect
        value={filters.categories}
        onChange={(categories) => updateFilters({ categories })}
      />
    </div>
  );
}
```

**Pattern 6: Replace vs Push with Search Params**
```tsx
function FilterPanel() {
  const [searchParams, setSearchParams] = useSearchParams();

  const handleFilterChange = (key: string, value: string) => {
    setSearchParams(
      (prev) => {
        prev.set(key, value);
        return prev;
      },
      { replace: true } // Don't add to history stack
    );
  };

  return (
    <div>
      {/* Use replace: true for transient updates like filters */}
      <input
        onChange={(e) => handleFilterChange('search', e.target.value)}
      />
    </div>
  );
}
```

### Anti-Pattern

❌ **WRONG: Manual URL parsing**
```tsx
const query = new URLSearchParams(window.location.search);
const category = query.get('category');
// Doesn't integrate with React Router, no reactivity
```

✅ **CORRECT: useSearchParams hook**
```tsx
const [searchParams] = useSearchParams();
const category = searchParams.get('category');
// Reactive, integrates with router
```

---

## 6. Lazy Loading Routes

### Problem
Large bundles slow initial page load; need code splitting for better performance.

### Solution
Use **React.lazy** with **Suspense** or React Router v6.9+ **lazy()** method for route-level code splitting.

### Implementation

**Pattern 1: React.lazy with Suspense**
```tsx
import { lazy, Suspense } from 'react';
import { createBrowserRouter } from 'react-router-dom';

// Lazy load route components
const Dashboard = lazy(() => import('./routes/Dashboard'));
const Analytics = lazy(() => import('./routes/Analytics'));
const Settings = lazy(() => import('./routes/Settings'));

const router = createBrowserRouter([
  {
    path: '/',
    element: <Root />,
    children: [
      {
        path: 'dashboard',
        element: (
          <Suspense fallback={<LoadingSpinner />}>
            <Dashboard />
          </Suspense>
        ),
      },
      {
        path: 'analytics',
        element: (
          <Suspense fallback={<LoadingSpinner />}>
            <Analytics />
          </Suspense>
        ),
      },
    ],
  },
]);

// Loading component
function LoadingSpinner() {
  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
    </div>
  );
}
```

**Pattern 2: Shared Suspense Boundary in Layout**
```tsx
import { Outlet } from 'react-router-dom';
import { Suspense } from 'react';

export default function DashboardLayout() {
  return (
    <div className="flex h-screen">
      <aside className="w-64">
        {/* Sidebar */}
      </aside>

      <main className="flex-1">
        {/* Single Suspense boundary for all child routes */}
        <Suspense
          fallback={
            <div className="flex items-center justify-center h-full">
              <LoadingSpinner />
            </div>
          }
        >
          <Outlet />
        </Suspense>
      </main>
    </div>
  );
}
```

**Pattern 3: React Router v6.9+ lazy() Method**
```tsx
import { createBrowserRouter } from 'react-router-dom';

const router = createBrowserRouter([
  {
    path: '/',
    element: <Root />,
    children: [
      {
        path: 'dashboard',
        lazy: async () => {
          const { Dashboard } = await import('./routes/Dashboard');
          return { Component: Dashboard };
        },
      },
      {
        path: 'analytics',
        lazy: async () => {
          // Can also load loader, action, etc.
          const { Analytics, loader } = await import('./routes/Analytics');
          return {
            Component: Analytics,
            loader,
          };
        },
      },
    ],
  },
]);
```

**Pattern 4: Parallel Loading (Data + Component)**
```tsx
// src/routes/UserDetail.tsx
export async function loader({ params }: LoaderFunctionArgs) {
  const user = await api.getUser(params.id!);
  return { user };
}

export function Component() {
  const { user } = useLoaderData<typeof loader>();
  return <div>{user.name}</div>;
}

// Router configuration
{
  path: 'users/:id',
  lazy: async () => {
    const module = await import('./routes/UserDetail');
    return {
      Component: module.Component,
      loader: module.loader,
    };
  },
}
// Component and data load in parallel!
```

**Pattern 5: Named Exports for Better Code Splitting**
```tsx
// ❌ WRONG: Default export only
export default function Dashboard() {
  return <div>Dashboard</div>;
}

// ✅ CORRECT: Named exports
export function Dashboard() {
  return <div>Dashboard</div>;
}

export async function loader() {
  const data = await api.getDashboard();
  return { data };
}

// Allows selective imports
lazy: async () => {
  const { Dashboard, loader } = await import('./routes/Dashboard');
  return { Component: Dashboard, loader };
}
```

**Pattern 6: Preloading Routes**
```tsx
import { useEffect } from 'react';

function Navigation() {
  useEffect(() => {
    // Preload dashboard route when hovering over link
    const preloadDashboard = () => {
      import('./routes/Dashboard');
    };

    const link = document.querySelector('a[href="/dashboard"]');
    link?.addEventListener('mouseenter', preloadDashboard);

    return () => {
      link?.removeEventListener('mouseenter', preloadDashboard);
    };
  }, []);

  return (
    <nav>
      <Link to="/dashboard">Dashboard</Link>
    </nav>
  );
}
```

**Pattern 7: Skeleton UI for Better UX**
```tsx
function DashboardSkeleton() {
  return (
    <div className="animate-pulse space-y-4 p-8">
      <div className="h-8 bg-gray-200 rounded w-1/4" />
      <div className="grid grid-cols-3 gap-4">
        <div className="h-32 bg-gray-200 rounded" />
        <div className="h-32 bg-gray-200 rounded" />
        <div className="h-32 bg-gray-200 rounded" />
      </div>
      <div className="h-64 bg-gray-200 rounded" />
    </div>
  );
}

// Use in Suspense
<Suspense fallback={<DashboardSkeleton />}>
  <Dashboard />
</Suspense>
```

### Anti-Pattern

❌ **WRONG: No code splitting**
```tsx
import Dashboard from './routes/Dashboard';
import Analytics from './routes/Analytics';
// All routes bundled together, large initial bundle
```

✅ **CORRECT: Lazy loading**
```tsx
const Dashboard = lazy(() => import('./routes/Dashboard'));
// Each route in separate bundle, faster initial load
```

---

## 7. Error Boundaries

### Problem
Handle errors during routing, data loading, and rendering without crashing the app.

### Solution
Use **errorElement** in route configuration for route-level error boundaries.

### Implementation

**Pattern 1: Root Error Boundary**
```tsx
// src/routes/ErrorPage.tsx
import { useRouteError, isRouteErrorResponse, Link } from 'react-router-dom';

export default function ErrorPage() {
  const error = useRouteError();

  if (isRouteErrorResponse(error)) {
    // Typed error from loader/action
    if (error.status === 404) {
      return (
        <div className="flex flex-col items-center justify-center min-h-screen">
          <h1 className="text-6xl font-bold text-gray-900 mb-4">404</h1>
          <p className="text-xl text-gray-600 mb-8">Page not found</p>
          <Link to="/" className="px-4 py-2 bg-blue-600 text-white rounded-md">
            Go Home
          </Link>
        </div>
      );
    }

    if (error.status === 403) {
      return (
        <div className="flex flex-col items-center justify-center min-h-screen">
          <h1 className="text-4xl font-bold text-red-600 mb-4">Access Denied</h1>
          <p className="text-xl text-gray-600 mb-8">{error.statusText}</p>
        </div>
      );
    }

    return (
      <div className="flex flex-col items-center justify-center min-h-screen">
        <h1 className="text-4xl font-bold text-red-600 mb-4">
          {error.status} {error.statusText}
        </h1>
        <p className="text-gray-600">{error.data?.message}</p>
      </div>
    );
  }

  // Unknown error
  return (
    <div className="flex flex-col items-center justify-center min-h-screen">
      <h1 className="text-4xl font-bold text-red-600 mb-4">Oops!</h1>
      <p className="text-xl text-gray-600 mb-4">Something went wrong</p>
      {error instanceof Error && (
        <pre className="mt-4 p-4 bg-gray-100 rounded-md text-sm overflow-auto">
          {error.message}
        </pre>
      )}
      <Link to="/" className="mt-8 px-4 py-2 bg-blue-600 text-white rounded-md">
        Go Home
      </Link>
    </div>
  );
}
```

**Router Configuration**
```tsx
const router = createBrowserRouter([
  {
    path: '/',
    element: <Root />,
    errorElement: <ErrorPage />, // Catches all errors in this route tree
    children: [
      {
        path: 'dashboard',
        element: <Dashboard />,
      },
    ],
  },
]);
```

**Pattern 2: Route-Specific Error Boundaries**
```tsx
const router = createBrowserRouter([
  {
    path: '/',
    element: <Root />,
    errorElement: <RootErrorPage />,
    children: [
      {
        path: 'dashboard',
        element: <Dashboard />,
        // Specific error page for dashboard
        errorElement: <DashboardError />,
      },
      {
        path: 'users/:id',
        element: <UserDetail />,
        loader: userLoader,
        // Handle user-not-found errors
        errorElement: <UserNotFound />,
      },
    ],
  },
]);
```

**Pattern 3: Throwing Errors in Loaders**
```tsx
// src/loaders/userLoader.ts
import { LoaderFunctionArgs } from 'react-router-dom';

export async function userLoader({ params }: LoaderFunctionArgs) {
  const user = await api.getUser(params.id!);

  if (!user) {
    // Throw response that errorElement can catch
    throw new Response('User not found', {
      status: 404,
      statusText: 'Not Found',
    });
  }

  return { user };
}

// With custom error data
export async function protectedLoader({ request }: LoaderFunctionArgs) {
  const user = await getCurrentUser();

  if (!user) {
    throw new Response(null, {
      status: 403,
      statusText: 'Forbidden',
      // Custom data in error response
      headers: {
        'X-Error-Message': 'You must be logged in',
      },
    });
  }

  return { user };
}
```

**Pattern 4: Catch-All 404 Route**
```tsx
const router = createBrowserRouter([
  {
    path: '/',
    element: <Root />,
    errorElement: <ErrorPage />,
    children: [
      {
        index: true,
        element: <Home />,
      },
      {
        path: 'about',
        element: <About />,
      },
      // Catch-all route for 404s
      {
        path: '*',
        element: <NotFoundPage />,
      },
    ],
  },
]);

function NotFoundPage() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen">
      <h1 className="text-6xl font-bold text-gray-900 mb-4">404</h1>
      <p className="text-xl text-gray-600 mb-8">
        The page you're looking for doesn't exist.
      </p>
      <Link to="/" className="px-4 py-2 bg-blue-600 text-white rounded-md">
        Go Home
      </Link>
    </div>
  );
}
```

**Pattern 5: Error Boundary with Retry**
```tsx
// src/routes/ErrorBoundaryWithRetry.tsx
import { useRouteError, useNavigate } from 'react-router-dom';
import { useState } from 'react';

export default function ErrorBoundaryWithRetry() {
  const error = useRouteError();
  const navigate = useNavigate();
  const [isRetrying, setIsRetrying] = useState(false);

  const handleRetry = async () => {
    setIsRetrying(true);
    // Force reload current route
    navigate(0);
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen">
      <h1 className="text-4xl font-bold text-red-600 mb-4">Something went wrong</h1>

      {error instanceof Error && (
        <p className="text-gray-600 mb-8">{error.message}</p>
      )}

      <div className="flex gap-4">
        <button
          onClick={handleRetry}
          disabled={isRetrying}
          className="px-4 py-2 bg-blue-600 text-white rounded-md disabled:opacity-50"
        >
          {isRetrying ? 'Retrying...' : 'Try Again'}
        </button>

        <button
          onClick={() => navigate(-1)}
          className="px-4 py-2 border border-gray-300 rounded-md"
        >
          Go Back
        </button>
      </div>
    </div>
  );
}
```

### Anti-Pattern

❌ **WRONG: No error boundary**
```tsx
const router = createBrowserRouter([
  { path: '/', element: <Root /> },
  // No errorElement, errors crash the app
]);
```

✅ **CORRECT: Root error boundary**
```tsx
const router = createBrowserRouter([
  {
    path: '/',
    element: <Root />,
    errorElement: <ErrorPage />,
  },
]);
```

---

## 8. Navigation Guards

### Problem
Warn users about unsaved changes before navigating away.

### Solution
Use **useBlocker** (React Router v6.4+) for internal navigation and **beforeunload** for external navigation.

### Implementation

**Pattern 1: useBlocker for Internal Navigation**
```tsx
import { useBlocker } from 'react-router-dom';
import { useState, useEffect } from 'react';

function EditForm() {
  const [isDirty, setIsDirty] = useState(false);

  // Block navigation when form has unsaved changes
  const blocker = useBlocker(
    ({ currentLocation, nextLocation }) =>
      isDirty && currentLocation.pathname !== nextLocation.pathname
  );

  useEffect(() => {
    if (blocker.state === 'blocked') {
      const shouldProceed = window.confirm(
        'You have unsaved changes. Are you sure you want to leave?'
      );

      if (shouldProceed) {
        blocker.proceed();
      } else {
        blocker.reset();
      }
    }
  }, [blocker]);

  const handleSubmit = async (data: FormData) => {
    await api.save(data);
    setIsDirty(false); // Clear dirty state after save
  };

  return (
    <form
      onChange={() => setIsDirty(true)}
      onSubmit={handleSubmit(onSubmit)}
    >
      {/* Form fields */}
    </form>
  );
}
```

**Pattern 2: Custom Confirmation Modal**
```tsx
import { useBlocker } from 'react-router-dom';
import { useState } from 'react';

function FormWithCustomModal() {
  const [isDirty, setIsDirty] = useState(false);
  const [showModal, setShowModal] = useState(false);

  const blocker = useBlocker(
    ({ currentLocation, nextLocation }) =>
      isDirty && currentLocation.pathname !== nextLocation.pathname
  );

  useEffect(() => {
    if (blocker.state === 'blocked') {
      setShowModal(true);
    }
  }, [blocker]);

  const handleConfirmLeave = () => {
    setShowModal(false);
    blocker.proceed?.();
  };

  const handleCancelLeave = () => {
    setShowModal(false);
    blocker.reset?.();
  };

  return (
    <>
      <form onChange={() => setIsDirty(true)}>
        {/* Form fields */}
      </form>

      {/* Custom modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
          <div className="bg-white p-6 rounded-lg shadow-xl max-w-md">
            <h2 className="text-xl font-bold mb-4">Unsaved Changes</h2>
            <p className="text-gray-600 mb-6">
              You have unsaved changes. Are you sure you want to leave?
            </p>
            <div className="flex justify-end gap-4">
              <button
                onClick={handleCancelLeave}
                className="px-4 py-2 border border-gray-300 rounded-md"
              >
                Stay
              </button>
              <button
                onClick={handleConfirmLeave}
                className="px-4 py-2 bg-red-600 text-white rounded-md"
              >
                Leave
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
```

**Pattern 3: beforeunload for External Navigation**
```tsx
import { useEffect } from 'react';

function FormWithBeforeUnload() {
  const [isDirty, setIsDirty] = useState(false);

  useEffect(() => {
    if (!isDirty) return;

    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      e.preventDefault();
      // Modern browsers show generic message
      e.returnValue = '';
    };

    window.addEventListener('beforeunload', handleBeforeUnload);

    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, [isDirty]);

  return (
    <form onChange={() => setIsDirty(true)}>
      {/* Form fields */}
    </form>
  );
}
```

**Pattern 4: Combined Guard (Internal + External)**
```tsx
import { useBlocker } from 'react-router-dom';
import { useState, useEffect } from 'react';

function useUnsavedChangesWarning(isDirty: boolean) {
  // Internal navigation guard
  const blocker = useBlocker(
    ({ currentLocation, nextLocation }) =>
      isDirty && currentLocation.pathname !== nextLocation.pathname
  );

  useEffect(() => {
    if (blocker.state === 'blocked') {
      const shouldProceed = window.confirm(
        'You have unsaved changes. Are you sure you want to leave?'
      );

      if (shouldProceed) {
        blocker.proceed();
      } else {
        blocker.reset();
      }
    }
  }, [blocker]);

  // External navigation guard
  useEffect(() => {
    if (!isDirty) return;

    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      e.preventDefault();
      e.returnValue = '';
    };

    window.addEventListener('beforeunload', handleBeforeUnload);

    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, [isDirty]);
}

// Usage
function EditForm() {
  const { formState: { isDirty } } = useForm();
  useUnsavedChangesWarning(isDirty);

  return <form>{/* Form fields */}</form>;
}
```

**Pattern 5: Integration with React Hook Form**
```tsx
import { useForm } from 'react-hook-form';
import { useBlocker } from 'react-router-dom';
import { useEffect } from 'react';

function FormWithRHF() {
  const {
    register,
    handleSubmit,
    formState: { isDirty, isSubmitSuccessful },
  } = useForm();

  const blocker = useBlocker(
    ({ currentLocation, nextLocation }) =>
      isDirty &&
      !isSubmitSuccessful &&
      currentLocation.pathname !== nextLocation.pathname
  );

  useEffect(() => {
    if (blocker.state === 'blocked') {
      const shouldProceed = window.confirm(
        'You have unsaved changes. Are you sure you want to leave?'
      );

      if (shouldProceed) {
        blocker.proceed();
      } else {
        blocker.reset();
      }
    }
  }, [blocker]);

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register('name')} />
      <button type="submit">Save</button>
    </form>
  );
}
```

### Anti-Pattern

❌ **WRONG: Only handling internal navigation**
```tsx
const blocker = useBlocker(isDirty);
// Doesn't prevent browser refresh/close
```

✅ **CORRECT: Handle both internal and external**
```tsx
const blocker = useBlocker(isDirty);
useEffect(() => {
  window.addEventListener('beforeunload', handler);
}, [isDirty]);
```

---

## 9. Route Transitions

### Problem
Add smooth animations between route changes without flicker.

### Solution
Use **View Transitions API** (React Router v6.4+) or custom animation libraries.

### Implementation

**Pattern 1: View Transitions API (Built-in)**
```tsx
import { Link, NavLink, Form } from 'react-router-dom';

function Navigation() {
  return (
    <nav>
      {/* Enable view transitions on Link */}
      <Link to="/dashboard" viewTransition>
        Dashboard
      </Link>

      {/* Works with NavLink too */}
      <NavLink to="/profile" viewTransition>
        Profile
      </NavLink>

      {/* And Form */}
      <Form action="/search" viewTransition>
        <input name="q" />
      </Form>
    </nav>
  );
}
```

**CSS for View Transitions**
```css
/* Basic cross-fade (automatic with viewTransition) */
::view-transition-old(root),
::view-transition-new(root) {
  animation-duration: 0.3s;
}

/* Custom animations */
@keyframes slide-from-right {
  from {
    transform: translateX(100%);
  }
}

@keyframes slide-to-left {
  to {
    transform: translateX(-100%);
  }
}

::view-transition-old(root) {
  animation: 0.3s ease-out slide-to-left;
}

::view-transition-new(root) {
  animation: 0.3s ease-out slide-from-right;
}

/* Fade + scale */
::view-transition-old(root) {
  animation: 0.3s ease-out both fade-out, 0.3s ease-out both scale-down;
}

::view-transition-new(root) {
  animation: 0.3s ease-out both fade-in, 0.3s ease-out both scale-up;
}

@keyframes fade-out {
  to { opacity: 0; }
}

@keyframes fade-in {
  from { opacity: 0; }
}

@keyframes scale-down {
  to { transform: scale(0.9); }
}

@keyframes scale-up {
  from { transform: scale(0.9); }
}
```

**Pattern 2: Loading Indicators with useNavigation**
```tsx
import { useNavigation } from 'react-router-dom';

export default function Root() {
  const navigation = useNavigation();

  return (
    <div>
      <nav>
        {/* Navigation */}
      </nav>

      {/* Loading bar */}
      {navigation.state === 'loading' && (
        <div className="fixed top-0 left-0 right-0 h-1 bg-blue-600 animate-pulse" />
      )}

      <main>
        <Outlet />
      </main>
    </div>
  );
}
```

**Pattern 3: Global Loading Indicator**
```tsx
import { useNavigation } from 'react-router-dom';

function GlobalLoadingBar() {
  const navigation = useNavigation();
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    if (navigation.state === 'loading') {
      setProgress(0);
      const interval = setInterval(() => {
        setProgress((prev) => {
          if (prev >= 90) return prev;
          return prev + 10;
        });
      }, 100);

      return () => clearInterval(interval);
    } else {
      setProgress(100);
      setTimeout(() => setProgress(0), 200);
    }
  }, [navigation.state]);

  if (progress === 0) return null;

  return (
    <div className="fixed top-0 left-0 right-0 h-1 bg-gray-200 z-50">
      <div
        className="h-full bg-blue-600 transition-all duration-200"
        style={{ width: `${progress}%` }}
      />
    </div>
  );
}
```

**Pattern 4: Page-Level Transitions with Framer Motion**
```tsx
import { motion, AnimatePresence } from 'framer-motion';
import { useLocation, Outlet } from 'react-router-dom';

function AnimatedOutlet() {
  const location = useLocation();

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={location.pathname}
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, x: -20 }}
        transition={{ duration: 0.3 }}
      >
        <Outlet />
      </motion.div>
    </AnimatePresence>
  );
}
```

**Pattern 5: Skeleton UI During Navigation**
```tsx
import { useNavigation } from 'react-router-dom';
import { Outlet } from 'react-router-dom';

function DashboardLayout() {
  const navigation = useNavigation();

  return (
    <div className="flex h-screen">
      <aside className="w-64">{/* Sidebar */}</aside>

      <main className="flex-1">
        {navigation.state === 'loading' ? (
          <DashboardSkeleton />
        ) : (
          <Outlet />
        )}
      </main>
    </div>
  );
}

function DashboardSkeleton() {
  return (
    <div className="animate-pulse p-8 space-y-4">
      <div className="h-8 bg-gray-200 rounded w-1/4" />
      <div className="grid grid-cols-3 gap-4">
        <div className="h-32 bg-gray-200 rounded" />
        <div className="h-32 bg-gray-200 rounded" />
        <div className="h-32 bg-gray-200 rounded" />
      </div>
    </div>
  );
}
```

### Anti-Pattern

❌ **WRONG: Blocking UI during navigation**
```tsx
if (navigation.state === 'loading') {
  return <FullPageSpinner />;
  // Entire UI disappears, poor UX
}
```

✅ **CORRECT: Non-blocking indicator**
```tsx
<>
  <LoadingBar show={navigation.state === 'loading'} />
  <Outlet />
</>
```

---

## 10. URL State Management

### Problem
Store filters, pagination, search queries in URL for shareable, bookmarkable state.

### Solution
Use **useSearchParams** to sync component state with URL query parameters.

### Implementation

**Pattern 1: Filters with Search Params**
```tsx
import { useSearchParams } from 'react-router-dom';

function ProductList() {
  const [searchParams, setSearchParams] = useSearchParams();

  // Read filters from URL
  const category = searchParams.get('category') ?? 'all';
  const sort = searchParams.get('sort') ?? 'name';
  const page = parseInt(searchParams.get('page') ?? '1', 10);

  // Update filters
  const handleCategoryChange = (newCategory: string) => {
    setSearchParams(
      {
        category: newCategory,
        sort,
        page: '1', // Reset to page 1 when filter changes
      },
      { replace: true } // Don't add to history
    );
  };

  const handlePageChange = (newPage: number) => {
    setSearchParams(
      (prev) => {
        prev.set('page', newPage.toString());
        return prev;
      },
      { replace: true }
    );
  };

  return (
    <div>
      <select value={category} onChange={(e) => handleCategoryChange(e.target.value)}>
        <option value="all">All</option>
        <option value="electronics">Electronics</option>
        <option value="books">Books</option>
      </select>

      <ProductGrid category={category} sort={sort} page={page} />

      <Pagination page={page} onPageChange={handlePageChange} />
    </div>
  );
}
```

**Pattern 2: Debounced Search Input**
```tsx
import { useSearchParams } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { useDebouncedCallback } from 'use-debounce';

function SearchInput() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [search, setSearch] = useState(searchParams.get('q') ?? '');

  // Debounced update to URL
  const debouncedSetSearch = useDebouncedCallback((value: string) => {
    if (value) {
      setSearchParams({ q: value }, { replace: true });
    } else {
      setSearchParams({}, { replace: true });
    }
  }, 300);

  const handleSearchChange = (value: string) => {
    setSearch(value);
    debouncedSetSearch(value);
  };

  return (
    <input
      type="text"
      value={search}
      onChange={(e) => handleSearchChange(e.target.value)}
      placeholder="Search..."
      className="px-4 py-2 border rounded-md"
    />
  );
}
```

**Pattern 3: Tab State in URL**
```tsx
import { useSearchParams } from 'react-router-dom';

function Settings() {
  const [searchParams, setSearchParams] = useSearchParams();
  const activeTab = searchParams.get('tab') ?? 'profile';

  const setActiveTab = (tab: string) => {
    setSearchParams({ tab }, { replace: true });
  };

  return (
    <div>
      <div className="flex border-b">
        <button
          onClick={() => setActiveTab('profile')}
          className={activeTab === 'profile' ? 'active' : ''}
        >
          Profile
        </button>
        <button
          onClick={() => setActiveTab('security')}
          className={activeTab === 'security' ? 'active' : ''}
        >
          Security
        </button>
        <button
          onClick={() => setActiveTab('notifications')}
          className={activeTab === 'notifications' ? 'active' : ''}
        >
          Notifications
        </button>
      </div>

      <div className="mt-4">
        {activeTab === 'profile' && <ProfileSettings />}
        {activeTab === 'security' && <SecuritySettings />}
        {activeTab === 'notifications' && <NotificationSettings />}
      </div>
    </div>
  );
}
```

**Pattern 4: Complex Filters with Object State**
```tsx
import { useSearchParams } from 'react-router-dom';
import { useMemo } from 'react';

interface Filters {
  categories: string[];
  priceMin?: number;
  priceMax?: number;
  inStock?: boolean;
  sort: 'name' | 'price' | 'date';
}

function useFilterParams() {
  const [searchParams, setSearchParams] = useSearchParams();

  // Parse URL params into object
  const filters = useMemo<Filters>(() => {
    const categoriesParam = searchParams.get('categories');

    return {
      categories: categoriesParam ? categoriesParam.split(',') : [],
      priceMin: searchParams.get('priceMin')
        ? Number(searchParams.get('priceMin'))
        : undefined,
      priceMax: searchParams.get('priceMax')
        ? Number(searchParams.get('priceMax'))
        : undefined,
      inStock: searchParams.get('inStock') === 'true',
      sort: (searchParams.get('sort') as Filters['sort']) ?? 'name',
    };
  }, [searchParams]);

  // Update filters
  const updateFilters = (updates: Partial<Filters>) => {
    const newFilters = { ...filters, ...updates };

    const params: Record<string, string> = {
      sort: newFilters.sort,
    };

    if (newFilters.categories.length > 0) {
      params.categories = newFilters.categories.join(',');
    }

    if (newFilters.priceMin !== undefined) {
      params.priceMin = newFilters.priceMin.toString();
    }

    if (newFilters.priceMax !== undefined) {
      params.priceMax = newFilters.priceMax.toString();
    }

    if (newFilters.inStock) {
      params.inStock = 'true';
    }

    setSearchParams(params, { replace: true });
  };

  return [filters, updateFilters] as const;
}

// Usage
function ProductSearch() {
  const [filters, updateFilters] = useFilterParams();

  return (
    <div>
      <MultiSelect
        value={filters.categories}
        onChange={(categories) => updateFilters({ categories })}
      />

      <RangeSlider
        min={filters.priceMin}
        max={filters.priceMax}
        onChange={(priceMin, priceMax) => updateFilters({ priceMin, priceMax })}
      />
    </div>
  );
}
```

**Pattern 5: Modal State in URL**
```tsx
import { useSearchParams, useNavigate } from 'react-router-dom';

function ProductList() {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();

  const selectedProduct = searchParams.get('product');

  const openModal = (productId: string) => {
    setSearchParams({ product: productId });
  };

  const closeModal = () => {
    setSearchParams({});
  };

  return (
    <div>
      <div className="grid grid-cols-3 gap-4">
        {products.map((product) => (
          <div key={product.id} onClick={() => openModal(product.id)}>
            {product.name}
          </div>
        ))}
      </div>

      {selectedProduct && (
        <ProductModal productId={selectedProduct} onClose={closeModal} />
      )}
    </div>
  );
}
```

### Anti-Pattern

❌ **WRONG: State only in React**
```tsx
const [filters, setFilters] = useState({ category: 'all' });
// Not shareable, lost on refresh
```

✅ **CORRECT: State in URL**
```tsx
const [searchParams, setSearchParams] = useSearchParams();
const category = searchParams.get('category') ?? 'all';
// Shareable, persistent
```

---

## 11. Modal Routes

### Problem
Show modals while preserving background page and URL state.

### Solution
Use search params or location state to control modal visibility.

### Implementation

**Pattern 1: Modal with Search Params**
```tsx
import { useSearchParams } from 'react-router-dom';

function UserList() {
  const [searchParams, setSearchParams] = useSearchParams();
  const userId = searchParams.get('user');

  const openUserModal = (id: string) => {
    setSearchParams({ user: id });
  };

  const closeModal = () => {
    setSearchParams({});
  };

  return (
    <div>
      <div className="grid grid-cols-3 gap-4">
        {users.map((user) => (
          <div key={user.id} onClick={() => openUserModal(user.id)}>
            {user.name}
          </div>
        ))}
      </div>

      {userId && (
        <UserModal userId={userId} onClose={closeModal} />
      )}
    </div>
  );
}
```

**Pattern 2: Modal with Background Location**
```tsx
import { useLocation, useNavigate, Link } from 'react-router-dom';

function UserList() {
  const location = useLocation();

  return (
    <div>
      {users.map((user) => (
        <Link
          key={user.id}
          to={`/users/${user.id}`}
          // Save current location as background
          state={{ backgroundLocation: location }}
        >
          {user.name}
        </Link>
      ))}
    </div>
  );
}

// Router configuration
const router = createBrowserRouter([
  {
    path: '/',
    element: <Root />,
    children: [
      {
        path: 'users',
        element: <UserList />,
      },
      {
        path: 'users/:id',
        element: <UserDetail />,
      },
    ],
  },
]);

// Root component
function Root() {
  const location = useLocation();
  const navigate = useNavigate();

  // Get background location from state
  const backgroundLocation = location.state?.backgroundLocation;

  return (
    <>
      {/* Show background route when modal is open */}
      <Routes location={backgroundLocation || location}>
        <Route path="/" element={<Home />} />
        <Route path="/users" element={<UserList />} />
        <Route path="/users/:id" element={<UserDetail />} />
      </Routes>

      {/* Show modal if background location exists */}
      {backgroundLocation && (
        <Routes>
          <Route
            path="/users/:id"
            element={
              <Modal onClose={() => navigate(-1)}>
                <UserDetail />
              </Modal>
            }
          />
        </Routes>
      )}
    </>
  );
}
```

**Pattern 3: Drawer with URL State**
```tsx
import { useSearchParams } from 'react-router-dom';
import { Drawer } from './components/Drawer';

function Dashboard() {
  const [searchParams, setSearchParams] = useSearchParams();
  const drawerOpen = searchParams.get('drawer') === 'true';

  const openDrawer = () => setSearchParams({ drawer: 'true' });
  const closeDrawer = () => setSearchParams({});

  return (
    <div>
      <button onClick={openDrawer}>Open Settings</button>

      <Drawer isOpen={drawerOpen} onClose={closeDrawer}>
        <SettingsPanel />
      </Drawer>
    </div>
  );
}
```

### Anti-Pattern

❌ **WRONG: Modal state in React only**
```tsx
const [modalOpen, setModalOpen] = useState(false);
// Can't share URL with modal open
```

✅ **CORRECT: Modal state in URL**
```tsx
const [searchParams, setSearchParams] = useSearchParams();
const modalOpen = searchParams.get('modal') === 'true';
// Shareable URL
```

---

## 12. Accessibility

### Problem
Ensure routing is accessible to keyboard users and screen readers.

### Solution
Implement focus management and route announcements.

### Implementation

**Pattern 1: Focus Management on Route Change**
```tsx
import { useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';

function FocusOnNavigate() {
  const location = useLocation();
  const mainRef = useRef<HTMLElement>(null);

  useEffect(() => {
    // Focus main content on route change
    mainRef.current?.focus();
  }, [location]);

  return (
    <main
      ref={mainRef}
      tabIndex={-1}
      className="outline-none"
    >
      <Outlet />
    </main>
  );
}
```

**Pattern 2: Route Announcements for Screen Readers**
```tsx
// src/components/RouteAnnouncer.tsx
import { useEffect } from 'react';
import { useLocation, useMatches } from 'react-router-dom';

export function RouteAnnouncer() {
  const location = useLocation();
  const matches = useMatches();

  useEffect(() => {
    // Get page title from route handle
    const currentMatch = matches[matches.length - 1];
    const title = currentMatch?.handle?.title || 'Page';

    // Announce to screen readers
    const announcement = `Navigated to ${title}`;
    announceToScreenReader(announcement);
  }, [location, matches]);

  return (
    <div
      role="status"
      aria-live="polite"
      aria-atomic="true"
      className="sr-only"
    >
      {/* Screen reader announcement */}
    </div>
  );
}

function announceToScreenReader(message: string) {
  const el = document.getElementById('route-announcer');
  if (el) {
    el.textContent = '';
    setTimeout(() => {
      el.textContent = message;
    }, 100);
  }
}
```

**Usage in Router**
```tsx
const router = createBrowserRouter([
  {
    path: '/',
    element: (
      <>
        <RouteAnnouncer />
        <Root />
      </>
    ),
    children: [
      {
        path: 'dashboard',
        element: <Dashboard />,
        handle: { title: 'Dashboard' },
      },
    ],
  },
]);
```

**Pattern 3: Skip Navigation Link**
```tsx
function Root() {
  return (
    <div>
      {/* Skip to main content */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-blue-600 focus:text-white focus:rounded-md"
      >
        Skip to main content
      </a>

      <nav>{/* Navigation */}</nav>

      <main id="main-content" tabIndex={-1}>
        <Outlet />
      </main>
    </div>
  );
}
```

**Pattern 4: Accessible NavLink**
```tsx
function AccessibleNav() {
  return (
    <nav aria-label="Main navigation">
      <ul>
        <li>
          <NavLink
            to="/dashboard"
            className={({ isActive }) => (isActive ? 'active' : '')}
            aria-current={({ isActive }) => (isActive ? 'page' : undefined)}
          >
            Dashboard
          </NavLink>
        </li>
      </ul>
    </nav>
  );
}
```

### Anti-Pattern

❌ **WRONG: No focus management**
```tsx
<Outlet />
// Focus stays on previous element
```

✅ **CORRECT: Focus main on route change**
```tsx
useEffect(() => {
  mainRef.current?.focus();
}, [location]);
<main ref={mainRef} tabIndex={-1}>
  <Outlet />
</main>
```

---

## 13. Common Anti-Patterns

### Anti-Pattern 1: Using BrowserRouter Instead of createBrowserRouter

❌ **WRONG:**
```tsx
<BrowserRouter>
  <Routes>
    <Route path="/" element={<Home />} />
  </Routes>
</BrowserRouter>
// Missing v6.4+ data APIs
```

✅ **CORRECT:**
```tsx
const router = createBrowserRouter([
  { path: '/', element: <Home /> },
]);
<RouterProvider router={router} />
```

---

### Anti-Pattern 2: Duplicating Protected Route Logic

❌ **WRONG:**
```tsx
<Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
<Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
```

✅ **CORRECT:**
```tsx
{
  element: <ProtectedRoute />,
  children: [
    { path: 'dashboard', element: <Dashboard /> },
    { path: 'profile', element: <Profile /> },
  ]
}
```

---

### Anti-Pattern 3: Not Using errorElement

❌ **WRONG:**
```tsx
const router = createBrowserRouter([
  { path: '/', element: <Root /> },
  // No error boundary
]);
```

✅ **CORRECT:**
```tsx
const router = createBrowserRouter([
  {
    path: '/',
    element: <Root />,
    errorElement: <ErrorPage />,
  },
]);
```

---

### Anti-Pattern 4: Manual URL Parsing

❌ **WRONG:**
```tsx
const query = new URLSearchParams(window.location.search);
const category = query.get('category');
```

✅ **CORRECT:**
```tsx
const [searchParams] = useSearchParams();
const category = searchParams.get('category');
```

---

### Anti-Pattern 5: Not Lazy Loading Routes

❌ **WRONG:**
```tsx
import Dashboard from './routes/Dashboard';
// All routes bundled together
```

✅ **CORRECT:**
```tsx
const Dashboard = lazy(() => import('./routes/Dashboard'));
```

---

### Anti-Pattern 6: State Only in React

❌ **WRONG:**
```tsx
const [filters, setFilters] = useState({});
// Lost on refresh, not shareable
```

✅ **CORRECT:**
```tsx
const [searchParams, setSearchParams] = useSearchParams();
// Persistent, shareable
```

---

### Anti-Pattern 7: Using Anchor Tags

❌ **WRONG:**
```tsx
<a href="/about">About</a>
// Full page reload
```

✅ **CORRECT:**
```tsx
<Link to="/about">About</Link>
// Client-side navigation
```

---

### Anti-Pattern 8: No Loading States

❌ **WRONG:**
```tsx
<Outlet />
// No indication of loading
```

✅ **CORRECT:**
```tsx
const navigation = useNavigation();
{navigation.state === 'loading' && <LoadingBar />}
<Outlet />
```

---

### Anti-Pattern 9: Blocking Navigation Without Warning

❌ **WRONG:**
```tsx
// No unsaved changes warning
```

✅ **CORRECT:**
```tsx
const blocker = useBlocker(isDirty);
// + beforeunload handler
```

---

### Anti-Pattern 10: No Accessibility

❌ **WRONG:**
```tsx
<Outlet />
// No focus management, no announcements
```

✅ **CORRECT:**
```tsx
useEffect(() => {
  mainRef.current?.focus();
}, [location]);
<main ref={mainRef} tabIndex={-1}>
  <Outlet />
</main>
```

---

## Summary

### Key Patterns

1. **createBrowserRouter + RouterProvider** - Modern setup with data APIs
2. **Nested Routes with Outlet** - Shared layouts without duplication
3. **Protected Routes with Outlet Pattern** - Authentication guards
4. **useParams & useSearchParams** - Type-safe route/query params
5. **Lazy Loading with React.lazy** - Code splitting for performance
6. **errorElement** - Route-level error boundaries
7. **useBlocker + beforeunload** - Unsaved changes warnings
8. **View Transitions API** - Smooth route transitions
9. **URL State Management** - Filters, pagination in search params
10. **Focus Management** - Accessibility on route change

### Common Mistakes

1. ❌ Using BrowserRouter instead of createBrowserRouter
2. ❌ Duplicating protected route logic
3. ❌ No error boundaries
4. ❌ Manual URL parsing
5. ❌ No lazy loading
6. ❌ State only in React, not URL
7. ❌ Using anchor tags instead of Link
8. ❌ No loading indicators
9. ❌ No unsaved changes warnings
10. ❌ No focus management for accessibility

### Quick Reference

**Basic Setup:**
```tsx
const router = createBrowserRouter([
  {
    path: '/',
    element: <Root />,
    errorElement: <ErrorPage />,
    children: [
      { index: true, element: <Home /> },
    ],
  },
]);
```

**Protected Routes:**
```tsx
{
  element: <ProtectedRoute />,
  children: [
    { path: 'dashboard', element: <Dashboard /> },
  ]
}
```

**Lazy Loading:**
```tsx
const Dashboard = lazy(() => import('./routes/Dashboard'));
<Suspense fallback={<Spinner />}>
  <Dashboard />
</Suspense>
```

**Search Params:**
```tsx
const [searchParams, setSearchParams] = useSearchParams();
const category = searchParams.get('category');
setSearchParams({ category: 'new' });
```

**Navigation:**
```tsx
const navigate = useNavigate();
navigate('/dashboard');
navigate(-1); // Go back
```

---

## Related Skills

- **[frontend-patterns/03-react-performance.md](./03-react-performance.md)** - Performance optimization
- **[frontend-patterns/05-form-handling.md](./05-form-handling.md)** - Form state management
- **[api-design.md](../api-design.md)** - API patterns for loaders/actions
- **[testing-strategy.md](../testing-strategy.md)** - Testing routes and navigation

---

## Sources

- [React Router Official Documentation](https://reactrouter.com/)
- [Type Safety | React Router](https://reactrouter.com/explanation/type-safety)
- [Master React Router + Vite + TSX: The 2025 Step-by-Step | JunKangWorld](https://junkangworld.com/blog/master-react-router-vite-tsx-the-2025-step-by-step)
- [React Router 7: Private Routes](https://www.robinwieruch.de/react-router-private-routes/)
- [Building Reliable Protected Routes with React Router v7](https://dev.to/ra1nbow1/building-reliable-protected-routes-with-react-router-v7-1ka0)
- [Role Based Authorization with React Router v6 and Typescript](https://www.adarsha.dev/blog/role-based-auth-with-react-router-v6)
- [The Guide to Nested Routes with React Router](https://ui.dev/react-router-nested-routes)
- [React Router 7: Nested Routes](https://www.robinwieruch.de/react-router-nested-routes/)
- [useNavigate | React Router](https://reactrouter.com/api/hooks/useNavigate)
- [Link and NavLink components in React-Router-Dom](https://www.geeksforgeeks.org/reactjs/link-and-navlink-components-in-react-router-dom/)
- [React router v6 useSearchParams](https://dev.to/jacobgavin/react-router-v6-usesearchparams-25hn)
- [React Router 7: Search Params (alias Query Params)](https://www.robinwieruch.de/react-router-search-params/)
- [Why URL state matters: A guide to useSearchParams in React](https://blog.logrocket.com/url-state-usesearchparams/)
- [Code Splitting with React Router v6, React Lazy and Suspense](https://dev.to/omogbai/code-splitting-with-react-router-v6-react-lazy-and-suspense-in-simple-terms-5365)
- [React Router 7 Lazy Loading](https://www.robinwieruch.de/react-router-lazy-loading/)
- [Lazy Loading Routes in React Router 6.4+ | Remix](https://remix.run/blog/lazy-loading-routes)
- [Error Boundaries | React Router](https://reactrouter.com/how-to/error-boundary)
- [errorElement | React Router](https://reactrouter.com/en/main/route/error-element)
- [404 Page with React Router V6.4](https://dev.to/salehmubashar/404-page-with-react-router-v64-145j)
- [[V6] [Feature] Getting usePrompt and useBlocker back in the router](https://github.com/remix-run/react-router/issues/8139)
- [Building a Robust Unsaved Changes Prompt with React and React Router DOM](https://medium.com/@serifcolakel/building-a-robust-unsaved-changes-prompt-with-react-and-react-router-dom-24f9157307ca)
- [View Transitions | React Router](https://reactrouter.com/how-to/view-transitions)
- [3 ways to show loading indicators while switching routes in React Router](https://www.saurabhmisra.dev/react-router-loading-indicators/)
- [Modals with React Router 6 and Remix](https://www.infoxicator.com/modals-with-react-router-6-and-remix)
- [Create contextual modal navigation with React Router V6](https://dev.to/ligzer_dev/create-contextual-modal-navigation-with-react-router-v6-28k2)
- [Accessibility | React Router](https://reactrouter.com/how-to/accessibility)
- [Focus Management? · Discussion #9555](https://github.com/remix-run/react-router/discussions/9555)
- [Making route changes accessible in React with an autofocusing h1](https://jshakespeare.com/accessible-route-change-react-router-autofocus-heading/)
