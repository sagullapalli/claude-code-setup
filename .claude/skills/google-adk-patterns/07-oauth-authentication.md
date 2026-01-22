# Module 07: OAuth 2.0 Authentication for Vertex AI Agent Engine

Complete guide to implementing OAuth 2.0 authentication in ADK agents deployed to Vertex AI Agent Engine.

> **For current auth API, use Context7:**
> ```
> get-library-docs: /google/adk-docs (topic: "OAuth authentication credentials")
> ```

**Last Updated:** 2025-12-26 (Based on production deployment)

---

## Overview

### The Core Challenge

When deploying ADK agents to Vertex AI Agent Engine, OAuth tokens are **not automatically injected** into tool contexts. You must explicitly:

1. **Declare security requirements** in OpenAPI specifications
2. **Retrieve credentials** from session state (using direct state access, NOT async methods)
3. **Configure tools** with credentials at runtime
4. **Handle auth failures** gracefully

### 🎯 Critical Discoveries (Read This First!)

**These are the most important production-verified learnings:**

1. **Token Storage Pattern** (Vertex AI Agent Engine):
   - ✅ Stored as `oauth2_RANDOMNUMBER` (e.g., `oauth2_1765206128403`)
   - ❌ NOT `temp:oauth2` (that's local ADK web server only)
   - ❌ NOT `oauth2` (random suffix ALWAYS appended)
   - ✅ Must use pattern matching: search for keys starting with `oauth2`

2. **ToolContext Async Methods Don't Work in Callbacks**:
   - `tool_context.load_credential()` returns a **coroutine object**
   - Cannot be awaited in synchronous `before_tool_callback` functions
   - ✅ Must use direct state access: `tool_context.state.__dict__.get('_value', {})`

3. **OpenAPI Security Block is Mandatory**:
   - Must inject `yaml_dict["security"] = [{"oauth2": []}]` at runtime
   - Without this, Agent Engine strips Authorization headers completely
   - UI configuration alone is insufficient

4. **State Data Location**:
   - Actual data in `state.__dict__['_value']`, NOT `state.__dict__['_state']`
   - State object is NOT a Python dict (can't use `.keys()`, `.items()`, `in` operator)

---

## 🚨 Critical Gotchas

### Gotcha #1: OpenAPI Security Definitions are Mandatory

**Problem:**
Even with OAuth configured in Gemini Enterprise UI and proper `auth_scheme`/`auth_credential` in Python, if the OpenAPI YAML lacks a `security:` block, Agent Engine treats all endpoints as public.

**Solution:**
Programmatically inject security definitions at runtime:

```python
# In agent.py, BEFORE creating OpenAPIToolset:

security_scheme_name = "oauth2"

# 1. Add securitySchemes to components
if "components" not in yaml_dict:
    yaml_dict["components"] = {}
if "securitySchemes" not in yaml_dict["components"]:
    yaml_dict["components"]["securitySchemes"] = {}

yaml_dict["components"]["securitySchemes"][security_scheme_name] = {
    "type": "oauth2",
    "description": "Google OAuth 2.0",
    "flows": {
        "authorizationCode": {
            "authorizationUrl": "https://accounts.google.com/o/oauth2/v2/auth",
            "tokenUrl": "https://oauth2.googleapis.com/token",
            "scopes": {
                "https://www.googleapis.com/auth/tagmanager.readonly": "Read GTM",
                "https://www.googleapis.com/auth/tagmanager.edit.containers": "Edit GTM"
            }
        }
    }
}

# 2. CRITICAL: Apply security globally
yaml_dict["security"] = [{security_scheme_name: []}]
```

**Why This Works:**
The `security: [{"oauth2": []}]` tells Agent Engine every operation requires OAuth2, triggering the platform to capture and store tokens in session state.

---

### Gotcha #2: ADK State Object is NOT a Python Dictionary

**Problem:**
Using dictionary methods on State object causes crashes:

```python
# ❌ CRASHES:
for key in tool_context.state.keys():  # AttributeError
    ...

# ❌ CRASHES:
if "temp:oauth2" in tool_context.state:  # TypeError
    ...
```

**Solution:**
Always use `.get()` method or `hasattr()`:

```python
# ✅ CORRECT:
access_token = tool_context.state.get("temp:oauth2")

# ✅ CORRECT (for debugging):
if hasattr(tool_context.state, '__dict__'):
    state_dict = tool_context.state.__dict__.get('_value', {})
    all_keys = list(state_dict.keys())
```

---

### Gotcha #3: State Data Lives in `_value`, Not `_state`

**Problem:**
Assuming data is in `_state`:

```python
# ❌ WRONG (returns empty dict):
state_dict = tool_context.state.__dict__.get('_state', {})
```

**Solution:**
Data is stored in `_value`:

```python
# ✅ CORRECT:
state_dict = tool_context.state.__dict__.get('_value', {})
```

---

### Gotcha #4: Tokens Stored WITHOUT `temp:` Prefix + Random Suffixes

**Problem:**
When you configure OAuth in Gemini Enterprise with "Authorization name" = `oauth2`, the platform:
1. Stores tokens directly with the auth_id (NO `temp:` prefix)
2. Appends a random suffix (e.g., `oauth2_1765206128403`)

**Production Evidence:**
```python
# From production logs:
🔍 DEBUG: All state keys: ['oauth2_1765206128403']
🔍 DEBUG: state['oauth2_1765206128403'] = ya29.a0Aa7pCA94RqYe9WQTOn9wCyE...
```

**Solution:**
Search for `oauth2*` pattern (WITHOUT `temp:` prefix):

```python
auth_id = os.getenv("AUTH_ID", "oauth2")

# Strategy 1: Direct pattern search (NO temp: prefix)
access_token = None
if hasattr(tool_context.state, '__dict__'):
    state_dict = tool_context.state.__dict__.get('_value', {})

    # Search for oauth2* keys (NOT temp:oauth2*)
    for key in state_dict.keys():
        if isinstance(key, str) and key.startswith('oauth2'):
            access_token = state_dict.get(key)
            if access_token and isinstance(access_token, str):
                logger.info(f"Found token at '{key}'")
                break

# Strategy 2: Try exact auth_id match (backward compatibility)
if not access_token:
    access_token = tool_context.state.get(auth_id)

# Strategy 3: Fallback to temp: prefix (for local ADK web server)
if not access_token:
    access_token = tool_context.state.get(f"temp:{auth_id}")
```

---

### Gotcha #5: `load_credential()` is ASYNC and Cannot Be Used in Sync Callbacks

**Problem:**
`tool_context.load_credential()` is an **async coroutine** that cannot be awaited in synchronous callbacks.

**Production Evidence:**
```python
credential = tool_context.load_credential("oauth2")
# Returns: <coroutine object CallbackContext.load_credential at 0x7f283fc00040>

# Error:
RuntimeWarning: coroutine 'CallbackContext.load_credential' was never awaited
```

**Solution:**
**Use direct state access instead of `load_credential()` in sync callbacks:**

```python
# ❌ DOES NOT WORK (returns coroutine):
credential = tool_context.load_credential("oauth2")

# ✅ WORKS (direct state access):
access_token = None
auth_id = os.getenv("AUTH_ID", "oauth2")

# Direct pattern search in state
if hasattr(tool_context.state, '__dict__'):
    state_dict = tool_context.state.__dict__.get('_value', {})

    for key in state_dict.keys():
        if isinstance(key, str) and key.startswith('oauth2'):
            access_token = state_dict.get(key)
            if access_token and isinstance(access_token, str):
                break

# Fallback to direct get
if not access_token:
    access_token = tool_context.state.get(auth_id)
```

**ToolContext Methods Reference:**
```python
# Available methods:
['get_auth_response', 'load_credential', 'request_credential', 'save_credential']

# NOTE: All credential methods are async and require await
# They CANNOT be used in before_tool_callback or after_tool_callback
```

---

### Gotcha #6: 401 Errors Trigger "Thinking Loops" Without Intervention

**Problem:**
When a tool returns a raw 401 error, the LLM:
1. Tries to "reason" its way out
2. Retries the same call multiple times
3. Eventually hallucinates data or times out

**Solution:**
Intercept 401 errors in `after_tool_callback`:

```python
def after_tool_callback(tool_context: ToolContext, tool, **kwargs):
    """Intercepts 401 errors to prevent retry loops."""
    tool_response = kwargs.get('tool_response')

    if isinstance(tool_response, dict) and tool_response.get('error'):
        error_msg = str(tool_response.get('error', '')).lower()

        if "401" in error_msg or "unauthenticated" in error_msg:
            logger.error(f"401 AUTH ERROR in {tool.name}")

            # Force the model to stop and ask the user
            return {
                "system_instruction": (
                    "CRITICAL: The API returned a 401 Unauthenticated error. "
                    "DO NOT RETRY. DO NOT HALLUCINATE. "
                    "Tell the user: 'I need you to sign in to access your account.' "
                    "and provide the authorization link if available."
                )
            }

    return None
```

---

## Complete Implementation Pattern

### Step 1: Inject Security Definitions into OpenAPI YAML

```python
import os
import yaml
import pathlib
from dotenv import load_dotenv
from google.adk.tools.openapi_tool.openapi_spec_parser.openapi_toolset import OpenAPIToolset

load_dotenv()

# Load OpenAPI spec
yaml_path = pathlib.Path(__file__).parent / "discovery_openapi" / "api.yaml"
with open(yaml_path, "r", encoding="utf-8") as f:
    yaml_dict = yaml.safe_load(f)

# Define security scheme
security_scheme_name = "oauth2"

# Inject security definitions
if "components" not in yaml_dict:
    yaml_dict["components"] = {}
if "securitySchemes" not in yaml_dict["components"]:
    yaml_dict["components"]["securitySchemes"] = {}

yaml_dict["components"]["securitySchemes"][security_scheme_name] = {
    "type": "oauth2",
    "description": "Google OAuth 2.0",
    "flows": {
        "authorizationCode": {
            "authorizationUrl": "https://accounts.google.com/o/oauth2/v2/auth",
            "tokenUrl": "https://oauth2.googleapis.com/token",
            "scopes": {
                "https://www.googleapis.com/auth/api.scope1": "Scope description",
                "https://www.googleapis.com/auth/api.scope2": "Scope description"
            }
        }
    }
}

# CRITICAL: Apply security globally
yaml_dict["security"] = [{security_scheme_name: []}]
```

---

### Step 2: Configure Auth Scheme and Credential

```python
from fastapi.openapi.models import OAuth2, OAuthFlows, OAuthFlowAuthorizationCode
from google.adk.auth.auth_credential import AuthCredential, AuthCredentialTypes, OAuth2Auth

scopes = {
    "https://www.googleapis.com/auth/api.scope1": "Scope 1",
    "https://www.googleapis.com/auth/api.scope2": "Scope 2",
}

auth_scheme = OAuth2(
    flows=OAuthFlows(
        authorizationCode=OAuthFlowAuthorizationCode(
            authorizationUrl="https://accounts.google.com/o/oauth2/v2/auth",
            tokenUrl="https://oauth2.googleapis.com/token",
            scopes=scopes,
        )
    )
)

auth_credential = AuthCredential(
    auth_type=AuthCredentialTypes.OAUTH2,
    oauth2=OAuth2Auth(
        client_id=os.getenv("OAUTH_CLIENT_ID"),
        client_secret=os.getenv("OAUTH_CLIENT_SECRET")
    ),
)

# Create toolset with auth
openapi_toolset = OpenAPIToolset(
    spec_dict=yaml_dict,
    spec_str_type="yaml",
    auth_scheme=auth_scheme,
    auth_credential=auth_credential,
)
```

---

### Step 3: Implement before_tool_callback for Credential Injection

```python
import logging
import os
from google.adk.tools import ToolContext
from google.adk.tools.openapi_tool.auth.auth_helpers import token_to_scheme_credential

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def before_tool_callback(tool_context: ToolContext, tool, **kwargs):
    """
    Injects OAuth credentials into API tools before execution.

    CRITICAL: Cannot use async methods like load_credential() here.
    Must use direct state access instead.
    """
    tool_name = getattr(tool, 'name', None)

    # Only handle API tools that need authentication
    if not (tool_name and tool_name.startswith('api_')):
        return None

    logger.info(f"Auth injection for: {tool_name}")

    access_token = None
    found_key = None
    auth_id = os.getenv("AUTH_ID", "oauth2")

    # Strategy 1: Direct pattern search for oauth2* keys (NO temp: prefix)
    # This is PRIMARY for Vertex AI Agent Engine
    if hasattr(tool_context.state, '__dict__'):
        state_dict = tool_context.state.__dict__.get('_value', {})

        # Search for oauth2* keys (Gemini Enterprise: oauth2_RANDOMSUFFIX)
        for key in state_dict.keys():
            if isinstance(key, str) and key.startswith('oauth2'):
                access_token = state_dict.get(key)
                if access_token and isinstance(access_token, str):
                    found_key = key
                    logger.info(f"✓ Found token via pattern search: '{key}'")
                    break

    # Strategy 2: Try exact auth_id match (backward compatibility)
    if not access_token and hasattr(tool_context.state, 'get'):
        access_token = tool_context.state.get(auth_id)
        if access_token:
            found_key = auth_id
            logger.info(f"✓ Found token using exact key '{auth_id}'")

    # Strategy 3: Fallback to temp: prefix (for local ADK web server)
    if not access_token and hasattr(tool_context.state, 'get'):
        fallback_keys = [
            f"temp:{auth_id}",
            "temp:oauth2",
            "temp:default",
        ]
        for fallback_key in fallback_keys:
            access_token = tool_context.state.get(fallback_key)
            if access_token:
                found_key = fallback_key
                logger.info(f"✓ Found token using fallback key '{fallback_key}'")
                break

    # Configure tool with credentials
    if access_token:
        logger.info(f"✓ Token retrieved from '{found_key}' (length: {len(access_token)})")

        try:
            # Use official ADK helper to create credentials
            auth_scheme, auth_credential = token_to_scheme_credential(
                token_type="oauth2Token",
                location="header",
                name="Authorization",
                credential_value=access_token
            )

            # Apply credentials to the tool
            tool.configure_auth_scheme(auth_scheme)
            tool.configure_auth_credential(auth_credential)
            logger.info("✓ Credentials configured successfully")

        except Exception as e:
            logger.error(f"Failed to configure credentials: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
    else:
        logger.warning("No OAuth token found - tool will proceed unauthenticated")

        # Debug: Log available state keys
        if hasattr(tool_context.state, '__dict__'):
            state_dict = tool_context.state.__dict__.get('_value', {})
            available_keys = list(state_dict.keys())
            logger.warning(f"Available state keys: {available_keys}")

    return None
```

---

### Step 4: Implement after_tool_callback for Error Handling

```python
def after_tool_callback(tool_context: ToolContext, tool, **kwargs):
    """
    Intercepts tool responses to handle authentication errors gracefully.

    Prevents the LLM from entering retry loops on 401 errors.
    """
    tool_name = getattr(tool, 'name', None)
    tool_response = kwargs.get('tool_response')

    if not tool_response:
        return None

    # Intercept 401/Auth errors
    if isinstance(tool_response, dict) and tool_response.get('error'):
        error_msg = str(tool_response.get('error', '')).lower()

        if "401" in error_msg or "unauthenticated" in error_msg or "credential" in error_msg:
            logger.error(f"🚨 401 AUTH ERROR in {tool_name}")

            # Return system instruction to stop retry loop
            return {
                "system_instruction": (
                    "CRITICAL: The API returned a 401 Unauthenticated error. "
                    "DO NOT RETRY. DO NOT HALLUCINATE. "
                    "Tell the user: 'I need you to sign in to access your account.' "
                    "and provide the authorization link if available."
                )
            }

    # Optional: Cache successful responses
    if tool_name == 'api_list_resources' and 'resources' in tool_response:
        resources = tool_response.get('resources', [])
        tool_context.state['cached_resources'] = resources
        logger.info(f"Cached {len(resources)} resources in state")

    return None
```

---

### Step 5: Create the Agent

```python
from google.adk.agents import Agent
from google.genai import types

# Combine API tools with custom tools
all_tools = openapi_toolset._tools + [custom_tool1, custom_tool2]

# Configure generation settings
generate_content_config = types.GenerateContentConfig(
    temperature=0.1,
    top_p=0.95,
)

# Create agent
root_agent = Agent(
    name="api_agent",
    model="gemini-2.0-flash-exp",
    description="Agent to manage API operations",
    tools=all_tools,
    instruction="You are an API assistant. Always confirm before destructive actions.",
    generate_content_config=generate_content_config,
    before_tool_callback=before_tool_callback,
    after_tool_callback=after_tool_callback
)
```

---

## Deployment Configuration

### OAuth Client Setup

**Google Cloud Console → APIs & Services → Credentials**

**Authorized redirect URIs (add ALL):**
```
# For Vertex AI Agent Engine:
https://vertexaisearch.cloud.google.com/oauth-redirect
https://vertexaisearch.cloud.google.com/static/oauth/oauth.html

# For local development (ADK web server):
http://localhost:8080/callback
http://127.0.0.1:8080/callback
```

### Environment Variables

```bash
# .env (NEVER commit to git)
OAUTH_CLIENT_ID=your-client-id.apps.googleusercontent.com
OAUTH_CLIENT_SECRET=your-client-secret
AUTH_ID=oauth2
GOOGLE_GENAI_USE_VERTEXAI=1
```

### Gemini Enterprise Configuration

**When registering agent in Gemini Enterprise:**

1. Click "Add authorization"
2. **Authorization name:** `oauth2` (must match AUTH_ID env var)
3. **OAuth details:**
   - Client ID: (from OAuth credentials)
   - Client secret: (from OAuth credentials)
   - Authorization URI: `https://accounts.google.com/o/oauth2/v2/auth`
   - Token URI: `https://oauth2.googleapis.com/token`
4. Save

**CRITICAL:** The "Authorization name" becomes your `auth_id`. If you enter `oauth2`, Gemini Enterprise may create `oauth2_RANDOMSUFFIX`, so your code must handle pattern searches.

---

## Debugging

### Enable Comprehensive Logging

```python
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Add debug logging to callbacks
def before_tool_callback(tool_context: ToolContext, tool, **kwargs):
    logger.warning("=" * 80)
    logger.warning(f"🔧 BEFORE_TOOL_CALLBACK: {tool.name}")
    logger.warning(f"State type: {type(tool_context.state).__name__}")

    # Log all state keys
    if hasattr(tool_context.state, '__dict__'):
        state_dict = tool_context.state.__dict__.get('_value', {})
        logger.warning(f"All state keys: {list(state_dict.keys())}")

    logger.warning("=" * 80)
    # ... rest of implementation
```

### View Logs in Cloud Console

```bash
# Real-time logs
gcloud logging tail "resource.type=aiplatform.googleapis.com/ReasoningEngine" \
  --project=your-project-id

# Search for specific patterns
gcloud logging read "resource.type=aiplatform.googleapis.com/ReasoningEngine" \
  --project=your-project-id \
  --limit=100 \
  --format=json | grep -E "🔍|✅|❌|🚨"
```

---

## Common Issues & Solutions

### Issue: State is Empty

**Symptom:**
```
🔍 DEBUG: All state keys: []
```

**Diagnosis:**
- OpenAPI YAML lacks `security:` block
- OAuth not configured in Gemini Enterprise
- User hasn't completed OAuth flow

**Solution:**
1. Verify YAML injection logs at startup
2. Check Gemini Enterprise agent authorization settings
3. Test OAuth flow end-to-end

---

### Issue: load_credential() Returns Coroutine

**Symptom:**
```
🔍 DEBUG: Credential type: <class 'coroutine'>
RuntimeWarning: coroutine 'CallbackContext.load_credential' was never awaited
```

**Solution:**
**Do NOT use `load_credential()` in callbacks. Use direct state access:**

```python
# ❌ WRONG (returns coroutine):
credential = tool_context.load_credential("oauth2")

# ✅ CORRECT (direct state access):
state_dict = tool_context.state.__dict__.get('_value', {})
for key in state_dict.keys():
    if key.startswith('oauth2'):
        access_token = state_dict.get(key)
        break
```

---

### Issue: 401 Errors Despite Token Present

**Symptom:**
```
✅ Token retrieved from 'oauth2_1234567890'
🚨 401 AUTH ERROR DETECTED
```

**Diagnosis:**
- Token expired
- Insufficient scopes
- Token format incorrect

**Solution:**
1. Check token expiration
2. Verify scopes in YAML match API requirements
3. Log token structure: `logger.debug(f"Token: {access_token[:20]}...")`

---

## State Object Structure Reference

```python
# Internal structure (for debugging only):
tool_context.state.__dict__ = {
    '_value': {  # ← Actual data lives here
        # CRITICAL: In Vertex AI, tokens stored WITHOUT temp: prefix
        'oauth2_1765206128403': 'ya29.a0Aa7pCA94RqYe9WQTOn9wCyE...',
        'cached_data': {...},
        'session_id': '...'
    },
    '_delta': {}  # Changes since last save
}

# Official API (use this):
tool_context.state.get('key')
tool_context.state['key'] = value

# For pattern matching (use this for OAuth tokens):
state_dict = tool_context.state.__dict__.get('_value', {})
for key in state_dict.keys():
    if key.startswith('oauth2'):  # NOT 'temp:oauth2'
        token = state_dict.get(key)
```

---

## Summary

**Key Takeaways:**

1. **Security block required** - Inject `security: [{"oauth2": []}]` into YAML
2. **Direct state access** - Cannot use async `load_credential()` in callbacks
3. **Pattern search for tokens** - Search for `oauth2*`, NOT `temp:oauth2`
4. **State data in `_value`** - NOT in `_state`
5. **Intercept 401 errors** - Use `after_tool_callback` to prevent retry loops
6. **Configure both environments** - Different redirect URIs for local vs deployed

**Common Errors:**

- ❌ Missing `security:` block → tokens not captured
- ❌ Using `load_credential()` in callbacks → returns coroutine
- ❌ Searching for `temp:oauth2` → won't find tokens in Vertex AI
- ❌ Not intercepting 401 errors → agent enters retry loop

**Correct Workflow:**

1. Inject security definitions into OpenAPI YAML
2. Configure auth_scheme and auth_credential
3. Implement before_tool_callback with direct state access
4. Implement after_tool_callback for 401 handling
5. Configure OAuth client with correct redirect URIs
6. Add authorization in Gemini Enterprise UI
7. Test OAuth flow end-to-end

---

**See Also:**
- [04-tool-integration.md](04-tool-integration.md) - Tool callbacks and patterns
- [03-state-management.md](03-state-management.md) - Session state basics
- [05-fastapi-integration.md](05-fastapi-integration.md) - API integration

**References:**
- [Vertex AI Agent Engine OAuth](https://cloud.google.com/agent-builder/agent-engine/agent-identity)
- [Register ADK Agents in Gemini Enterprise](https://docs.cloud.google.com/gemini/enterprise/docs/register-and-manage-an-adk-agent)
- [OpenAPI 3.0 Security](https://swagger.io/docs/specification/authentication/)
