import httpx
from typing import List, Optional
from app.utils.config import settings

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
        url = f"{self.base_url}/posts"
        
        # Missive expects 'posts' to be a key-value object (dict), 
        # where keys are the external_ids.
        posts_map = {}
        import time
        for msg in messages:
            if "channel_id" not in msg:
                msg["channel_id"] = settings.missive_channel_id
            
            # Use external_id as the key, falling back to a timestamp if missing
            ext_id = msg.get("external_id") or f"msg_{int(time.time())}"
            posts_map[ext_id] = msg
        
        payload = {"posts": posts_map}
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload, headers=self.headers)
                if response.status_code != 201 and response.status_code != 200:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Missive API error: {response.status_code} - {response.text}")
                response.raise_for_status()
                return response.json() if response.content else {"status": "success"}
            except httpx.HTTPStatusError as e:
                raise e

missive_client = MissiveClient()

