# Cloud Run Deployment Patterns

**Last updated**: 2025-12-11

This skill provides Cloud Run deployment patterns, traffic management, and service configuration best practices.

---

## Table of Contents

1. [Deployment Strategies](#1-deployment-strategies)
2. [Cloud Run Service Configuration](#2-cloud-run-service-configuration)
3. [Traffic Management](#3-traffic-management)
4. [Health Checks](#4-health-checks)
5. [Authenticated Services](#5-authenticated-services)
6. [Custom Domains](#6-custom-domains)

---

## 1. Deployment Strategies

### 1.1 Blue-Green Deployment (Cloud Run Traffic Splitting)

Deploy new version alongside current version, then switch traffic:

```bash
# Deploy new revision without traffic
gcloud run deploy my-app \
  --image us-central1-docker.pkg.dev/PROJECT_ID/REPO/my-app:v2 \
  --region us-central1 \
  --no-traffic \
  --tag blue

# Test the new revision at: https://blue---my-app-hash.run.app

# Switch 100% traffic to new revision
gcloud run services update-traffic my-app \
  --region us-central1 \
  --to-revisions LATEST=100
```

**Advantages:**
- Zero downtime
- Easy rollback (switch traffic back)
- Test production environment before switch
- Both versions running simultaneously

**Disadvantages:**
- Higher cost during transition (2x instances)
- Database migrations require careful planning
- May not work for stateful applications

### 1.2 Canary Deployment (Gradual Rollout)

Deploy to small percentage of users, then gradually increase:

```bash
# Deploy new revision without traffic
gcloud run deploy my-app \
  --image us-central1-docker.pkg.dev/PROJECT_ID/REPO/my-app:v2 \
  --region us-central1 \
  --no-traffic

# Route 10% to new revision, 90% to current
gcloud run services update-traffic my-app \
  --region us-central1 \
  --to-revisions LATEST=10,PREVIOUS=90

# Monitor metrics, then increase to 50%
gcloud run services update-traffic my-app \
  --to-revisions LATEST=50,PREVIOUS=50

# Finally, 100% to new revision
gcloud run services update-traffic my-app \
  --to-revisions LATEST=100
```

**Advantages:**
- Early detection of issues with limited blast radius
- Data-driven deployment decisions
- Gradual risk mitigation
- Real user testing in production

**Disadvantages:**
- Longer deployment time
- Requires robust monitoring
- More complex traffic routing
- Multiple versions running simultaneously

### 1.3 Rolling Update (Cloud Run Default)

Cloud Run automatically manages rolling updates when you deploy:

```bash
# Deploy new version (Cloud Run handles rolling update)
gcloud run deploy my-app \
  --image us-central1-docker.pkg.dev/PROJECT_ID/REPO/my-app:v2 \
  --region us-central1
```

**How it works:**
- New instances spin up with new version
- Health checks ensure new instances are ready
- Old instances drain connections and shut down
- Zero downtime

**Advantages:**
- Simple, automatic
- No manual traffic management
- Cloud Run handles everything
- Zero downtime

**Disadvantages:**
- Less control over rollout speed
- Both versions briefly running together
- Harder to test before full rollout

### 1.4 Recreate Deployment (Not Recommended for Production)

Stop old version, deploy new version (use only for dev/staging):

```bash
# Delete current service
gcloud run services delete my-app --region us-central1

# Deploy new version
gcloud run deploy my-app \
  --image us-central1-docker.pkg.dev/PROJECT_ID/REPO/my-app:v2 \
  --region us-central1
```

**When to use:**
- Development environments
- Staging with no uptime requirements
- Major breaking changes that can't coexist

**Do NOT use for production** (causes downtime)

---

## 2. Cloud Run Service Configuration

### 2.1 Basic Cloud Run Service (Terraform)

```hcl
# main.tf
resource "google_cloud_run_service" "app" {
  name     = "my-app"
  location = "us-central1"

  template {
    spec {
      service_account_name = google_service_account.app.email

      containers {
        image = "us-central1-docker.pkg.dev/${var.project_id}/my-repo/my-app:latest"

        ports {
          container_port = 8080
        }

        resources {
          limits = {
            cpu    = "1000m"
            memory = "512Mi"
          }
        }

        env {
          name  = "ENV"
          value = "production"
        }

        # Secret from Secret Manager
        env {
          name = "DATABASE_PASSWORD"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.db_password.secret_id
              key  = "latest"
            }
          }
        }
      }

      # Connect to Cloud SQL via private IP
      metadata {
        annotations = {
          "run.googleapis.com/cloudsql-instances" = google_sql_database_instance.main.connection_name
          "autoscaling.knative.dev/maxScale"      = "10"
          "autoscaling.knative.dev/minScale"      = "0"
        }
      }
    }

    metadata {
      annotations = {
        "autoscaling.knative.dev/maxScale" = "100"
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  lifecycle {
    ignore_changes = [
      template[0].metadata[0].annotations["run.googleapis.com/client-name"],
      template[0].metadata[0].annotations["run.googleapis.com/client-version"],
    ]
  }
}

# Service Account for Cloud Run
resource "google_service_account" "app" {
  account_id   = "my-app-sa"
  display_name = "My App Service Account"
}

# IAM: Allow Cloud Run to access Cloud SQL
resource "google_project_iam_member" "cloudsql_client" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.app.email}"
}

# IAM: Allow Cloud Run to read secrets
resource "google_secret_manager_secret_iam_member" "app_access" {
  secret_id = google_secret_manager_secret.db_password.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.app.email}"
}

# IAM: Make service publicly accessible (use with caution)
# For authenticated access only, omit this resource
resource "google_cloud_run_service_iam_member" "public_access" {
  service  = google_cloud_run_service.app.name
  location = google_cloud_run_service.app.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}
```

### 2.2 Cloud Run with Load Balancer (Custom Domain + HTTPS)

```hcl
# Load Balancer with managed SSL certificate
resource "google_compute_global_address" "app" {
  name = "my-app-ip"
}

resource "google_compute_managed_ssl_certificate" "app" {
  name = "my-app-cert"

  managed {
    domains = ["app.example.com"]
  }
}

resource "google_compute_backend_service" "app" {
  name = "my-app-backend"

  backend {
    group = google_compute_region_network_endpoint_group.app.id
  }

  log_config {
    enable = true
  }
}

resource "google_compute_region_network_endpoint_group" "app" {
  name                  = "my-app-neg"
  network_endpoint_type = "SERVERLESS"
  region                = "us-central1"

  cloud_run {
    service = google_cloud_run_service.app.name
  }
}

resource "google_compute_url_map" "app" {
  name            = "my-app-url-map"
  default_service = google_compute_backend_service.app.id
}

resource "google_compute_target_https_proxy" "app" {
  name             = "my-app-https-proxy"
  url_map          = google_compute_url_map.app.id
  ssl_certificates = [google_compute_managed_ssl_certificate.app.id]
}

resource "google_compute_global_forwarding_rule" "app" {
  name       = "my-app-https"
  target     = google_compute_target_https_proxy.app.id
  port_range = "443"
  ip_address = google_compute_global_address.app.address
}
```

---

## 3. Traffic Management

### 3.1 Parallel Deployment Pattern

**Anti-Pattern** ❌:
```yaml
# Both deployments run in parallel (can cause issues)
- name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
  id: 'deploy-backend'
  entrypoint: 'gcloud'
  args: ['run', 'deploy', 'backend', ...]

- name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
  id: 'deploy-frontend'
  entrypoint: 'gcloud'
  args: ['run', 'deploy', 'frontend', ...]
```

**Better Pattern** ✅:
```yaml
# Deploy backend first, then frontend (sequential)
- name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
  id: 'deploy-backend'
  entrypoint: 'gcloud'
  args: ['run', 'deploy', 'backend', ...]

- name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
  id: 'deploy-frontend'
  waitFor: ['deploy-backend']  # Wait for backend to finish
  entrypoint: 'gcloud'
  args: ['run', 'deploy', 'frontend', ...]
```

### 3.2 Rollback Pattern

```bash
# Option 1: Switch traffic back to previous revision
gcloud run services update-traffic my-app \
  --to-revisions PREVIOUS=100

# Option 2: Re-deploy previous version
gcloud run deploy my-app \
  --image us-central1-docker.pkg.dev/PROJECT_ID/REPO/my-app:PREVIOUS_SHA

# Option 3: Delete latest revision (traffic goes to previous)
gcloud run revisions delete my-app-00042-abc --region us-central1
```

---

## 4. Health Checks

### 4.1 FastAPI Health Check Endpoints

```python
# app/main.py
from fastapi import FastAPI, HTTPException
from datetime import datetime
from sqlalchemy import text
from app.database import get_db


app = FastAPI()


@app.get("/health")
async def health_check():
    """
    Liveness probe: Is the service running?
    Returns 200 if service is alive, regardless of dependencies.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "my-app",
        "version": "1.0.0"
    }


@app.get("/ready")
async def readiness_check():
    """
    Readiness probe: Can the service handle traffic?
    Checks critical dependencies (database, cache, etc.).
    Returns 200 only if service is ready to accept requests.
    """
    checks = {}

    # Check database connection
    try:
        db = next(get_db())
        db.execute(text("SELECT 1"))
        checks["database"] = "healthy"
    except Exception as e:
        checks["database"] = f"unhealthy: {str(e)}"
        raise HTTPException(
            status_code=503,
            detail={"status": "not ready", "checks": checks}
        )

    # Check Redis (if using cache)
    try:
        from app.cache import redis_client
        redis_client.ping()
        checks["cache"] = "healthy"
    except Exception as e:
        checks["cache"] = f"unhealthy: {str(e)}"
        raise HTTPException(
            status_code=503,
            detail={"status": "not ready", "checks": checks}
        )

    return {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": checks
    }
```

---

## 5. Authenticated Services

### 5.1 Internal Service Configuration

```hcl
# For internal services (no public access)
resource "google_cloud_run_service" "internal_service" {
  name     = "internal-api"
  location = "us-central1"

  # ... service config ...
}

# Allow only specific service accounts to invoke
resource "google_cloud_run_service_iam_member" "internal_invoker" {
  service  = google_cloud_run_service.internal_service.name
  location = google_cloud_run_service.internal_service.location
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.frontend.email}"
}

# DO NOT use:
# member = "allUsers"  # Makes service public
```

### 5.2 Calling Authenticated Cloud Run Services

```python
# app/clients.py
import google.auth
import google.auth.transport.requests
import requests


def call_authenticated_service(url: str) -> dict:
    """Call an authenticated Cloud Run service.

    Args:
        url: Cloud Run service URL

    Returns:
        JSON response
    """
    # Get credentials from environment (works in Cloud Run)
    credentials, project = google.auth.default()

    # Create an ID token
    auth_req = google.auth.transport.requests.Request()
    credentials.refresh(auth_req)
    id_token = credentials.id_token

    # Make authenticated request
    headers = {"Authorization": f"Bearer {id_token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    return response.json()
```

---

## 6. Custom Domains

### 6.1 Direct Cloud Run Domain Mapping (No Load Balancer)

**Recommended for simple setups** ($0/month vs. $28/month for Load Balancer):

```bash
# Map custom domain to Cloud Run service
gcloud run domain-mappings create \
  --service=my-app \
  --domain=api.example.com \
  --region=us-central1 \
  --project=my-project

# Get DNS configuration
gcloud run domain-mappings describe \
  --domain=api.example.com \
  --region=us-central1 \
  --project=my-project
```

**DNS Configuration**:
- **Subdomain**: CNAME record pointing to `ghs.googlehosted.com`
- **Root domain**: A records with Google's IP addresses (provided by `domain-mappings describe`)

**SSL Certificate Provisioning**:
- Google automatically provisions SSL certificates
- Typically takes **15 minutes to 4 hours** (usually 1-2 hours)
- Do not delete/recreate domain mapping if stuck in "Pending" (resets timer)

### 6.2 Cloud Run URL Format Unpredictability

**Discovery**: Cloud Run generates different URL formats at different times:

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

**Implication**: Cannot hardcode URLs in configuration until services are deployed.

**Pattern**:
1. Deploy services first with placeholder configuration
2. Get actual Cloud Run URLs from deployment output
3. Update configuration with actual URLs
4. Redeploy services to pick up correct URLs

---

## 7. Common Gotchas

### 7.1 Always Specify `--port` for Backend Services

**Problem**: Cloud Run defaults to port 8080, but backend might listen on 8000.

**Correct Pattern** ✅:
```bash
gcloud run deploy [BACKEND_SERVICE] \
  --image europe-west1-docker.pkg.dev/PROJECT_ID/[APP_NAME]/backend:$SHORT_SHA \
  --region europe-west1 \
  --port 8000  # ✅ Explicitly specify backend port
  --service-account backend-sa@PROJECT_ID.iam.gserviceaccount.com
```

### 7.2 Include All Required Environment Variables

**Problem**: Cloud Run service starts but fails health checks due to missing env vars.

**Anti-Pattern** ❌:
```bash
# Missing required environment variables
gcloud run deploy backend --image ... --region ...
# Backend fails: "OAUTH_CLIENT_ID environment variable not set"
```

**Correct Pattern** ✅:
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
- [ ] Health endpoint (`/api/v1/health`) works with provided env vars

---

## References

- **Cloud Run Documentation**: https://cloud.google.com/run/docs
- **Cloud Run Domain Mapping**: https://cloud.google.com/run/docs/mapping-custom-domains
- **Traffic Management**: https://cloud.google.com/run/docs/managing-traffic

---

**Remember**:
> "Use rolling updates for simple deployments, canary for risky changes, blue-green for critical services. Always specify --port and all required environment variables."
