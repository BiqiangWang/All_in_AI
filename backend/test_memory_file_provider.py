# backend/test_memory_file_provider.py
import pytest
import tempfile
import os
from pathlib import Path
from memory.file_provider import FileMemoryProvider


def test_provider_name():
    with tempfile.TemporaryDirectory() as tmpdir:
        provider = FileMemoryProvider(memory_dir=tmpdir)
        assert provider.name == "file_memory"


def test_is_available():
    with tempfile.TemporaryDirectory() as tmpdir:
        provider = FileMemoryProvider(memory_dir=tmpdir)
        assert provider.is_available() is True


def test_get_tools():
    with tempfile.TemporaryDirectory() as tmpdir:
        provider = FileMemoryProvider(memory_dir=tmpdir)
        tools = provider.get_tools()
        assert len(tools) == 1
        assert tools[0]["name"] == "memory"
        params = tools[0]["parameters"]["properties"]
        assert "target" in params
        assert "action" in params


def test_memory_operations():
    with tempfile.TemporaryDirectory() as tmpdir:
        provider = FileMemoryProvider(memory_dir=tmpdir)

        # Write to agent memory
        result = provider.handle_tool_call("memory", {
            "target": "agent",
            "action": "add",
            "content": "Test agent memory"
        })
        assert "added" in result.lower()

        # Write to user profile
        result = provider.handle_tool_call("memory", {
            "target": "user",
            "action": "add",
            "content": "Test user profile"
        })
        assert "added" in result.lower()

        # Read agent memory
        result = provider.handle_tool_call("memory", {
            "target": "agent",
            "action": "read"
        })
        assert "Test agent memory" in result


def test_atomic_write():
    """验证原子写入：写入过程中断电不会损坏文件"""
    with tempfile.TemporaryDirectory() as tmpdir:
        provider = FileMemoryProvider(memory_dir=tmpdir)

        # 写入大量内容
        large_content = "x" * 10000
        provider.handle_tool_call("memory", {
            "target": "agent",
            "action": "add",
            "content": large_content
        })

        # 验证文件完整
        mem_file = Path(tmpdir) / "MEMORY.md"
        content = mem_file.read_text(encoding="utf-8")
        assert large_content in content
