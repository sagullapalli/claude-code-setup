# Cloud Build CI/CD Patterns

**Last updated**: 2025-12-11

This skill provides Cloud Build configuration patterns, trigger management, and CI/CD best practices.

---

## Table of Contents

1. [Cloud Build Configuration](#1-cloud-build-configuration)
2. [Triggers and Automation](#2-triggers-and-automation)
3. [GitHub Actions Alternative](#3-github-actions-alternative)
4. [Best Practices](#4-best-practices)
5. [Common Errors](#5-common-errors)

---

## 1. Cloud Build Configuration

### 1.1 Complete cloudbuild.yaml Example

```yaml
# cloudbuild.yaml
steps:
  # 1. Run tests
  - name: 'python:3.11-slim'
    id: 'test'
    entrypoint: 'bash'
    args:
      - '-c'
      - |
        pip install --no-cache-dir -r requirements.txt
        pytest --cov=app --cov-report=term-missing

  # 2. Build Docker image
  - name: 'gcr.io/cloud-builders/docker'
    id: 'build'
    args:
      - 'build'
      - '-t'
      - 'us-central1-docker.pkg.dev/$PROJECT_ID/my-repo/my-app:$COMMIT_SHA'
      - '-t'
      - 'us-central1-docker.pkg.dev/$PROJECT_ID/my-repo/my-app:latest'
      - '.'

  # 3. Push to Artifact Registry
  - name: 'gcr.io/cloud-builders/docker'
    id: 'push'
    args:
      - 'push'
      - '--all-tags'
      - 'us-central1-docker.pkg.dev/$PROJECT_ID/my-repo/my-app'

  # 4. Deploy to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    id: 'deploy'
    entrypoint: 'gcloud'
    args:
      - 'run'
      - 'deploy'
      - 'my-app'
      - '--image=us-central1-docker.pkg.dev/$PROJECT_ID/my-repo/my-app:$COMMIT_SHA'
      - '--region=us-central1'
      - '--platform=managed'
      - '--service-account=my-app-sa@$PROJECT_ID.iam.gserviceaccount.com'
      # DO NOT use --allow-unauthenticated unless truly public
      # For authenticated services, omit this flag

options:
  logging: CLOUD_LOGGING_ONLY
  machineType: 'N1_HIGHCPU_8'

timeout: '1200s'
```

### 1.2 Multi-Service Build Pattern

```yaml
# cloudbuild.yaml for microservices
steps:
  # Backend: Test
  - name: 'python:3.11-slim'
    dir: 'backend'
    entrypoint: 'bash'
    args:
      - '-c'
      - |
        pip install -r requirements-test.txt
        pytest tests/ --cov=app --cov-report=term
    id: 'test-backend'

  # Backend: Build
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'build'
      - '-t'
      - 'europe-west1-docker.pkg.dev/$PROJECT_ID/[APP_NAME]/backend:$SHORT_SHA'
      - '-t'
      - 'europe-west1-docker.pkg.dev/$PROJECT_ID/[APP_NAME]/backend:latest'
      - '-f'
      - 'backend/Dockerfile'
      - 'backend/'
    id: 'build-backend'
    waitFor: ['test-backend']

  # Backend: Push
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'push'
      - '--all-tags'
      - 'europe-west1-docker.pkg.dev/$PROJECT_ID/[APP_NAME]/backend'
    id: 'push-backend'
    waitFor: ['build-backend']

  # Frontend: Build static files
  - name: 'node:18-alpine'
    dir: 'frontend-v2'
    entrypoint: 'sh'
    args:
      - '-c'
      - |
        npm ci
        npm run build
    env:
      - 'VITE_API_URL=https://[BACKEND_SERVICE]-XXXXX-ew.a.run.app'
    id: 'build-frontend-static'

  # Frontend: Build Docker image
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'build'
      - '-t'
      - 'europe-west1-docker.pkg.dev/$PROJECT_ID/[APP_NAME]/frontend:$SHORT_SHA'
      - '-t'
      - 'europe-west1-docker.pkg.dev/$PROJECT_ID/[APP_NAME]/frontend:latest'
      - '-f'
      - 'frontend-v2/Dockerfile'
      - 'frontend-v2/'
    id: 'build-frontend'
    waitFor: ['build-frontend-static']

  # Frontend: Push
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'push'
      - '--all-tags'
      - 'europe-west1-docker.pkg.dev/$PROJECT_ID/[APP_NAME]/frontend'
    id: 'push-frontend'
    waitFor: ['build-frontend']

  # Deploy: Backend
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: 'gcloud'
    args:
      - 'run'
      - 'deploy'
      - '[BACKEND_SERVICE]'
      - '--image=europe-west1-docker.pkg.dev/$PROJECT_ID/[APP_NAME]/backend:$SHORT_SHA'
      - '--region=europe-west1'
      - '--platform=managed'
      - '--service-account=[BACKEND_SERVICE]-sa@$PROJECT_ID.iam.gserviceaccount.com'
      - '--allow-unauthenticated'
      - '--cpu=2'
      - '--memory=2Gi'
      - '--timeout=300'
      - '--max-instances=10'
      - '--min-instances=0'
      - '--set-env-vars=GCP_PROJECT=$PROJECT_ID,GCP_REGION=europe-west1'
      - '--set-secrets=OAUTH_CLIENT_ID=oauth-client-id:latest,OAUTH_CLIENT_SECRET=oauth-client-secret:latest'
    id: 'deploy-backend'
    waitFor: ['push-backend']

  # Deploy: Frontend (after backend)
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: 'gcloud'
    args:
      - 'run'
      - 'deploy'
      - '[FRONTEND_SERVICE]'
      - '--image=europe-west1-docker.pkg.dev/$PROJECT_ID/[APP_NAME]/frontend:$SHORT_SHA'
      - '--region=europe-west1'
      - '--platform=managed'
      - '--allow-unauthenticated'
      - '--cpu=1'
      - '--memory=256Mi'
      - '--port=8080'
    id: 'deploy-frontend'
    waitFor: ['push-frontend', 'deploy-backend']

  # Health checks
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: 'bash'
    args:
      - '-c'
      - |
        BACKEND_URL=$(gcloud run services describe [BACKEND_SERVICE] --region=europe-west1 --format='value(status.url)')
        FRONTEND_URL=$(gcloud run services describe [FRONTEND_SERVICE] --region=europe-west1 --format='value(status.url)')

        echo "Backend URL: $BACKEND_URL"
        echo "Frontend URL: $FRONTEND_URL"

        # Health check backend
        curl -f "$BACKEND_URL/health" || exit 1

        # Health check frontend
        curl -f "$FRONTEND_URL/health" || exit 1

        echo "Deployment successful!"
    id: 'health-check'
    waitFor: ['deploy-backend', 'deploy-frontend']

# Timeout for entire build
timeout: 1800s

# Use Cloud Build service account
serviceAccount: 'projects/[PROJECT_ID]/serviceAccounts/cloudbuild-sa@[PROJECT_ID].iam.gserviceaccount.com'

options:
  logging: CLOUD_LOGGING_ONLY
  machineType: 'N1_HIGHCPU_8'
```

---

## 2. Triggers and Automation

### 2.1 Cloud Build Trigger (Terraform)

```hcl
# Enable required APIs
resource "google_project_service" "cloudbuild" {
  service = "cloudbuild.googleapis.com"
}

resource "google_project_service" "artifactregistry" {
  service = "artifactregistry.googleapis.com"
}

# Artifact Registry repository
resource "google_artifact_registry_repository" "repo" {
  location      = "us-central1"
  repository_id = "my-repo"
  format        = "DOCKER"
}

# Cloud Build trigger on GitHub push
resource "google_cloudbuild_trigger" "main_branch" {
  name     = "deploy-main"
  filename = "cloudbuild.yaml"

  github {
    owner = "my-org"
    name  = "my-repo"

    push {
      branch = "^main$"
    }
  }

  # Grant Cloud Build permissions
  service_account = google_service_account.cloudbuild.id
}

# Service account for Cloud Build
resource "google_service_account" "cloudbuild" {
  account_id   = "cloudbuild-sa"
  display_name = "Cloud Build Service Account"
}

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
```

### 2.2 Manual Build with Substitutions

```bash
# Manual builds: Always provide SHORT_SHA explicitly
gcloud builds submit --config=cloudbuild.yaml \
  --substitutions=SHORT_SHA=$(git rev-parse --short HEAD)

# GitHub triggers: SHORT_SHA auto-populated, no --substitutions needed
```

---

## 3. GitHub Actions Alternative

### 3.1 Using Workload Identity Federation (NOT service account keys)

```yaml
# .github/workflows/deploy.yml
name: Deploy to Cloud Run

on:
  push:
    branches: [main]

env:
  PROJECT_ID: my-project-id
  REGION: us-central1
  SERVICE_NAME: my-app
  WORKLOAD_IDENTITY_PROVIDER: projects/123456789/locations/global/workloadIdentityPools/github-pool/providers/github-provider
  SERVICE_ACCOUNT: github-actions@my-project-id.iam.gserviceaccount.com

jobs:
  deploy:
    runs-on: ubuntu-latest

    permissions:
      contents: read
      id-token: write

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Authenticate to Google Cloud
        uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: ${{ env.WORKLOAD_IDENTITY_PROVIDER }}
          service_account: ${{ env.SERVICE_ACCOUNT }}

      - name: Set up Cloud SDK
        uses: google-github-actions/setup-gcloud@v2

      - name: Configure Docker for Artifact Registry
        run: gcloud auth configure-docker us-central1-docker.pkg.dev

      - name: Run tests
        run: |
          pip install -r requirements.txt
          pytest --cov=app

      - name: Build Docker image
        run: |
          docker build \
            -t us-central1-docker.pkg.dev/${{ env.PROJECT_ID }}/my-repo/${{ env.SERVICE_NAME }}:${{ github.sha }} \
            -t us-central1-docker.pkg.dev/${{ env.PROJECT_ID }}/my-repo/${{ env.SERVICE_NAME }}:latest \
            .

      - name: Push to Artifact Registry
        run: |
          docker push --all-tags us-central1-docker.pkg.dev/${{ env.PROJECT_ID }}/my-repo/${{ env.SERVICE_NAME }}

      - name: Deploy to Cloud Run
        run: |
          gcloud run deploy ${{ env.SERVICE_NAME }} \
            --image us-central1-docker.pkg.dev/${{ env.PROJECT_ID }}/my-repo/${{ env.SERVICE_NAME }}:${{ github.sha }} \
            --region ${{ env.REGION }} \
            --platform managed \
            --service-account my-app-sa@${{ env.PROJECT_ID }}.iam.gserviceaccount.com
```

### 3.2 Workload Identity Federation Setup (Terraform)

```hcl
# Create Workload Identity Pool
resource "google_iam_workload_identity_pool" "github" {
  workload_identity_pool_id = "github-pool"
  display_name              = "GitHub Actions Pool"
}

# Create Workload Identity Provider (GitHub)
resource "google_iam_workload_identity_pool_provider" "github" {
  workload_identity_pool_id          = google_iam_workload_identity_pool.github.workload_identity_pool_id
  workload_identity_pool_provider_id = "github-provider"
  display_name                       = "GitHub Provider"

  attribute_mapping = {
    "google.subject"       = "assertion.sub"
    "attribute.actor"      = "assertion.actor"
    "attribute.repository" = "assertion.repository"
  }

  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }
}

# Service account for GitHub Actions
resource "google_service_account" "github_actions" {
  account_id   = "github-actions"
  display_name = "GitHub Actions"
}

# Allow GitHub Actions to impersonate service account
resource "google_service_account_iam_member" "github_actions_workload_identity" {
  service_account_id = google_service_account.github_actions.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github.name}/attribute.repository/my-org/my-repo"
}

# Grant necessary permissions to service account
resource "google_project_iam_member" "github_actions_run_admin" {
  project = var.project_id
  role    = "roles/run.admin"
  member  = "serviceAccount:${google_service_account.github_actions.email}"
}

resource "google_project_iam_member" "github_actions_sa_user" {
  project = var.project_id
  role    = "roles/iam.serviceAccountUser"
  member  = "serviceAccount:${google_service_account.github_actions.email}"
}

resource "google_project_iam_member" "github_actions_artifact_admin" {
  project = var.project_id
  role    = "roles/artifactregistry.admin"
  member  = "serviceAccount:${google_service_account.github_actions.email}"
}
```

---

## 4. Best Practices

### 4.1 Don't Gate Deployments on Test Coverage (Controversial)

**Problem**: 70% test coverage requirement blocked staging deployment despite passing integration tests.

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
# Let developers fix test issues before merging, not during deployment
```

**Recommendation**:
- **Staging**: Run tests, log coverage, don't block (fast iteration)
- **Production**: Enforce 70% coverage in PR checks (before merge, not deployment)
- **CI/CD**: Use integration tests only (skip brittle E2E tests in Cloud Build)

### 4.2 Use `SHORT_SHA` Substitution Correctly

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

### 4.3 Check Base Image Versions Match Dependencies

**Problem**: Frontend Dockerfile used `node:18-alpine`, but dependency `marked@17.0.1` requires Node.js >= 20.

**Anti-Pattern** ❌:
```dockerfile
# Dockerfile doesn't match package.json engines field
FROM node:18-alpine  # ❌ Node 18

# package.json requires Node 20+
{
  "engines": {
    "node": ">= 20"
  }
}
```

**Correct Pattern** ✅:
```bash
# 1. Check package.json engines field BEFORE writing Dockerfile
cat frontend-v2/package.json | jq '.engines'
# Output: { "node": ">= 20" }

# 2. Use matching base image in Dockerfile
FROM node:20-alpine  # ✅ Matches package.json requirement
```

---

## 5. Common Errors

### 5.1 Docker Image Tag Format Error

**Symptom**:
```
invalid argument "europe-west1-docker.pkg.dev/PROJECT_ID/REPO/IMAGE:" for "-t, --tag" flag: invalid reference format
```

**Root Cause**: `$SHORT_SHA` substitution variable is empty.

**Fix**:
```bash
# Always provide SHORT_SHA for manual builds
gcloud builds submit --config=cloudbuild.yaml \
  --substitutions=SHORT_SHA=$(git rev-parse --short HEAD)
```

### 5.2 Node.js Version Mismatch

**Symptom**:
```
npm warn EBADENGINE Unsupported engine {
  package: 'marked@17.0.1',
  required: { node: '>= 20' },
  current: { node: 'v18.20.8' }
}
```

**Fix**:
```dockerfile
# Update Dockerfile to match package.json engines
FROM node:20-alpine  # Match "node": ">= 20" from package.json
```

---

## References

- **Cloud Build Documentation**: https://cloud.google.com/build/docs
- **Cloud Build Triggers**: https://cloud.google.com/build/docs/automating-builds/create-manage-triggers
- **Workload Identity Federation**: https://cloud.google.com/iam/docs/workload-identity-federation

---

**Remember**:
> "Always provide SHORT_SHA for manual builds. Check Node.js/Python versions match before writing Dockerfiles. Don't gate staging deployments on test coverage."
