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
        url = f"{self.base_url}/posts"
        cid = channel_id or settings.missive_channel_id
        
        # For the global /posts endpoint, 'posts' must be a key-value object
        # where keys are the external_ids and each object MUST contain the channel_id.
        posts_map = {}
        for msg in messages:
            # Ensure channel_id is inside the message
            if "channel_id" not in msg:
                msg["channel_id"] = cid
            
            # Use external_id as the key
            ext_id = msg.get("external_id") or f"msg_{int(time.time())}"
            posts_map[ext_id] = msg
        
        payload = {"posts": posts_map}
        logger.info(f"Pushing to Missive global /posts: {payload}")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload, headers=self.headers)
                if response.status_code != 201 and response.status_code != 200:
                    logger.error(f"Missive API error: {response.status_code} - {response.text}")
                response.raise_for_status()
                return response.json() if response.content else {"status": "success"}
            except httpx.HTTPStatusError as e:
                raise e

missive_client = MissiveClient()

