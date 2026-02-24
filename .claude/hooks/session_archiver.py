#!/usr/bin/env python3
"""
Session Transcript Archiver
Trigger: SessionEnd

Archives Claude Code session transcripts to project-local storage with gzip
compression. Prevents data loss from the 30-day auto-cleanup policy.

Archive location: .claude/logs/session-transcripts/{YYYY-MM-DD}_{session_id}.jsonl.gz
"""

import gzip
import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path


def get_input() -> dict:
    """Read and parse JSON input from stdin."""
    try:
        return json.load(sys.stdin)
    except json.JSONDecodeError:
        return {}


def log(msg: str) -> None:
    """Log to stderr (hooks should be quiet on stdout)."""
    print(f"[session_archiver] {msg}", file=sys.stderr)


def get_archive_dir() -> Path:
    """Get the archive directory, creating it if needed."""
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
    archive_dir = Path(project_dir) / ".claude" / "logs" / "session-transcripts"
    archive_dir.mkdir(parents=True, exist_ok=True)
    return archive_dir


def archive_session(transcript_path: str, session_id: str) -> bool:
    """
    Copy and gzip-compress a session transcript to the archive.

    Returns True on success, False on failure.
    """
    source = Path(transcript_path)

    if not source.exists():
        log(f"Transcript not found: {transcript_path}")
        return False

    if not source.suffix == ".jsonl":
        log(f"Unexpected file type (expected .jsonl): {source.name}")
        return False

    # Build archive filename: YYYY-MM-DD_session-id.jsonl.gz
    # Use file modification time for the date (more accurate than "now")
    try:
        mtime = datetime.fromtimestamp(source.stat().st_mtime)
    except OSError:
        mtime = datetime.now()

    date_str = mtime.strftime("%Y-%m-%d")
    archive_name = f"{date_str}_{session_id}.jsonl.gz"

    archive_dir = get_archive_dir()
    dest = archive_dir / archive_name

    # Skip if already archived
    if dest.exists():
        log(f"Already archived: {archive_name}")
        return True

    # Compress and copy
    try:
        with open(source, "rb") as f_in, gzip.open(dest, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)

        source_size = source.stat().st_size
        dest_size = dest.stat().st_size
        ratio = (1 - dest_size / source_size) * 100 if source_size > 0 else 0

        log(f"Archived: {archive_name} ({source_size:,}B -> {dest_size:,}B, {ratio:.0f}% reduction)")
        return True

    except OSError as e:
        log(f"Failed to archive {session_id}: {e}")
        # Clean up partial file
        if dest.exists():
            try:
                dest.unlink()
            except OSError:
                pass
        return False


def main():
    input_data = get_input()

    transcript_path = input_data.get("transcript_path", "")
    session_id = input_data.get("session_id", "unknown")

    if not transcript_path:
        log("No transcript_path in hook input, skipping")
        sys.exit(0)

    success = archive_session(transcript_path, session_id)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
