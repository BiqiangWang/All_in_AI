import threading
from typing import Any
from .provider import MemoryProvider


class MemoryManager:
    """记忆管理器，负责编排多个 MemoryProvider"""

    def __init__(self):
        self._providers: list[MemoryProvider] = []
        self._snapshot: str | None = None
        self._prefetch_cache: str | None = None
        self._prefetch_lock = threading.Lock()

    def get_snapshot(self) -> str:
        """获取快照，如果还没生成则生成"""
        if self._snapshot is None:
            with self._prefetch_lock:
                # 双重检查
                if self._snapshot is None:
                    self._snapshot = self._take_snapshot_impl()
        return self._snapshot

    def _take_snapshot_impl(self) -> str:
        """实际生成快照的内部方法"""
        parts = []
        for provider in self._providers:
            for tool in provider.get_tools():
                if tool["name"] == "memory":
                    try:
                        # Read both agent and user memory
                        agent_result = provider.handle_tool_call("memory", {"target": "agent", "action": "read"})
                        user_result = provider.handle_tool_call("memory", {"target": "user", "action": "read"})
                        if agent_result:
                            parts.append(agent_result)
                        if user_result:
                            parts.append(user_result)
                    except Exception as e:
                        print(f"Error reading memory: {e}")
                elif tool["name"] == "user_profile":
                    try:
                        result = provider.handle_tool_call("user_profile", {"target": "user", "action": "read"})
                        if result:
                            parts.append(result)
                    except Exception as e:
                        print(f"Error reading user_profile: {e}")
        return "\n\n".join(parts)

    def prefetch(self) -> None:
        """后台预取相关记忆"""
        def _run():
            try:
                with self._prefetch_lock:
                    self._prefetch_cache = self.get_snapshot()
            except Exception as e:
                print(f"Prefetch error: {e}")

        thread = threading.Thread(target=_run, daemon=True)
        thread.start()

    def get_prefetch_cache(self) -> str | None:
        return self._prefetch_cache

    def clear_snapshot(self) -> None:
        """清除快照，用于会话结束"""
        self._snapshot = None
        self._prefetch_cache = None

    def add_provider(self, provider: MemoryProvider) -> None:
        self._providers.append(provider)

    def get_tools(self) -> list[dict[str, Any]]:
        """收集所有 Provider 的工具"""
        tools = []
        for provider in self._providers:
            tools.extend(provider.get_tools())
        return tools

    def handle_tool_call(self, tool_name: str, args: dict[str, Any]) -> str:
        """委托给对应 Provider 处理"""
        matched_provider: MemoryProvider | None = None
        for provider in self._providers:
            for tool in provider.get_tools():
                if tool.get("name") == tool_name:
                    if matched_provider is not None:
                        raise ValueError(
                            f"Tool '{tool_name}' is registered in multiple providers: "
                            f"{matched_provider.name}, {provider.name}"
                        )
                    matched_provider = provider
        if matched_provider is None:
            raise ValueError(f"Tool '{tool_name}' not found in any provider")
        return matched_provider.handle_tool_call(tool_name, args)
