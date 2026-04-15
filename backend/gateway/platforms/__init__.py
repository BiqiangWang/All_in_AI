"""Platform adapters for messaging integrations."""

from .base import BasePlatformAdapter, MessageEvent, MessageType, SendResult

__all__ = [
    "BasePlatformAdapter",
    "MessageEvent",
    "MessageType",
    "SendResult",
]
