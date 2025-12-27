# Sage - Solution Architect

Last updated: 2025-12-24

## Active Protocols (Read Every Session)

### Skills-First Protocol
**MANDATORY**: Before ANY architectural design or technical review:
1. Identify technology/domain relevant to the task
2. Check `.claude/skills/[technology]-patterns.md`
3. Search for relevant pattern (2 minutes)
4. Use documented pattern if found, OR investigate + document after verification

**Full protocol**: See CLAUDE.md

## Project Config
- **Project**: The Interface - Web-based IDE wrapping Claude Code CLI
- **GCP Project**: [To be configured for production]
- **Region**: europe-west1 (ALWAYS use Europe regions)
- **Stack**: FastAPI + Claude Agent SDK + React/Vite + Monaco + Puppeteer
- **Repository**: /home/sunny/projects/interface

## Current Status

**Phase**: Architecture Design (2025-12-27)
- Architecture validated and approved
- 5-phase implementation plan defined
- Awaiting Phase 1 implementation kickoff

**Key Decisions Made**:
- Claude Agent SDK (`ClaudeSDKClient`) for multi-turn agent
- Dual streaming: WebSocket (agent) + Socket.io (browser frames)
- Chrome DevTools MCP for browser control
- Critic agent as async observer (not blocking)
- Leverage existing `.claude/hooks/` infrastructure

## Architecture Decisions (ADRs)

### ADR-004: Agent Memory Scaling Strategy (2025-12-27) - PROPOSED
- **Decision**: Phased approach - Context optimization -> pgvector search (100+ docs) -> Graph RAG (only if multi-hop proven)
- **Rationale**: YAGNI - current scale (78 docs) doesn't justify Graph RAG complexity/cost
- **Key Choice**: pgvector in Cloud SQL over Vertex AI Vector Search (simpler, cheaper, already in stack)
- **Trigger for Phase 2**: 100+ docs OR agents frequently miss relevant context
- **Trigger for Graph RAG**: Multi-hop queries become common requirement
- **Full details**: [To be documented in docs/adr/004-memory-scaling.md]

### ADR-001: Dual Streaming Channels (2025-12-27)
- **Decision**: Separate WebSocket (agent events) from Socket.io (browser frames)
- **Rationale**: Different traffic patterns - agent is text/low-volume, browser is binary/high-volume. Prevents frame floods blocking agent events.
- **Alternatives Rejected**: Single WebSocket for both, SSE for agent
- **Full details**: [To be documented in docs/adr/001-interface-architecture.md]

### ADR-002: Critic as Observer Pattern (2025-12-27)
- **Decision**: Critic runs async via event queue, uses lightweight `anthropic` SDK (not Agent SDK)
- **Rationale**: Agent SDK is overkill for review-only task. Async prevents blocking main agent.
- **Alternatives Rejected**: Critic as full Agent SDK instance, synchronous inline critique
- **Full details**: [To be documented in docs/adr/001-interface-architecture.md]

### ADR-003: Hook Integration Strategy (2025-12-27)
- **Decision**: Backend reads existing hook outputs (`.claude/logs/`), doesn't duplicate hooks
- **Rationale**: Existing hooks are sophisticated. Web UI should extend, not replace.
- **Alternatives Rejected**: Separate hook infrastructure for web UI
- **Full details**: See existing hooks in `.claude/hooks/`

## Key Patterns

- **WebSocket Streaming**: Use `websocket-streaming.md` patterns (already verified working)
- **Agent SDK**: Use `ClaudeSDKClient` with context manager, always set `max_turns` and `max_budget_usd`
- **MCP Tool Naming**: `mcp__<server>__<tool>` format for `allowed_tools`
- **State Updates**: React `prev =>` pattern for functional updates during streaming

## Lessons Learned

### Graph RAG vs Vector Search Decision (2025-12-27)
**Pattern**: Graph RAG is for multi-hop reasoning ("find X related to Y that references Z"). Simple vector search handles single-hop retrieval ("find docs relevant to X"). Don't over-engineer - start with vector search, add graph only when multi-hop queries are proven need.
**Key insight**: pgvector in Cloud SQL is underrated - same DB, no new infra, handles 100k+ vectors easily.

## Documentation Map

| Topic | Document | What It Contains |
|-------|----------|------------------|
| Architecture | docs/adr/001-interface-architecture.md | Full architecture ADR (to be created) |
| WebSocket | .claude/skills/websocket-streaming.md | Streaming patterns |
| Agent SDK | .claude/skills/claude-agent-sdk-patterns/ | SDK usage patterns |
| Existing Hooks | .claude/hooks/ | Tool tracing, session analytics |

## Implementation Phases

| Phase | Priority | Goal | Dependencies |
|-------|----------|------|--------------|
| 1 | P1 | Agent streaming + markdown rendering | None |
| 2 | P2 | Monaco editor + file operations | Phase 1 |
| 3 | P3 | Browser preview + agent control | Phase 1 |
| 4 | P4 | Critic agent sidebar | Phase 1 |
| 5 | - | OAuth + Cloud deployment | All |

---

**Memory Guidelines:**
- Keep entries concise with bullet points
- Record specifics (paths, commands, project IDs, regions)
- Focus on project-specific context, not general patterns (those go in skills)
- Update after significant milestones or discoveries
