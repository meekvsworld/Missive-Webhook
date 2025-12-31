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
        # Option A: Single post endpoint (FLAT payload)
        url = f"{self.base_url}/posts"
        
        if not messages:
            return {"status": "ignored", "reason": "no messages"}

        # We take the first message and send it as a flat object
        # since each Sendblue webhook represents one message.
        message_to_push = messages[0]
        
        # Ensure 'channel' is set if not already present
        if "channel" not in message_to_push:
            message_to_push["channel"] = settings.missive_channel_id
        
        logger.info(f"Pushing FLAT payload to Missive /v1/posts: {message_to_push}")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=message_to_push, headers=self.headers)
                if response.status_code != 201 and response.status_code != 200:
                    logger.error(f"Missive API error: {response.status_code} - {response.text}")
                response.raise_for_status()
                return response.json() if response.content else {"status": "success"}
            except httpx.HTTPStatusError as e:
                raise e

missive_client = MissiveClient()

