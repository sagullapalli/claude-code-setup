# The Interface - Implementation Plan

> **Version**: 1.0
> **Created**: 2025-12-27
> **Status**: Proposed (Pending User Approval)
> **Session**: Initial Architecture Planning

---

## Table of Contents

1. [Vision & Goals](#vision--goals)
2. [Technology Stack](#technology-stack)
3. [System Architecture](#system-architecture)
4. [Key Architecture Decisions](#key-architecture-decisions)
5. [Project Structure](#project-structure)
6. [API Contracts](#api-contracts)
7. [Implementation Phases](#implementation-phases)
8. [Session Insights](#session-insights)
9. [Open Questions](#open-questions)
10. [References](#references)

---

## Vision & Goals

### What is The Interface?

A custom web-based IDE that wraps Claude Code CLI with enhanced UI/UX features. Think: **VS Code + Claude Code Extension + Custom AI Visualization**.

### Core Requirements (User-Defined)

| Priority | Feature | Description |
|----------|---------|-------------|
| 1 | **Markdown Rendering** | Streaming thinking traces, tool actions, outputs with collapsible sections |
| 2 | **Code Editor** | VS Code-like experience with Monaco Editor |
| 3 | **Chrome DevTools** | Embedded browser controlled by agent, visible to user |
| 4 | **Critic Agent** | Observer agent providing third-eye insights |
| - | **Foundation** | Built on existing `.claude/` folder (hooks, skills, rules, etc.) |

### User Context

- **Target Platform**: Web app (not Electron)
- **Primary User**: Personal use, eventual web deployment with Google OAuth
- **Agent Runtime**: Local execution (cloud/hybrid possible later)
- **Code Editor**: Full VS Code features via Monaco
- **Browser**: Embedded Chrome pane controlled by agent, user sees live preview

---

## Technology Stack

### Frontend

| Technology | Purpose | Why |
|------------|---------|-----|
| **React 18+** | UI Framework | Component-based, large ecosystem |
| **TypeScript** | Type Safety | Catch errors at compile time |
| **Vite** | Build Tool | Fast dev server, modern bundling |
| **Tailwind CSS** | Styling | Utility-first, rapid UI development |
| **TanStack Query** | Data Fetching | Caching, loading states, mutations |
| **Monaco Editor** | Code Editing | Same engine as VS Code |
| **xterm.js** | Terminal | Full terminal emulation |
| **react-markdown** | Markdown | Render thinking traces |
| **Socket.io Client** | Browser Streaming | Real-time frame updates |

### Backend

| Technology | Purpose | Why |
|------------|---------|-----|
| **Python 3.11+** | Runtime | Project standard, AI ecosystem |
| **FastAPI** | API Framework | Async, WebSocket support, fast |
| **Claude Agent SDK** | Agent Runtime | Official SDK, wraps Claude Code CLI |
| **Puppeteer** | Browser Control | Chrome DevTools Protocol |
| **Socket.io (python-socketio)** | Frame Streaming | Binary-optimized, reconnection |
| **anthropic SDK** | Critic Agent | Lightweight API calls |

### Infrastructure (Later)

| Technology | Purpose |
|------------|---------|
| **Cloud Run** | Backend hosting |
| **Cloud Build** | CI/CD |
| **Google OAuth** | Authentication |
| **Terraform** | Infrastructure as code |

---

## System Architecture

### High-Level Diagram

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         THE INTERFACE (Web App)                          │
├──────────────┬──────────────┬──────────────┬──────────────┬──────────────┤
│   Explorer   │    Monaco    │   Browser    │    Agent     │    Critic    │
│   (Files)    │   Editor     │   Preview    │    Panel     │    Panel     │
│              │              │  (CDP frames)│  (Markdown)  │  (Insights)  │
├──────────────┴──────────────┴──────────────┴──────────────┴──────────────┤
│                           Terminal (xterm.js)                             │
└────────────────────────────────┬─────────────────────────────────────────┘
                                 │
              ┌──────────────────┴──────────────────┐
              │ WebSocket (/ws/agent)               │ Socket.io (/browser)
              │ Agent events                        │ Browser frames
              ▼                                     ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                          BACKEND (FastAPI + Python)                        │
├─────────────────┬─────────────────┬─────────────────┬──────────────────────┤
│   Agent Service │  Browser Service │   File Service  │   Terminal Service   │
│  (Claude SDK)   │  (Puppeteer/CDP) │   (Local FS)    │   (PTY subprocess)   │
├─────────────────┴─────────────────┴─────────────────┴──────────────────────┤
│                         MCP Server Manager                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │ Chrome DevTools │  │  Custom Tools   │  │   Critic Agent  │             │
│  │      MCP        │  │     MCP         │  │   (Observer)    │             │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘             │
├────────────────────────────────────────────────────────────────────────────┤
│                          .claude/ Integration                               │
│   settings.json  │  hooks/  │  logs/  │  memory/  │  skills/  │  rules/    │
└────────────────────────────────────────────────────────────────────────────┘
```

### Data Flows

#### 1. Agent Streaming (Markdown Rendering)

```
User Input
    │
    ▼
WebSocket (/ws/agent)
    │
    ▼
ClaudeSDKClient.query(prompt, options={include_partial_messages: True})
    │
    ▼
async for message in client.receive_response():
    │
    ├─ ThinkingBlock → WS emit → React → Collapsible thinking trace
    ├─ ToolUseBlock  → WS emit → React → Action card (tool, params, status)
    ├─ ToolResult    → WS emit → React → Result display
    └─ TextBlock     → WS emit → React → Response markdown
```

#### 2. Browser Preview (CDP Screencast)

```
Agent calls chrome-devtools MCP tool
    │
    ▼
Puppeteer executes command
    │
    ▼
CDP: Page.startScreencast(format: 'jpeg', quality: 70)
    │
    ▼
Page.screencastFrame events
    │
    ▼
Socket.io emit('frame', base64_jpeg)
    │
    ▼
React: <img src={`data:image/jpeg;base64,${frame}`} />
    │
    ▼
User click → Socket.io emit('click', {x, y}) → Puppeteer.click()
```

#### 3. Critic Agent (Async Observer)

```
Agent events stream
    │
    ▼
Event copied to async queue (non-blocking)
    │
    ▼
Critic service background task (every 5 seconds)
    │
    ▼
Batch analyze with Haiku model
    │
    ▼
Generate insights
    │
    ▼
Push to frontend via separate channel
    │
    ▼
CriticPanel displays insights
```

---

## Key Architecture Decisions

Three Architecture Decision Records (ADRs) were created:

### ADR-001: Dual Streaming Channels

**Decision**: Use WebSocket for agent events, Socket.io for browser frames.

**Rationale**:
- Prevents frame floods from blocking agent messages
- Different QoS requirements (reliable vs best-effort)
- Independent throttling and quality control

**Files**: `docs/adr/ADR-001-dual-streaming.md`

### ADR-002: Critic Agent Pattern

**Decision**: Async observer with event queue, periodic batch analysis.

**Rationale**:
- Main agent performance unaffected
- Can be enabled/disabled independently
- Uses lightweight Haiku model for analysis

**Critic Watches For**:
1. Errors the agent ignores
2. Better patterns available in codebase
3. Agent going in circles
4. When user input would help

**Files**: `docs/adr/ADR-002-critic-pattern.md`

### ADR-003: Hook Integration Strategy

**Decision**: Extend existing `.claude/` infrastructure, don't duplicate.

**Rationale**:
- Single source of truth for tool traces
- Existing hooks continue to work
- Non-destructive to CLI workflow

**Integration Points**:
- Read from `.claude/logs/tool-trace.jsonl`
- Extend `.claude/settings.json`
- Surface rules, skills, memory in UI

**Files**: `docs/adr/ADR-003-hook-integration.md`

---

## Project Structure

```
interface/
├── frontend/                    # React + TypeScript + Vite
│   ├── src/
│   │   ├── components/
│   │   │   ├── Layout/          # Panel management, resizing
│   │   │   │   ├── MainLayout.tsx
│   │   │   │   ├── PanelContainer.tsx
│   │   │   │   └── ResizablePanel.tsx
│   │   │   ├── Explorer/        # File tree
│   │   │   │   ├── FileTree.tsx
│   │   │   │   ├── FileNode.tsx
│   │   │   │   └── useFileTree.ts
│   │   │   ├── Editor/          # Monaco wrapper
│   │   │   │   ├── CodeEditor.tsx
│   │   │   │   ├── EditorTabs.tsx
│   │   │   │   └── useEditor.ts
│   │   │   ├── Terminal/        # xterm.js
│   │   │   │   ├── Terminal.tsx
│   │   │   │   └── useTerminal.ts
│   │   │   ├── AgentPanel/      # Thinking, actions, output
│   │   │   │   ├── AgentPanel.tsx
│   │   │   │   ├── ThinkingBlock.tsx
│   │   │   │   ├── ToolActionCard.tsx
│   │   │   │   ├── MessageRenderer.tsx
│   │   │   │   └── useAgentStream.ts
│   │   │   ├── BrowserPreview/  # CDP screencast viewer
│   │   │   │   ├── BrowserPreview.tsx
│   │   │   │   ├── ConsolePanel.tsx
│   │   │   │   └── useBrowserStream.ts
│   │   │   └── CriticPanel/     # Observer insights
│   │   │       ├── CriticPanel.tsx
│   │   │       ├── InsightCard.tsx
│   │   │       └── useCriticStream.ts
│   │   ├── hooks/               # Shared React hooks
│   │   │   ├── useWebSocket.ts
│   │   │   ├── useSocketIO.ts
│   │   │   └── useLocalStorage.ts
│   │   ├── services/            # API clients
│   │   │   ├── fileService.ts
│   │   │   └── agentService.ts
│   │   ├── types/               # TypeScript interfaces
│   │   │   ├── agent.ts
│   │   │   ├── file.ts
│   │   │   └── browser.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── index.html
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   └── package.json
│
├── backend/                     # FastAPI + Python
│   ├── api/
│   │   ├── routes/
│   │   │   ├── agent.py         # Agent WebSocket endpoint
│   │   │   ├── files.py         # File operations REST API
│   │   │   ├── terminal.py      # Terminal PTY management
│   │   │   └── browser.py       # Browser control endpoints
│   │   ├── websocket.py         # WebSocket connection manager
│   │   └── deps.py              # FastAPI dependencies
│   ├── services/
│   │   ├── agent_service.py     # ClaudeSDKClient wrapper
│   │   ├── browser_service.py   # Puppeteer + CDP screencast
│   │   ├── critic_service.py    # Observer agent
│   │   ├── file_service.py      # Local filesystem ops
│   │   └── terminal_service.py  # PTY subprocess management
│   ├── mcp/
│   │   ├── custom_tools.py      # @tool definitions
│   │   └── server.py            # MCP server setup
│   ├── models/
│   │   ├── agent.py             # Pydantic models for agent events
│   │   ├── file.py              # File operation models
│   │   └── browser.py           # Browser event models
│   ├── config.py                # Settings and configuration
│   ├── main.py                  # FastAPI app entry point
│   └── requirements.txt
│
├── docs/
│   ├── adr/                     # Architecture Decision Records
│   │   ├── ADR-001-dual-streaming.md
│   │   ├── ADR-002-critic-pattern.md
│   │   └── ADR-003-hook-integration.md
│   └── THE_INTERFACE_IMPLEMENTATION_PLAN.md  # This document
│
├── .claude/                     # EXISTING - extend, don't replace
│   ├── agents/                  # Agent definitions
│   ├── commands/                # Custom slash commands
│   ├── context/                 # Shared context files
│   ├── hooks/                   # Pre/post tool hooks
│   ├── logs/                    # Tool traces, session logs
│   ├── memory/                  # Agent memory files
│   ├── rules/                   # Mandatory protocols
│   ├── skills/                  # Technical patterns
│   └── settings.json            # Claude Code configuration
│
├── pyproject.toml               # Python project config
├── package.json                 # Root package.json (workspace)
└── README.md
```

---

## API Contracts

### WebSocket: Agent Events

**Endpoint**: `ws://localhost:8000/ws/agent`

#### Client → Server

```typescript
// Send user message
{ type: "message", content: "user prompt here" }

// Abort current generation
{ type: "abort" }

// Resume session
{ type: "resume", session_id: "uuid" }
```

#### Server → Client

```typescript
// Thinking block (collapsible)
{
  type: "thinking",
  content: "Let me analyze this...",
  timestamp: "2025-12-27T10:00:00Z"
}

// Tool use started
{
  type: "tool_use",
  id: "tool_123",
  name: "Read",
  params: { file_path: "/path/to/file" },
  status: "started",
  timestamp: "2025-12-27T10:00:01Z"
}

// Tool result
{
  type: "tool_result",
  id: "tool_123",
  name: "Read",
  result: { content: "file contents..." },
  status: "completed",
  timestamp: "2025-12-27T10:00:02Z"
}

// Text output
{
  type: "text",
  content: "Here's what I found...",
  timestamp: "2025-12-27T10:00:03Z"
}

// Generation complete
{
  type: "done",
  session_id: "uuid",
  timestamp: "2025-12-27T10:00:04Z"
}

// Error
{
  type: "error",
  message: "Something went wrong",
  code: "AGENT_ERROR",
  timestamp: "2025-12-27T10:00:05Z"
}
```

### Socket.io: Browser Events

**Namespace**: `/browser`

#### Server → Client

```typescript
// Browser frame (JPEG)
{
  event: "frame",
  data: "base64_encoded_jpeg_string",
  width: 1280,
  height: 720,
  timestamp: 1703674800000
}

// Console message
{
  event: "console",
  level: "log" | "warn" | "error" | "info",
  message: "Console output here",
  source: "https://example.com",
  line: 42,
  timestamp: 1703674800000
}

// Page navigation
{
  event: "navigation",
  url: "https://example.com/page",
  title: "Page Title",
  timestamp: 1703674800000
}
```

#### Client → Server

```typescript
// User click (for interactive mode)
{
  event: "click",
  x: 100,
  y: 200,
  button: "left" | "right"
}

// User input
{
  event: "input",
  selector: "#input-field",
  value: "typed text"
}

// User scroll
{
  event: "scroll",
  deltaX: 0,
  deltaY: 100
}
```

### REST API: Files

**Base**: `http://localhost:8000/api/files`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/tree?path=/` | Get file tree |
| GET | `/{path}` | Read file content |
| PUT | `/{path}` | Write file content |
| DELETE | `/{path}` | Delete file |
| POST | `/mkdir` | Create directory |

### REST API: Browser

**Base**: `http://localhost:8000/api/browser`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/start` | Launch Puppeteer |
| POST | `/stop` | Close browser |
| GET | `/status` | Get browser status |
| POST | `/navigate` | Navigate to URL |
| POST | `/screenshot` | Take screenshot |

### REST API: Critic

**Base**: `http://localhost:8000/api/critic`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/insights` | Get latest insights |
| POST | `/toggle` | Enable/disable critic |
| GET | `/status` | Get critic status |

---

## Implementation Phases

### Phase 1: Agent Streaming + Markdown (Priority 1)

**Goal**: User can chat with Claude, see streaming thinking/actions/output.

**Deliverables**:
- [ ] FastAPI backend with WebSocket endpoint
- [ ] `ClaudeSDKClient` integration with streaming
- [ ] React AgentPanel component
- [ ] Markdown rendering with react-markdown
- [ ] Collapsible thinking blocks
- [ ] Tool action cards with status indicators
- [ ] Basic input field for user messages

**Key Implementation Details**:
```python
# backend/services/agent_service.py
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

class AgentService:
    async def stream_response(self, prompt: str):
        options = ClaudeAgentOptions(
            include_partial_messages=True,  # Critical for streaming
        )
        async for message in self.client.query(prompt, options):
            yield self._transform_to_event(message)
```

**Dependencies**: None (can start immediately)

**Skills to Reference**:
- `.claude/skills/claude-agent-sdk-patterns/SKILL.md`
- `.claude/skills/websocket-streaming.md`
- `.claude/skills/frontend-patterns/SKILL.md`

---

### Phase 2: Monaco Editor (Priority 2)

**Goal**: Full code editing experience with file explorer.

**Deliverables**:
- [ ] Monaco Editor React wrapper
- [ ] File explorer tree component
- [ ] File operations REST API
- [ ] Multi-tab editing
- [ ] Syntax highlighting (all languages)
- [ ] Basic search in file
- [ ] Save/autosave functionality

**Key Implementation Details**:
```typescript
// frontend/src/components/Editor/CodeEditor.tsx
import Editor from '@monaco-editor/react';

const CodeEditor = ({ file, onChange }) => (
  <Editor
    height="100%"
    language={detectLanguage(file.path)}
    value={file.content}
    onChange={onChange}
    options={{
      minimap: { enabled: true },
      fontSize: 14,
      wordWrap: 'on',
    }}
  />
);
```

**Dependencies**: Phase 1 (agent needs file operations)

---

### Phase 3: Browser Preview (Priority 3)

**Goal**: Embedded Chrome controlled by agent, live preview for user.

**Deliverables**:
- [ ] Puppeteer service with CDP session
- [ ] Chrome DevTools MCP integration
- [ ] CDP Screencast implementation
- [ ] Socket.io streaming to frontend
- [ ] BrowserPreview React component
- [ ] Console log capture and display
- [ ] User input relay (optional)

**Key Implementation Details**:
```python
# backend/services/browser_service.py
from pyppeteer import launch

class BrowserService:
    async def start_screencast(self, socket):
        client = await self.page.target.createCDPSession()
        await client.send('Page.startScreencast', {
            'format': 'jpeg',
            'quality': 70,
            'everyNthFrame': 1
        })

        client.on('Page.screencastFrame', lambda frame:
            socket.emit('frame', frame['data']))
```

**Dependencies**: Phase 1 (agent needs browser tools)

**External**: Chrome DevTools MCP server installation

---

### Phase 4: Critic Agent (Priority 4)

**Goal**: Observer agent providing insights on main agent's work.

**Deliverables**:
- [ ] Async event queue for observation
- [ ] Critic service with Haiku model
- [ ] Periodic batch analysis
- [ ] Insights data model
- [ ] CriticPanel React component
- [ ] Enable/disable toggle
- [ ] Insight categories (error, suggestion, summary)

**Key Implementation Details**:
```python
# backend/services/critic_service.py
class CriticService:
    SYSTEM_PROMPT = """You are a code review critic observing an AI coding agent.
    Analyze the agent's actions and identify:
    1. Errors or issues the agent missed
    2. Better approaches available
    3. Patterns the agent is repeating inefficiently
    4. When user input would be helpful

    Be concise. Only report high-confidence observations."""

    async def analyze_batch(self, events: list) -> list[Insight]:
        response = await self.client.messages.create(
            model="claude-3-haiku-20240307",
            system=self.SYSTEM_PROMPT,
            messages=[{"role": "user", "content": json.dumps(events)}]
        )
        return self._parse_insights(response)
```

**Dependencies**: Phase 1 (needs agent event stream)

---

### Phase 5: Polish & Deploy

**Goal**: Production-ready with authentication.

**Deliverables**:
- [ ] Google OAuth integration
- [ ] Session persistence
- [ ] Settings UI (theme, preferences)
- [ ] MCP server configuration UI
- [ ] Error handling and recovery
- [ ] Cloud Run deployment
- [ ] CI/CD pipeline

**Dependencies**: All previous phases

---

## Session Insights

### Key Research Findings

#### Claude Agent SDK
- **Package**: `pip install claude-agent-sdk`
- **Streaming**: Use `include_partial_messages=True` in options
- **Custom Tools**: `@tool` decorator + `create_sdk_mcp_server()`
- **Message Types**: `ThinkingBlock`, `ToolUseBlock`, `TextBlock`, `ResultMessage`
- **Existing Pattern**: `.claude/skills/claude-agent-sdk-patterns/SKILL.md`
- **Existing Hook**: `.claude/hooks/tool_trace_logger.py` logs all tool calls

#### Browser Embedding
- **Recommended**: Chrome DevTools MCP (Google) - 26 production-ready tools
- **Streaming**: CDP Screencast + Socket.io (~100-300ms latency)
- **Installation**: `claude mcp add chrome-devtools npx chrome-devtools-mcp@latest`
- **Alternative**: Playwright MCP (Microsoft) - 40+ tools

#### Frontend Terminology (For User Reference)
- **Vite** = Build tool (compiles/bundles code) - like Webpack but faster
- **Tailwind CSS** = Styling framework (utility CSS classes)
- **TanStack Query** = Data fetching library (API calls, caching)
- These are **complementary**, not alternatives

### Identified Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| Context window exhaustion | High | Add summarization/windowing for long sessions |
| Browser screencast bandwidth | Medium | Adaptive quality + framerate throttling |
| Critic slowing main agent | Medium | Async, non-blocking observation |
| Hook conflicts with CLI | Medium | Read-only integration, extend don't replace |

### Architecture Validation

Sage (Solution Architect) validated the architecture with refinements:
- **Approved**: Overall architecture is sound
- **Refinement**: Dual streaming channels (WebSocket + Socket.io)
- **Refinement**: Critic as async observer pattern
- **Refinement**: Extend `.claude/` infrastructure, don't duplicate

---

## Open Questions

These questions should be resolved before or during implementation:

1. **Terminal Integration**: Should the terminal be a separate xterm.js instance or integrate with the agent's Bash tool execution?

2. **File Watching**: Should the editor watch for external file changes (e.g., when agent modifies files)?

3. **Session Persistence**: How should agent sessions be persisted? (localStorage, backend DB, files?)

4. **Multi-Agent**: Could multiple agents run simultaneously, or always single agent?

5. **Keyboard Shortcuts**: What shortcuts should be available? (Cmd+K for chat, etc.)

6. **Theme**: Dark mode default? User preference?

7. **Layout Persistence**: Should panel sizes/arrangement persist across sessions?

---

## References

### Project Files
- ADRs: `docs/adr/ADR-001-*.md`, `docs/adr/ADR-002-*.md`, `docs/adr/ADR-003-*.md`
- Skills: `.claude/skills/claude-agent-sdk-patterns/SKILL.md`
- Skills: `.claude/skills/frontend-patterns/SKILL.md`
- Skills: `.claude/skills/websocket-streaming.md`
- Existing Hooks: `.claude/hooks/tool_trace_logger.py`

### External Resources
- [Claude Agent SDK GitHub](https://github.com/anthropics/claude-agent-sdk-python)
- [Chrome DevTools MCP](https://github.com/anthropics/claude-mcp-servers/tree/main/chrome-devtools)
- [Monaco Editor React](https://github.com/suren-atoyan/monaco-react)
- [xterm.js](https://xtermjs.org/)
- [Puppeteer CDP Screencast](https://github.com/nickyout/puppeteer-screencast)

### Session Agents
- **Scout** (General Worker): Researched Claude Agent SDK and browser embedding
- **Sage** (Solution Architect): Validated architecture, created ADRs

---

## Next Steps (Pending Approval)

Once this plan is approved:

1. **Scaffold Project**: Create directory structure, package.json, pyproject.toml
2. **Phase 1 Sprint**: Kai implements agent streaming + markdown rendering
3. **Iterate**: Review each phase before proceeding to next

---

*Document created by Ezio (Main Orchestrator) - 2025-12-27*
