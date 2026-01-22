# Terraform Infrastructure Patterns

**Last Updated**: 2025-12-11

This skill provides Terraform patterns for managing Google Cloud Platform infrastructure, including state management, lifecycle blocks, and resource dependencies.

---

## Table of Contents

1. [Terraform State Management](#terraform-state-management)
2. [Resource Configuration](#resource-configuration)
3. [Lifecycle Blocks](#lifecycle-blocks)
4. [IAM & Service Accounts](#iam--service-accounts)
5. [Cloud Run & Cloud Build](#cloud-run--cloud-build)
6. [Workload Identity Federation](#workload-identity-federation)
7. [Best Practices](#best-practices)
8. [Quick Reference](#quick-reference)

---

## Terraform State Management

### Remote State in GCS (CRITICAL)

**NEVER commit Terraform state to Git**. Always use remote state with GCS backend.

```hcl
# backend.tf
terraform {
  backend "gcs" {
    bucket  = "[PROJECT_ID]-terraform-state"
    prefix  = "[APP_NAME]/staging"
  }

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }

  required_version = ">= 1.5"
}
```

**State Bucket Setup**:
```bash
# Create state bucket (one-time setup)
gcloud storage buckets create gs://[PROJECT_ID]-terraform-state \
  --location=europe-west1 \
  --uniform-bucket-level-access

# Enable versioning (for state recovery)
gcloud storage buckets update gs://[PROJECT_ID]-terraform-state \
  --versioning
```

### State Safety

**DO**:
- ✅ Use GCS backend with versioning
- ✅ Add `*.tfstate*` to `.gitignore`
- ✅ Run `terraform plan` before `terraform apply`
- ✅ Use state locking (automatic with GCS)
- ✅ One state per environment (separate workspaces or directories)

**DON'T**:
- ❌ Commit state files to Git
- ❌ Manually edit state files
- ❌ Run concurrent `terraform apply` (state locking prevents this)
- ❌ Delete state bucket accidentally

### State Recovery

```bash
# Backup state before risky operations
terraform state pull > backup.tfstate

# Restore from GCS version history (if needed)
gcloud storage cp \
  gs://[PROJECT_ID]-terraform-state/[APP_NAME]/staging/default.tfstate#<version-id> \
  local-restore.tfstate

# Import existing resource into state
terraform import google_cloud_run_service.backend [BACKEND_SERVICE]
```

---

## Resource Configuration

### Artifact Registry Repository

```hcl
resource "google_artifact_registry_repository" "repo" {
  location      = "europe-west1"
  repository_id = "[APP_NAME]"
  format        = "DOCKER"
  
  description = "Docker images for Application"
}
```

### Cloud SQL Instance

```hcl
resource "google_sql_database_instance" "main" {
  name             = "my-app-db"
  database_version = "POSTGRES_15"
  region           = "us-central1"

  settings {
    tier = "db-f1-micro"

    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.vpc.id
    }

    backup_configuration {
      enabled                        = true
      start_time                     = "03:00"
      point_in_time_recovery_enabled = true
    }
  }

  deletion_protection = true
}
```

### VPC Connector for Cloud Run

```hcl
resource "google_vpc_access_connector" "connector" {
  name          = "vpc-connector"
  region        = "us-central1"
  network       = google_compute_network.vpc.name
  ip_cidr_range = "10.8.0.0/28"
}
```

---

## Lifecycle Blocks

### Ignore Changes for Cloud Run Images (CRITICAL)

**Problem**: CI/CD deploys new images, but Terraform wants to revert to placeholder image on next `terraform apply`.

**Solution**: Use `lifecycle { ignore_changes }` block:

```hcl
resource "google_cloud_run_service" "backend" {
  name     = "[BACKEND_SERVICE]"
  location = "europe-west1"

  template {
    spec {
      containers {
        image = "europe-west1-docker.pkg.dev/[PROJECT_ID]/[APP_NAME]/backend:placeholder"
        # CI/CD will deploy actual images (e.g., backend:abc123)
      }
    }
  }

  # CRITICAL: Prevent Terraform from rolling back CI/CD-deployed images
  lifecycle {
    ignore_changes = [
      template[0].spec[0].containers[0].image,
      template[0].metadata[0].annotations["run.googleapis.com/client-name"],
      template[0].metadata[0].annotations["run.googleapis.com/client-version"],
    ]
  }
}
```

**Why This Matters**:
- Terraform initially deploys with placeholder image
- CI/CD (Cloud Build) deploys real images (`backend:abc123`, `backend:def456`)
- Without `ignore_changes`, `terraform apply` would revert to placeholder
- With `ignore_changes`, Terraform leaves image management to CI/CD

### Prevent Accidental Deletion

```hcl
resource "google_sql_database_instance" "main" {
  # ... config ...

  # Prevent accidental database deletion
  deletion_protection = true
  
  lifecycle {
    prevent_destroy = true  # Terraform will refuse to destroy this resource
  }
}
```

### Create Before Destroy

```hcl
resource "google_compute_instance" "app" {
  # ... config ...

  lifecycle {
    create_before_destroy = true  # Create new instance before destroying old
  }
}
```

---

## IAM & Service Accounts

### Service Account Creation

```hcl
# Service account for Cloud Run backend
resource "google_service_account" "backend" {
  account_id   = "[BACKEND_SERVICE]-sa"
  display_name = "Backend Service Account"
}

# Service account for Cloud Build
resource "google_service_account" "cloudbuild" {
  account_id   = "cloudbuild-sa"
  display_name = "Cloud Build Service Account"
}
```

### IAM Bindings (Least Privilege)

```hcl
# Backend SA: Access Secret Manager
resource "google_project_iam_member" "backend_secret_manager" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.backend.email}"
}

# Backend SA: Use Vertex AI
resource "google_project_iam_member" "backend_vertex_ai" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.backend.email}"
}

# Backend SA: Write to GCS session bucket
resource "google_storage_bucket_iam_member" "backend_sessions_admin" {
  bucket = google_storage_bucket.sessions.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.backend.email}"
}

# Cloud Build SA: Deploy Cloud Run services
resource "google_project_iam_member" "cloudbuild_run_admin" {
  project = var.project_id
  role    = "roles/run.admin"
  member  = "serviceAccount:${google_service_account.cloudbuild.email}"
}

# Cloud Build SA: Impersonate service accounts
resource "google_project_iam_member" "cloudbuild_sa_user" {
  project = var.project_id
  role    = "roles/iam.serviceAccountUser"
  member  = "serviceAccount:${google_service_account.cloudbuild.email}"
}
```

### Depends_on for IAM Propagation

**Terraform `depends_on` prevents Terraform operations before IAM is ready**:

```hcl
resource "google_cloud_run_service" "backend" {
  # ... config ...

  # CRITICAL: Wait for IAM bindings before deploying
  depends_on = [
    google_project_iam_member.backend_secret_manager,
    google_project_iam_member.backend_vertex_ai,
    google_storage_bucket_iam_member.backend_sessions_admin,
  ]
}
```

**Important**: `depends_on` only works for Terraform-managed resources. For manual operations (e.g., `gcloud builds submit`), you must wait 90 seconds after `terraform apply`.

---

## Cloud Run & Cloud Build

### Cloud Build Trigger

```hcl
# GitHub connection (must be created manually first)
# See oauth-deployment.md for OAuth setup

# Cloud Build trigger on main branch push
resource "google_cloudbuild_trigger" "deploy_staging" {
  name     = "[APP_NAME]-deploy-staging"
  filename = "cloudbuild.yaml"

  github {
    owner = "my-org"
    name  = "my-repo"

    push {
      branch = "^main$"
    }
  }

  # Use custom service account (not default)
  service_account = google_service_account.cloudbuild.id
}
```

**Note**: GitHub connection requires manual OAuth authorization before trigger can be created.

### Secret Manager Secrets

```hcl
# Create secret
resource "google_secret_manager_secret" "oauth_client_id" {
  secret_id = "oauth-client-id"

  replication {
    automatic = true
  }
}

# Add secret version (for initial placeholder)
resource "google_secret_manager_secret_version" "oauth_client_id" {
  secret      = google_secret_manager_secret.oauth_client_id.id
  secret_data = var.oauth_client_id  # Pass via Terraform variable
}

# Update secret version later (after OAuth client created)
# echo "REAL_CLIENT_ID" | gcloud secrets versions add oauth-client-id --data-file=-
```

**Secret Version Strategy**:
- Use `"latest"` for dynamic values (OAuth URLs, frontend URLs)
- Use pinned versions for static secrets (API keys, database passwords)

---

## Workload Identity Federation

### Setup for GitHub Actions

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

resource "google_project_iam_member" "github_actions_artifact_admin" {
  project = var.project_id
  role    = "roles/artifactregistry.admin"
  member  = "serviceAccount:${google_service_account.github_actions.email}"
}
```

---

## Best Practices

### File Organization

```
terraform/
├── main.tf               # Core resources
├── variables.tf          # Input variables
├── outputs.tf            # Output values
├── backend.tf            # Remote state config
├── versions.tf           # Provider versions
├── terraform.tfvars      # Secret values (git-ignored)
└── .terraform.lock.hcl   # Provider lock file (commit to Git)
```

### Variable Management

```hcl
# variables.tf
variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "Primary GCP region"
  type        = string
  default     = "europe-west1"
}

variable "oauth_client_id" {
  description = "OAuth 2.0 Client ID"
  type        = string
  sensitive   = true  # Don't show in plan output
}

# terraform.tfvars (git-ignored)
project_id      = "[PROJECT_ID]"
region          = "europe-west1"
oauth_client_id = "YOUR_CLIENT_ID"
```

**Add to .gitignore**:
```
terraform.tfvars
*.tfstate
*.tfstate.*
.terraform/
```

### Pin Provider Versions

```hcl
# versions.tf
terraform {
  required_version = ">= 1.5"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"  # Pin major version, allow minor updates
    }
  }
}
```

### Resource Naming

```hcl
# Use consistent naming convention
resource "google_cloud_run_service" "backend" {
  name = "${var.app_name}-backend"  # [BACKEND_SERVICE]
  # ...
}

resource "google_service_account" "backend" {
  account_id = "${var.app_name}-backend-sa"  # [BACKEND_SERVICE]-sa
  # ...
}
```

### Enable Required APIs

```hcl
# Enable APIs before using them
resource "google_project_service" "run" {
  service = "run.googleapis.com"
}

resource "google_project_service" "cloudbuild" {
  service = "cloudbuild.googleapis.com"
}

resource "google_project_service" "artifactregistry" {
  service = "artifactregistry.googleapis.com"
}

resource "google_project_service" "secretmanager" {
  service = "secretmanager.googleapis.com"
}

# Make other resources depend on APIs being enabled
resource "google_cloud_run_service" "backend" {
  # ...
  depends_on = [google_project_service.run]
}
```

---

## Quick Reference

### Common Commands

```bash
# Initialize Terraform (download providers)
terraform init

# Format code
terraform fmt

# Validate configuration
terraform validate

# Plan changes (dry run)
terraform plan

# Apply changes
terraform apply

# Apply without confirmation (use with caution)
terraform apply -auto-approve

# Destroy all resources (use with EXTREME caution)
terraform destroy

# List resources in state
terraform state list

# Show resource details
terraform state show google_cloud_run_service.backend

# Import existing resource
terraform import google_cloud_run_service.backend [BACKEND_SERVICE]

# Refresh state (sync with actual infrastructure)
terraform refresh

# Output values
terraform output

# Pull remote state
terraform state pull

# Unlock state (if locked after crash)
terraform force-unlock LOCK_ID
```

### Terraform Workflow

```bash
# 1. Make changes to .tf files

# 2. Format and validate
terraform fmt
terraform validate

# 3. Review plan
terraform plan

# 4. Apply if plan looks good
terraform apply

# 5. CRITICAL: Wait 90 seconds for IAM propagation (if IAM changes were made)
echo "⏳ Waiting 90 seconds for IAM propagation..."
sleep 90

# 6. Now safe to deploy (Cloud Build, etc.)
gcloud builds submit --config=cloudbuild.yaml
```

### Outputs

```hcl
# outputs.tf
output "backend_url" {
  description = "Cloud Run backend URL"
  value       = google_cloud_run_service.backend.status[0].url
}

output "backend_service_account" {
  description = "Backend service account email"
  value       = google_service_account.backend.email
}

output "artifact_registry_url" {
  description = "Artifact Registry repository URL"
  value       = "${google_artifact_registry_repository.repo.location}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.repo.repository_id}"
}
```

---

## Related Skills

- **[cloud-run.md](cloud-run.md)** - Cloud Run deployment patterns
- **[cloud-build.md](cloud-build.md)** - CI/CD pipeline configuration
- **[troubleshooting.md](troubleshooting.md)** - IAM propagation, common Terraform errors

---

**Remember**: Always use remote state with GCS backend, add `lifecycle { ignore_changes }` for CI/CD-managed resources, and wait 90 seconds after `terraform apply` for IAM propagation.
