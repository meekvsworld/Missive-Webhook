import hmac
import hashlib
from fastapi import Request, HTTPException, Header
from app.utils.config import settings

async def verify_missive_signature(request: Request):
    """Verifies the Missive signature."""
    if not settings.missive_webhook_secret:
        return

    signature = request.headers.get("X-Missive-Signature")
    if not signature:
        raise HTTPException(status_code=401, detail="Missing X-Missive-Signature header")

    body = await request.body()
    expected_signature = hmac.new(
        settings.missive_webhook_secret.encode(),
        body,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(signature, expected_signature):
        raise HTTPException(status_code=401, detail="Invalid Missive signature")

def verify_sendblue_secret(sb_signing_secret: str = Header(None)):
    """Verifies the Sendblue secret."""
    if not settings.sendblue_signing_secret:
        return

    if sb_signing_secret != settings.sendblue_signing_secret:
        raise HTTPException(status_code=401, detail="Invalid Sendblue secret")

