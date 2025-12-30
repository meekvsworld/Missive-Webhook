import pytest
import httpx
from api.main import app
from unittest.mock import AsyncMock, patch

@pytest.fixture
def anyio_backend():
    return 'asyncio'

@pytest.mark.anyio
async def test_health_check():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@patch("api.main.sendblue_client.send_message", new_callable=AsyncMock)
@patch("api.main.verify_missive_signature", return_value=None)
@pytest.mark.anyio
async def test_handle_missive_outgoing(mock_verify, mock_send):
    mock_send.return_value = {"message_handle": "test_handle"}
    
    payload = {
        "type": "message_sent",
        "message": {
            "id": "msg_123",
            "body": "Hello from Missive",
            "recipient": {"username": "+1234567890"}
        },
        "channel": {"id": "chan_123"}
    }
    
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/missive/outgoing", json=payload)
    
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    mock_send.assert_called_once_with(
        number="+1234567890",
        content="Hello from Missive"
    )

@patch("api.main.missive_client.push_messages", new_callable=AsyncMock)
@patch("api.main.verify_sendblue_secret", return_value=None)
@pytest.mark.anyio
async def test_handle_sendblue_incoming(mock_verify, mock_push):
    mock_push.return_value = {"status": "success"}
    
    payload = {
        "number": "+1234567890",
        "content": "Hello from Sendblue",
        "status": "RECEIVED",
        "message_handle": "sb_123",
        "is_outbound": False
    }
    
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/sendblue/incoming", json=payload)
    
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    mock_push.assert_called_once()
    args, _ = mock_push.call_args
    assert args[0][0]["body"] == "Hello from Sendblue"
    assert args[0][0]["from_handle"] == "+1234567890"

@pytest.mark.anyio
async def test_handle_sendblue_incoming_outbound():
    payload = {
        "number": "+1234567890",
        "content": "Our own message",
        "status": "SENT",
        "is_outbound": True
    }
    
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/sendblue/incoming", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "ignored"
