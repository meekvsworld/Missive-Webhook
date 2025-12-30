from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    missive_api_token: str
    missive_webhook_secret: Optional[str] = None
    missive_channel_id: str
    
    sendblue_api_key: str
    sendblue_api_secret: str
    sendblue_signing_secret: Optional[str] = None
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

