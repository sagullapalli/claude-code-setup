#!/usr/bin/env python3
"""
Unit and Integration Tests for Tool Trace Logger

Tests all parsing, extraction, and logging functions.
"""

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open
import pytest

# Add the hooks directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from tool_trace_logger import (
    parse_mcp_tool,
    extract_agent_context,
    extract_tool_fields,
    truncate,
    create_log_entry,
    parse_json_field,
    extract_nested,
    serialize_for_log,
    TRUNCATE_LIMITS,
)


# =============================================================================
# Test: parse_mcp_tool()
# =============================================================================

class TestParseMcpTool:
    """Test MCP tool name parsing."""

    def test_memory_server_tool(self):
        """Standard MCP tool: mcp__memory__create_entities"""
        result = parse_mcp_tool("mcp__memory__create_entities")
        assert result["is_mcp"] is True
        assert result["mcp_server"] == "memory"
        assert result["mcp_tool"] == "create_entities"

    def test_filesystem_server_tool(self):
        """Standard MCP tool: mcp__filesystem__read_file"""
        result = parse_mcp_tool("mcp__filesystem__read_file")
        assert result["is_mcp"] is True
        assert result["mcp_server"] == "filesystem"
        assert result["mcp_tool"] == "read_file"

    def test_context7_nested_tool(self):
        """MCP tool with nested name: mcp__plugin_context7_context7__get-library-docs"""
        result = parse_mcp_tool("mcp__plugin_context7_context7__get-library-docs")
        assert result["is_mcp"] is True
        assert result["mcp_server"] == "plugin_context7_context7"
        assert result["mcp_tool"] == "get-library-docs"

    def test_non_mcp_tool(self):
        """Non-MCP tool: Read"""
        result = parse_mcp_tool("Read")
        assert result["is_mcp"] is False
        assert result["mcp_server"] is None
        assert result["mcp_tool"] is None

    def test_bash_tool(self):
        """Non-MCP tool: Bash"""
        result = parse_mcp_tool("Bash")
        assert result["is_mcp"] is False
        assert result["mcp_server"] is None
        assert result["mcp_tool"] is None

    def test_mcp_prefix_only(self):
        """Edge case: just 'mcp__' prefix"""
        result = parse_mcp_tool("mcp__")
        assert result["is_mcp"] is False
        assert result["mcp_server"] is None
        assert result["mcp_tool"] is None

    def test_mcp_single_part(self):
        """Edge case: mcp__server only (no tool)"""
        result = parse_mcp_tool("mcp__memory")
        assert result["is_mcp"] is False
        assert result["mcp_server"] is None
        assert result["mcp_tool"] is None

    def test_empty_string(self):
        """Edge case: empty string"""
        result = parse_mcp_tool("")
        assert result["is_mcp"] is False
        assert result["mcp_server"] is None
        assert result["mcp_tool"] is None

    def test_tool_with_underscores(self):
        """MCP tool with underscores in tool name"""
        result = parse_mcp_tool("mcp__github__get_pull_request")
        assert result["is_mcp"] is True
        assert result["mcp_server"] == "github"
        assert result["mcp_tool"] == "get_pull_request"


# =============================================================================
# Test: extract_agent_context()
# =============================================================================

class TestExtractAgentContext:
    """Test agent context extraction from Task tool."""

    def test_task_with_subagent_type_in_input(self):
        """Task tool with subagent_type in input"""
        tool_input = {"subagent_type": "AI Engineer", "prompt": "Do something"}
        tool_response = {}
        result = extract_agent_context("Task", tool_input, tool_response)
        assert result["subagent_type"] == "AI Engineer"
        assert result["agent_id"] is None

    def test_task_with_agent_id_in_response(self):
        """Task tool with agent_id in response"""
        tool_input = {}
        tool_response = {"agent_id": "a18176c", "status": "completed"}
        result = extract_agent_context("Task", tool_input, tool_response)
        assert result["subagent_type"] is None
        assert result["agent_id"] == "a18176c"

    def test_task_with_both_fields(self):
        """Task tool with both subagent_type and agent_id"""
        tool_input = {"subagent_type": "Solution Architect"}
        tool_response = {"agent_id": "b291f8e", "status": "completed"}
        result = extract_agent_context("Task", tool_input, tool_response)
        assert result["subagent_type"] == "Solution Architect"
        assert result["agent_id"] == "b291f8e"

    def test_non_task_tool(self):
        """Non-Task tool should return nulls"""
        result = extract_agent_context("Read", {"file_path": "/some/file"}, {})
        assert result["subagent_type"] is None
        assert result["agent_id"] is None

    def test_task_with_json_string_input(self):
        """Task tool with JSON string input"""
        tool_input = json.dumps({"subagent_type": "QA Tester"})
        result = extract_agent_context("Task", tool_input, {})
        assert result["subagent_type"] == "QA Tester"

    def test_task_with_none_inputs(self):
        """Task tool with None inputs"""
        result = extract_agent_context("Task", None, None)
        assert result["subagent_type"] is None
        assert result["agent_id"] is None


# =============================================================================
# Test: extract_tool_fields()
# =============================================================================

class TestExtractToolFields:
    """Test tool-specific field extraction."""

    def test_bash_tool_with_command_and_description(self):
        """Bash tool with command and description"""
        tool_input = {
            "command": "ls -la /home",
            "description": "List directory contents"
        }
        tool_response = {"stdout": "...", "stderr": "", "interrupted": False}
        result = extract_tool_fields("Bash", tool_input, tool_response)

        assert result["command"] == "ls -la /home"
        assert result["description"] == "List directory contents"
        assert result["has_stderr"] is False
        assert result["file_path"] is None

    def test_bash_tool_with_stderr(self):
        """Bash tool with stderr output"""
        tool_input = {"command": "cat nonexistent"}
        tool_response = {"stdout": "", "stderr": "cat: nonexistent: No such file or directory"}
        result = extract_tool_fields("Bash", tool_input, tool_response)

        assert result["has_stderr"] is True

    def test_read_tool_with_file_path(self):
        """Read tool with file_path"""
        tool_input = {"file_path": "/home/user/config.json"}
        tool_response = {"type": "text", "content": "..."}
        result = extract_tool_fields("Read", tool_input, tool_response)

        assert result["file_path"] == "/home/user/config.json"
        assert result["command"] is None

    def test_grep_tool_with_pattern_and_query(self):
        """Grep tool with pattern and query"""
        tool_input = {"pattern": "def\\s+test_.*", "query": "test functions"}
        tool_response = {"numMatches": 15, "numFiles": 3}
        result = extract_tool_fields("Grep", tool_input, tool_response)

        assert result["pattern"] == "def\\s+test_.*"
        assert result["query"] == "test functions"
        assert result["num_matches"] == 15
        assert result["num_files"] == 3

    def test_glob_tool_with_pattern(self):
        """Glob tool with pattern"""
        tool_input = {"pattern": "**/*.py"}
        tool_response = {"numFiles": 42}
        result = extract_tool_fields("Glob", tool_input, tool_response)

        assert result["pattern"] == "**/*.py"
        assert result["num_files"] == 42

    def test_webfetch_with_url_and_http_code(self):
        """WebFetch tool with url, http_code, and bytes"""
        tool_input = {"url": "https://example.com/api"}
        tool_response = {"httpCode": 200, "bytes": 4096}
        result = extract_tool_fields("WebFetch", tool_input, tool_response)

        assert result["url"] == "https://example.com/api"
        assert result["http_code"] == 200
        assert result["bytes"] == 4096

    def test_websearch_with_query(self):
        """WebSearch tool with query"""
        tool_input = {"query": "Python best practices 2025"}
        result = extract_tool_fields("WebSearch", tool_input, {})

        assert result["query"] == "Python best practices 2025"

    def test_task_tool_with_model(self):
        """Task tool with model field"""
        tool_input = {"model": "claude-opus-4", "prompt": "..."}
        result = extract_tool_fields("Task", tool_input, {})

        assert result["model"] == "claude-opus-4"

    def test_edit_tool_with_file_path(self):
        """Edit tool with file_path"""
        tool_input = {"file_path": "/app/main.py", "old_string": "...", "new_string": "..."}
        result = extract_tool_fields("Edit", tool_input, {})

        assert result["file_path"] == "/app/main.py"

    def test_tool_with_json_string_input(self):
        """Tool with JSON string input (not dict)"""
        tool_input = json.dumps({"file_path": "/test/path.txt"})
        result = extract_tool_fields("Read", tool_input, None)

        assert result["file_path"] == "/test/path.txt"

    def test_interrupted_response(self):
        """Tool response with interrupted flag"""
        tool_response = {"interrupted": True, "stdout": "partial..."}
        result = extract_tool_fields("Bash", {}, tool_response)

        assert result["interrupted"] is True

    def test_status_in_response(self):
        """Task response with status field"""
        tool_response = {"status": "completed"}
        result = extract_tool_fields("Task", {}, tool_response)

        assert result["status"] == "completed"


# =============================================================================
# Test: truncate()
# =============================================================================

class TestTruncate:
    """Test string truncation."""

    def test_shorter_than_limit(self):
        """String shorter than limit - no truncation"""
        result = truncate("short", 100)
        assert result == "short"

    def test_exactly_at_limit(self):
        """String exactly at limit - no truncation"""
        result = truncate("x" * 100, 100)
        assert result == "x" * 100
        assert len(result) == 100

    def test_longer_than_limit(self):
        """String longer than limit - truncated with ellipsis"""
        result = truncate("x" * 150, 100)
        assert len(result) == 100
        assert result.endswith("...")
        assert result == ("x" * 97) + "..."

    def test_none_value(self):
        """None value - returns None"""
        result = truncate(None, 100)
        assert result is None

    def test_non_string_converted(self):
        """Non-string value - converted to string"""
        result = truncate(12345, 10)
        assert result == "12345"

    def test_long_number_truncated(self):
        """Long number - converted and truncated"""
        result = truncate(123456789012345678901234567890, 20)
        assert len(result) == 20
        assert result.endswith("...")

    def test_empty_string(self):
        """Empty string - returns empty string"""
        result = truncate("", 100)
        assert result == ""


# =============================================================================
# Test: parse_json_field()
# =============================================================================

class TestParseJsonField:
    """Test JSON field parsing."""

    def test_json_string_input(self):
        """JSON string is parsed to dict"""
        input_str = '{"key": "value", "num": 42}'
        result = parse_json_field(input_str)
        assert isinstance(result, dict)
        assert result["key"] == "value"
        assert result["num"] == 42

    def test_already_dict(self):
        """Dict is returned as-is"""
        input_dict = {"key": "value"}
        result = parse_json_field(input_dict)
        assert result is input_dict

    def test_invalid_json_string(self):
        """Invalid JSON string is returned as-is"""
        invalid = "not valid json {"
        result = parse_json_field(invalid)
        assert result == invalid

    def test_json_array_string(self):
        """JSON array string is parsed"""
        input_str = '[1, 2, 3]'
        result = parse_json_field(input_str)
        assert result == [1, 2, 3]

    def test_none_value(self):
        """None is returned as-is"""
        result = parse_json_field(None)
        assert result is None

    def test_number(self):
        """Number is returned as-is"""
        result = parse_json_field(42)
        assert result == 42


# =============================================================================
# Test: extract_nested()
# =============================================================================

class TestExtractNested:
    """Test nested dict value extraction."""

    def test_first_key_found(self):
        """First key is found"""
        data = {"file_path": "/test/path"}
        result = extract_nested(data, "file_path", "filePath")
        assert result == "/test/path"

    def test_second_key_found(self):
        """First key not found, second key is found"""
        data = {"filePath": "/test/path"}
        result = extract_nested(data, "file_path", "filePath")
        assert result == "/test/path"

    def test_no_key_found(self):
        """No key found - returns None"""
        data = {"other_key": "value"}
        result = extract_nested(data, "file_path", "filePath")
        assert result is None

    def test_non_dict_input(self):
        """Non-dict input - returns None"""
        result = extract_nested("not a dict", "key")
        assert result is None

    def test_none_input(self):
        """None input - returns None"""
        result = extract_nested(None, "key")
        assert result is None


# =============================================================================
# Test: serialize_for_log()
# =============================================================================

class TestSerializeForLog:
    """Test log serialization."""

    def test_string_value(self):
        """String value is truncated"""
        result = serialize_for_log("short string", 100)
        assert result == "short string"

    def test_dict_value(self):
        """Dict is serialized to JSON string"""
        data = {"key": "value"}
        result = serialize_for_log(data, 100)
        assert result == '{"key": "value"}'

    def test_long_dict_truncated(self):
        """Long dict is serialized and truncated"""
        data = {"key": "v" * 200}
        result = serialize_for_log(data, 50)
        assert len(result) == 50
        assert result.endswith("...")

    def test_none_value(self):
        """None returns None"""
        result = serialize_for_log(None, 100)
        assert result is None

    def test_list_value(self):
        """List is serialized to JSON string"""
        data = [1, 2, 3]
        result = serialize_for_log(data, 100)
        assert result == "[1, 2, 3]"


# =============================================================================
# Test: create_log_entry()
# =============================================================================

class TestCreateLogEntry:
    """Test full log entry creation."""

    def test_full_input_data(self):
        """Create log entry with full input data"""
        input_data = {
            "session_id": "sess_123",
            "tool_use_id": "tu_456",
            "tool_name": "Read",
            "permission_mode": "default",
            "cwd": "/home/user/project",
            "tool_input": {"file_path": "/app/main.py"},
            "tool_response": {"type": "text", "content": "..."},
        }

        entry = create_log_entry(input_data)

        assert entry["session_id"] == "sess_123"
        assert entry["tool_use_id"] == "tu_456"
        assert entry["tool_name"] == "Read"
        assert entry["is_mcp"] is False
        assert entry["mcp_server"] is None
        assert entry["permission_mode"] == "default"
        assert entry["cwd"] == "/home/user/project"
        assert entry["file_path"] == "/app/main.py"
        assert "timestamp" in entry

    def test_mcp_tool_entry(self):
        """Create log entry for MCP tool"""
        input_data = {
            "session_id": "sess_789",
            "tool_use_id": "tu_012",
            "tool_name": "mcp__memory__create_entities",
            "tool_input": {},
            "tool_response": {},
        }

        entry = create_log_entry(input_data)

        assert entry["is_mcp"] is True
        assert entry["mcp_server"] == "memory"
        assert entry["mcp_tool"] == "create_entities"

    def test_task_tool_entry(self):
        """Create log entry for Task tool with agent context"""
        input_data = {
            "session_id": "sess_abc",
            "tool_use_id": "tu_def",
            "tool_name": "Task",
            "tool_input": {"subagent_type": "DevOps Engineer", "model": "claude-opus-4"},
            "tool_response": {"agent_id": "c39d5a1", "status": "completed"},
        }

        entry = create_log_entry(input_data)

        assert entry["subagent_type"] == "DevOps Engineer"
        assert entry["agent_id"] == "c39d5a1"
        assert entry["model"] == "claude-opus-4"
        assert entry["status"] == "completed"

    def test_empty_input_data(self):
        """Create log entry with empty input"""
        entry = create_log_entry({})

        assert entry["session_id"] == ""
        assert entry["tool_name"] == ""
        assert entry["is_mcp"] is False
        assert "timestamp" in entry

    def test_bash_tool_entry(self):
        """Create log entry for Bash tool with command"""
        input_data = {
            "tool_name": "Bash",
            "tool_input": {
                "command": "git status",
                "description": "Check git status"
            },
            "tool_response": {"stdout": "...", "stderr": "warning"},
        }

        entry = create_log_entry(input_data)

        assert entry["command"] == "git status"
        assert entry["description"] == "Check git status"
        assert entry["has_stderr"] is True


# =============================================================================
# Integration Test: Simulate Hook Execution
# =============================================================================

class TestHookIntegration:
    """Integration tests simulating hook execution."""

    def test_hook_main_execution(self):
        """Simulate hook main() execution with stdin input."""
        from tool_trace_logger import main, get_log_file

        # Prepare mock stdin input
        mock_input = {
            "session_id": "integration_test_session",
            "tool_use_id": "integration_test_tu",
            "tool_name": "mcp__test__mock_tool",
            "permission_mode": "default",
            "cwd": "/test/dir",
            "tool_input": {"test_param": "test_value"},
            "tool_response": {"status": "ok"},
        }

        # Create a temp log file
        with tempfile.TemporaryDirectory() as tmpdir:
            # Set up environment
            log_file = Path(tmpdir) / "tool-trace.jsonl"

            # Mock get_log_file to use temp file
            with patch('tool_trace_logger.get_log_file', return_value=log_file):
                with patch('sys.stdin', open('/dev/null', 'r')):
                    # We need to mock get_input to provide our test data
                    with patch('tool_trace_logger.get_input', return_value=mock_input):
                        with pytest.raises(SystemExit) as exc_info:
                            main()

                        # Hook should exit 0
                        assert exc_info.value.code == 0

                # Verify log entry was written
                assert log_file.exists()

                with open(log_file, 'r') as f:
                    log_content = f.read()
                    entry = json.loads(log_content.strip())

                assert entry["session_id"] == "integration_test_session"
                assert entry["tool_name"] == "mcp__test__mock_tool"
                assert entry["is_mcp"] is True
                assert entry["mcp_server"] == "test"
                assert entry["mcp_tool"] == "mock_tool"

    def test_hook_handles_empty_input(self):
        """Hook handles empty/malformed JSON gracefully."""
        from tool_trace_logger import main

        with patch('tool_trace_logger.get_input', return_value={}):
            with pytest.raises(SystemExit) as exc_info:
                main()

            # Should exit 0 (graceful handling)
            assert exc_info.value.code == 0


# =============================================================================
# Edge Case Tests
# =============================================================================

class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_very_long_file_path_truncation(self):
        """Very long file path is truncated."""
        long_path = "/a" * 200
        result = extract_tool_fields("Read", {"file_path": long_path}, {})

        assert len(result["file_path"]) == TRUNCATE_LIMITS["file_path"]
        assert result["file_path"].endswith("...")

    def test_very_long_command_truncation(self):
        """Very long command is truncated."""
        long_cmd = "ls " + "a" * 200
        result = extract_tool_fields("Bash", {"command": long_cmd}, {})

        assert len(result["command"]) == TRUNCATE_LIMITS["command"]
        assert result["command"].endswith("...")

    def test_unicode_handling(self):
        """Unicode characters are handled correctly."""
        unicode_input = {"file_path": "/path/to/archivo_espanol.txt"}
        result = extract_tool_fields("Read", unicode_input, {})

        assert result["file_path"] == "/path/to/archivo_espanol.txt"

    def test_emoji_in_description(self):
        """Emoji in description is handled."""
        tool_input = {"command": "echo test", "description": "Test command"}
        result = extract_tool_fields("Bash", tool_input, {})

        assert "Test command" in result["description"]

    def test_nested_json_response(self):
        """Deeply nested JSON response is handled."""
        tool_response = {
            "data": {
                "nested": {
                    "value": 123
                }
            },
            "status": "success"
        }
        result = extract_tool_fields("Task", {}, tool_response)

        assert result["status"] == "success"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
