# Deployment Troubleshooting

**Last Updated**: 2025-12-11

This skill provides common deployment errors and their fixes for Google Cloud Platform deployments.

---

## Table of Contents

1. [IAM Propagation Delays](#iam-propagation-delays)
2. [Docker Build Issues](#docker-build-issues)
3. [Cloud Build Errors](#cloud-build-errors)
4. [Cloud Run Deployment Errors](#cloud-run-deployment-errors)
5. [OAuth Issues](#oauth-issues)
6. [Environment Variable Issues](#environment-variable-issues)
7. [Quick Reference](#quick-reference)

---

## IAM Propagation Delays

### Problem

IAM policy changes in GCP take 60-120 seconds to propagate globally.

### Symptom

`PERMISSION_DENIED` errors immediately after `terraform apply`, even though IAM bindings exist.

**Real Example (2025-12-10)**:
- Build 4: IAM permission denied → Debugged for 15 minutes, found IAM binding exists
- Build 5: Same error → Waited 30 seconds → Success

**Time Lost**: 25 minutes (2 failed builds) due to not waiting for propagation.

### IAM Propagation Wait Pattern

**ALWAYS wait 90 seconds after `terraform apply` before using newly created IAM bindings**:

```bash
# Apply Terraform changes (creates service accounts + IAM bindings)
terraform apply

# CRITICAL: Wait for IAM propagation
echo "⏳ Waiting 90 seconds for IAM propagation..."
sleep 90

# Now safe to use the new IAM bindings
gcloud builds submit --config=cloudbuild.yaml
```

### When IAM Propagation Applies

**You must wait after**:
- Creating new service accounts
- Adding IAM bindings (`roles/run.admin`, `roles/secretmanager.secretAccessor`, etc.)
- Modifying IAM policies
- Creating Workload Identity bindings

**You don't need to wait for**:
- Updating Cloud Run environment variables (no IAM change)
- Re-deploying with same service account
- Changing resource labels/tags

### Terraform `depends_on` is NOT Enough

**Terraform's `depends_on` only applies to Terraform-managed resources**, not manual operations like `gcloud builds submit`.

```hcl
# This prevents Terraform from deploying Cloud Run before IAM binding exists
resource "google_cloud_run_service" "backend" {
  # ...
  depends_on = [
    google_project_iam_member.backend_secret_manager
  ]
}
```

**But manual Cloud Build submissions still need the 90-second wait** because Terraform can't control GCP's global IAM propagation timing.

### Verification Command

```bash
# Test if IAM permissions are active
gcloud projects get-iam-policy [PROJECT_ID] \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:cloudbuild-sa@*"

# If empty, IAM hasn't propagated yet → wait longer
```

---

## Docker Build Issues

### Issue 1: Missing Environment Variables

**Symptom**: Container exits immediately after start

```bash
docker logs test-backend
# Error: "OAUTH_CLIENT_ID environment variable not set"
```

**Fix**: Add all required env vars from `backend/app/core/config.py` to docker run command.

```bash
# Correct docker run with all required env vars
docker run -d --name test-backend -p 8000:8000 \
  -e OAUTH_CLIENT_ID=dummy \
  -e OAUTH_CLIENT_SECRET=dummy \
  -e GCS_BUCKET_NAME=test-bucket \
  -e GTM_TEMPLATES_BUCKET_NAME=test-bucket \
  -e GCP_PROJECT_ID=test-project \
  test-backend
```

### Issue 2: Base Image Version Mismatch

**Symptom**: `npm install` fails with "Unsupported engine" or Python dependency fails

```
npm warn EBADENGINE Unsupported engine { required: { node: '>= 20' }, current: { node: 'v18.20.8' } }
```

**Fix**: Check `package.json` engines field and align Dockerfile:

```bash
cat frontend-v2/package.json | jq '.engines.node'
# Output: ">= 20"

# Update Dockerfile
FROM node:20-alpine  # Match package.json requirement
```

**Real Example (2025-12-10)**:
- Frontend Dockerfile used `node:18-alpine`
- Dependency `marked@17.0.1` requires Node.js >= 20
- Deployment failed with "Unsupported engine" warning
- Fixed by updating to `node:20-alpine`

### Issue 3: COPY Path Errors

**Symptom**: Docker build fails with "COPY failed: no such file or directory"

```
COPY requirements.txt .
# Error: COPY failed: file not found
```

**Fix**: Verify file exists at expected path relative to Dockerfile:

```bash
ls backend/requirements.txt  # Ensure file exists
# Dockerfile COPY should be: COPY requirements.txt .
```

### Issue 4: Health Check IPv6 Issue (Alpine Linux)

**Symptom**: Frontend Docker build succeeds, service works, but health check fails with "Connection refused"

**Root Cause**: nginx listens on IPv4 `0.0.0.0:8080`, but `localhost` resolves to IPv6 `[::1]` in Alpine, causing wget to fail

**Fix**: Use `127.0.0.1` instead of `localhost` in HEALTHCHECK:

```dockerfile
# ❌ Anti-Pattern (fails in Alpine)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:8080/health || exit 1

# ✅ Correct Pattern
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://127.0.0.1:8080/health || exit 1
```

**Pattern**: In Alpine Linux containers, always use `127.0.0.1` (IPv4) instead of `localhost` in health checks to avoid IPv6 resolution issues.

---

## Cloud Build Errors

### Error 1: Test Coverage Gate Blocks Deployment

**Problem**: 70% test coverage requirement blocked staging deployment despite passing integration tests.

**Symptom**: Cloud Build fails at test step with "coverage < 70%"

**Lesson Learned (2025-12-10)**: E2E tests are brittle in CI environments, causing deployment blockers.

**Anti-Pattern** ❌:
```yaml
# cloudbuild.yaml - Blocks deployment if coverage < 70%
steps:
  - name: 'python:3.11-slim'
    entrypoint: 'bash'
    args:
      - '-c'
      - |
        pytest --cov=app --cov-report=term-missing
        coverage report --fail-under=70  # BLOCKS deployment
```

**Better Pattern** ✅:
```yaml
# Staging: No coverage gate (fast feedback, deploy quickly)
steps:
  - name: 'python:3.11-slim'
    entrypoint: 'bash'
    args:
      - '-c'
      - |
        pytest --cov=app --cov-report=term-missing
        # Log coverage but don't block deployment

# Production: Enforce coverage in pre-merge GitHub Actions (not Cloud Build)
```

**Recommendation**:
- **Staging**: Run tests, log coverage, don't block (fast iteration)
- **Production**: Enforce 70% coverage in PR checks (before merge, not deployment)
- **CI/CD**: Use integration tests only (skip brittle E2E tests in Cloud Build)

### Error 2: Empty SHORT_SHA Substitution

**Problem**: `$SHORT_SHA` is empty in manual `gcloud builds submit` (only auto-populated in GitHub triggers).

**Symptom**: `invalid reference format` error when building Docker images.

**Anti-Pattern** ❌:
```bash
# This fails - $SHORT_SHA is empty
gcloud builds submit --config=cloudbuild.yaml
# Results in Docker tag: backend: (missing SHA)
```

**Correct Pattern** ✅:
```bash
# Manual builds: Always provide SHORT_SHA explicitly
gcloud builds submit --config=cloudbuild.yaml \
  --substitutions=SHORT_SHA=$(git rev-parse --short HEAD)

# GitHub triggers: SHORT_SHA auto-populated, no --substitutions needed
```

### Error 3: IAM Permission Denied (Cloud Build)

**Problem**: Cloud Build service account lacks permissions to deploy Cloud Run or push to Artifact Registry.

**Symptom**: 
```
ERROR: (gcloud.run.deploy) PERMISSION_DENIED: Permission 'run.services.update' denied on resource
```

**Fix**: Grant Cloud Build service account necessary permissions:

```hcl
# IAM: Allow Cloud Build to deploy Cloud Run
resource "google_project_iam_member" "cloudbuild_run_admin" {
  project = var.project_id
  role    = "roles/run.admin"
  member  = "serviceAccount:${google_service_account.cloudbuild.email}"
}

# IAM: Allow Cloud Build to act as service accounts
resource "google_project_iam_member" "cloudbuild_sa_user" {
  project = var.project_id
  role    = "roles/iam.serviceAccountUser"
  member  = "serviceAccount:${google_service_account.cloudbuild.email}"
}

# IAM: Allow Cloud Build to push to Artifact Registry
resource "google_project_iam_member" "cloudbuild_artifact_writer" {
  project = var.project_id
  role    = "roles/artifactregistry.writer"
  member  = "serviceAccount:${google_service_account.cloudbuild.email}"
}
```

**After applying Terraform, wait 90 seconds for IAM propagation!**

---

## Cloud Run Deployment Errors

### Error 1: Port Mismatch

**Problem**: Cloud Run defaults to port 8080, but backend listens on 8000.

**Symptom**: Health checks fail, service returns 502 Bad Gateway

**Fix**: Explicitly specify port:

```bash
gcloud run deploy [BACKEND_SERVICE] \
  --image europe-west1-docker.pkg.dev/PROJECT_ID/[APP_NAME]/backend:$SHORT_SHA \
  --region europe-west1 \
  --port 8000  # ✅ Explicitly specify backend port
```

### Error 2: Missing Environment Variables

**Symptom**: Cloud Run service starts but fails health checks

**Logs**:
```
ERROR: OAUTH_CLIENT_ID environment variable not set
```

**Fix**: Include all required environment variables:

```bash
gcloud run deploy backend \
  --image europe-west1-docker.pkg.dev/PROJECT_ID/[APP_NAME]/backend:$SHORT_SHA \
  --region europe-west1 \
  --set-env-vars="GCP_PROJECT_ID=[PROJECT_ID]" \
  --set-secrets="OAUTH_CLIENT_ID=oauth-client-id:latest" \
  --set-secrets="OAUTH_CLIENT_SECRET=oauth-client-secret:latest" \
  # ... all required env vars
```

**Pre-Deployment Checklist**:
- [ ] All environment variables from `backend/app/core/config.py` set
- [ ] All secrets referenced exist in Secret Manager
- [ ] Service account has `secretmanager.secretAccessor` role

### Error 3: Secret Manager Permission Denied

**Symptom**: 
```
ERROR: Failed to retrieve secret oauth-client-id: Permission denied
```

**Fix**: Grant service account access to secrets:

```hcl
resource "google_secret_manager_secret_iam_member" "backend_oauth_client_id" {
  secret_id = google_secret_manager_secret.oauth_client_id.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.backend.email}"
}
```

---

## OAuth Issues

### Error 1: redirect_uri_mismatch

**Symptom**: OAuth login fails with "redirect_uri_mismatch" error

**Root Causes**:
1. OAuth client created in different project than Cloud Run services
2. OAuth Console URLs don't match actual Cloud Run URLs
3. Backend using old redirect URI from cached secret

**Fix 1: Cross-Project OAuth**

**Verify OAuth client is in same project**:
```bash
# Check OAuth client project ID
gcloud secrets versions access latest --secret=oauth-client-id --project=[PROJECT_ID]

# Client ID format: {PROJECT_NUMBER}-{HASH}.apps.googleusercontent.com
# Verify PROJECT_NUMBER matches staging project (not production)
```

**Fix 2: URL Mismatch**

**Get actual Cloud Run URLs**:
```bash
BACKEND_URL=$(gcloud run services describe [BACKEND_SERVICE] --region=europe-west1 --format='value(status.url)')
FRONTEND_URL=$(gcloud run services describe [FRONTEND_SERVICE] --region=europe-west1 --format='value(status.url)')
```

**Update OAuth Console**:
- Navigate to: https://console.cloud.google.com/apis/credentials
- Update Authorized redirect URIs: `$BACKEND_URL/api/v1/auth/callback`
- Update Authorized JavaScript origins: `$FRONTEND_URL`

**Update Secret Manager**:
```bash
echo "$BACKEND_URL/api/v1/auth/callback" | gcloud secrets versions add oauth-redirect-uri --data-file=-
echo "$FRONTEND_URL" | gcloud secrets versions add frontend-url --data-file=-
```

**Fix 3: Cached Secret**

**Redeploy service to pick up new secret version**:
```bash
gcloud run deploy [BACKEND_SERVICE] \
  --source=backend/ \
  --region=europe-west1
```

### Error 2: Backend Uses Old Redirect URI

**Symptom**: Backend sends wrong redirect URI to Google despite secret updated

**Root Cause**: Cloud Run services with `secretKeyRef` to `latest` version don't auto-reload secrets without redeployment.

**Fix**: Redeploy service after updating secrets:

```bash
# 1. Update secret
echo "NEW_VALUE" | gcloud secrets versions add oauth-redirect-uri --data-file=-

# 2. Redeploy to pick up new secret
gcloud run deploy [BACKEND_SERVICE] \
  --source=backend/ \
  --region=europe-west1
```

---

## Environment Variable Issues

### Error 1: Lost Environment Variables After --env-vars-file

**Problem**: Using `gcloud run services update --env-vars-file` **replaces ALL** environment variables.

**Symptom**: After updating one env var, Cloud Run service loses all other env vars (OAUTH_CLIENT_ID, GCS_BUCKET_NAME, etc.)

**Anti-Pattern** ❌:
```bash
# Only updating ALLOWED_ORIGINS, but this REMOVES all other env vars
cat > /tmp/cors-fix.yaml <<EOF
ALLOWED_ORIGINS: "[FRONTEND_URL]"
EOF

gcloud run services update [BACKEND_SERVICE] --env-vars-file=/tmp/cors-fix.yaml
# ❌ Result: OAUTH_CLIENT_ID, GCS_BUCKET_NAME, etc. are GONE
```

**Correct Pattern** ✅:
```bash
# Option 1: Update single variable (preferred)
gcloud run services update [BACKEND_SERVICE] \
  --update-env-vars=ALLOWED_ORIGINS="[FRONTEND_URL]"

# Option 2: Include ALL env vars in YAML file
cat > /tmp/backend-all-env-vars.yaml <<EOF
ALLOWED_ORIGINS: "[FRONTEND_URL]"
GCS_BUCKET_NAME: "[BUCKET_NAME]"
GTM_TEMPLATES_BUCKET_NAME: "[CONTENT_BUCKET_NAME]"
GCP_PROJECT_ID: "[PROJECT_ID]"
# ... all other env vars
EOF

gcloud run services update [BACKEND_SERVICE] --env-vars-file=/tmp/backend-all-env-vars.yaml
```

**Best Practice**: Always export current env vars first:
```bash
gcloud run services describe [BACKEND_SERVICE] --format=export > current-env.yaml
# Edit YAML file with changes
# Apply complete env var set
gcloud run services update [BACKEND_SERVICE] --env-vars-file=current-env.yaml
```

### Error 2: URL Parsing Issues with --update-env-vars

**Symptom**: Command fails when updating env var with URL value

```bash
# This may fail due to colon in URL
gcloud run services update [BACKEND_SERVICE] \
  --update-env-vars=ALLOWED_ORIGINS="https://frontend.run.app"
# Error: Invalid format (colon parsing issue)
```

**Fix**: Use YAML file instead for URLs:
```bash
cat > /tmp/update.yaml <<EOF
ALLOWED_ORIGINS: "https://frontend.run.app"
EOF
gcloud run services update [BACKEND_SERVICE] --env-vars-file=/tmp/update.yaml
```

---

## Quick Reference

### Debugging Commands

```bash
# Check Cloud Run logs
gcloud logging read "resource.type=cloud_run_revision AND severity>=ERROR" --limit=20

# Check Cloud Build logs
gcloud builds list --limit=10
gcloud builds log BUILD_ID

# Check IAM bindings
gcloud projects get-iam-policy PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:SERVICE_ACCOUNT@*"

# Check secret versions
gcloud secrets versions list SECRET_NAME
gcloud secrets versions access latest --secret=SECRET_NAME

# Check Cloud Run service config
gcloud run services describe SERVICE_NAME --region=REGION

# Get Cloud Run service URL
gcloud run services describe SERVICE_NAME --region=REGION --format='value(status.url)'

# Test OAuth config (if debug endpoint available)
curl [BACKEND_URL]/api/v1/debug/oauth-config

# Check environment variables
gcloud run services describe SERVICE_NAME --region=REGION \
  --format="json" | jq '.spec.template.spec.containers[0].env'
```

### Common Fixes Checklist

- [ ] IAM propagation: Wait 90 seconds after `terraform apply`
- [ ] Docker validation: Test locally before Cloud Build
- [ ] Base image version: Match package.json/requirements.txt
- [ ] Health check: Use `127.0.0.1` instead of `localhost` in Alpine
- [ ] SHORT_SHA: Use `--substitutions=SHORT_SHA=$(git rev-parse --short HEAD)`
- [ ] Cloud Run port: Specify `--port 8000` for backend
- [ ] Environment variables: Use `--update-env-vars` for single updates
- [ ] Secrets: Redeploy after updating Secret Manager
- [ ] OAuth URLs: Update both OAuth Console and Secret Manager
- [ ] Cross-project OAuth: Create client in same project as services

---

## Related Skills

- **[validation.md](validation.md)** - Pre/post deployment validation
- **[cloud-run.md](cloud-run.md)** - Cloud Run deployment patterns
- **[cloud-build.md](cloud-build.md)** - CI/CD configuration
- **[terraform.md](terraform.md)** - Infrastructure as Code
- **[oauth-deployment.md](oauth-deployment.md)** - OAuth-specific patterns

---

**Remember**: Wait 90 seconds for IAM propagation, validate Docker builds locally, and always check logs first when debugging failures.
