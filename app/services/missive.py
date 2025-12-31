import httpx
import time
import logging
from typing import List, Optional
from app.utils.config import settings

logger = logging.getLogger(__name__)

class MissiveClient:
    """Client for interacting with the Missive API."""

    def __init__(self):
        # Use the public.missiveapp.com base URL as per documentation
        self.base_url = "https://public.missiveapp.com/v1"
        self.headers = {
            "Authorization": f"Bearer {settings.missive_api_token}",
            "Content-Type": "application/json",
        }

    async def push_messages(self, messages: List[dict], channel_id: Optional[str] = None) -> dict:
        """Pushes messages to Missive.

        Args:
            messages (List[dict]): List of message objects to push.
            channel_id (Optional[str]): The channel ID to push to.

        Returns:
            dict: The API response.
        """
        cid = channel_id or settings.missive_channel_id
        # Use the channel-specific endpoint for custom channels
        url = f"{self.base_url}/channels/{cid}/posts"
        
        # In this endpoint, 'posts' is expected to be a LIST
        payload = {"posts": messages}
        logger.info(f"Pushing to Missive channel {cid}: {payload}")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload, headers=self.headers)
                if response.status_code != 201 and response.status_code != 200:
                    logger.error(f"Missive API error: {response.status_code} - {response.text}")
                response.raise_for_status()
                return response.json() if response.content else {"status": "success"}
            except httpx.HTTPStatusError as e:
                # If the channel-specific endpoint fails with 404, fallback to global
                if e.response.status_code == 404:
                    logger.warning("Channel-specific endpoint not found, falling back to global /posts")
                    global_url = f"{self.base_url}/posts"
                    # For global endpoint, 'posts' must be a key-value object
                    posts_map = {msg.get("external_id") or f"msg_{int(time.time())}": msg for msg in messages}
                    global_payload = {"posts": posts_map}
                    resp = await client.post(global_url, json=global_payload, headers=self.headers)
                    resp.raise_for_status()
                    return resp.json() if resp.content else {"status": "success"}
                raise e

missive_client = MissiveClient()

