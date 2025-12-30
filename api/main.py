from fastapi import FastAPI, Depends, Request, HTTPException
from app.models.schemas import MissiveOutgoingPayload, SendblueIncomingPayload
from app.services.sendblue import sendblue_client
from app.services.missive import missive_client
from app.utils.security import verify_missive_signature, verify_sendblue_secret
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
    payload: MissiveOutgoingPayload,
    _=Depends(verify_missive_signature)
):
    """Handles outgoing messages from Missive and sends them via Sendblue."""
    logger.info(f"Received outgoing message from Missive: {payload.message.id}")
    
    if payload.type != "message_sent":
        logger.warning(f"Unsupported Missive event type: {payload.type}")
        return {"status": "ignored"}

    recipient = payload.message.recipient
    if not recipient or not recipient.username:
        logger.error("No recipient username provided in Missive payload")
        raise HTTPException(status_code=400, detail="Recipient username is required")

    try:
        response = await sendblue_client.send_message(
            number=recipient.username,
            content=payload.message.body
        )
        logger.info(f"Successfully sent message via Sendblue: {response.get('message_handle')}")
        return {"status": "success", "sendblue_response": response}
    except Exception as e:
        logger.error(f"Error sending message via Sendblue: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/sendblue/incoming")
async def handle_sendblue_incoming(
    payload: SendblueIncomingPayload,
    _=Depends(verify_sendblue_secret)
):
    """Handles incoming messages from Sendblue and pushes them to Missive."""
    logger.info(f"Received incoming message from Sendblue from: {payload.number}")
    
    # We only care about RECEIVED messages (not our own outbound messages if Sendblue loops them back)
    if payload.is_outbound:
        logger.info("Ignoring outbound message from Sendblue")
        return {"status": "ignored"}

    try:
        missive_msg = {
            "external_id": payload.message_handle or f"sb_{payload.date_sent}",
            "body": payload.content,
            "from_handle": payload.number,
            "to_handle": ["Sendblue"], # Placeholder or actual Sendblue number if known
        }
        
        response = await missive_client.push_messages([missive_msg])
        logger.info("Successfully pushed message to Missive")
        return {"status": "success", "missive_response": response}
    except Exception as e:
        logger.error(f"Error pushing message to Missive: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

