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

def test_write_with_line_range():
    """write should replace specified line range"""
    with tempfile.TemporaryDirectory() as tmpdir:
        provider = FileMemoryProvider(memory_dir=tmpdir)
        # Initial content: 5 lines
        provider.handle_tool_call("memory", {
            "action": "write",
            "target": "user",
            "content": "Line 1\nLine 2\nLine 3\nLine 4\nLine 5",
            "start_line": 1,
            "end_line": 5
        })
        # Replace lines 2-3
        result = provider.handle_tool_call("memory", {
            "action": "write",
            "target": "user",
            "content": "New Line 2\nNew Line 3",
            "start_line": 2,
            "end_line": 3
        })
        # Verify
        content = provider.handle_tool_call("memory", {
            "action": "read",
            "target": "user"
        })
        assert "New Line 2" in content
        assert "New Line 3" in content
        assert "Line 1" in content
        assert "Line 4" in content
        assert "Line 5" in content

def test_write_end_line_exceeds_file():
    """end_line beyond file length should truncate"""
    with tempfile.TemporaryDirectory() as tmpdir:
        provider = FileMemoryProvider(memory_dir=tmpdir)
        # Initial: 3 lines
        provider.handle_tool_call("memory", {
            "action": "write",
            "target": "user",
            "content": "L1\nL2\nL3",
            "start_line": 1,
            "end_line": 3
        })
        # Try to replace lines 2-10 (only 3 exist)
        provider.handle_tool_call("memory", {
            "action": "write",
            "target": "user",
            "content": "New L2",
            "start_line": 2,
            "end_line": 10
        })
        content = provider.handle_tool_call("memory", {
            "action": "read",
            "target": "user"
        })
        assert "New L2" in content
        assert "L3" in content