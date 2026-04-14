"""Memory tool."""

import sys
from pathlib import Path
from typing import Any

from langchain_core.tools import tool
from pydantic import Field

# Lazy-loaded memory provider
_memory_provider = None


def _get_memory_provider():
    """Lazy initialization of memory provider."""
    global _memory_provider
    if _memory_provider is None:
        project_root = Path(__file__).parent.parent.parent.parent
        backend_dir = Path(__file__).parent.parent.parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        if str(backend_dir) not in sys.path:
            sys.path.insert(0, str(backend_dir))

        from backend.memory.file_provider import FileMemoryProvider
        _memory_provider = FileMemoryProvider()
    return _memory_provider


class MemoryTool:
    """Memory tool for reading/writing persistent information."""

    @staticmethod
    @tool
    def memory(
        target: str = Field(description="Target store: 'agent' for agent memory, 'user' for user profile"),
        action: str = Field(description="Action: 'read' or 'write'"),
        content: str = Field(default=None, description="Content to write (required for write)"),
        start_line: int = Field(default=None, description="Start line number (1-indexed, inclusive). Required for write."),
        end_line: int = Field(default=None, description="End line number (1-indexed, inclusive). Required for write. If exceeds file length, truncates to last line."),
    ) -> str:
        """Read from or write to memory store.

        Memory stores persistent information across conversations. Think of it as
        writing notes to yourself about the user.

        ## When to Write
        Write when the user states a preference, corrects something you said, shares
        personal info worth remembering, or changes their mind.

        ## Workflow
        1. Call read(target="user" or "agent") to see what's stored
        2. Decide whether to append new fact or replace existing lines
        3. Call write with appropriate line range

        ## Format
        Write plain factual statements in natural language. Not structured data.

        ## Line Range
        Line numbers are 1-indexed, inclusive. end_line exceeding file length
        truncates to last existing line.
        """
        return _get_memory_provider().handle_tool_call("memory", {
            "target": target,
            "action": action,
            "content": content,
            "start_line": start_line,
            "end_line": end_line,
        })
