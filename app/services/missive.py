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

    async def push_messages(self, messages: List[dict]) -> dict:
        """Pushes messages to Missive.

        Args:
            messages (List[dict]): List of message objects to push.

        Returns:
            dict: The API response.
        """
        # Global posts endpoint
        url = f"{self.base_url}/posts"
        
        # Missive expects a JSON object with a "posts" key.
        # The value of "posts" must be a dictionary where:
        # - The keys are the external_ids.
        # - The values are the message objects (which must include channel_id).
        posts_dict = {}
        for msg in messages:
            if "channel_id" not in msg:
                msg["channel_id"] = settings.missive_channel_id
            
            ext_id = msg.get("external_id")
            if not ext_id:
                ext_id = f"sb_{int(time.time())}"
            
            posts_dict[ext_id] = msg
        
        payload = {"posts": posts_dict}
        logger.info(f"Final push to Missive global /posts: {payload}")
        
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

