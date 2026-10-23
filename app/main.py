"""
FastAPI application — entry point.

Routes:
  GET  /webhook  — Meta webhook verification (kept for when Meta is ready)
  POST /webhook  — Incoming messages
                   Twilio sends: application/x-www-form-urlencoded
                   Meta sends:   application/json  (commented out below)
  GET  /health   — Health check for Render
"""
import asyncio
import logging
import sys

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import PlainTextResponse

from app.config import config
from app.security.rate_limiter import is_rate_limited
from app.security.webhook_auth import verify_twilio_signature
from app.whatsapp.handler import handle_twilio_event

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    stream=sys.stdout,
    level=getattr(logging, config.LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Setu — Government Scheme Voice Agent",
    version="1.0.0",
    docs_url="/docs" if config.APP_ENV == "development" else None,
    redoc_url=None,
)


# ── Health check ───────────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok", "service": "setu-agent"}


# ── Meta webhook verification GET (kept for when Meta is ready) ────────────────
@app.get("/webhook")
async def verify_meta_webhook(request: Request):
    """Meta hub verification — kept commented-friendly for future use."""
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")
    if mode == "subscribe" and token == config.WHATSAPP_VERIFY_TOKEN:
        logger.info("Meta webhook verified.")
        return PlainTextResponse(content=challenge, status_code=200)
    raise HTTPException(status_code=403, detail="Verification failed")


# ── Incoming webhook POST ──────────────────────────────────────────────────────
@app.post("/webhook")
async def receive_message(request: Request):
    raw_body = await request.body()
    content_type = request.headers.get("content-type", "")
    logger.info("POST /webhook received. content-type=%s body_len=%d", content_type, len(raw_body))
    logger.info("Headers: %s", dict(request.headers))

    # Twilio signature verification
    url = str(request.url)
    sig = request.headers.get("X-Twilio-Signature", "")
    if not verify_twilio_signature(raw_body, sig, url):
        logger.warning("Invalid Twilio signature — request rejected.")
        raise HTTPException(status_code=401, detail="Invalid signature")

    # Parse form data
    form = await request.form()
    form_data = dict(form)

    # Rate limit by sender
    sender = form_data.get("From", request.client.host if request.client else "unknown")
    if is_rate_limited(sender):
        # Return TwiML empty response — Twilio expects valid XML on 200
        return Response(
            content="<Response></Response>",
            media_type="text/xml",
            status_code=200,
        )

    # Acknowledge immediately, process async
    asyncio.create_task(handle_twilio_event(form_data))
    return Response(content="<Response></Response>", media_type="text/xml", status_code=200)

    # ── META (commented out — restore when Meta WhatsApp is ready) ─────────────
    # from app.security.webhook_auth import verify_webhook_signature
    # from app.whatsapp.handler import handle_meta_event
    #
    # sig_header = request.headers.get("X-Hub-Signature-256")
    # if not verify_webhook_signature(raw_body, sig_header):
    #     raise HTTPException(status_code=401, detail="Invalid signature")
    #
    # payload = await request.json() if raw_body else {}
    # try:
    #     sender = payload["entry"][0]["changes"][0]["value"]["messages"][0]["from"]
    # except (KeyError, IndexError, TypeError):
    #     sender = request.client.host if request.client else "unknown"
    #
    # if is_rate_limited(sender):
    #     return Response(status_code=429)
    #
    # asyncio.create_task(handle_meta_event(payload))
    # return Response(status_code=200)
