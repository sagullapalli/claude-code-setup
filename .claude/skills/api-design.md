# API Design Skill

This skill helps with designing robust, scalable, and developer-friendly APIs.

## Usage

Use this skill when you need to:
- Design RESTful or GraphQL APIs
- Create API specifications and documentation
- Implement API versioning strategies
- Design authentication and authorization
- Optimize API performance

## API Design Principles

### 1. RESTful API Design

#### Resource-Based URLs
```
Good:
GET    /users           # List users
GET    /users/{id}      # Get specific user
POST   /users           # Create user
PUT    /users/{id}      # Update user
DELETE /users/{id}      # Delete user

Bad:
GET /getUsers
POST /createUser
```

#### HTTP Methods
- **GET**: Retrieve resources (idempotent, cacheable)
- **POST**: Create resources (not idempotent)
- **PUT**: Update/replace entire resource (idempotent)
- **PATCH**: Partial update (not necessarily idempotent)
- **DELETE**: Remove resource (idempotent)

#### HTTP Status Codes
- **2xx Success**
  - 200 OK: Request succeeded
  - 201 Created: Resource created
  - 204 No Content: Success with no response body
- **3xx Redirection**
  - 301 Moved Permanently
  - 304 Not Modified (caching)
- **4xx Client Errors**
  - 400 Bad Request: Invalid input
  - 401 Unauthorized: Authentication required
  - 403 Forbidden: Not allowed
  - 404 Not Found: Resource doesn't exist
  - 422 Unprocessable Entity: Validation errors
  - 429 Too Many Requests: Rate limit exceeded
- **5xx Server Errors**
  - 500 Internal Server Error
  - 502 Bad Gateway
  - 503 Service Unavailable

### 2. GraphQL API Design

#### Schema Design
```graphql
type Query {
  user(id: ID!): User
  users(limit: Int, offset: Int): UserConnection
}

type Mutation {
  createUser(input: CreateUserInput!): User
  updateUser(id: ID!, input: UpdateUserInput!): User
  deleteUser(id: ID!): Boolean
}

type User {
  id: ID!
  email: String!
  name: String
  posts: [Post!]!
}
```

#### Best Practices
- Use nullable types appropriately
- Implement pagination (cursor or offset-based)
- Avoid N+1 queries with DataLoader
- Use input types for mutations
- Implement proper error handling
- Add descriptions to schema fields

### 3. Request/Response Design

#### Request Body (JSON)
```json
{
  "email": "user@example.com",
  "name": "John Doe",
  "role": "admin"
}
```

#### Response Format
```json
{
  "data": {
    "id": "123",
    "email": "user@example.com",
    "name": "John Doe",
    "role": "admin",
    "createdAt": "2024-01-15T10:30:00Z"
  },
  "meta": {
    "requestId": "abc-123",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

#### Error Response
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input provided",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ]
  },
  "meta": {
    "requestId": "abc-123",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

### 4. Pagination

#### Offset-Based Pagination
```
GET /users?limit=20&offset=40
```

Response:
```json
{
  "data": [...],
  "pagination": {
    "limit": 20,
    "offset": 40,
    "total": 150,
    "hasMore": true
  }
}
```

#### Cursor-Based Pagination
```
GET /users?limit=20&cursor=eyJpZCI6MTIzfQ
```

Response:
```json
{
  "data": [...],
  "pagination": {
    "nextCursor": "eyJpZCI6MTQzfQ",
    "hasMore": true
  }
}
```

### 5. Authentication & Authorization

#### Authentication Methods

**JWT (JSON Web Tokens)**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**API Keys**
```
X-API-Key: your-api-key-here
```

**OAuth 2.0**
- Authorization Code Flow (web apps)
- Client Credentials Flow (service-to-service)
- PKCE (mobile/SPA apps)

**OAuth 2.0 Scopes**

Design granular permissions instead of coarse-grained roles:

**Good:**
```
user:read         # Read user data
user:write        # Modify user data
order:create      # Create orders
order:read        # Read orders
admin:users       # Admin-level user management
payment:process   # Process payments
```

**Bad:**
```
admin            # Too broad, unclear permissions
user             # Ambiguous permission level
full_access      # Violates principle of least privilege
```

**Best Practices:**
- Use colon notation for namespacing (`resource:action`)
- Start with least privilege, expand as needed
- Combine scopes for complex operations
- Document scope requirements per endpoint

#### Authorization Patterns
- **Role-Based Access Control (RBAC)**: Permissions based on roles
- **Attribute-Based Access Control (ABAC)**: Permissions based on attributes
- **Resource-Based**: Permissions on specific resources
- **Scope-Based** (OAuth): Granular permissions per token

### 6. Versioning

#### URL Versioning
```
/v1/users
/v2/users
```

#### Header Versioning
```
Accept: application/vnd.api.v1+json
```

#### Query Parameter Versioning
```
/users?version=1
```

**Recommendation**: URL versioning for major changes, header for minor changes

### 7. Rate Limiting

#### Response Headers
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 950
X-RateLimit-Reset: 1640000000
Retry-After: 3600
```

**When rate limit exceeded (429):**
```
HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1640000000
Retry-After: 3600

{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Try again in 3600 seconds."
  }
}
```

#### Strategies
- **Fixed Window**: Reset at fixed intervals
- **Sliding Window**: Rolling time window
- **Token Bucket**: Burst handling
- **Leaky Bucket**: Smooth rate limiting

### 8. Caching

#### Cache Headers
```
Cache-Control: public, max-age=3600
ETag: "33a64df551425fcc55e4d42a148795d9"
Last-Modified: Wed, 15 Jan 2024 10:30:00 GMT
```

#### Caching Strategies
- **Browser Cache**: Static resources
- **CDN Cache**: Distributed caching
- **API Gateway Cache**: Response caching
- **Application Cache**: Redis, Memcached

### 9. Performance Optimization

#### Field Selection
```
GET /users?fields=id,name,email
```

#### Compression
- Enable gzip/brotli compression
- Reduce payload size

#### Async Operations
```
POST /users/bulk
Response: 202 Accepted
Location: /jobs/abc-123

GET /jobs/abc-123
Response: { "status": "processing", "progress": 45 }
```

### 10. Idempotency & Reliability

#### Idempotency Keys

For non-idempotent operations (POST), use idempotency keys to prevent duplicate operations:

```
POST /payments
Content-Type: application/json
Idempotency-Key: 550e8400-e29b-41d4-a716-446655440000

{
  "amount": 1000,
  "currency": "USD",
  "description": "Payment for order #123"
}
```

**Implementation Guidelines:**
- **Client-side**: Generate unique UUID for each request
- **Server-side**: Store idempotency key with response for 24 hours
- **Duplicate detection**: Return same response (with status code) if duplicate key received
- **Scope**: Keys should be scoped to the endpoint and user

**Critical for:**
- Payment processing
- Resource creation (users, orders)
- State-changing operations
- Distributed systems with retries

**Example Response Storage:**
```json
{
  "idempotency_key": "550e8400-e29b-41d4-a716-446655440000",
  "status_code": 201,
  "response_body": { "id": "payment_123", "status": "succeeded" },
  "created_at": "2024-01-15T10:30:00Z",
  "expires_at": "2024-01-16T10:30:00Z"
}
```

#### Retry Strategies

**Client-side retry logic:**
- **Idempotent operations** (GET, PUT, DELETE): Safe to retry
- **Non-idempotent operations** (POST): Only retry with idempotency keys
- **Exponential backoff**: Wait 1s, 2s, 4s, 8s between retries
- **Max attempts**: Limit to 3-5 retries
- **Jitter**: Add randomness to prevent thundering herd

**Server responses to guide retries:**
- `503 Service Unavailable` + `Retry-After: 60` - Temporary outage
- `429 Too Many Requests` + `Retry-After: 3600` - Rate limited
- `408 Request Timeout` - Safe to retry
- `5xx errors` - Retry with backoff (except 501)

### 11. Webhooks & Event-Driven APIs

#### Webhook Registration

Allow clients to subscribe to events:

```
POST /webhooks
Content-Type: application/json

{
  "url": "https://client.example.com/webhook",
  "events": ["user.created", "user.updated", "order.completed"],
  "secret": "whsec_generated_by_server"
}

Response: 201 Created
{
  "data": {
    "id": "webhook_123",
    "url": "https://client.example.com/webhook",
    "events": ["user.created", "user.updated", "order.completed"],
    "status": "active",
    "createdAt": "2024-01-15T10:30:00Z"
  }
}
```

#### Webhook Delivery

**Request Format:**
```
POST https://client.example.com/webhook
Content-Type: application/json
X-Webhook-ID: evt_1234567890
X-Webhook-Signature: sha256=5d7b1e...
X-Webhook-Timestamp: 1640000000

{
  "event": "user.created",
  "data": {
    "id": "user_123",
    "email": "user@example.com",
    "createdAt": "2024-01-15T10:30:00Z"
  },
  "webhookId": "webhook_123"
}
```

#### Security (Signature Verification)

**Server-side (generate signature):**
```python
import hmac
import hashlib

def generate_signature(payload: str, secret: str) -> str:
    signature = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return f"sha256={signature}"
```

**Client-side (verify signature):**
```python
def verify_signature(payload: str, signature: str, secret: str) -> bool:
    expected = generate_signature(payload, secret)
    return hmac.compare_digest(expected, signature)
```

#### Retry & Delivery Guarantees

**Retry Strategy:**
- **Attempts**: 5 retries over 24 hours
- **Schedule**: Immediate, 5min, 30min, 2hr, 12hr
- **Success**: Any 2xx status code
- **Failure**: 4xx/5xx or timeout
- **Timeout**: 30 seconds per attempt

**Delivery Status:**
```
GET /webhooks/{id}/deliveries

{
  "data": [
    {
      "id": "delivery_123",
      "eventId": "evt_1234567890",
      "status": "succeeded",
      "statusCode": 200,
      "attempts": 1,
      "lastAttempt": "2024-01-15T10:30:00Z"
    }
  ]
}
```

**Best Practices:**
- **Idempotency**: Clients should handle duplicate deliveries
- **Acknowledgment**: Respond with 200 quickly, process asynchronously
- **Monitoring**: Track delivery success rates
- **Dead Letter Queue**: Store failed deliveries for manual retry

### 12. Documentation

#### OpenAPI/Swagger Specification
```yaml
openapi: 3.0.0
info:
  title: User API
  version: 1.0.0
paths:
  /users:
    get:
      summary: List users
      parameters:
        - name: limit
          in: query
          schema:
            type: integer
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/User'
components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: string
        email:
          type: string
```

#### Documentation Tools
- **Swagger UI**: Interactive API documentation
- **Redoc**: Beautiful API documentation
- **Postman**: API testing and documentation
- **API Blueprint**: High-level API description

#### Contract Testing

Ensure API implementation matches specification:

**Pact (Consumer-Driven Contracts)**
```javascript
// Consumer test (frontend)
const pact = new Pact({
  consumer: 'UserUI',
  provider: 'UserAPI'
});

await pact
  .addInteraction({
    state: 'user exists',
    uponReceiving: 'a request for user',
    withRequest: {
      method: 'GET',
      path: '/users/123'
    },
    willRespondWith: {
      status: 200,
      body: { id: '123', email: 'user@example.com' }
    }
  })
  .verify();
```

**Dredd (OpenAPI Validation)**
```bash
# Validate API implementation against OpenAPI spec
dredd openapi.yaml http://localhost:8000
```

**Postman/Newman**
```bash
# Run contract tests in CI/CD
newman run api-contract-tests.json --environment production.json
```

**Best Practices:**
- Run contract tests in CI/CD pipeline
- Version contracts alongside API versions
- Generate contracts from OpenAPI specs
- Test both request validation and response structure
- Include error scenarios (4xx, 5xx)

## API Security Best Practices

- [ ] Use HTTPS everywhere
- [ ] Implement authentication (JWT, OAuth)
- [ ] Validate all inputs (use schema validation: Pydantic, Zod)
- [ ] Sanitize outputs to prevent XSS
- [ ] Use parameterized queries to prevent SQL injection
- [ ] Implement rate limiting
- [ ] Use CORS properly
- [ ] Add security headers (CSP, X-Frame-Options, etc.)
- [ ] Don't expose sensitive data in responses
- [ ] Implement proper error handling (don't leak stack traces)
- [ ] Use API keys for service-to-service communication
- [ ] Implement request signing for critical operations
- [ ] Log security events
- [ ] Regularly audit and update dependencies

### PII & Data Privacy

- [ ] **Identify PII**: Name, email, phone, SSN, address, IP address, etc.
- [ ] **Mask in logs**: Replace sensitive data with `***` or hash values
  ```python
  # Good
  logger.info(f"User login attempt: email=***@{email.split('@')[1]}")

  # Bad
  logger.info(f"User login: {email}, password={password}")
  ```
- [ ] **Encrypt at rest**: PII in databases should be encrypted
- [ ] **Encrypt in transit**: Use TLS 1.2+ for all API calls
- [ ] **Minimize exposure**: Only return PII when absolutely necessary
- [ ] **Data retention policies**: Define and enforce data deletion schedules
- [ ] **GDPR/CCPA Compliance**:
  - Right to Access: `GET /users/{id}/data-export`
  - Right to Deletion: `DELETE /users/{id}` (hard delete + cascade)
  - Right to Portability: Provide data in JSON/CSV format
  - Right to Rectification: `PATCH /users/{id}`
- [ ] **Consent tracking**: Store consent timestamps and purposes
- [ ] **Data breach procedures**: Have incident response plan
- [ ] **Third-party sharing**: Document and get consent for data sharing

## API Design Checklist

- [ ] RESTful or GraphQL design chosen appropriately
- [ ] Consistent naming conventions
- [ ] Proper HTTP methods and status codes
- [ ] Comprehensive error handling
- [ ] Request/response validation (schema-based: Pydantic, Zod)
- [ ] Authentication and authorization (with granular scopes)
- [ ] Rate limiting implemented (with Retry-After headers)
- [ ] Pagination for list endpoints
- [ ] Versioning strategy
- [ ] Caching strategy (ETag, Last-Modified)
- [ ] Idempotency keys for non-idempotent operations
- [ ] Retry strategies documented
- [ ] Webhooks for event-driven integration (if applicable)
- [ ] API documentation (OpenAPI/GraphQL schema)
- [ ] Contract testing implemented (Pact, Dredd)
- [ ] Input validation and sanitization
- [ ] Security headers configured
- [ ] CORS configured properly
- [ ] PII identified and protected
- [ ] Data privacy compliance (GDPR/CCPA)
- [ ] Monitoring and logging (with PII masking)
- [ ] Performance optimization
- [ ] Backward compatibility considerations

## Common API Pitfalls

- Using verbs in URLs instead of nouns
- Inconsistent naming conventions
- Not using appropriate HTTP status codes
- Poor error messages (missing error codes, details)
- Missing pagination on list endpoints
- No rate limiting (or missing Retry-After headers)
- **Missing idempotency keys for critical operations** (payments, creation)
- Exposing internal implementation details
- Not versioning the API
- Missing or poor documentation
- Not validating inputs (or using ad-hoc validation instead of schemas)
- **Coarse-grained permissions** (admin/user instead of granular scopes)
- Returning too much data (no field selection/sparse fieldsets)
- Tight coupling between API and database schema
- Not considering backward compatibility
- **Logging PII without masking** (emails, passwords, SSN in plaintext logs)
- **No webhook signature verification** (insecure event delivery)
- Not implementing contract tests (spec drift from implementation)
- **Missing retry guidance** for clients (no exponential backoff docs)
- Ignoring GDPR/CCPA requirements (no data export/deletion endpoints)
