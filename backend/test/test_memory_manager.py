import pytest
import tempfile
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from memory.memory_manager import MemoryManager
from memory.file_provider import FileMemoryProvider

def test_memory_manager_snapshot_reads():
    """snapshot should call read action"""
    manager = MemoryManager()
    with tempfile.TemporaryDirectory() as tmpdir:
        provider = FileMemoryProvider(memory_dir=tmpdir)
        manager.add_provider(provider)

        # Write something first
        provider.handle_tool_call("memory", {
            "action": "write",
            "target": "user",
            "content": "type: name\ndescription: 用户称呼\ncontent: 小汪",
            "start_line": 1,
            "end_line": 10
        })

        # Get snapshot
        snapshot = manager.get_snapshot()
        assert "小汪" in snapshot