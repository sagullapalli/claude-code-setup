# Google ADK Patterns - Quick Reference

**Google ADK (Agent Development Kit)** is the official framework for building production-ready multi-agent applications with Vertex AI.

**IMPORTANT**: Google ADK (`google-adk`) ≠ Google GenAI SDK (`google-genai`). ADK is a complete agent framework; GenAI SDK is for direct Gemini API calls.

---

## Modules

1. **[01-agent-setup.md](01-agent-setup.md)** - Agent Creation & Configuration
   - Installation (Python 3.10+ required)
   - Authentication (Vertex AI, Google AI Studio)
   - Creating agents (LlmAgent, SequentialAgent)
   - Model configuration

2. **[02-event-persistence.md](02-event-persistence.md)** - Event Handling & Persistence
   - Event structure and serialization
   - `model_dump(mode='json')` for bytes handling
   - Manual event persistence (critical gotchas)
   - Complete conversation history management

3. **[03-state-management.md](03-state-management.md)** - Session State & Reloads
   - Session management patterns
   - State loss on reload (critical gotcha)
   - Metadata tracking across reloads
   - GCS-backed session storage

4. **[04-tool-integration.md](04-tool-integration.md)** - Function Calling & Tools
   - Python function tools (type hints, docstrings)
   - @adk_tool decorator
   - Tool best practices
   - Error handling

5. **[05-fastapi-integration.md](05-fastapi-integration.md)** - API Integration Patterns
   - FastAPI + ADK integration
   - Async execution patterns
   - Error handling in production
   - Complete examples

6. **[06-multi-agent-deployment.md](06-multi-agent-deployment.md)** - Multi-Agent Systems & Deployment
   - Hierarchical agents (coordinator/specialist)
   - Sequential workflows
   - RAG pattern
   - Deployment to Vertex AI Agent Engine

7. **[07-oauth-authentication.md](07-oauth-authentication.md)** - OAuth 2.0 for Vertex AI Agent Engine
   - OpenAPI security definitions (mandatory)
   - Token retrieval from session state (direct access patterns)
   - Credential injection in callbacks (before_tool_callback)
   - 401 error handling (after_tool_callback)
   - Gemini Enterprise OAuth configuration

---

## Quick Lookup

**Common Issues:**
- Event not persisting? → [02-event-persistence.md](02-event-persistence.md) - Manual append required
- State lost after reload? → [03-state-management.md](03-state-management.md) - Separate tracking needed
- Tool not called? → [04-tool-integration.md](04-tool-integration.md) - Check type hints/docstrings
- Session not saving? → [03-state-management.md](03-state-management.md) - GCS session service
- Performance issues? → [02-event-persistence.md](02-event-persistence.md) - Batch saves
- Authentication failing? → [01-agent-setup.md](01-agent-setup.md) - Vertex AI auth
- OAuth tokens not found? → [07-oauth-authentication.md](07-oauth-authentication.md) - Direct state access patterns
- 401 errors looping? → [07-oauth-authentication.md](07-oauth-authentication.md) - after_tool_callback interception

**First Time Setup:**
1. Start with [01-agent-setup.md](01-agent-setup.md) for installation
2. Read [02-event-persistence.md](02-event-persistence.md) for critical gotchas
3. Check [03-state-management.md](03-state-management.md) for session patterns

---

## Anti-Patterns (Common Gotchas)

❌ **Assuming `run_async()` auto-persists events**
→ ✅ See [02-event-persistence.md](02-event-persistence.md) - Manual `session.events.append()` + `extend()` required

❌ **Expecting state to survive reload without save**
→ ✅ See [03-state-management.md](03-state-management.md) - Track separately, restore after reload

❌ **Using `model_dump()` instead of `model_dump(mode='json')`**
→ ✅ See [02-event-persistence.md](02-event-persistence.md) - Bytes won't serialize without `mode='json'`

❌ **Forgetting `name` parameter on agents**
→ ✅ See [01-agent-setup.md](01-agent-setup.md) - `name` is required

❌ **Using GenAI SDK instead of ADK**
→ ✅ See [01-agent-setup.md](01-agent-setup.md) - `pip install google-adk`, NOT `google-genai`

❌ **Multiple saves per request**
→ ✅ See [02-event-persistence.md](02-event-persistence.md) - Batch updates, save once

❌ **Using `load_credential()` in sync callbacks**
→ ✅ See [07-oauth-authentication.md](07-oauth-authentication.md) - Returns coroutine, use direct state access

❌ **Searching for `temp:oauth2` in Vertex AI**
→ ✅ See [07-oauth-authentication.md](07-oauth-authentication.md) - Pattern is `oauth2_*`, NOT `temp:oauth2`

❌ **Omitting OpenAPI security definitions**
→ ✅ See [07-oauth-authentication.md](07-oauth-authentication.md) - Must inject `security: [{"oauth2": []}]`

---

## When to Use Which Module

| Task | Module | Why |
|------|--------|-----|
| Building new agent | [01-agent-setup.md](01-agent-setup.md) | Installation, creation, config |
| Debugging persistence | [02-event-persistence.md](02-event-persistence.md) | Event handling, save patterns |
| Session reload issues | [03-state-management.md](03-state-management.md) | State loss gotchas |
| Adding tools | [04-tool-integration.md](04-tool-integration.md) | Function calling patterns |
| API integration | [05-fastapi-integration.md](05-fastapi-integration.md) | FastAPI + ADK |
| Multi-agent system | [06-multi-agent-deployment.md](06-multi-agent-deployment.md) | Hierarchical, sequential, RAG |
| Production deployment | [06-multi-agent-deployment.md](06-multi-agent-deployment.md) | Vertex AI Agent Engine |
| OAuth authentication | [07-oauth-authentication.md](07-oauth-authentication.md) | OpenAPI OAuth, token retrieval, 401 handling |

---

## Quick Start

```python
# Install
pip install google-adk  # Python 3.10+ required

# Imports
from google.adk.agents import LlmAgent
from google.adk.runners import InMemoryRunner

# Auth (Vertex AI)
import os
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "TRUE"
os.environ["GOOGLE_CLOUD_PROJECT"] = "your-project"
os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"

# Create & Run
agent = LlmAgent(model="gemini-2.0-flash", name="assistant")
runner = InMemoryRunner(agent=agent, app_name="app")
response = await runner.run_debug("Hello!")
```

**Next Steps**: Read [01-agent-setup.md](01-agent-setup.md) for complete setup guide.

---

## Resources

- **Official Docs**: https://google.github.io/adk-docs/
- **GitHub**: https://github.com/google/adk-python
- **PyPI**: https://pypi.org/project/google-adk/
- **Examples**: https://github.com/google/adk-python/tree/main/examples

---

**Last Updated**: 2025-12-08 (Based on Google ADK 1.19.0)
