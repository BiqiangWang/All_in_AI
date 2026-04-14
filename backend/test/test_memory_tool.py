import pytest
import tempfile
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from memory.file_provider import FileMemoryProvider

def test_write_requires_line_range():
    """write without line range should raise error"""
    with tempfile.TemporaryDirectory() as tmpdir:
        provider = FileMemoryProvider(memory_dir=tmpdir)
        with pytest.raises(ValueError, match="start_line and end_line are required"):
            provider.handle_tool_call("memory", {
                "action": "write",
                "target": "user",
                "content": "test"
            })

def test_read_returns_content():
    """read should return all content wrapped in memory-context"""
    with tempfile.TemporaryDirectory() as tmpdir:
        provider = FileMemoryProvider(memory_dir=tmpdir)
        result = provider.handle_tool_call("memory", {
            "action": "read",
            "target": "user"
        })
        assert "<memory-context>" in result
        assert "</memory-context>" in result