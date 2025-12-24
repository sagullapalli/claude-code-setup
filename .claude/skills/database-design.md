# Database Design Skill

This skill helps with designing efficient, scalable database schemas and data models.

## Usage

Use this skill when you need to:
- Design database schemas
- Optimize existing database structures
- Choose between SQL and NoSQL databases
- Plan data partitioning and sharding strategies
- Design indexes for query optimization

## Process

### 1. Requirements Analysis
- Identify data entities and relationships
- Understand access patterns and query requirements
- Determine data volume and growth projections
- Identify read vs write ratios

### 2. Database Selection

#### SQL Databases (PostgreSQL, MySQL, SQLite)
**Best for:**
- Structured data with clear relationships
- ACID compliance requirements
- Complex queries and joins
- Transactional systems

**Trade-offs:**
- Vertical scaling limitations
- Schema changes can be complex
- May require careful indexing for performance

#### NoSQL Databases (MongoDB, Cassandra, DynamoDB)
**Best for:**
- Unstructured or semi-structured data
- High write throughput
- Horizontal scaling needs
- Flexible schema requirements

**Trade-offs:**
- Limited query flexibility
- Eventual consistency in some cases
- No built-in joins

#### Vector Databases

**Option 1: PostgreSQL + pgvector (Recommended for <10M vectors)**
- Extension for existing Cloud SQL PostgreSQL
- No additional infrastructure required
- HNSW and IVFFlat indexing support
- Good performance for most RAG applications
- Cost-effective (uses existing database)

**Best for:**
- Small to medium vector collections (<10M)
- Projects already using PostgreSQL
- Avoiding additional infrastructure complexity

**Option 2: Dedicated Vector DB (Pinecone, Weaviate, Chroma)**
- Specialized for massive scale (>10M vectors)
- Optimized performance at scale
- Advanced features (hybrid search, filtering)
- Managed service options available

**Best for:**
- Large-scale vector search (>10M vectors)
- High-performance requirements
- Specialized vector search features

**Trade-offs:**
- Additional infrastructure and complexity
- Higher cost
- Another service to manage and monitor

### 3. Schema Design

#### Normalization
- **1NF**: Atomic values, no repeating groups
- **2NF**: No partial dependencies
- **3NF**: No transitive dependencies
- **BCNF**: Every determinant is a candidate key

**When to normalize:**
- Transactional systems (OLTP)
- Data integrity is critical
- Minimize data redundancy

**When to denormalize:**
- Read-heavy applications
- Performance optimization needed
- Analytical systems (OLAP)

#### Common Patterns
- **One-to-Many**: Foreign key in child table
- **Many-to-Many**: Junction/bridge table
- **One-to-One**: Share primary key or unique foreign key
- **Polymorphic**: Single table inheritance or class table inheritance

#### Multi-Tenancy Strategies

**CRITICAL for SaaS Applications**: Most modern web apps serve multiple customers (tenants). Choose the right isolation strategy early.

**Row-Level Isolation (Recommended for Most Cases)**
```sql
-- Add tenant_id to every table
CREATE TABLE documents (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL REFERENCES tenants(id),
  content TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index for tenant queries
CREATE INDEX idx_documents_tenant ON documents(tenant_id);
```

**Pros:**
- Simple to implement and manage
- Cost-effective (single database)
- Good query performance with proper indexing
- Easy to query across all tenants (analytics, admin)

**Cons:**
- Requires discipline (every query must filter by tenant_id)
- Risk of data leakage if query forgets tenant filter
- Single database limits (mitigated by Row Level Security)

**Use when:** Building most SaaS applications with standard security requirements.

**Schema-Per-Tenant**
```sql
-- Create separate schema for each tenant
CREATE SCHEMA tenant_acme;
CREATE SCHEMA tenant_globex;

-- Tables in each schema
CREATE TABLE tenant_acme.documents (...);
CREATE TABLE tenant_globex.documents (...);
```

**Pros:**
- Better isolation than row-level
- Easy to export single tenant data
- Can set different permissions per schema

**Cons:**
- More complex migrations (must run for each schema)
- Higher overhead (more database objects)
- Cross-tenant queries more difficult

**Use when:** Compliance requires stronger isolation, or tenants need custom schema changes.

**Database-Per-Tenant**
```sql
-- Completely separate databases
CREATE DATABASE tenant_acme;
CREATE DATABASE tenant_globex;
```

**Pros:**
- Maximum isolation and security
- Can be on different database servers
- Easy to meet strict compliance requirements
- Simple to backup/restore individual tenant

**Cons:**
- Highest complexity and cost
- Difficult to manage at scale (100+ tenants)
- Cross-tenant queries nearly impossible
- Schema migrations must run on every database

**Use when:** Enterprise customers require complete data isolation, strict compliance (HIPAA, SOC2), or contractual guarantees of separation.

**Best Practice:** Start with Row-Level Isolation + PostgreSQL Row Level Security (see Data Integrity section). Migrate to schema/database-per-tenant only when explicitly required.

#### Modern Web Patterns

**Soft Deletes**

Instead of `DELETE FROM users WHERE id = ?`, mark as deleted:

```sql
-- Add deleted_at column
ALTER TABLE users ADD COLUMN deleted_at TIMESTAMPTZ;

-- Create partial index for active users only
CREATE INDEX idx_users_active ON users(id) WHERE deleted_at IS NULL;

-- "Delete" a user
UPDATE users SET deleted_at = NOW() WHERE id = ?;

-- Query only active users
SELECT * FROM users WHERE deleted_at IS NULL;
```

**Benefits:**
- Data recovery possible
- Maintains referential integrity
- Audit trail of deletions

**Trade-offs:**
- Queries must remember to filter deleted records
- Unique constraints need adjustment
- Storage grows over time (need archive strategy)

**Audit Trails**

Track who changed what and when:

**Option 1: Application-Level Logging**
```python
# In FastAPI endpoint
audit_log.create(
    user_id=current_user.id,
    action="UPDATE",
    table_name="users",
    record_id=user.id,
    changes={"email": {"old": old_email, "new": new_email}}
)
```

**Option 2: Database Triggers** (PostgreSQL)
```sql
CREATE TABLE audit_log (
  id SERIAL PRIMARY KEY,
  table_name TEXT,
  record_id UUID,
  action TEXT,
  old_data JSONB,
  new_data JSONB,
  changed_by UUID,
  changed_at TIMESTAMPTZ DEFAULT NOW()
);

-- Trigger function to log changes
CREATE OR REPLACE FUNCTION audit_trigger() RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO audit_log (table_name, record_id, action, old_data, new_data)
  VALUES (TG_TABLE_NAME, NEW.id, TG_OP, row_to_json(OLD), row_to_json(NEW));
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Attach to table
CREATE TRIGGER users_audit AFTER INSERT OR UPDATE OR DELETE ON users
  FOR EACH ROW EXECUTE FUNCTION audit_trigger();
```

**Recommendation:** Use application-level for most cases (easier to debug, more flexible). Use triggers only when you need guaranteed audit trails that can't be bypassed.

**JSONB for Flexible Schema**

Use JSONB for metadata/settings that don't need to be queried frequently:

```sql
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email TEXT NOT NULL,
  name TEXT NOT NULL,
  -- Structured columns for queryable data
  status TEXT NOT NULL,
  created_at TIMESTAMPTZ,

  -- JSONB for flexible metadata
  preferences JSONB DEFAULT '{}',
  metadata JSONB DEFAULT '{}'
);

-- Create GIN index for JSONB queries
CREATE INDEX idx_users_preferences ON users USING GIN (preferences);

-- Query JSONB data
SELECT * FROM users WHERE preferences->>'theme' = 'dark';
SELECT * FROM users WHERE metadata @> '{"beta_features": true}';
```

**Benefits:**
- Avoid EAV (Entity-Attribute-Value) anti-pattern
- Schema flexibility without migrations
- Good performance with GIN indexes

**Trade-offs:**
- Less strict validation
- Harder to enforce constraints
- Can become dumping ground for unstructured data

**Best Practice:** Use JSONB for truly flexible data (user preferences, feature flags, metadata). Use structured columns for anything you need to query, filter, or join on.

### 4. Indexing Strategy

#### Index Types
- **B-Tree**: Default for most databases, good for range queries
- **Hash**: Fast equality lookups, no range queries
- **GiST/GIN**: Full-text search, JSON data (PostgreSQL)
- **Covering Index**: Include all columns needed for a query

#### Indexing Best Practices
- Index foreign keys used in joins
- Index columns used in WHERE clauses
- Index columns used in ORDER BY
- Avoid over-indexing (impacts write performance)
- Use composite indexes for multi-column queries
- Monitor index usage and remove unused indexes

**Partial Indexes** (PostgreSQL-specific, high-impact)

Index only the rows you actually query:

```sql
-- Only index active users (saves space, faster lookups)
CREATE INDEX idx_users_active ON users(email) WHERE deleted_at IS NULL;

-- Only index pending tasks
CREATE INDEX idx_tasks_pending ON tasks(created_at) WHERE status = 'pending';

-- Only index recent records
CREATE INDEX idx_events_recent ON events(created_at)
  WHERE created_at > NOW() - INTERVAL '30 days';
```

**Benefits:**
- Smaller index size (faster, less storage)
- Faster writes (fewer index updates)
- Perfect for soft deletes, status-based queries, time-based filtering

**Composite Index Left-to-Right Rule**

Composite indexes work left-to-right. An index on `(tenant_id, created_at)` can be used for:
- `WHERE tenant_id = ?` ✅
- `WHERE tenant_id = ? AND created_at > ?` ✅
- `WHERE created_at > ?` ❌ (index not used)

**Don't create redundant indexes:**
- If you have `(tenant_id, created_at)`, you DON'T need `(tenant_id)` alone
- If you need `(created_at)` alone, create a separate index

**Example:**
```sql
-- Good: Single composite index
CREATE INDEX idx_documents_tenant_date ON documents(tenant_id, created_at);

-- Bad: Redundant index (already covered by composite)
CREATE INDEX idx_documents_tenant ON documents(tenant_id);

-- Good: Separate index if you query by date alone
CREATE INDEX idx_documents_date ON documents(created_at);

### 5. Performance Optimization

#### Query Optimization
- Use EXPLAIN/EXPLAIN ANALYZE to understand query plans
- Avoid SELECT *, fetch only needed columns
- Use appropriate JOIN types
- Limit result sets with pagination
- Use prepared statements to prevent SQL injection

#### ORM Performance Pitfalls

**The N+1 Query Problem** (Most Common Performance Killer)

This happens when an ORM fetches a list of objects, then makes separate queries for related data.

**Bad Example** (Makes N+1 queries):
```python
from sqlalchemy.orm import Session

# Fetches all users (1 query)
users = db.query(User).all()

# Then fetches posts for EACH user (N queries)
for user in users:
    print(f"{user.name} has {len(user.posts)} posts")  # Separate query per user!

# Result: 1 + 100 = 101 queries if you have 100 users
```

**Good Example** (Makes 1-2 queries with eager loading):
```python
from sqlalchemy.orm import Session, joinedload

# Eager load posts in a single query with JOIN
users = db.query(User).options(joinedload(User.posts)).all()

for user in users:
    print(f"{user.name} has {len(user.posts)} posts")  # No additional query!

# Result: 1-2 queries total (depending on relationship type)
```

**SQLAlchemy Loading Strategies:**

1. **`joinedload()`** - Use LEFT OUTER JOIN (single query)
   ```python
   # Best for one-to-one or small one-to-many
   users = db.query(User).options(joinedload(User.profile)).all()
   ```

2. **`selectinload()`** - Separate SELECT IN query (2 queries total)
   ```python
   # Best for one-to-many or many-to-many (avoids duplicate rows)
   users = db.query(User).options(selectinload(User.posts)).all()
   ```

3. **`subqueryload()`** - Uses subquery (2 queries total)
   ```python
   # Alternative to selectinload
   users = db.query(User).options(subqueryload(User.posts)).all()
   ```

**How to Detect N+1 Queries:**

1. **Enable SQLAlchemy query logging** (development):
   ```python
   import logging
   logging.basicConfig()
   logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
   ```

2. **Use database monitoring** (Cloud SQL Query Insights in GCP)

3. **Watch for patterns**: Any loop that accesses a relationship is suspicious

**Rule of Thumb:**
- If you access a relationship in a loop → use eager loading
- If you only need the parent object → lazy loading is fine
- Always profile in production-like conditions

#### Caching Strategies
- **Application-Level Cache**: Redis, Memcached
- **Query Result Cache**: Cache frequently accessed queries
- **Database Query Cache**: Built-in database caching
- **CDN**: For static content and assets

#### Connection Pooling

**CRITICAL for Cloud Run / Serverless Environments**

Traditional connection pooling advice (10-20 connections) **DOES NOT WORK** for serverless platforms (Cloud Run, Lambda, Vercel).

**The Problem:**
- Each Cloud Run instance creates its own connection pool
- With auto-scaling, you get: `instances × pool_size = total connections`
- Cloud SQL default max connections: 100
- Example: 20 instances × 5 connections = 100 (maxed out immediately)

**Solution 1: Cloud SQL Auth Proxy (Recommended for GCP)**

```python
# Use Cloud SQL Proxy with connection pooling
from sqlalchemy import create_engine

# Cloud Run automatically provides /cloudsql socket
engine = create_engine(
    "postgresql+psycopg2://user:pass@/dbname",
    connect_args={
        "host": "/cloudsql/PROJECT:REGION:INSTANCE",
    },
    # Small pool per instance (Cloud Run auto-scales instances)
    pool_size=5,
    max_overflow=2,
    pool_pre_ping=True,  # Handle stale connections
    pool_recycle=3600,   # Recycle connections every hour
)
```

**Solution 2: External Connection Pooler (PgBouncer)**

Deploy PgBouncer as a separate Cloud Run service:

```yaml
# pgbouncer.yaml (Cloud Run)
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: pgbouncer
spec:
  template:
    spec:
      containers:
      - image: pgbouncer/pgbouncer
        env:
        - name: DATABASES_HOST
          value: /cloudsql/PROJECT:REGION:INSTANCE
        - name: POOL_MODE
          value: transaction  # Connection per transaction, not per session
```

Then connect your app to PgBouncer instead of Cloud SQL directly.

**Solution 3: HTTP-Based Database Drivers** (Emerging)

For extremely short-lived functions (Vercel Edge, Cloudflare Workers):

```typescript
// Use HTTP-based driver (no persistent connections)
import { Client } from '@planetscale/database'

const client = new Client({
  url: process.env.DATABASE_URL
})

// Each query is a separate HTTP request (no connection pooling needed)
const result = await client.execute('SELECT * FROM users WHERE id = ?', [id])
```

**Traditional Server Environments (Non-Serverless)**

If you're using a single server or VM (not Cloud Run):

```python
# Standard connection pooling
engine = create_engine(
    "postgresql://user:pass@host/dbname",
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
)
```

**Recommended Settings by Environment:**

| Environment | Pool Size | Max Overflow | Strategy |
|-------------|-----------|--------------|----------|
| Cloud Run | 5 | 2 | Cloud SQL Proxy + small pool per instance |
| AWS Lambda | 1-2 | 0 | PgBouncer or Aurora Serverless Data API |
| Traditional Server | 10-20 | 10-20 | Standard SQLAlchemy pooling |
| Vercel/CF Workers | N/A | N/A | HTTP-based driver (no pooling) |

**Monitoring Connection Usage:**

```sql
-- Check current connections (PostgreSQL)
SELECT count(*) FROM pg_stat_activity WHERE datname = 'your_database';

-- Check max connections limit
SHOW max_connections;

-- Find connection leaks (long-running connections)
SELECT pid, usename, application_name, client_addr, state, state_change
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY state_change;
```

**Common Mistakes:**
- Using default pool_size=10 on Cloud Run (exhausts connections quickly)
- Not setting `pool_pre_ping=True` (stale connections cause errors)
- Not setting `pool_recycle` (connections hang forever)
- Connecting directly to Cloud SQL without Cloud SQL Proxy (no connection reuse)

### 6. Scalability Patterns

**IMPORTANT: Do these IN ORDER. Don't skip steps.**

#### Step 1: Optimize Queries (Do This First)
- Fix N+1 queries (see ORM section)
- Add missing indexes (use EXPLAIN ANALYZE)
- Remove unnecessary SELECT *
- Add pagination/limits to large result sets

**Most "slow database" problems are actually "bad query" problems.**

#### Step 2: Vertical Scaling (Still Simple)
- Increase Cloud SQL CPU, RAM, storage
- GCP makes this easy (no downtime with HA instances)
- Cost-effective up to a point
- Can get expensive at extreme scale

**Example Cloud SQL sizing:**
- Small app: db-custom-1-3840 (1 vCPU, 3.75 GB RAM)
- Medium app: db-custom-4-16384 (4 vCPU, 16 GB RAM)
- Large app: db-custom-8-32768 (8 vCPU, 32 GB RAM)

#### Step 3: Read Replicas (For Read-Heavy Apps)

**When to use:**
- Read/write ratio > 70% reads
- You've maxed out CPU on primary
- Specific features need separate read capacity (analytics, reporting)

**Cloud SQL Read Replicas:**
```sql
-- Read queries go to replica
SELECT * FROM users WHERE status = 'active';

-- Write queries go to primary
INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com');
```

**Implementation:**
```python
# FastAPI with read/write split
from sqlalchemy import create_engine

# Primary for writes
primary_engine = create_engine("postgresql://user:pass@primary-host/db")

# Replica for reads
replica_engine = create_engine("postgresql://user:pass@replica-host/db")

# Use in application
def get_users():
    return replica_engine.execute("SELECT * FROM users")

def create_user(name):
    return primary_engine.execute("INSERT INTO users (name) VALUES (?)", name)
```

**Trade-offs:**
- Eventual consistency (replica lag, usually <1 second)
- Added complexity in application code
- Cost (replica instance costs same as primary)

#### Step 4: Caching (Before Sharding!)

Add Redis/Memcached for frequently accessed data:

```python
from redis import Redis
import json

cache = Redis(host='localhost', port=6379)

def get_user(user_id):
    # Check cache first
    cached = cache.get(f"user:{user_id}")
    if cached:
        return json.loads(cached)

    # Cache miss - query database
    user = db.query(User).filter(User.id == user_id).first()
    cache.setex(f"user:{user_id}", 300, json.dumps(user))  # 5 min TTL
    return user
```

#### Step 5: Table Partitioning (Large Tables Only)

**When to use:**
- Single table > 100 GB
- Time-series data (logs, events, metrics)
- Clear partition key (date, region, tenant_id)

**PostgreSQL Native Partitioning:**
```sql
-- Partition by date range
CREATE TABLE events (
  id UUID,
  user_id UUID,
  event_type TEXT,
  created_at TIMESTAMPTZ
) PARTITION BY RANGE (created_at);

-- Create partitions for each month
CREATE TABLE events_2025_01 PARTITION OF events
  FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

CREATE TABLE events_2025_02 PARTITION OF events
  FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');
```

**Benefits:**
- Faster queries (only scans relevant partitions)
- Easier maintenance (drop old partitions instead of DELETE)
- Better index performance (smaller indexes per partition)

**Trade-offs:**
- Requires partition key in WHERE clauses
- More database objects to manage
- Partition creation must be automated

#### Step 6: Managed Serverless Scaling (Consider Before Sharding)

**GCP AlloyDB** (PostgreSQL-compatible, auto-scaling):
- Auto-scales read replicas based on load
- Columnar engine for analytics
- No sharding needed for most workloads

**Alternatives (if leaving GCP):**
- AWS Aurora Serverless (auto-scales)
- PlanetScale (auto-scales, Vitess-based)
- CockroachDB (distributed PostgreSQL)

#### Step 7: Sharding ⚠️ LAST RESORT

**Only consider sharding if:**
- You've done steps 1-6
- You're handling >10M transactions/day
- Single database can't handle write volume
- You have strong technical team (sharding is complex)

**Sharding = Partitioning data across multiple separate databases**

**Common Sharding Strategies:**

1. **Hash-based** (Most common)
   ```python
   shard = hash(user_id) % num_shards
   db = shards[shard]
   ```

2. **Range-based** (tenant_id, user_id ranges)
   ```python
   if user_id < 1000000:
       db = shard_0
   elif user_id < 2000000:
       db = shard_1
   ```

3. **Geo-based** (by region)
   ```python
   if user.region == 'us-east':
       db = us_east_shard
   elif user.region == 'europe':
       db = europe_shard
   ```

**Massive Complexity Added:**
- ❌ No cross-shard JOINs
- ❌ No cross-shard transactions
- ❌ Difficult to rebalance shards
- ❌ Application must route queries to correct shard
- ❌ Reporting/analytics becomes extremely complex

**Better Alternative:**
Use a distributed database (CockroachDB, Spanner) that handles sharding automatically.

### 7. Data Integrity

#### Constraints
- **Primary Key**: Unique identifier
- **Foreign Key**: Referential integrity
- **Unique**: No duplicates
- **Check**: Custom validation rules
- **Not Null**: Required fields

#### Transactions
- Use ACID transactions for critical operations
- Keep transactions short
- Handle deadlocks gracefully
- Use appropriate isolation levels

#### Row Level Security (PostgreSQL)

**CRITICAL for Multi-Tenant SaaS Applications**

Row Level Security (RLS) enforces tenant isolation at the database level, preventing data leakage even if application code forgets to filter by `tenant_id`.

**Basic RLS Setup:**

```sql
-- 1. Enable RLS on table
CREATE TABLE documents (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL REFERENCES tenants(id),
  title TEXT,
  content TEXT
);

ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- 2. Create policy: users can only see their tenant's data
CREATE POLICY tenant_isolation ON documents
  USING (tenant_id = current_setting('app.tenant_id')::uuid);

-- 3. Create policy for INSERT (must set tenant_id to session tenant)
CREATE POLICY tenant_isolation_insert ON documents
  FOR INSERT
  WITH CHECK (tenant_id = current_setting('app.tenant_id')::uuid);
```

**Application Integration (FastAPI + SQLAlchemy):**

```python
from sqlalchemy import event, text
from fastapi import Depends

def get_current_tenant(request: Request) -> str:
    # Extract tenant from JWT, subdomain, or header
    return request.state.tenant_id

@app.middleware("http")
async def set_tenant_context(request: Request, call_next):
    tenant_id = get_current_tenant(request)

    # Set tenant context for this database session
    db = SessionLocal()
    try:
        db.execute(text(f"SET app.tenant_id = '{tenant_id}'"))
        request.state.db = db
        response = await call_next(request)
        return response
    finally:
        db.close()

# Now all queries automatically filter by tenant_id
@app.get("/documents")
def get_documents(db: Session = Depends(get_db)):
    # This query is automatically filtered by RLS policy
    return db.query(Document).all()
```

**Benefits:**
- **Defense in depth**: Even if code forgets `WHERE tenant_id = ?`, RLS blocks it
- **Prevents data leakage**: Database enforces isolation
- **Audit compliance**: Can prove tenant separation at DB level

**Trade-offs:**
- PostgreSQL-specific (not portable to MySQL)
- Slight performance overhead (minimal, usually <1%)
- Must set session context on every connection (handle in connection pool)
- Can be confusing when debugging (queries silently filtered)

**Best Practice:**
- Use RLS as a safety net, NOT as a replacement for proper queries
- Still filter by `tenant_id` in application queries (explicit is better)
- Create indexes on tenant_id for performance
- Test RLS policies thoroughly (ensure they actually work)

**Testing RLS Policies:**

```sql
-- Test as admin (should see all data)
SET app.tenant_id = '';
SELECT count(*) FROM documents;  -- Should see all documents

-- Test as tenant A
SET app.tenant_id = 'tenant-a-uuid';
SELECT count(*) FROM documents;  -- Should only see tenant A's documents

-- Test insertion (should only allow tenant A's ID)
INSERT INTO documents (id, tenant_id, title)
VALUES (gen_random_uuid(), 'tenant-b-uuid', 'Test');  -- Should FAIL with CHECK violation
```

#### Timezone Handling

**ALWAYS use `TIMESTAMPTZ` (timestamp with timezone) in PostgreSQL**

```sql
-- Good: Stores UTC time + timezone info
CREATE TABLE users (
  id UUID PRIMARY KEY,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Bad: Loses timezone information
CREATE TABLE users (
  created_at TIMESTAMP DEFAULT NOW()  -- DON'T DO THIS
);
```

**Best Practices:**

1. **Store in UTC**
   ```python
   from datetime import datetime, timezone

   # Always use timezone-aware datetimes
   now = datetime.now(timezone.utc)

   # SQLAlchemy models
   class User(Base):
       created_at: Mapped[datetime] = mapped_column(
           DateTime(timezone=True),  # Ensures TIMESTAMPTZ
           default=lambda: datetime.now(timezone.utc)
       )
   ```

2. **Display in User's Timezone**
   ```python
   from zoneinfo import ZoneInfo

   # Convert UTC to user's timezone for display
   utc_time = user.created_at
   user_tz = ZoneInfo(user.timezone)  # e.g., "America/New_York"
   local_time = utc_time.astimezone(user_tz)
   ```

3. **API Responses**
   ```python
   # FastAPI automatically serializes to ISO 8601 with timezone
   class UserResponse(BaseModel):
       id: UUID
       created_at: datetime  # Returns "2025-01-15T14:30:00Z"
   ```

**Common Mistakes:**
- ❌ Using `TIMESTAMP` instead of `TIMESTAMPTZ`
- ❌ Storing timezone as separate column
- ❌ Converting to local time before storing
- ❌ Not handling daylight saving time transitions

**Migration from TIMESTAMP to TIMESTAMPTZ:**

```sql
-- Safe migration (assumes existing timestamps are UTC)
ALTER TABLE users
  ALTER COLUMN created_at TYPE TIMESTAMPTZ
  USING created_at AT TIME ZONE 'UTC';
```

### 8. Migration Strategy

#### Schema Migrations
- Version control schema changes
- Use migration tools (Flyway, Liquibase, Alembic)
- Test migrations in staging
- Plan rollback strategies
- Avoid destructive changes in production

#### Data Migrations
- Plan for data transformation
- Handle backward compatibility
- Implement in phases if large-scale
- Verify data integrity after migration

### 9. GCP Cloud SQL Best Practices

**Our Default Stack: Cloud SQL for PostgreSQL on GCP**

#### Connection Methods

**1. Cloud SQL Auth Proxy (Recommended)**

```python
# Connects via Unix socket (most secure, no IP whitelisting needed)
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql+psycopg2://user:password@/dbname",
    connect_args={
        "host": "/cloudsql/PROJECT_ID:REGION:INSTANCE_NAME"
    }
)
```

**Benefits:**
- Automatic IAM authentication (no password in env vars)
- Encrypted connection
- Works from Cloud Run, GKE, Cloud Functions
- No VPC peering needed

**2. Private IP (For VPC-connected services)**

```python
# Requires VPC peering or Serverless VPC Access Connector
engine = create_engine(
    "postgresql://user:password@10.x.x.x:5432/dbname"
)
```

**Use when:** Connecting from GKE or Compute Engine in same VPC.

#### High Availability Configuration

```bash
# Enable HA when creating instance (recommended for production)
gcloud sql instances create my-instance \
  --database-version=POSTGRES_15 \
  --tier=db-custom-2-8192 \
  --region=us-central1 \
  --availability-type=REGIONAL  # Enables HA with automatic failover
```

**HA Benefits:**
- Automatic failover (<60 seconds downtime)
- Synchronous replication to standby
- Covers zone failures
- Cost: 2x instance price

#### Automated Backups

```bash
# Enable automated backups (4am daily, 7-day retention)
gcloud sql instances patch my-instance \
  --backup-start-time=04:00 \
  --backup-location=us \
  --retained-backups-count=7

# Point-in-time recovery (requires binary logging)
gcloud sql instances patch my-instance \
  --enable-bin-log \
  --retained-transaction-log-days=7
```

**IMPORTANT:** Test your restore process regularly!

```bash
# Test restore to new instance
gcloud sql backups restore BACKUP_ID \
  --backup-instance=source-instance \
  --restore-instance=test-restore-instance
```

#### Secrets Management

**Never hardcode database credentials!**

**Option 1: Secret Manager (Recommended)**

```python
from google.cloud import secretmanager

def get_db_password():
    client = secretmanager.SecretManagerServiceClient()
    name = "projects/PROJECT_ID/secrets/db-password/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

# Use in connection string
db_url = f"postgresql://user:{get_db_password()}@host/dbname"
```

**Option 2: IAM Authentication (No Password Needed)**

```python
from google.cloud.sql.connector import Connector

connector = Connector()

def getconn():
    conn = connector.connect(
        "PROJECT:REGION:INSTANCE",
        "pg8000",
        user="my-user@project.iam",
        db="mydb",
        enable_iam_auth=True  # Uses service account, no password!
    )
    return conn

engine = create_engine(
    "postgresql+pg8000://",
    creator=getconn,
)
```

#### Monitoring & Alerts

**Enable Query Insights:**

```bash
gcloud sql instances patch my-instance \
  --insights-config-query-insights-enabled \
  --insights-config-query-string-length=1024 \
  --insights-config-record-application-tags
```

**View in console:** Cloud SQL → Instance → Query Insights

**Key metrics to monitor:**
- CPU utilization (alert if >80% for 5 min)
- Memory utilization (alert if >90%)
- Active connections (alert if approaching max_connections)
- Disk utilization (alert if >80%)
- Replication lag (alert if >5 seconds)

**Set up alerts:**

```bash
# Example: Alert on high CPU
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="Cloud SQL High CPU" \
  --condition-display-name="CPU > 80%" \
  --condition-threshold-value=0.8 \
  --condition-threshold-duration=300s
```

#### Performance Optimization (Cloud SQL-specific)

1. **Enable database flags for performance:**

```bash
gcloud sql instances patch my-instance \
  --database-flags=max_connections=100,shared_buffers=256MB,effective_cache_size=1GB,work_mem=16MB
```

2. **Use appropriate machine type:**

```bash
# Development: db-f1-micro (free tier eligible)
# Staging: db-custom-2-8192 (2 vCPU, 8 GB RAM)
# Production: db-custom-4-16384 (4 vCPU, 16 GB RAM)
```

3. **Enable automatic storage increase:**

```bash
gcloud sql instances patch my-instance \
  --storage-auto-increase \
  --storage-auto-increase-limit=500
```

#### Maintenance Windows

```bash
# Set maintenance window to Sunday 3-4am
gcloud sql instances patch my-instance \
  --maintenance-window-day=SUN \
  --maintenance-window-hour=3 \
  --maintenance-release-channel=production
```

#### Cost Optimization

1. **Use committed use discounts** (1-year or 3-year)
2. **Right-size instances** (monitor CPU/memory usage)
3. **Delete unused read replicas**
4. **Use Cloud SQL Proxy** (avoid data egress charges)
5. **Archive old data** (reduce storage costs)

```sql
-- Example: Archive events older than 90 days
DELETE FROM events WHERE created_at < NOW() - INTERVAL '90 days';
```

## Best Practices Checklist

### Schema Design
- [ ] Document schema design decisions in ADRs
- [ ] Use consistent naming conventions (snake_case for PostgreSQL)
- [ ] Choose multi-tenancy strategy (row-level, schema-per-tenant, db-per-tenant)
- [ ] Use `TIMESTAMPTZ` for all datetime columns (never `TIMESTAMP`)
- [ ] Add `tenant_id` to all tables (for row-level multi-tenancy)
- [ ] Plan for soft deletes (add `deleted_at TIMESTAMPTZ`)
- [ ] Use JSONB for flexible metadata (not EAV pattern)

### Indexes & Performance
- [ ] Add indexes to foreign keys
- [ ] Add indexes to columns in WHERE clauses
- [ ] Use partial indexes for filtered queries (e.g., `WHERE deleted_at IS NULL`)
- [ ] Create composite indexes for multi-column queries
- [ ] Avoid N+1 queries (use eager loading with SQLAlchemy)
- [ ] Monitor index usage and remove unused indexes

### Security & Integrity
- [ ] Enable Row Level Security (RLS) for multi-tenant tables
- [ ] Set up foreign key constraints
- [ ] Use constraints (NOT NULL, UNIQUE, CHECK)
- [ ] Store secrets in Secret Manager (not env vars)
- [ ] Use IAM authentication when possible (no passwords)
- [ ] Enable SSL/TLS connections

### GCP Cloud SQL
- [ ] Use Cloud SQL Auth Proxy for connections
- [ ] Enable High Availability (production)
- [ ] Configure automated backups (daily)
- [ ] Enable point-in-time recovery
- [ ] Set up Query Insights monitoring
- [ ] Configure alerts (CPU, memory, connections, disk)
- [ ] Set maintenance window (low-traffic hours)

### Connection Pooling
- [ ] Use small pool size for Cloud Run (pool_size=5, max_overflow=2)
- [ ] Set `pool_pre_ping=True` (handle stale connections)
- [ ] Set `pool_recycle=3600` (recycle connections hourly)
- [ ] Monitor active connections

### Data Integrity & Migration
- [ ] Use transactions for critical operations
- [ ] Version control schema changes (Alembic)
- [ ] Test migrations in staging first
- [ ] Plan rollback strategies
- [ ] Verify data integrity after migrations

### Scalability & Growth
- [ ] Plan for data growth (monitoring trends)
- [ ] Implement pagination for large result sets
- [ ] Consider read replicas (if read-heavy)
- [ ] Archive old data (reduce storage costs)
- [ ] Test with realistic data volumes

### Monitoring & Operations
- [ ] Monitor query performance (EXPLAIN ANALYZE)
- [ ] Enable SQLAlchemy query logging (development)
- [ ] Track slow queries (Cloud SQL Query Insights)
- [ ] Monitor connection pool exhaustion
- [ ] Test backup restore process regularly

## Common Pitfalls to Avoid

### Schema Design Mistakes
- ❌ **Using `TIMESTAMP` instead of `TIMESTAMPTZ`** - Always use timezone-aware timestamps
- ❌ **Not planning for multi-tenancy** - Add `tenant_id` from day one if building SaaS
- ❌ **Over-normalization** - Don't normalize to the point of unreadable queries
- ❌ **Using EAV pattern** - Use JSONB instead for flexible schema
- ❌ **Storing timezone as separate column** - Use TIMESTAMPTZ, store in UTC
- ❌ **Poor naming conventions** - Use snake_case for PostgreSQL, be consistent

### Performance Killers
- ❌ **N+1 Query Problem** - Most common ORM performance issue. Use eager loading!
- ❌ **Missing indexes on foreign keys** - Always index columns used in JOINs
- ❌ **Missing indexes on tenant_id** - Critical for multi-tenant queries
- ❌ **Not using partial indexes** - Waste space indexing deleted rows
- ❌ **SELECT * in production code** - Fetch only needed columns
- ❌ **No pagination** - Never return unbounded result sets
- ❌ **Not monitoring query performance** - Use EXPLAIN ANALYZE regularly

### Multi-Tenancy Mistakes
- ❌ **Forgetting to filter by tenant_id** - Use RLS as safety net
- ❌ **Not testing tenant isolation** - Verify no cross-tenant data leakage
- ❌ **Missing tenant_id in indexes** - Composite indexes should start with tenant_id
- ❌ **Hardcoding tenant ID** - Always derive from auth context

### Serverless / Cloud Run Mistakes
- ❌ **Using default connection pool size** - pool_size=10 on Cloud Run exhausts connections
- ❌ **Not using Cloud SQL Proxy** - Direct connections don't pool properly
- ❌ **Not setting pool_pre_ping=True** - Stale connections cause errors
- ❌ **Not setting pool_recycle** - Long-lived connections hang forever
- ❌ **Connecting without IAM auth** - Hardcoded passwords in code

### Security Mistakes
- ❌ **Hardcoding database credentials** - Use Secret Manager or IAM auth
- ❌ **Not enabling Row Level Security** - RLS prevents data leakage bugs
- ❌ **String concatenation for SQL** - Always use parameterized queries
- ❌ **Exposing database errors to users** - Log detailed errors, show generic messages
- ❌ **Not encrypting sensitive columns** - Use pgcrypto for PII

### Scalability Mistakes
- ❌ **Jumping to sharding immediately** - Optimize queries first!
- ❌ **Sharding before 10M+ transactions/day** - Premature complexity
- ❌ **Not using read replicas for read-heavy apps** - Easy horizontal scaling
- ❌ **Not caching frequently accessed data** - Redis before sharding
- ❌ **Ignoring Cloud SQL performance tiers** - Vertical scaling is simple

### Migration Mistakes
- ❌ **Not testing migrations in staging** - Always test before production
- ❌ **Destructive migrations without backups** - Take snapshot first
- ❌ **Not planning rollback** - Every migration needs rollback plan
- ❌ **Running long migrations during peak hours** - Use maintenance window
- ❌ **Not using migration tools** - Use Alembic, don't write raw SQL scripts

### Monitoring & Operations
- ❌ **Not monitoring database** - Set up alerts BEFORE problems occur
- ❌ **Not testing backup restore** - Backups are useless if you can't restore
- ❌ **No query logging in development** - Enable SQLAlchemy logging to catch issues
- ❌ **Not using Cloud SQL Query Insights** - Free tool for finding slow queries
- ❌ **No connection pool monitoring** - Watch for pool exhaustion

### Data Integrity Mistakes
- ❌ **Not using transactions** - Use ACID for critical operations
- ❌ **Long-running transactions** - Keep transactions short to avoid locks
- ❌ **Not handling deadlocks** - Implement retry logic
- ❌ **Soft delete without index** - Index `WHERE deleted_at IS NULL`
- ❌ **Not validating data at database level** - Use CHECK constraints

### Cost Mistakes (GCP)
- ❌ **Not using committed use discounts** - 1-year or 3-year saves 37-52%
- ❌ **Over-provisioned instances** - Right-size based on monitoring
- ❌ **Not archiving old data** - Storage costs add up
- ❌ **Unused read replicas running** - Delete if not used
- ❌ **Not enabling auto storage increase** - Manual increases cost more

### Documentation & Process
- ❌ **Not documenting schema decisions** - Write ADRs for major choices
- ❌ **No schema diagrams** - Visual representation helps onboarding
- ❌ **Not reviewing database changes** - Require review on schema changes
- ❌ **No load testing** - Test with production-like data volumes
