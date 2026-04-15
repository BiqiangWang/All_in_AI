"""
Base platform adapter interface.

All platform adapters inherit from this and implement required methods.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, Awaitable, Optional, Any

logger = logging.getLogger(__name__)


class MessageType:
    """Types of incoming messages."""
    TEXT = "text"
    VOICE = "voice"
    PHOTO = "photo"
    COMMAND = "command"


@dataclass
class MessageEvent:
    """Incoming message from a platform."""
    text: str
    message_type: str = MessageType.TEXT
    source: Optional[Any] = None
    message_id: Optional[str] = None
    media_urls: list = field(default_factory=list)
    media_types: list = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)

    def is_command(self) -> bool:
        """Check if this is a command message."""
        return self.text.startswith("/")

    def get_command(self) -> Optional[str]:
        """Extract command name if this is a command."""
        if not self.is_command():
            return None
        parts = self.text.split(maxsplit=1)
        return parts[0][1:].lower() if parts else None


@dataclass
class SendResult:
    """Result of sending a message."""
    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None


# Type for message handlers
MessageHandler = Callable[[MessageEvent], Awaitable[Optional[str]]]


class BasePlatformAdapter(ABC):
    """Base class for platform adapters."""

    def __init__(self, config, platform: str):
        self.config = config
        self.platform = platform
        self._message_handler: Optional[MessageHandler] = None
        self._running = False

    @property
    def name(self) -> str:
        return self.platform

    @property
    def is_connected(self) -> bool:
        return self._running

    def set_message_handler(self, handler: MessageHandler) -> None:
        """Set the handler for incoming messages."""
        self._message_handler = handler

    async def handle_message(self, event: MessageEvent) -> None:
        """Process an incoming message."""
        if not self._message_handler:
            return
        try:
            response = await self._message_handler(event)
            if response:
                await self._send_response(event, response)
        except Exception as e:
            logger.error(f"Error handling message: {e}")

    async def _send_response(self, event: MessageEvent, content: str) -> None:
        """Send response back to the platform."""
        result = await self.send(event.source.chat_id, content)
        if not result.success:
            logger.warning(f"Failed to send response: {result.error}")

    @abstractmethod
    async def connect(self) -> bool:
        """Connect to the platform and start receiving messages."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the platform."""
        pass

    @abstractmethod
    async def send(self, chat_id: str, content: str) -> SendResult:
        """Send a message to a chat."""
        pass

    async def send_typing(self, chat_id: str) -> None:
        """Send typing indicator. Override in subclasses if supported."""
        pass
