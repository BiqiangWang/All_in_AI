"""
Gateway runner - starts messaging platform adapters.
"""

import asyncio
import logging
import signal
import sys
from typing import Optional

from .config import load_gateway_config, Platform
from .platforms.feishu import FeishuAdapter

logger = logging.getLogger(__name__)


class GatewayRunner:
    """Manages the gateway lifecycle."""

    def __init__(self):
        self.config = load_gateway_config()
        self.adapters: dict = {}
        self._running = False

    def _create_adapter(self, platform: Platform):
        """Create adapter instance for platform."""
        if platform == Platform.FEISHU:
            from .platforms.feishu import FeishuAdapter
            return FeishuAdapter(self.config.platforms[platform])
        raise ValueError(f"Unknown platform: {platform}")

    async def start(self):
        """Start all configured platform adapters."""
        self._running = True
        for platform in self.config.get_connected_platforms():
            try:
                adapter = self._create_adapter(platform)
                await adapter.connect()
                self.adapters[platform] = adapter
                logger.info(f"Started {platform.value} adapter")
            except Exception as e:
                logger.error(f"Failed to start {platform.value}: {e}")

    async def stop(self):
        """Stop all adapters gracefully."""
        self._running = False
        for platform, adapter in self.adapters.items():
            try:
                await adapter.disconnect()
                logger.info(f"Stopped {platform.value} adapter")
            except Exception as e:
                logger.error(f"Error stopping {platform.value}: {e}")


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
