import sys
import os

# Add the project root to sys.path so 'app' module can be found when running on Vercel
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Depends, Request, HTTPException
from app.models.schemas import MissiveOutgoingPayload, SendblueIncomingPayload
from app.services.sendblue import sendblue_client
from app.services.missive import missive_client
from app.utils.security import verify_missive_signature, verify_sendblue_secret
from app.utils.config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Missive-Sendblue Webhook Bridge")

@app.get("/")
async def health_check():
    return {"status": "ok"}

@app.post("/missive/outgoing")
async def handle_missive_outgoing(
    request: Request,
    _=Depends(verify_missive_signature)
):
    """Handles outgoing messages from Missive and sends them via Sendblue."""
    try:
        body = await request.json()
        logger.info(f"Received Missive payload: {body}")
        payload = MissiveOutgoingPayload(**body)
    except Exception as e:
        logger.error(f"Failed to parse Missive payload: {str(e)}")
        # Log the raw body for debugging
        raw_body = await request.body()
        logger.error(f"Raw body: {raw_body.decode()}")
        raise HTTPException(status_code=422, detail=f"Invalid payload: {str(e)}")

    if not settings.sendblue_api_key or not settings.sendblue_api_secret:
        logger.error("Sendblue API credentials missing")
        raise HTTPException(status_code=500, detail="Sendblue credentials not configured")

    # In Custom Channels, Missive might send different event types
    # We'll process anything that looks like a message being sent
    if payload.type not in ["message_sent", "draft_sent"]:
        logger.info(f"Ignoring Missive event type: {payload.type}")
        return {"status": "ignored", "reason": f"Unsupported event type: {payload.type}"}

    # Try to find the phone number in various fields
    phone_number = None
    
    # 1. Check recipient.username (standard for custom channels)
    if payload.message.recipient and payload.message.recipient.username:
        phone_number = payload.message.recipient.username
        logger.info(f"Found phone number in recipient.username: {phone_number}")
    
    # 2. Check to_handle (sometimes used in other contexts)
    if not phone_number and payload.message.to_handle:
        # Take the first handle if it looks like a phone number
        for handle in payload.message.to_handle:
            if handle.startswith("+") or handle.replace(" ", "").replace("-", "").isdigit():
                phone_number = handle
                logger.info(f"Found phone number in to_handle: {phone_number}")
                break

    if not phone_number:
        logger.error("Could not determine recipient phone number from payload")
        # Log more info to help debug
        logger.error(f"Message object: {payload.message.dict()}")
        raise HTTPException(status_code=400, detail="Recipient phone number not found in payload")

    try:
        response = await sendblue_client.send_message(
            number=phone_number,
            content=payload.message.body
        )
        logger.info(f"Successfully sent via Sendblue: {response.get('message_handle')}")
        return {"status": "success", "sendblue_response": response}
    except Exception as e:
        logger.error(f"Error sending via Sendblue: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/sendblue/incoming")
async def handle_sendblue_incoming(
    request: Request,
    _=Depends(verify_sendblue_secret)
):
    """Handles incoming messages from Sendblue and pushes them to Missive."""
    try:
        body = await request.json()
        logger.info(f"Received Sendblue payload: {body}")
        payload = SendblueIncomingPayload(**body)
    except Exception as e:
        logger.error(f"Failed to parse Sendblue payload: {str(e)}")
        raw_body = await request.body()
        logger.error(f"Raw Sendblue body: {raw_body.decode()}")
        raise HTTPException(status_code=422, detail=f"Invalid payload: {str(e)}")

    if not settings.missive_api_token or not settings.missive_channel_id:
        logger.error("Missive API credentials missing")
        raise HTTPException(status_code=500, detail="Missive credentials not configured")

    # We only care about RECEIVED messages
    if payload.is_outbound:
        logger.info("Ignoring outbound message from Sendblue")
        return {"status": "ignored"}

    # Extract number and content from flexible fields
    from_number = payload.from_number or payload.number
    message_content = payload.body or payload.content
    to_number = payload.sendblue_number or "Sendblue" # Your own number or channel name

    if not from_number:
        logger.error("No phone number found in Sendblue payload")
        raise HTTPException(status_code=400, detail="Phone number not found")
    
    if not message_content:
        logger.error("No message content found in Sendblue payload")
        # Don't fail completely, just ignore empty messages
        return {"status": "ignored", "reason": "empty content"}

    logger.info(f"Processing message from {from_number}")

    try:
        # notification is required, and one of text/markdown/attachments is required
        missive_msg = {
            "external_id": payload.message_handle or f"sb_{payload.date_sent or 'unknown'}",
            "text": message_content,
            "body": message_content, # Redundant but safe
            "notification": message_content[:100],
            "from_handle": from_number,
            "to_handle": [to_number],
        }
        
        response = await missive_client.push_messages([missive_msg], settings.missive_channel_id)
        logger.info("Successfully pushed message to Missive")
        return {"status": "success", "missive_response": response}
    except Exception as e:
        logger.error(f"Error pushing message to Missive: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

