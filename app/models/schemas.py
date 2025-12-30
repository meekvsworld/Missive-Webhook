from pydantic import BaseModel, Field
from typing import Optional, List

# Missive Schemas
class MissiveRecipient(BaseModel):
    username: str

class MissiveMessage(BaseModel):
    id: str
    body: str
    from_handle: Optional[str] = None
    to_handle: Optional[List[str]] = None
    recipient: Optional[MissiveRecipient] = None

class MissiveChannel(BaseModel):
    id: str

class MissiveOutgoingPayload(BaseModel):
    type: str
    message: MissiveMessage
    channel: Optional[MissiveChannel] = None

# Sendblue Schemas
class SendblueIncomingPayload(BaseModel):
    number: str
    content: str
    status: str
    message_handle: Optional[str] = None
    date_sent: Optional[str] = None
    is_outbound: bool = False

# Missive API Schemas for Pushing
class MissiveExternalMessage(BaseModel):
    external_id: str
    body: str
    from_handle: str
    to_handle: List[str]
    delivered_at: Optional[int] = None # Unix timestamp

class MissivePushPayload(BaseModel):
    messages: List[MissiveExternalMessage]

