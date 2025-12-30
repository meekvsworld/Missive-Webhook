import httpx
from app.utils.config import settings

class SendblueClient:
    """Client for interacting with the Sendblue API."""

    def __init__(self):
        self.base_url = "https://api.sendblue.co/api/v1"
        self.headers = {
            "sb-api-key": settings.sendblue_api_key,
            "sb-api-secret": settings.sendblue_api_secret,
            "Content-Type": "application/json",
        }

    async def send_message(self, number: str, content: str) -> dict:
        """Sends an iMessage/SMS via Sendblue.

        Args:
            number (str): The recipient's phone number.
            content (str): The message content.

        Returns:
            dict: The API response.
        """
        url = f"{self.base_url}/send-message"
        payload = {
            "number": number,
            "content": content,
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()

sendblue_client = SendblueClient()

