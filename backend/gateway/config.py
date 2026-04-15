"""
Gateway configuration for messaging platforms.
"""

import os
import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, Optional, Any
from enum import Enum

logger = logging.getLogger(__name__)


class Platform(Enum):
    """Supported messaging platforms."""
    FEISHU = "feishu"


@dataclass
class PlatformConfig:
    """Configuration for a single messaging platform."""
    enabled: bool = False
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GatewayConfig:
    """Main gateway configuration."""
    platforms: Dict[Platform, PlatformConfig] = field(default_factory=dict)

    def get_connected_platforms(self) -> list:
        """Return list of platforms that are enabled and configured."""
        connected = []
        for platform, config in self.platforms.items():
            if not config.enabled:
                continue
            if platform == Platform.FEISHU:
                if config.extra.get("app_id") and config.extra.get("app_secret"):
                    connected.append(platform)
        return connected


def load_gateway_config() -> GatewayConfig:
    """Load gateway configuration from environment variables."""
    config = GatewayConfig()

    # Feishu
    feishu_app_id = os.getenv("FEISHU_APP_ID")
    feishu_app_secret = os.getenv("FEISHU_APP_SECRET")
    if feishu_app_id and feishu_app_secret:
        config.platforms[Platform.FEISHU] = PlatformConfig(
            enabled=True,
            extra={
                "app_id": feishu_app_id,
                "app_secret": feishu_app_secret,
                "domain": os.getenv("FEISHU_DOMAIN", "feishu"),
                "connection_mode": os.getenv("FEISHU_CONNECTION_MODE", "websocket"),
            }
        )

    return config
