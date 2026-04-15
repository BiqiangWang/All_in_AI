"""
Feishu/Lark platform adapter.

Supports WebSocket long connection mode for receiving and sending messages.
"""

import asyncio
import logging
from typing import Optional, Any

try:
    import lark_oapi as lark
    from lark_oapi.api.im.v1 import CreateMessageRequest, CreateMessageRequestBody
    from lark_oapi.event.dispatcher_handler import EventDispatcherHandler
    from lark_oapi.ws import Client as FeishuWSClient
    FEISHU_AVAILABLE = True
except ImportError:
    FEISHU_AVAILABLE = False
    lark = None

from .base import BasePlatformAdapter, MessageEvent, MessageType, SendResult

logger = logging.getLogger(__name__)


class FeishuAdapter(BasePlatformAdapter):
    """Feishu/Lark platform adapter using WebSocket connection."""

    def __init__(self, config: Any) -> None:
        super().__init__(config, "feishu")
        self._ws_client: Optional[FeishuWSClient] = None
        self._app_id: str = config.extra.get("app_id", "")
        self._app_secret: str = config.extra.get("app_secret", "")
        self._domain: str = config.extra.get("domain", "feishu")

    async def connect(self) -> bool:
        """Connect to Feishu via WebSocket."""
        if not FEISHU_AVAILABLE:
            raise RuntimeError("lark-oapi not installed. Run: pip install lark-oapi")

        # Create Lark client
        client = lark.Client.builder()\
            .app_id(self._app_id)\
            .app_secret(self._app_secret)\
            .log_level(lark.LogLevel.INFO)\
            .build()

        handler = EventDispatcherHandler.builder()\
            .register_p2_im_message_receive_v1(self._on_message)\
            .build()

        # Create WebSocket client
        self._ws_client = FeishuWSClient(
            client,
            handler,
            auto_reconnect=True,
        )

        # Start connection in background
        asyncio.create_task(self._ws_client.start())
        self._running = True
        logger.info("Feishu WebSocket connection started")
        return True

    async def disconnect(self) -> None:
        """Disconnect from Feishu."""
        if self._ws_client:
            self._ws_client.stop()
        self._running = False
        logger.info("Feishu adapter stopped")

    async def _on_message(self, data: Any) -> None:
        """Handle incoming message from Feishu."""
        try:
            event = self._parse_message(data)
            if event:
                await self.handle_message(event)
        except Exception as e:
            logger.error(f"Error processing Feishu message: {e}")

    def _parse_message(self, data: Any) -> Optional[MessageEvent]:
        """Parse Feishu message into MessageEvent."""
        # lark-oapi passes event objects where message data is nested under event.message
        message = getattr(data, "message", None) or (data.get("message") if isinstance(data, dict) else None)
        if not message:
            return None

        msg_type = getattr(message, "msg_type", None) or message.get("msg_type", "text")
        content = getattr(message, "content", None) or message.get("content", {})

        if msg_type == "text":
            text = content.get("text", "") if isinstance(content, dict) else ""
        else:
            text = str(content)

        sender = getattr(message, "sender", None) or message.get("sender", {}) if isinstance(message, dict) else None
        event = MessageEvent(
            text=text,
            message_type=MessageType.TEXT if msg_type == "text" else msg_type,
            message_id=getattr(message, "message_id", None) or message.get("message_id") if isinstance(message, dict) else None,
            source=self._build_source(message),
        )
        return event

    def _build_source(self, message: Any) -> Any:
        """Build session source from message."""
        sender = getattr(message, "sender", None) or (message.get("sender") if isinstance(message, dict) else None) or {}
        chat = getattr(message, "chat_id", None) or (message.get("chat_id") if isinstance(message, dict) else "")

        class Source:
            def __init__(self, chat_id: str, user_id: Optional[str], user_name: str) -> None:
                self.chat_id = chat_id
                self.user_id = user_id
                self.user_name = user_name

        sender_id = getattr(sender, "sender_id", None) or (sender.get("sender_id") if isinstance(sender, dict) else None)
        open_id = getattr(sender_id, "open_id", None) or (sender_id.get("open_id") if isinstance(sender_id, dict) else None) if sender_id else None
        sender_nickname = getattr(sender, "sender_nickname", None) or (sender.get("sender_nickname") if isinstance(sender, dict) else "")

        return Source(
            chat_id=chat,
            user_id=open_id,
            user_name=sender_nickname,
        )

    async def send(self, chat_id: str, content: str) -> SendResult:
        """Send a message to Feishu chat."""
        try:
            client = lark.Client.builder()\
                .app_id(self._app_id)\
                .app_secret(self._app_secret)\
                .build()

            request = CreateMessageRequest.builder()\
                .receive_id_type("chat_id")\
                .create_message_request_body(
                    CreateMessageRequestBody.builder()
                    .receive_id(chat_id)
                    .msg_type("text")
                    .content(f'{{"text":"{content}"}}')
                    .build()
                )\
                .build()

            response = client.im.v1.message.create(request)

            if response.code == 0:
                return SendResult(
                    success=True,
                    message_id=response.data and response.data.message_id,
                )
            else:
                return SendResult(success=False, error=response.msg)

        except Exception as e:
            logger.error(f"Feishu send error: {e}")
            return SendResult(success=False, error=str(e))
