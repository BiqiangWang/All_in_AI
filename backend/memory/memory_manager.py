from typing import Any
from .provider import MemoryProvider


class MemoryManager:
    """记忆管理器，负责编排多个 MemoryProvider"""

    def __init__(self):
        self._providers: list[MemoryProvider] = []

    def add_provider(self, provider: MemoryProvider) -> None:
        self._providers.append(provider)

    def get_tools(self) -> list[dict[str, Any]]:
        """收集所有 Provider 的工具"""
        tools = []
        for provider in self._providers:
            tools.extend(provider.get_tools())
        return tools

    def handle_tool_call(self, tool_name: str, args: dict[str, Any]) -> str | None:
        """委托给对应 Provider 处理"""
        for provider in self._providers:
            if any(t.get("name") == tool_name for t in provider.get_tools()):
                return provider.handle_tool_call(tool_name, args)
        return None
