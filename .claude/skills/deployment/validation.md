# Deployment Validation

**Last Updated**: 2025-12-11

This skill provides comprehensive pre-deployment and post-deployment validation checklists to ensure safe, efficient deployments to GCP.

**Purpose**: Catch 80% of deployment issues in 20% of the time (locally, before Cloud Build).

---

## Table of Contents

1. [Pre-Deployment Validation](#pre-deployment-validation)
2. [Docker Build Validation](#docker-build-validation)
3. [IAM Permission Verification](#iam-permission-verification)
4. [Environment Variable Validation](#environment-variable-validation)
5. [Post-Deployment Health Checks](#post-deployment-health-checks)
6. [Complete Deployment Workflow](#complete-deployment-workflow)
7. [Validation Metrics](#validation-metrics)

---

## Pre-Deployment Validation

### Complete Pre-Deployment Checklist

Run through this checklist BEFORE submitting to Cloud Build:

```bash
# === PHASE 1: CODE QUALITY ===
# 1. Run tests locally
cd backend
pytest --cov=app --cov-report=term-missing
# Verify tests pass (coverage gate optional for staging)

# 2. Type checking (if using mypy)
mypy app/

# 3. Linting
black app/ --check
ruff app/

# === PHASE 2: DOCKER VALIDATION ===
# 4. Backend Docker build validation
cd backend
docker build -t test-backend .
# Should complete without errors

# 5. Backend Docker run validation
docker run -d --name test-backend -p 8000:8000 \
  -e OAUTH_CLIENT_ID=dummy \
  -e OAUTH_CLIENT_SECRET=dummy \
  -e GCS_BUCKET_NAME=test-bucket \
  -e GTM_TEMPLATES_BUCKET_NAME=test-bucket \
  -e GCP_PROJECT_ID=test-project \
  test-backend

# Wait 5 seconds for startup
sleep 5

# Test health endpoint
curl http://localhost:8000/api/v1/health
# Expected: {"status": "healthy"}

# Clean up
docker stop test-backend && docker rm test-backend

# 6. Frontend Docker build validation
cd frontend-v2
npm run build  # Verify Vite build succeeds
docker build -t test-frontend .

# 7. Frontend Docker run validation
docker run -d --name test-frontend -p 8080:8080 test-frontend
sleep 5
curl http://localhost:8080/health
# Expected: {"status": "healthy"}

# Clean up
docker stop test-frontend && docker rm test-frontend

# === PHASE 3: DEPENDENCY VALIDATION ===
# 8. Node.js version alignment check
cat frontend-v2/package.json | jq '.engines.node'
grep "FROM node:" frontend-v2/Dockerfile
# Ensure versions match (e.g., ">=20" → FROM node:20-alpine)

# 9. Python version alignment check
cat backend/pyproject.toml | grep "python"  # or requirements.txt
grep "FROM python:" backend/Dockerfile
# Ensure versions match (e.g., ">=3.11" → FROM python:3.11-slim)

# === PHASE 4: CLOUD BUILD VALIDATION ===
# 10. Validate cloudbuild.yaml syntax
gcloud builds submit --config=cloudbuild.yaml \
  --substitutions=SHORT_SHA=test \
  --dry-run

# === PHASE 5: IAM & TERRAFORM ===
# 11. If Terraform changes were made, apply and WAIT
cd terraform
terraform plan  # Review changes
terraform apply

# CRITICAL: Wait for IAM propagation
echo "⏳ Waiting 90 seconds for IAM propagation..."
sleep 90

# === PHASE 6: READY TO DEPLOY ===
# 12. Submit to Cloud Build with correct substitutions
cd ..  # Back to project root
gcloud builds submit --config=cloudbuild.yaml \
  --substitutions=SHORT_SHA=$(git rev-parse --short HEAD)
```

### Quick Validation (Minimal - 5 minutes)

If you've already validated Docker builds before (no Dockerfile changes):

```bash
# 1. Run tests
pytest --cov=app

# 2. Check for Terraform changes
cd terraform && terraform plan
# If IAM changes: terraform apply && sleep 90

# 3. Submit to Cloud Build
gcloud builds submit --config=cloudbuild.yaml \
  --substitutions=SHORT_SHA=$(git rev-parse --short HEAD)
```

---

## Docker Build Validation

### Why This Matters

Catches 80% of build failures before Cloud Build (saves 30+ minutes).

**Time Investment**:
- Local Docker build: 2-5 minutes
- Cloud Build: 8-10 minutes per submission

**Efficiency Comparison**:
- **Without local validation**: 6 × 8 min = 48 min (wasted on Cloud Build failures)
- **With local validation**: 15 min local testing + 1 × 8 min = 23 min total

**Time Saved**: 25-30 minutes per deployment (50% faster)

### Backend Validation Script

```bash
#!/bin/bash
# backend/validate-docker.sh

set -e  # Exit on error

echo "🔨 Building backend Docker image..."
docker build -t test-backend .

echo "🚀 Starting backend container..."
docker run -d --name test-backend -p 8000:8000 \
  -e OAUTH_CLIENT_ID=dummy \
  -e OAUTH_CLIENT_SECRET=dummy \
  -e GCS_BUCKET_NAME=test-bucket \
  -e GTM_TEMPLATES_BUCKET_NAME=test-bucket \
  -e GCP_PROJECT_ID=test-project \
  test-backend

echo "⏳ Waiting for container to start..."
sleep 5

echo "🏥 Testing health endpoint..."
HEALTH_RESPONSE=$(curl -s http://localhost:8000/api/v1/health)

if echo "$HEALTH_RESPONSE" | grep -q '"status":"healthy"'; then
  echo "✅ Backend Docker validation PASSED"
else
  echo "❌ Backend Docker validation FAILED"
  echo "Response: $HEALTH_RESPONSE"
  docker logs test-backend
  docker stop test-backend && docker rm test-backend
  exit 1
fi

# Clean up
docker stop test-backend && docker rm test-backend
echo "🧹 Cleaned up test container"
```

### Frontend Validation Script

```bash
#!/bin/bash
# frontend-v2/validate-docker.sh

set -e

echo "🔨 Building frontend static files..."
npm run build

echo "🐳 Building frontend Docker image..."
docker build -t test-frontend .

echo "🚀 Starting frontend container..."
docker run -d --name test-frontend -p 8080:8080 test-frontend

echo "⏳ Waiting for nginx to start..."
sleep 5

echo "🏥 Testing health endpoint..."
HEALTH_RESPONSE=$(curl -s http://localhost:8080/health)

if echo "$HEALTH_RESPONSE" | grep -q '"status":"healthy"'; then
  echo "✅ Frontend Docker validation PASSED"
else
  echo "❌ Frontend Docker validation FAILED"
  echo "Response: $HEALTH_RESPONSE"
  docker logs test-frontend
  docker stop test-frontend && docker rm test-frontend
  exit 1
fi

# Test that index.html is served
INDEX_RESPONSE=$(curl -s http://localhost:8080/)
if echo "$INDEX_RESPONSE" | grep -q "<html"; then
  echo "✅ Frontend serves index.html correctly"
else
  echo "❌ Frontend failed to serve index.html"
  docker stop test-frontend && docker rm test-frontend
  exit 1
fi

# Clean up
docker stop test-frontend && docker rm test-frontend
echo "🧹 Cleaned up test container"
```

### Common Issues

**For complete troubleshooting, see**: [troubleshooting.md](troubleshooting.md)

**Quick reference**:
- Missing env vars → Container exits immediately
- Base image mismatch → npm/pip install fails
- COPY path errors → Docker build fails
- Health check failures → Container starts but endpoint fails

---

## IAM Permission Verification

### IAM Propagation Wait

**CRITICAL**: Always wait 90 seconds after `terraform apply` before using new IAM bindings.

**For complete IAM propagation patterns, see**: [troubleshooting.md](troubleshooting.md)#IAM-Propagation-Delays

**Quick validation command**:
```bash
# Test if IAM permissions are active
gcloud projects get-iam-policy [PROJECT_ID] \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:cloudbuild-sa@*"

# If empty, IAM hasn't propagated yet → wait longer
```

### Verify IAM Bindings Exist

**Before deploying, verify that all required IAM bindings exist**:

```bash
# Check Cloud Build service account permissions
gcloud projects get-iam-policy [PROJECT_ID] \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:cloudbuild-sa@*" \
  --format="table(bindings.role)"

# Expected output:
# ROLE
# roles/run.admin
# roles/iam.serviceAccountUser
# roles/artifactregistry.writer

# Check backend service account permissions
gcloud projects get-iam-policy [PROJECT_ID] \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:[BACKEND_SERVICE]-sa@*" \
  --format="table(bindings.role)"

# Expected output:
# ROLE
# roles/secretmanager.secretAccessor
# roles/aiplatform.user
# roles/storage.objectAdmin (for [BUCKET_NAME] bucket)
# roles/storage.objectViewer (for [CONTENT_BUCKET_NAME] bucket)
```

### IAM Validation Checklist

Before deploying:
- [ ] Cloud Build SA has `roles/run.admin` (deploy Cloud Run services)
- [ ] Cloud Build SA has `roles/iam.serviceAccountUser` (impersonate backend SA)
- [ ] Cloud Build SA has `roles/artifactregistry.writer` (push images)
- [ ] Backend SA has `roles/secretmanager.secretAccessor` (read secrets)
- [ ] Backend SA has `roles/aiplatform.user` (Vertex AI access)
- [ ] Backend SA has `roles/storage.objectAdmin` (write to session bucket)
- [ ] Backend SA has `roles/storage.objectViewer` (read from content bucket)
- [ ] If Terraform applied in last 90 seconds: **WAIT** before deploying

---

## Environment Variable Validation

### Backend Environment Variables

**Required Variables** (from `backend/app/core/config.py`):

```bash
# Core Configuration
GCP_PROJECT_ID=[PROJECT_ID]
GCS_BUCKET_NAME=[BUCKET_NAME]  # Agent session persistence
GTM_TEMPLATES_BUCKET_NAME=[CONTENT_BUCKET_NAME]  # GTM templates

# OAuth Configuration (from Secret Manager)
OAUTH_CLIENT_ID=<secret>
OAUTH_CLIENT_SECRET=<secret>
OAUTH_REDIRECT_URI=https://[BACKEND_SERVICE]-HASH.europe-west1.run.app/api/v1/auth/callback
FRONTEND_URL=https://[FRONTEND_SERVICE]-HASH.europe-west1.run.app

# Optional
LOG_LEVEL=INFO  # Default: INFO
```

### Frontend Environment Variables

**Build-Time Variables** (Vite):

```bash
# Set during docker build (in cloudbuild.yaml)
VITE_API_BASE_URL=https://[BACKEND_SERVICE]-HASH.europe-west1.run.app
```

**Note**: Vite variables are baked into the build at Docker build time, not runtime.

### Environment Variable Validation Script

```bash
#!/bin/bash
# scripts/validate-env-vars.sh

set -e

echo "🔍 Validating backend environment variables..."

# Check required variables are set in Cloud Run deployment
REQUIRED_VARS=(
  "GCP_PROJECT_ID"
  "GCS_BUCKET_NAME"
  "GTM_TEMPLATES_BUCKET_NAME"
)

REQUIRED_SECRETS=(
  "OAUTH_CLIENT_ID"
  "OAUTH_CLIENT_SECRET"
  "OAUTH_REDIRECT_URI"
  "FRONTEND_URL"
)

# Get Cloud Run service environment variables
SERVICE_ENV=$(gcloud run services describe [BACKEND_SERVICE] \
  --region=europe-west1 \
  --format="json" | jq -r '.spec.template.spec.containers[0].env')

echo "Checking environment variables..."
for VAR in "${REQUIRED_VARS[@]}"; do
  if echo "$SERVICE_ENV" | jq -e ".[] | select(.name==\"$VAR\")" > /dev/null; then
    echo "✅ $VAR is set"
  else
    echo "❌ $VAR is MISSING"
    exit 1
  fi
done

echo "Checking secrets..."
for SECRET in "${REQUIRED_SECRETS[@]}"; do
  if echo "$SERVICE_ENV" | jq -e ".[] | select(.name==\"$SECRET\")" > /dev/null; then
    echo "✅ $SECRET is set"
  else
    echo "❌ $SECRET is MISSING"
    exit 1
  fi
done

echo "✅ All environment variables validated"
```

---

## Post-Deployment Health Checks

### Immediate Health Checks (First 5 Minutes)

**After deployment succeeds, run these checks**:

```bash
#!/bin/bash
# scripts/post-deployment-health-check.sh

set -e

BACKEND_URL="[BACKEND_URL]"
FRONTEND_URL="[FRONTEND_URL]"

echo "🏥 Running post-deployment health checks..."

# 1. Backend health check
echo "Checking backend health endpoint..."
BACKEND_HEALTH=$(curl -s "$BACKEND_URL/api/v1/health")
if echo "$BACKEND_HEALTH" | jq -e '.status == "healthy"' > /dev/null; then
  echo "✅ Backend health check PASSED"
else
  echo "❌ Backend health check FAILED"
  echo "Response: $BACKEND_HEALTH"
  exit 1
fi

# 2. Frontend health check
echo "Checking frontend health endpoint..."
FRONTEND_HEALTH=$(curl -s "$FRONTEND_URL/health")
if echo "$FRONTEND_HEALTH" | jq -e '.status == "healthy"' > /dev/null; then
  echo "✅ Frontend health check PASSED"
else
  echo "❌ Frontend health check FAILED"
  echo "Response: $FRONTEND_HEALTH"
  exit 1
fi

# 3. Frontend serves index.html
echo "Checking frontend serves application..."
FRONTEND_INDEX=$(curl -s "$FRONTEND_URL/")
if echo "$FRONTEND_INDEX" | grep -q "<html"; then
  echo "✅ Frontend serves index.html correctly"
else
  echo "❌ Frontend failed to serve application"
  exit 1
fi

# 4. Backend API documentation accessible
echo "Checking backend API docs..."
BACKEND_DOCS=$(curl -s "$BACKEND_URL/docs")
if echo "$BACKEND_DOCS" | grep -q "FastAPI"; then
  echo "✅ Backend API docs accessible"
else
  echo "❌ Backend API docs not accessible"
  exit 1
fi

# 5. Check for any Cloud Run errors in logs (last 5 minutes)
echo "Checking for errors in Cloud Run logs..."
ERROR_COUNT=$(gcloud logging read "resource.type=cloud_run_revision AND severity>=ERROR AND timestamp>=\"$(date -u -d '5 minutes ago' +%Y-%m-%dT%H:%M:%SZ)\"" \
  --limit=50 \
  --format=json | jq '. | length')

if [ "$ERROR_COUNT" -eq 0 ]; then
  echo "✅ No errors in Cloud Run logs (last 5 minutes)"
else
  echo "⚠️ Found $ERROR_COUNT errors in Cloud Run logs"
  echo "Review logs: gcloud logging read 'resource.type=cloud_run_revision AND severity>=ERROR' --limit=10"
fi

echo "✅ All post-deployment health checks PASSED"
```

### Extended Health Checks (First 30 Minutes)

**Monitor these metrics after deployment**:

```bash
# 1. Check Cloud Run service status
gcloud run services describe [BACKEND_SERVICE] --region=europe-west1 \
  --format="value(status.conditions)"

# Expected: All conditions should be "True"

# 2. Monitor error rates
gcloud logging read \
  "resource.type=cloud_run_revision AND severity>=ERROR AND timestamp>=\"$(date -u -d '30 minutes ago' +%Y-%m-%dT%H:%M:%SZ)\"" \
  --limit=50

# 3. Check request latency (p95)
gcloud monitoring time-series list \
  --filter='metric.type="run.googleapis.com/request_latencies" AND resource.labels.service_name="[BACKEND_SERVICE]"' \
  --interval-start-time="$(date -u -d '30 minutes ago' +%Y-%m-%dT%H:%M:%SZ)" \
  --interval-end-time="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# 4. Check instance count (should auto-scale based on traffic)
gcloud run services describe [BACKEND_SERVICE] --region=europe-west1 \
  --format="value(status.traffic[0].percent)"
```

### Health Check Failure Response

**If health checks fail**:

1. **Check Cloud Run logs immediately**:
   ```bash
   gcloud logging read "resource.type=cloud_run_revision AND severity>=ERROR" --limit=20
   ```

2. **Check service status**:
   ```bash
   gcloud run services describe [BACKEND_SERVICE] --region=europe-west1
   ```

3. **Rollback if critical**:
   ```bash
   # Switch traffic back to previous revision
   gcloud run services update-traffic [BACKEND_SERVICE] \
     --region=europe-west1 \
     --to-revisions PREVIOUS=100
   ```

4. **Debug the issue**:
   - Missing environment variables → Update deployment with correct vars
   - IAM permission errors → Verify service account permissions
   - Application errors → Check application logs for stack traces

---

## Complete Deployment Workflow

**Putting it all together**:

```bash
#!/bin/bash
# scripts/deploy-to-staging.sh

set -e

echo "🚀 Starting deployment to staging..."

# === PHASE 1: PRE-DEPLOYMENT VALIDATION ===
echo "📋 Phase 1: Pre-deployment validation"

# 1. Run backend tests
cd backend
pytest --cov=app
cd ..

# 2. Validate Docker builds locally
cd backend
bash validate-docker.sh
cd ..

cd frontend-v2
bash validate-docker.sh
cd ..

# 3. Check Node.js version alignment
echo "Checking Node.js version alignment..."
PACKAGE_NODE_VERSION=$(cat frontend-v2/package.json | jq -r '.engines.node')
DOCKERFILE_NODE_VERSION=$(grep "FROM node:" frontend-v2/Dockerfile | cut -d':' -f2 | cut -d'-' -f1)
echo "package.json requires: $PACKAGE_NODE_VERSION"
echo "Dockerfile uses: node:$DOCKERFILE_NODE_VERSION"

# === PHASE 2: TERRAFORM (IF NEEDED) ===
echo "📋 Phase 2: Terraform infrastructure"
cd terraform
if terraform plan -detailed-exitcode; then
  echo "✅ No Terraform changes needed"
else
  echo "⚠️ Terraform changes detected, applying..."
  terraform apply -auto-approve

  echo "⏳ Waiting 90 seconds for IAM propagation..."
  sleep 90
fi
cd ..

# === PHASE 3: DEPLOY TO CLOUD BUILD ===
echo "📋 Phase 3: Deploying to Cloud Build"
SHORT_SHA=$(git rev-parse --short HEAD)
gcloud builds submit --config=cloudbuild.yaml \
  --substitutions=SHORT_SHA=$SHORT_SHA

# === PHASE 4: POST-DEPLOYMENT VALIDATION ===
echo "📋 Phase 4: Post-deployment health checks"
sleep 10  # Wait for services to stabilize
bash scripts/post-deployment-health-check.sh

echo "✅ Deployment to staging COMPLETE"
echo "Backend: [BACKEND_URL]"
echo "Frontend: [FRONTEND_URL]"
```

---

## Validation Metrics

**Track these metrics to measure deployment quality**:

| Metric | Target | How to Measure |
|--------|--------|----------------|
| **Failed builds before success** | ≤ 1 | Count Cloud Build failures |
| **Time to deploy (end-to-end)** | ≤ 30 min | Start of validation → Health checks pass |
| **Health check failures** | 0 | Post-deployment script exits with 0 |
| **Rollback rate** | < 5% | Deployments requiring rollback |
| **Zero-downtime deployments** | 100% | No 5xx errors during deployment |

**Example tracking**:
```
Deployment #1 (2025-12-10):
- Failed builds: 6 ❌
- Time to deploy: 4 hours ❌
- Lessons: Need local Docker validation

Deployment #2 (2025-12-11 - after skill updates):
- Failed builds: 0 ✅
- Time to deploy: 25 minutes ✅
- Improvement: 87% faster
```

---

## Related Skills

- **[cloud-build.md](cloud-build.md)** - Cloud Build CI/CD patterns
- **[cloud-run.md](cloud-run.md)** - Cloud Run deployment strategies
- **[terraform.md](terraform.md)** - Infrastructure as Code
- **[troubleshooting.md](troubleshooting.md)** - Common deployment errors and fixes

---

**Remember**: Validate locally FIRST (15 min local testing >> 1.5 hours Cloud Build debugging). Wait 90 seconds after Terraform apply. Always run health checks after deployment.
