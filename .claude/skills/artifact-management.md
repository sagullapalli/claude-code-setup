---
name: artifact-management
description: File and artifact handling patterns for uploads, downloads, GCS storage. Use when working with file uploads, downloads, or cloud storage.
---

# Artifact Management Patterns

> **Purpose**: Patterns for implementing artifact storage, sharing, and management with GCS backend and React frontend.

**Last Updated**: 2025-12-09
**Source**: Session 4B implementation (Artifact Management System)

---

## Overview

**Artifacts**: Saved tool results (GTM account lists, container configs, etc.) that users can reference later and share with team.

**Storage**: Google Cloud Storage (GCS) with private and shared folders
**Permissions**: Owner-based (only creator can delete/unshare shared artifacts)

---

## Backend: GCS Artifact Service

### Directory Structure

```
gs://[BUCKET_NAME]/
  artifacts/
    private/
      {user_id}/
        {artifact_id}.json
    shared/
      {artifact_id}.json
```

**Private**: Only accessible by owner
**Shared**: Accessible by all users (with owner metadata)

---

### Artifact Schema

**Private Artifact**:
```json
{
  "artifact_id": "art-abc12345-1733456789",
  "session_id": "user-x7k2p9q-1733456700",
  "name": "GTM Account List",
  "type": "table",
  "data": [...],
  "created_at": "2025-12-07T10:00:00Z",
  "tags": ["gtm", "accounts"]
}
```

**Shared Artifact** (additional fields):
```json
{
  ...private_fields,
  "owner_user_id": "user-abc123",
  "shared_at": "2025-12-07T11:00:00Z",
  "shared_by": "user-abc123"
}
```

**Artifact Types**:
- `table`: Array data (rendered as table)
- `markdown`: String data (rendered as markdown)
- `json`: Object data (formatted JSON)
- `chart`: Data for visualization (future)

---

### Artifact Service Implementation

```python
from google.cloud import storage
import json
import uuid
from datetime import datetime, timezone

class ArtifactService:
    """Service for managing user artifacts in GCS."""

    def __init__(self):
        self.storage_client = storage.Client()
        self.bucket = self.storage_client.bucket(settings.gcs_bucket_name)

    def create_artifact(
        self,
        user_id: str,
        session_id: str,
        name: str,
        artifact_type: str,
        data: Any,
        tags: List[str] = None
    ) -> Dict[str, Any]:
        """Create a new private artifact."""
        # Validate inputs
        validate_user_id(user_id)

        # Generate unique ID: art-{uuid8}-{timestamp}
        artifact_id = f"art-{uuid.uuid4().hex[:8]}-{int(datetime.now(timezone.utc).timestamp())}"

        artifact = {
            "artifact_id": artifact_id,
            "session_id": session_id,
            "name": name,
            "type": artifact_type,
            "data": data,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "tags": tags or []
        }

        # Save to private folder
        blob_path = f"artifacts/private/{user_id}/{artifact_id}.json"
        blob = self.bucket.blob(blob_path)
        blob.upload_from_string(
            json.dumps(artifact, indent=2),
            content_type="application/json"
        )

        logger.info(f"Created artifact {artifact_id} for user {user_id}")
        return artifact
```

**Key Points**:
- ✅ Validate user_id to prevent path traversal
- ✅ Generate unique IDs with UUID + timestamp (sortable by creation time)
- ✅ Use `indent=2` for human-readable JSON
- ✅ Set `content_type="application/json"` for proper GCS metadata

---

### List Artifacts

```python
def list_user_artifacts(self, user_id: str) -> List[Dict[str, Any]]:
    """List all private artifacts for a user."""
    validate_user_id(user_id)

    prefix = f"artifacts/private/{user_id}/"
    blobs = self.bucket.list_blobs(prefix=prefix)

    artifacts = []
    for blob in blobs:
        if blob.name.endswith(".json"):
            try:
                artifact_data = json.loads(blob.download_as_text())
                artifacts.append(artifact_data)
            except Exception as e:
                logger.error(f"Failed to load artifact {blob.name}: {e}")

    return artifacts

def list_shared_artifacts(self) -> List[Dict[str, Any]]:
    """List all shared artifacts (all users)."""
    prefix = "artifacts/shared/"
    blobs = self.bucket.list_blobs(prefix=prefix)

    artifacts = []
    for blob in blobs:
        if blob.name.endswith(".json"):
            try:
                artifact_data = json.loads(blob.download_as_text())
                artifacts.append(artifact_data)
            except Exception as e:
                logger.error(f"Failed to load shared artifact {blob.name}: {e}")

    return artifacts
```

**Key Points**:
- ✅ Always validate user_id before GCS operations
- ✅ Filter by `.json` extension (ignore other files)
- ✅ Handle parse errors gracefully (log and skip)

---

### Share Artifact (Move to Shared)

```python
def share_artifact(self, artifact_id: str, user_id: str) -> Dict[str, Any]:
    """Move artifact from private to shared."""
    validate_artifact_id(artifact_id)
    validate_user_id(user_id)

    # Load from private
    private_path = f"artifacts/private/{user_id}/{artifact_id}.json"
    private_blob = self.bucket.blob(private_path)

    if not private_blob.exists():
        raise HTTPException(status_code=404, detail=f"Artifact {artifact_id} not found")

    artifact = json.loads(private_blob.download_as_text())

    # Add sharing metadata
    artifact["shared_at"] = datetime.now(timezone.utc).isoformat()
    artifact["shared_by"] = user_id
    artifact["owner_user_id"] = user_id

    # Copy to shared folder
    shared_path = f"artifacts/shared/{artifact_id}.json"
    shared_blob = self.bucket.blob(shared_path)
    shared_blob.upload_from_string(
        json.dumps(artifact, indent=2),
        content_type="application/json"
    )

    # Delete from private
    private_blob.delete()

    logger.info(f"Shared artifact {artifact_id} by user {user_id}")
    return artifact
```

**Key Points**:
- ✅ Verify artifact exists before sharing
- ✅ Add owner metadata (owner_user_id, shared_at, shared_by)
- ✅ Copy to shared folder first, then delete from private (safer)

---

### Unshare Artifact (Move Back to Private)

```python
def unshare_artifact(self, artifact_id: str, user_id: str) -> Dict[str, Any]:
    """Move artifact from shared back to private."""
    validate_artifact_id(artifact_id)
    validate_user_id(user_id)

    # Load from shared
    shared_path = f"artifacts/shared/{artifact_id}.json"
    shared_blob = self.bucket.blob(shared_path)

    if not shared_blob.exists():
        raise HTTPException(status_code=404, detail=f"Artifact {artifact_id} not found")

    artifact = json.loads(shared_blob.download_as_text())

    # ✅ PERMISSION CHECK: Verify ownership
    if artifact.get("owner_user_id") != user_id:
        raise HTTPException(status_code=403, detail="Only owner can unshare artifact")

    # Remove sharing metadata
    artifact.pop("shared_at", None)
    artifact.pop("shared_by", None)
    artifact.pop("owner_user_id", None)

    # Copy to private folder
    private_path = f"artifacts/private/{user_id}/{artifact_id}.json"
    private_blob = self.bucket.blob(private_path)
    private_blob.upload_from_string(
        json.dumps(artifact, indent=2),
        content_type="application/json"
    )

    # Delete from shared
    shared_blob.delete()

    logger.info(f"Unshared artifact {artifact_id} by user {user_id}")
    return artifact
```

**Key Points**:
- ✅ **CRITICAL**: Always verify owner_user_id matches user_id (permission check!)
- ✅ Remove sharing metadata when moving back to private
- ✅ Use `.pop()` to safely remove fields (no error if missing)

---

### Delete Artifact

```python
def delete_artifact(self, artifact_id: str, user_id: str) -> bool:
    """Delete artifact (check private first, then shared if owner)."""
    validate_artifact_id(artifact_id)
    validate_user_id(user_id)

    # Try private folder
    private_path = f"artifacts/private/{user_id}/{artifact_id}.json"
    private_blob = self.bucket.blob(private_path)
    if private_blob.exists():
        private_blob.delete()
        logger.info(f"Deleted private artifact {artifact_id}")
        return True

    # Try shared folder (only if owner)
    shared_path = f"artifacts/shared/{artifact_id}.json"
    shared_blob = self.bucket.blob(shared_path)
    if shared_blob.exists():
        artifact = json.loads(shared_blob.download_as_text())

        # ✅ PERMISSION CHECK: Verify ownership
        if artifact.get("owner_user_id") == user_id:
            shared_blob.delete()
            logger.info(f"Deleted shared artifact {artifact_id}")
            return True
        else:
            raise HTTPException(status_code=403, detail="Only owner can delete shared artifact")

    raise HTTPException(status_code=404, detail=f"Artifact {artifact_id} not found")
```

**Key Points**:
- ✅ Check private folder first (most common case)
- ✅ **CRITICAL**: Verify ownership before deleting shared artifacts
- ✅ Return 404 if not found in either location

---

## Security: Path Traversal Prevention

### Validation Functions

```python
import re
from fastapi import HTTPException

def validate_user_id(user_id: str):
    """Validate user_id format (alphanumeric + hyphens only)."""
    if not re.match(r'^[a-zA-Z0-9\-]+$', user_id):
        raise HTTPException(status_code=400, detail="Invalid user_id format")

def validate_artifact_id(artifact_id: str):
    """Validate artifact_id format (art-{uuid}-{timestamp})."""
    if not re.match(r'^art-[a-zA-Z0-9\-]+$', artifact_id):
        raise HTTPException(status_code=400, detail="Invalid artifact_id format")
```

**Why This Matters**:
- Prevents path traversal attacks: `../../../etc/passwd`
- Ensures GCS blob paths are safe
- Returns 400 (Bad Request) for invalid formats

**Always call these validators**:
```python
def create_artifact(self, user_id: str, ...):
    validate_user_id(user_id)  # ✅ First thing!
    # ... rest of method
```

---

## Frontend: React Artifact UI

### Artifact API Client

```typescript
// services/api.ts
export interface Artifact {
  artifact_id: string;
  session_id: string;
  name: string;
  type: 'table' | 'markdown' | 'json' | 'chart';
  data: any;
  created_at: string;
  tags: string[];
  // Shared artifacts only
  owner_user_id?: string;
  shared_at?: string;
  shared_by?: string;
}

export const artifactApi = {
  listUserArtifacts: (userId: string) =>
    fetchAPI(`/api/v1/artifacts?user_id=${userId}`),

  listSharedArtifacts: () =>
    fetchAPI('/api/v1/artifacts/shared'),

  createArtifact: (data: CreateArtifactRequest) =>
    fetchAPI('/api/v1/artifacts', {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  shareArtifact: (artifactId: string, userId: string) =>
    fetchAPI(`/api/v1/artifacts/${artifactId}/share?user_id=${userId}`, {
      method: 'POST'
    }),

  deleteArtifact: (artifactId: string, userId: string) =>
    fetchAPI(`/api/v1/artifacts/${artifactId}?user_id=${userId}`, {
      method: 'DELETE'
    })
};
```

---

### TanStack Query Integration

```typescript
import { useQuery, useQueryClient } from '@tanstack/react-query';

const userId = getUserId();
const queryClient = useQueryClient();

// Fetch saved artifacts (lazy load when tab active)
const { data: savedArtifactsData, refetch: refetchSaved } = useQuery({
  queryKey: ['artifacts', userId],
  queryFn: () => artifactApi.listUserArtifacts(userId),
  enabled: activeTab === 'saved'  // Performance optimization
});

// Fetch shared artifacts
const { data: sharedArtifactsData, refetch: refetchShared } = useQuery({
  queryKey: ['artifacts', 'shared'],
  queryFn: () => artifactApi.listSharedArtifacts(),
  enabled: activeTab === 'saved'
});

// Instant UI updates after mutations
const handleShare = async (artifactId: string) => {
  await artifactApi.shareArtifact(artifactId, userId);
  refetchSaved();   // Refetch private list (artifact removed)
  refetchShared();  // Refetch shared list (artifact added)
};
```

**Key Points**:
- ✅ Use `enabled` to lazy-load artifacts (only when tab active)
- ✅ Call `refetch()` after mutations for instant UI updates
- ✅ Separate query keys for private and shared artifacts

---

### Auto-Detect Artifact Type

```typescript
const handleSaveArtifacts = async (selectedTools: ToolCall[], isShared: boolean) => {
  for (const tool of selectedTools) {
    // Auto-detect artifact type from result
    let artifactType: 'table' | 'markdown' | 'json' | 'chart' = 'json';

    if (Array.isArray(tool.result)) {
      artifactType = 'table';  // GTM accounts, containers → table
    } else if (typeof tool.result === 'string') {
      artifactType = 'markdown';  // Text responses → markdown
    }

    // Create artifact
    const artifact = await artifactApi.createArtifact({
      user_id: userId,
      session_id: currentSessionId,
      name: tool.name,
      type: artifactType,
      data: tool.result,
      tags: [tool.name.split('_')[0]]  // e.g., "gtm" from "list_gtm_accounts"
    });

    // Share if requested
    if (isShared) {
      await artifactApi.shareArtifact(artifact.artifact_id, userId);
    }
  }
};
```

**Key Points**:
- ✅ Detect type from data structure (array → table, string → markdown)
- ✅ Extract tags from tool name (first segment before underscore)
- ✅ Share immediately after creation if requested

---

### Permission-Based UI

```typescript
const SavedTab: React.FC<{
  sharedArtifacts: Artifact[];
  userId: string;
}> = ({ sharedArtifacts, userId }) => {
  return (
    <div>
      {sharedArtifacts.map((artifact) => {
        const isOwner = artifact.owner_user_id === userId;

        return (
          <div key={artifact.artifact_id}>
            <p>{artifact.name}</p>

            {/* Only show Unshare/Delete for owned shared artifacts */}
            {isOwner && (
              <div>
                <button onClick={() => onUnshare(artifact.artifact_id)}>
                  Unshare
                </button>
                <button onClick={() => onDelete(artifact.artifact_id)}>
                  Delete
                </button>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};
```

**Key Points**:
- ✅ Compare `owner_user_id` with current `userId` to determine ownership
- ✅ Only show Unshare/Delete buttons for owned shared artifacts
- ✅ All users can view shared artifacts, only owner can modify

---

### Save Prompt on Session Switch

```typescript
const [showSaveDialog, setShowSaveDialog] = useState(false);
const [pendingSessionSwitch, setPendingSessionSwitch] = useState<string | null>(null);

const handleSessionClick = (sessionId: string) => {
  // Check if current session has unsaved artifacts
  if (allToolCalls.length > 0 && sessionId !== currentSessionId) {
    const savableTools = allToolCalls.filter(tc => tc.result !== null && !tc.error);

    if (savableTools.length > 0) {
      const shouldSave = confirm(
        `You have ${savableTools.length} unsaved artifact${savableTools.length !== 1 ? 's' : ''} in this session. Would you like to save them before switching?`
      );

      if (shouldSave) {
        setPendingSessionSwitch(sessionId);
        setShowSaveDialog(true);
        return;  // Don't switch yet
      }
    }
  }

  // Proceed with session switch
  setCurrentSessionId(sessionId);
  setAllToolCalls([]);
};
```

**Key Points**:
- ✅ Check for savable tools (result !== null && !error)
- ✅ Store pending session switch to resume after save
- ✅ Show save dialog before switching

---

## Common Gotchas

### 1. Large Artifacts (>10MB)

**Problem**: Large GTM container JSON may exceed reasonable limits

**Solution**: Add size check and truncate if needed

```python
import sys

def create_artifact(self, ..., data: Any, ...):
    # Check data size
    data_size = sys.getsizeof(json.dumps(data))
    if data_size > 5_000_000:  # 5MB limit
        logger.warning(f"Artifact too large ({data_size} bytes), truncating")
        # Option 1: Reject
        raise HTTPException(status_code=413, detail="Artifact too large (max 5MB)")
        # Option 2: Truncate
        data = str(data)[:5_000_000] + "...[truncated]"
```

---

### 2. Concurrent Share/Delete

**Problem**: User shares artifact while another user is viewing it

**Solution**: GCS operations are atomic - no special handling needed

- Share operation: Copy → Delete (if copy fails, private artifact remains)
- Delete operation: Single blob delete (atomic)

---

### 3. Artifact Type Misclassification

**Problem**: Auto-detection may incorrectly classify data

**Future Enhancement**: Allow manual type override in save dialog

```typescript
<select value={artifactType} onChange={(e) => setArtifactType(e.target.value)}>
  <option value="table">Table</option>
  <option value="markdown">Markdown</option>
  <option value="json">JSON</option>
  <option value="chart">Chart</option>
</select>
```

---

## Testing

### Backend API Tests (curl)

```bash
# Create artifact
curl -X POST http://localhost:8000/api/v1/artifacts \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-test123",
    "session_id": "user-test123-1234567890",
    "name": "Test GTM Accounts",
    "type": "table",
    "data": [{"id": 1, "name": "Account 1"}],
    "tags": ["gtm", "test"]
  }'

# List user artifacts
curl http://localhost:8000/api/v1/artifacts?user_id=user-test123

# Share artifact
curl -X POST http://localhost:8000/api/v1/artifacts/{artifact_id}/share?user_id=user-test123

# List shared artifacts
curl http://localhost:8000/api/v1/artifacts/shared

# Delete artifact
curl -X DELETE http://localhost:8000/api/v1/artifacts/{artifact_id}?user_id=user-test123
```

---

### Frontend Manual Tests

1. **Create Artifact**: Send message → Switch session → Confirm save → Check "Saved" tab
2. **Share Artifact**: Click "Share" → Verify moves to "Shared with Team"
3. **Unshare Artifact**: Click "Unshare" → Verify moves back to "My Artifacts"
4. **Delete Artifact**: Click "Delete" → Confirm → Verify removed
5. **Persistence**: Save artifact → Refresh page → Verify still visible

---

## API Endpoints Summary

| Endpoint | Method | Description | Permission |
|----------|--------|-------------|------------|
| `/api/v1/artifacts` | GET | List user's private artifacts | Owner only |
| `/api/v1/artifacts/shared` | GET | List all shared artifacts | All users |
| `/api/v1/artifacts/{id}` | GET | Get specific artifact | Owner or if shared |
| `/api/v1/artifacts` | POST | Create new artifact | Authenticated |
| `/api/v1/artifacts/{id}/share` | POST | Share artifact | Owner only |
| `/api/v1/artifacts/{id}/unshare` | POST | Unshare artifact | Owner only |
| `/api/v1/artifacts/{id}` | DELETE | Delete artifact | Owner only |

---

## Related Patterns

- **GCS Storage**: `.claude/skills/gcp-deployment.md`
- **Security**: `.claude/skills/security-best-practices.md`
- **TanStack Query**: `.claude/skills/frontend-patterns/04-tanstack-query.md`

---

**Verified Working**: Session 4B (2025-12-09)
**Files**: `backend/app/services/artifact_service.py`, `backend/app/api/routes.py:181-328`, `frontend-v2/src/components/SaveArtifactsDialog.tsx`
