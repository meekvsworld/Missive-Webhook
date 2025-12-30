# Missive-Sendblue Webhook Bridge

This project implements a webhook server to bridge Missive Custom Channels with the Sendblue API (iMessage/SMS). It allows users to send and receive iMessages directly within Missive.

## Architecture

The bridge consists of two main flows:

1.  **Missive to Sendblue (Outgoing Messages)**
    *   **Source:** Missive Custom Channel Outgoing Webhook.
    *   **Endpoint:** `POST /missive/outgoing`
    *   **Logic:** Receives message data from Missive, extracts the recipient and content, and calls the Sendblue API to send the message.
    *   **Security:** Validates Missive's signature using the `X-Missive-Signature` header.

2.  **Sendblue to Missive (Incoming Messages)**
    *   **Source:** Sendblue Incoming Webhook.
    *   **Endpoint:** `POST /sendblue/incoming`
    *   **Logic:** Receives message data from Sendblue, and pushes it to the Missive API.
    *   **Security:** Validates Sendblue's signing secret using the `sb-signing-secret` header.

## Tech Stack

*   **Language:** Python 3.10+
*   **Framework:** FastAPI
*   **Validation:** Pydantic
*   **Deployment:** Vercel (Serverless Functions)
*   **API Clients:** `httpx`

## Configuration

Environment variables:
*   `MISSIVE_API_TOKEN`: To push messages to Missive.
*   `MISSIVE_WEBHOOK_SECRET`: To verify outgoing requests from Missive.
*   `SENDBLUE_API_KEY`: To send messages via Sendblue.
*   `SENDBLUE_API_SECRET`: To send messages via Sendblue.
*   `SENDBLUE_SIGNING_SECRET`: To verify incoming requests from Sendblue.
*   `MISSIVE_CHANNEL_ID`: The ID of the custom channel in Missive.

## File Structure

```
/
├── api/
│   └── main.py          # FastAPI application entry point
├── app/
│   ├── __init__.py
│   ├── models/          # Pydantic models for validation
│   ├── services/        # Logic for interacting with APIs
│   └── utils/           # Helper functions (e.g., signature verification)
├── tests/               # Pytest unit tests
├── vercel.json          # Vercel configuration
├── requirements.txt     # Dependencies
└── .env.example         # Template for environment variables
```

