# OAuth Deployment Pattern

**Last Updated**: 2025-12-11

This skill provides OAuth-specific deployment patterns for Google Cloud Platform, covering cross-project issues, deployment order, and secret management.

**Lesson Learned (2025-12-10)**: Wrong OAuth deployment sequence caused 2-3 hours of debugging. Correct sequence takes 15-20 minutes.

---

## Table of Contents

1. [Problem: Cross-Project OAuth Clients](#problem-cross-project-oauth-clients)
2. [Deployment Order](#deployment-order)
3. [Cloud Run URL Format Unpredictability](#cloud-run-url-format-unpredictability)
4. [Secret Version Strategy](#secret-version-strategy)
5. [Environment Variable Recovery](#environment-variable-recovery)
6. [Complete Workflow](#complete-workflow)
7. [Quick Reference](#quick-reference)

---

## Problem: Cross-Project OAuth Clients

### Symptom

`redirect_uri_mismatch` errors despite correct URLs in OAuth Console

### Root Cause

OAuth client created in different GCP project than Cloud Run services

**Real Example (2025-12-10)**:
- OAuth client created in `[PROJECT_ID]` (production project)
- Cloud Run services deployed in `[PROJECT_ID]` (staging project)
- Result: Multiple hours debugging redirect URI mismatches

### Solution

**ALWAYS create OAuth client in same project as Cloud Run services**:

1. **Staging environment**: OAuth client in `{project}-stg`
2. **Production environment**: OAuth client in `{project}`

### Verification

```bash
# Check OAuth client project ID matches Cloud Run service project
gcloud secrets versions access latest --secret=oauth-client-id --project=[PROJECT_ID]

# Client ID format: {PROJECT_NUMBER}-{HASH}.apps.googleusercontent.com
# Verify PROJECT_NUMBER matches staging project (not production)
```

---

## Deployment Order

### Wrong Sequence ❌ (causes multiple iterations)

1. Create OAuth client with Terraform placeholder URLs
2. Deploy Cloud Run services (get different URLs than placeholders)
3. Fix OAuth redirect URIs
4. Redeploy services
5. Fix again (multiple rounds)

**Time Investment**: 2-3 hours

### Correct Sequence ✅ (single iteration)

1. **Deploy Cloud Run services first** (get actual URLs)
2. **Create OAuth client** with actual Cloud Run URLs
3. **Update Secret Manager** with OAuth credentials
4. **Redeploy services** to pick up secrets (one-time)

**Time Investment**: 15-20 minutes

### Why This Matters

- Cloud Run URL format is unpredictable until deployment
- Terraform placeholder: `-{PROJECT_NUMBER}.{REGION}.run.app`
- Actual deployment: `-{HASH}-{REGION_CODE}.a.run.app`
- OAuth requires exact URL matches (no wildcards)

---

## Cloud Run URL Format Unpredictability

### Discovery

Cloud Run generates different URL formats at different times:

**Terraform-generated placeholder** (before first deployment):
```
https://{SERVICE}-{PROJECT_NUMBER}.{REGION}.run.app
Format: {SERVICE}-{PROJECT_NUMBER}.{REGION}.run.app
```

**Actual Cloud Run URL** (after deployment):
```
https://{SERVICE}-{HASH}-{REGION_CODE}.a.run.app
Format: {SERVICE}-{HASH}-{REGION_CODE}.a.run.app
```

### Implication

**Cannot hardcode OAuth redirect URIs or frontend URLs until services are deployed.**

### Pattern

1. Deploy services first with placeholder secrets
2. Get actual Cloud Run URLs from deployment output
3. Update Secret Manager with actual URLs
4. Redeploy services to pick up correct URLs

### Get Actual URLs

```bash
# Get actual Cloud Run URLs
BACKEND_URL=$(gcloud run services describe [BACKEND_SERVICE] --region=europe-west1 --format='value(status.url)')
FRONTEND_URL=$(gcloud run services describe [FRONTEND_SERVICE] --region=europe-west1 --format='value(status.url)')

echo "Backend URL: $BACKEND_URL"
echo "Frontend URL: $FRONTEND_URL"

# Update secrets with actual URLs (not Terraform placeholders)
echo "$BACKEND_URL/api/v1/auth/callback" | \
  gcloud secrets versions add oauth-redirect-uri --data-file=-

echo "$FRONTEND_URL" | \
  gcloud secrets versions add frontend-url --data-file=-
```

---

## Secret Version Strategy

### Use "latest" vs. Pinned Versions

**Use `latest`**: OAuth URLs, frontend URLs (change during deployment)
**Use pinned versions**: Static credentials, API keys (never change)

### Anti-Pattern ❌

```hcl
# Terraform pinned to specific version (requires manual update after every secret change)
env {
  name = "OAUTH_REDIRECT_URI"
  value_from {
    secret_key_ref {
      key     = "oauth-redirect-uri"
      version = "2"  # ❌ Hardcoded version - requires Terraform update when secret changes
    }
  }
}
```

### Correct Pattern ✅

```hcl
# Use "latest" for secrets that change during deployment
env {
  name = "OAUTH_REDIRECT_URI"
  value_from {
    secret_key_ref {
      key     = "oauth-redirect-uri"
      version = "latest"  # ✅ Automatically picks up new secret versions
    }
  }
}
```

### Real Issue (2025-12-10)

- Terraform used `version = "2"` for OAuth redirect URI
- Updated secret to version 5 with actual Cloud Run URL
- Backend continued using version 2 (old Terraform placeholder URL)
- Required Terraform update to use `"latest"` instead of `"2"`

### When to Use Each

- **`latest`**: OAuth URLs, API endpoints, frontend URLs (change with deployments)
- **Pinned version**: API keys, database passwords, truly static secrets

### Secret Rotation Behavior

**Important**: Cloud Run services with `secretKeyRef` to `latest` version don't auto-reload secrets without a new deployment.

**To pick up updated secrets**:
```bash
# Update secret version
echo "NEW_VALUE" | gcloud secrets versions add oauth-redirect-uri --data-file=-

# Redeploy service to pick up new secret
gcloud run deploy [BACKEND_SERVICE] \
  --source=backend/ \
  --region=europe-west1
```

---

## Environment Variable Recovery

### Problem

Using `gcloud run services update --env-vars-file` **replaces ALL** environment variables, not just the ones specified.

### Symptom

After updating one env var, Cloud Run service loses all other env vars (OAUTH_CLIENT_ID, GCS_BUCKET_NAME, etc.)

### Anti-Pattern ❌

```bash
# Only updating ALLOWED_ORIGINS, but this REMOVES all other env vars
cat > /tmp/cors-fix.yaml <<EOF
ALLOWED_ORIGINS: "[FRONTEND_URL]"
EOF

gcloud run services update [BACKEND_SERVICE] --env-vars-file=/tmp/cors-fix.yaml
# ❌ Result: OAUTH_CLIENT_ID, GCS_BUCKET_NAME, etc. are GONE
```

### Correct Pattern ✅

```bash
# Option 1: Update single variable (preferred for simple updates)
gcloud run services update [BACKEND_SERVICE] \
  --update-env-vars=ALLOWED_ORIGINS="[FRONTEND_URL]"

# Option 2: Include ALL env vars in YAML file (for complex updates)
cat > /tmp/backend-all-env-vars.yaml <<EOF
ALLOWED_ORIGINS: "[FRONTEND_URL]"
GCS_BUCKET_NAME: "[BUCKET_NAME]"
GTM_TEMPLATES_BUCKET_NAME: "[CONTENT_BUCKET_NAME]"
GCP_PROJECT_ID: "[PROJECT_ID]"
# ... all other env vars
EOF

gcloud run services update [BACKEND_SERVICE] --env-vars-file=/tmp/backend-all-env-vars.yaml
```

### Best Practice

**Always export current env vars first**:
```bash
gcloud run services describe [BACKEND_SERVICE] --format=export > current-env.yaml
# Edit YAML file with changes
# Apply complete env var set
gcloud run services update [BACKEND_SERVICE] --env-vars-file=current-env.yaml
```

### Real Issue (2025-12-10)

- Updated ALLOWED_ORIGINS via `--env-vars-file` with only one variable
- Lost OAUTH_CLIENT_ID, GCS_BUCKET_NAME, GTM_TEMPLATES_BUCKET_NAME
- Backend failed to start due to missing env vars
- Required complete env var YAML file to restore all variables

### URL Parsing Issues with --update-env-vars

⚠️ **URLs with colons can cause parsing issues**:

```bash
# This may fail due to colon in URL
gcloud run services update [BACKEND_SERVICE] \
  --update-env-vars=ALLOWED_ORIGINS="https://frontend.run.app"
# Error: Invalid format (colon parsing issue)

# Use YAML file instead for URLs
cat > /tmp/update.yaml <<EOF
ALLOWED_ORIGINS: "https://frontend.run.app"
EOF
gcloud run services update [BACKEND_SERVICE] --env-vars-file=/tmp/update.yaml
```

---

## Complete Workflow

### OAuth Setup from Scratch

**Complete OAuth setup workflow**:

```bash
# Step 1: Deploy Cloud Run services (get actual URLs)
gcloud builds submit --config=cloudbuild.yaml \
  --substitutions=SHORT_SHA=$(git rev-parse --short HEAD)

# Step 2: Get actual Cloud Run URLs
BACKEND_URL=$(gcloud run services describe [BACKEND_SERVICE] --region=europe-west1 --format='value(status.url)')
FRONTEND_URL=$(gcloud run services describe [FRONTEND_SERVICE] --region=europe-west1 --format='value(status.url)')

echo "Backend URL: $BACKEND_URL"
echo "Frontend URL: $FRONTEND_URL"

# Step 3: Create OAuth client in Google Cloud Console (SAME PROJECT as services)
# - Project: [PROJECT_ID] (NOT [PROJECT_ID])
# - Authorized redirect URIs: $BACKEND_URL/api/v1/auth/callback
# - Authorized JavaScript origins: $FRONTEND_URL

# Step 4: Update Secret Manager with OAuth credentials
echo "YOUR_OAUTH_CLIENT_ID" | gcloud secrets versions add oauth-client-id --data-file=-
echo "YOUR_OAUTH_CLIENT_SECRET" | gcloud secrets versions add oauth-client-secret --data-file=-
echo "$BACKEND_URL/api/v1/auth/callback" | gcloud secrets versions add oauth-redirect-uri --data-file=-
echo "$FRONTEND_URL" | gcloud secrets versions add frontend-url --data-file=-

# Step 5: Redeploy backend to pick up secrets
gcloud run deploy [BACKEND_SERVICE] \
  --source=backend/ \
  --region=europe-west1

# Step 6: Verify OAuth flow works
curl "$BACKEND_URL/api/v1/auth/login"
# Should redirect to Google OAuth consent screen
```

**Time Investment**:
- Correct sequence: 15-20 minutes
- Wrong sequence (cross-project OAuth): 2-3 hours debugging

### Updating OAuth Configuration

**After Cloud Run URLs change** (new deployment, region change, etc.):

```bash
# 1. Get new URLs
BACKEND_URL=$(gcloud run services describe [BACKEND_SERVICE] --region=europe-west1 --format='value(status.url)')
FRONTEND_URL=$(gcloud run services describe [FRONTEND_SERVICE] --region=europe-west1 --format='value(status.url)')

# 2. Update Google OAuth Console
# - Navigate to: https://console.cloud.google.com/apis/credentials
# - Update Authorized redirect URIs: $BACKEND_URL/api/v1/auth/callback
# - Update Authorized JavaScript origins: $FRONTEND_URL

# 3. Update Secret Manager
echo "$BACKEND_URL/api/v1/auth/callback" | gcloud secrets versions add oauth-redirect-uri --data-file=-
echo "$FRONTEND_URL" | gcloud secrets versions add frontend-url --data-file=-

# 4. Redeploy to pick up new secret versions
gcloud run deploy [BACKEND_SERVICE] --source=backend/ --region=europe-west1
```

---

## Quick Reference

### OAuth Checklist

- [ ] OAuth client created in **same project** as Cloud Run services
- [ ] Cloud Run services deployed **first** (to get actual URLs)
- [ ] OAuth Console configured with **actual URLs** (not Terraform placeholders)
- [ ] Secret Manager secrets use `version: "latest"` (not pinned versions)
- [ ] Backend redeployed after secrets updated
- [ ] Verified OAuth flow works (test login endpoint)

### Common Errors

**Error: `redirect_uri_mismatch`**
- **Cause**: OAuth Console URLs don't match actual Cloud Run URLs
- **Fix**: Get actual URLs with `gcloud run services describe`, update OAuth Console

**Error: Backend uses old redirect URI**
- **Cause**: Secret Manager updated but service not redeployed
- **Fix**: Redeploy service to pick up new secret version

**Error: Missing env vars after update**
- **Cause**: Used `--env-vars-file` without including all variables
- **Fix**: Export current env vars, edit, then apply complete set

### Debugging Commands

```bash
# Get current backend environment variables
gcloud run services describe [BACKEND_SERVICE] --region=europe-west1 \
  --format="json" | jq '.spec.template.spec.containers[0].env'

# Test OAuth config endpoint (if available)
curl https://[BACKEND_SERVICE]-HASH.run.app/api/v1/debug/oauth-config

# Check secret versions
gcloud secrets versions list oauth-redirect-uri
gcloud secrets versions access latest --secret=oauth-redirect-uri

# Check frontend URL is correct
curl https://[BACKEND_SERVICE]-HASH.run.app/api/v1/auth/login
# Should redirect to Google OAuth with correct redirect_uri parameter
```

---

## Related Skills

- **[cloud-run.md](cloud-run.md)** - Cloud Run deployment patterns
- **[terraform.md](terraform.md)** - Secret Manager, lifecycle blocks
- **[troubleshooting.md](troubleshooting.md)** - OAuth debugging, environment variable issues

---

**Remember**: Deploy services first to get actual URLs, create OAuth client in same project, use `version: "latest"` for dynamic secrets, and always include ALL env vars when using `--env-vars-file`.
