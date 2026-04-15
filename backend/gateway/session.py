"""
Session management for the gateway.

Handles session context tracking and message routing.
"""

import uuid
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional

from backend.gateway.config import Platform

logger = logging.getLogger(__name__)


@dataclass
class SessionSource:
    """Describes where a message originated from."""
    platform: Platform
    chat_id: str
    chat_name: Optional[str] = None
    chat_type: str = "dm"
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    thread_id: Optional[str] = None


def build_session_key(source: SessionSource) -> str:
    """Build a unique key for a session."""
    parts = [source.platform.value, source.chat_id]
    if source.thread_id:
        parts.append(source.thread_id)
    return ":".join(parts)


class SessionStore:
    """In-memory session store."""

    def __init__(self) -> None:
        self._sessions: Dict[str, Dict] = {}

    def get_or_create_session(self, source: SessionSource) -> str:
        """Get or create a session for the source."""
        key = build_session_key(source)
        if key not in self._sessions:
            self._sessions[key] = {
                "id": str(uuid.uuid4()),
                "source": source,
                "created_at": datetime.now(),
                "last_active": datetime.now(),
                "thread_id": None,
            }
        else:
            self._sessions[key]["last_active"] = datetime.now()
        return key

    def get_session(self, key: str) -> Optional[Dict]:
        """Get session by key."""
        return self._sessions.get(key)

    def set_thread_id(self, key: str, thread_id: str) -> None:
        """Set the Aegra thread ID for a session."""
        if key in self._sessions:
            self._sessions[key]["thread_id"] = thread_id

    def get_thread_id(self, key: str) -> Optional[str]:
        """Get the Aegra thread ID for a session."""
        session = self._sessions.get(key)
        return session["thread_id"] if session else None
