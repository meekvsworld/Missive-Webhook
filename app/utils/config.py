from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os

class Settings(BaseSettings):
    # Make these optional in the schema so the app doesn't crash on boot
    # but we will validate them when used.
    missive_api_token: Optional[str] = None
    missive_webhook_secret: Optional[str] = None
    missive_channel_id: Optional[str] = None
    
    sendblue_api_key: Optional[str] = None
    sendblue_api_secret: Optional[str] = None
    sendblue_signing_secret: Optional[str] = None
    
    model_config = SettingsConfigDict(
        env_file=".env", 
        extra="ignore",
        env_prefix="" # Ensure no prefix is expected
    )

# Reason: Catching validation errors at boot to prevent Vercel Function Invocation Failed
try:
    settings = Settings()
except Exception as e:
    print(f"Configuration error: {e}")
    settings = Settings.model_construct() # Fallback to empty settings

