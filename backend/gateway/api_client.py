"""
Aegra API client for gateway.

Handles communication with Aegra agent via Agent Protocol.
"""

import asyncio
import logging

import httpx

logger = logging.getLogger(__name__)


class AegraAPIClient:
    """Client for interacting with Aegra API."""

    def __init__(self, base_url: str = "http://localhost:2026") -> None:
        self.base_url = base_url.rstrip("/")
        self._client = httpx.AsyncClient(timeout=30.0)

    async def create_thread(self) -> str:
        """Create a new thread and return thread_id."""
        response = await self._client.post(f"{self.base_url}/v1/threads")
        response.raise_for_status()
        data = response.json()
        return data.get("thread_id", data.get("id"))

    async def send_message(
        self,
        thread_id: str,
        content: str,
    ) -> str:
        """Send a message to a thread and return assistant response content."""
        # Create run
        run_response = await self._client.post(
            f"{self.base_url}/v1/threads/{thread_id}/runs",
            json={"content": content}
        )
        run_response.raise_for_status()
        run_data = run_response.json()
        run_id = run_data.get("run_id", run_data.get("id"))

        # Wait for completion
        for _ in range(60):
            await asyncio.sleep(1)
            status_response = await self._client.get(
                f"{self.base_url}/v1/threads/{thread_id}/runs/{run_id}"
            )
            status_data = status_response.json()
            status = status_data.get("status", status_data.get("state"))

            if status in ("completed", "success"):
                msgs_response = await self._client.get(
                    f"{self.base_url}/v1/threads/{thread_id}/messages"
                )
                msgs = msgs_response.json()
                for msg in reversed(msgs.get("data", [])):
                    if msg.get("type") == "assistant":
                        return msg.get("content", "")
                return ""
            elif status in ("failed", "cancelled", "expired"):
                raise RuntimeError(f"Run {status}: {status_data}")

        raise TimeoutError("Run timed out")

    async def close(self) -> None:
        """Close the client."""
        await self._client.aclose()

    async def __aenter__(self) -> "AegraAPIClient":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()
