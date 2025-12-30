# Missive-Sendblue Webhook Bridge

A FastAPI-based webhook server to bridge Missive Custom Channels with Sendblue for iMessage/SMS support.

## Features

- **Missive to Sendblue:** Automatically sends iMessages when you reply from Missive.
- **Sendblue to Missive:** Pushes incoming iMessages directly into your Missive inbox.
- **Security:** Support for webhook signature verification from both Missive and Sendblue.
- **Deployment Ready:** Configured for easy deployment on Vercel.

## Setup

1.  **Clone the repository.**
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Configure environment variables:**
    Copy `.env.example` to `.env` and fill in your API keys.
4.  **Deploy to Vercel:**
    Use the Vercel CLI:
    ```bash
    vercel
    ```

## Webhook URLs

- **Missive Outgoing Webhook:** `https://your-domain.vercel.app/missive/outgoing`
- **Sendblue Incoming Webhook:** `https://your-domain.vercel.app/sendblue/incoming`

## Configuration Details

### Missive
1.  Create a **Custom Channel** in Missive.
2.  Set the **Outgoing webhook URL** to `.../missive/outgoing`.
3.  (Optional) Set a **Signature secret** and add it to `MISSIVE_WEBHOOK_SECRET` in your env.
4.  Get your **API Token** from Missive settings.
5.  Get the **Channel ID** of your custom channel.

### Sendblue
1.  Get your **API Key** and **API Secret** from the Sendblue dashboard.
2.  Set the **Webhook URL** in Sendblue to `.../sendblue/incoming`.
3.  (Optional) Note the **Signing Secret** and add it to `SENDBLUE_SIGNING_SECRET` in your env.

