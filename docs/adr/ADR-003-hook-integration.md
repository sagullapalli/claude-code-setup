# ADR-003: Hook Integration Strategy

## Status
Proposed

## Context
The Interface wraps Claude Code CLI, which has an existing hook system in `.claude/`:

```
.claude/
├── hooks/           # Python scripts for pre/post tool events
├── settings.json    # Hook configuration
├── logs/            # Tool traces, session logs
├── rules/           # Mandatory protocols
├── skills/          # Technical patterns
├── memory/          # Agent memory files
├── agents/          # Agent definitions
└── context/         # Shared context
```

The existing `tool_trace_logger.py` already logs all tool calls to `.claude/logs/tool-trace.jsonl`.

**Question**: Should The Interface duplicate this functionality or integrate with existing infrastructure?

## Decision
**Extend hooks, don't duplicate.** The Interface backend will:

1. **Read from existing logs** (`.claude/logs/`) for trace visualization
2. **Configure hooks via settings.json** (not bypass them)
3. **Add Interface-specific hooks** that write to the same log format
4. **Leverage existing infrastructure** wherever possible

### Integration Points

| `.claude/` Component | Interface Integration |
|---------------------|----------------------|
| `hooks/` | Add Interface hooks, respect existing ones |
| `logs/` | Read for trace visualization, critic analysis |
| `settings.json` | Extend with Interface-specific settings |
| `rules/` | Load and display in UI (enforcement by Claude) |
| `skills/` | Surface in UI for reference |
| `memory/` | Display agent memory, allow edits |
| `agents/` | Load agent definitions for UI |
| `context/` | Include in agent context |

## Consequences

### Positive
- Single source of truth for tool traces
- Existing hooks continue to work
- No duplicate logging infrastructure
- User's customizations preserved
- Consistent with Claude Code CLI behavior

### Negative
- Dependency on `.claude/` folder structure
- Must handle file format changes
- Can't modify hooks without affecting CLI usage

### Neutral
- Interface becomes a "view" into `.claude/` rather than replacement

## Implementation Pattern

### 1. Log Reading (Read-Only Integration)

```python
# backend/services/trace_service.py

import json
from pathlib import Path

class TraceService:
    def __init__(self, claude_dir: Path = Path(".claude")):
        self.logs_dir = claude_dir / "logs"

    async def get_recent_traces(self, limit: int = 100) -> list[ToolTrace]:
        """Read from existing tool-trace.jsonl"""
        trace_file = self.logs_dir / "tool-trace.jsonl"
        traces = []
        async with aiofiles.open(trace_file) as f:
            async for line in f:
                traces.append(json.loads(line))
        return traces[-limit:]

    async def stream_traces(self) -> AsyncGenerator[ToolTrace, None]:
        """Watch for new entries (tail -f style)"""
        trace_file = self.logs_dir / "tool-trace.jsonl"
        async for line in tail_file(trace_file):
            yield json.loads(line)
```

### 2. Settings Extension

```json
// .claude/settings.json - add Interface section
{
  "hooks": {
    "PostToolUse": [
      {
        "type": "command",
        "command": "python .claude/hooks/tool_trace_logger.py"
      }
    ]
  },
  "interface": {
    "enabled": true,
    "browser_preview": true,
    "critic_enabled": true,
    "theme": "dark"
  }
}
```

### 3. Interface-Specific Hook

```python
# .claude/hooks/interface_notifier.py
# Notifies Interface backend of events via local socket

import socket
import json
import os

def notify_interface(event: dict):
    """Send event to Interface backend if running"""
    try:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect("/tmp/interface.sock")
        sock.send(json.dumps(event).encode())
        sock.close()
    except:
        pass  # Interface not running, ignore

if __name__ == "__main__":
    event = json.loads(os.environ.get("TOOL_EVENT", "{}"))
    notify_interface(event)
```

## File Format Compatibility

The Interface must handle the existing log format:

```jsonl
// .claude/logs/tool-trace.jsonl
{"timestamp": "2025-12-27T08:00:00Z", "tool": "Read", "params": {...}, "result": {...}}
{"timestamp": "2025-12-27T08:00:01Z", "tool": "Edit", "params": {...}, "result": {...}}
```

If format changes, the TraceService should handle gracefully (version detection).

## UI Integration

| Component | Data Source |
|-----------|-------------|
| Thinking Trace Panel | Real-time stream + `.claude/logs/tool-trace.jsonl` |
| Rules Panel | `.claude/rules/*.md` |
| Skills Browser | `.claude/skills/**/*.md` |
| Memory Editor | `.claude/memory/*.md` |
| Agent Selector | `.claude/agents/*.md` |

## Alternatives Considered

1. **Bypass hooks entirely** - Rejected: Loses existing functionality
2. **Fork/copy hooks** - Rejected: Maintenance burden, divergence
3. **Custom logging format** - Rejected: Incompatible with CLI usage
4. **No log integration** - Rejected: Misses opportunity for unified experience

## Migration Path

For users with existing `.claude/` setup:
1. Interface detects existing configuration
2. Adds Interface-specific settings (non-destructive)
3. Works alongside existing hooks
4. No breaking changes to CLI workflow

## References
- Existing hook: `.claude/hooks/tool_trace_logger.py`
- Settings: `.claude/settings.json`
- Sage validation (2025-12-27)
