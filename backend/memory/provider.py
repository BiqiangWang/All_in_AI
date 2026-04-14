from abc import ABC, abstractmethod
from typing import Any


class MemoryProvider(ABC):
    """记忆 Provider 抽象基类，参考 hermes-agent 设计"""

    @property
    def name(self) -> str:
        """Provider 名称"""
        return "base"

    @abstractmethod
    def is_available(self) -> bool:
        """Provider 是否可用"""

    @abstractmethod
    def get_tools(self) -> list[dict[str, Any]]:
        """返回该 Provider 提供的工具 schema 列表"""

    @abstractmethod
    def handle_tool_call(self, tool_name: str, args: dict[str, Any]) -> str:
        """处理工具调用"""
