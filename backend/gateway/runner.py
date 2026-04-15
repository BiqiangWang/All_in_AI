"""
Gateway runner - starts messaging platform adapters.
"""

import asyncio
import logging
import signal
import sys
from typing import Optional

from .config import load_gateway_config, Platform
from .session import SessionStore, SessionSource
from .api_client import AegraAPIClient
from .platforms.feishu import FeishuAdapter
from .platforms.base import MessageEvent, BasePlatformAdapter

logger = logging.getLogger(__name__)


class GatewayRunner:
    """Manages the gateway lifecycle."""

    def __init__(self) -> None:
        self.config = load_gateway_config()
        self.adapters: dict[Platform, BasePlatformAdapter] = {}
        self.sessions = SessionStore()
        self.api_client = AegraAPIClient()
        self._running = False

    def _create_adapter(self, platform: Platform) -> FeishuAdapter:
        """Create adapter instance for platform."""
        if platform == Platform.FEISHU:
            return FeishuAdapter(self.config.platforms[platform])
        raise ValueError(f"Unknown platform: {platform}")

    async def _handle_message(self, event: MessageEvent) -> Optional[str]:
        """Handle incoming message - create or continue session."""
        if not event.source:
            return "Error: no source"

        source = event.source
        session_source = SessionSource(
            platform=Platform.FEISHU,  # Platform is known at adapter level
            chat_id=source.chat_id,
            user_id=getattr(source, "user_id", None),
            user_name=getattr(source, "user_name", None),
        )
        session_key = await self.sessions.get_or_create_session(session_source)

        # Get or create thread
        thread_id = await self.sessions.get_thread_id(session_key)
        if not thread_id:
            thread_id = await self.api_client.create_thread()
            await self.sessions.set_thread_id(session_key, thread_id)

        # Send to agent
        try:
            response = await self.api_client.send_message(thread_id, event.text)
            return response
        except Exception as e:
            logger.error(f"Error calling agent: {e}")
            return f"Error: {e}"

    async def start(self) -> None:
        """Start all configured platform adapters."""
        self._running = True
        for platform in self.config.get_connected_platforms():
            try:
                adapter = self._create_adapter(platform)
                adapter.set_message_handler(self._handle_message)
                await adapter.connect()
                self.adapters[platform] = adapter
                logger.info(f"Started {platform.value} adapter")
            except Exception as e:
                logger.error(f"Failed to start {platform.value}: {e}")

    async def stop(self) -> None:
        """Stop all adapters gracefully."""
        self._running = False
        for platform, adapter in self.adapters.items():
            try:
                await adapter.disconnect()
                logger.info(f"Stopped {platform.value} adapter")
            except Exception as e:
                logger.error(f"Error stopping {platform.value}: {e}")
        await self.api_client.close()


def run_gateway():
    """Main entry point for gateway."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    runner = GatewayRunner()

    async def main():
        await runner.start()
        # Keep running
        while runner._running:
            await asyncio.sleep(1)

    # Handle signals
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    def signal_handler(sig, frame):
        logger.info("Received shutdown signal")
        loop.run_until_complete(runner.stop())
        loop.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(runner.stop())
        loop.close()


if __name__ == "__main__":
    run_gateway()
