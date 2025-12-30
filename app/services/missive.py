import httpx
from typing import List, Optional
from app.utils.config import settings

class MissiveClient:
    """Client for interacting with the Missive API."""

    def __init__(self):
        self.base_url = "https://api.missiveapp.com/v1"
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
        # The Missive API expects a 'posts' key with the list of messages
        # and each message should have the channel_id if not already handled
        # by the specific channel endpoint.
        for msg in messages:
            if "channel_id" not in msg:
                msg["channel_id"] = settings.missive_channel_id
        
        payload = {"posts": messages}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()

missive_client = MissiveClient()

