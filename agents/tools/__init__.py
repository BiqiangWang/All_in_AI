"""Agent tools registry."""

from .search_web import search_web
from .memory import MemoryTool

memory = MemoryTool.memory

__all__ = ["search_web", "memory"]
