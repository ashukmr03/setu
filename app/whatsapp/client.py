"""
Messaging client — currently using Twilio WhatsApp Sandbox.

To switch back to Meta WhatsApp Cloud API:
  1. Set USE_TWILIO = False
  2. Fill WHATSAPP_TOKEN, WHATSAPP_PHONE_NUMBER_ID, WHATSAPP_APP_SECRET in .env
  3. Uncomment the Meta section at the bottom of this file
"""
import logging
import tempfile
import os

import httpx
from twilio.rest import Client as TwilioClient

from app.config import config

logger = logging.getLogger(__name__)

# ── Toggle ─────────────────────────────────────────────────────────────────────
USE_TWILIO = True   # ← flip to False when Meta WhatsApp is ready

# ── Twilio client (lazy init) ──────────────────────────────────────────────────
_twilio: TwilioClient | None = None

def _get_twilio() -> TwilioClient:
    global _twilio
    if _twilio is None:
        _twilio = TwilioClient(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN)
    return _twilio


# ══════════════════════════════════════════════════════════════════════════════
#  TWILIO IMPLEMENTATION
# ══════════════════════════════════════════════════════════════════════════════

async def send_text_message(to: str, body: str) -> dict:
    """Send a WhatsApp text message via Twilio sandbox."""
    client = _get_twilio()
    # Twilio requires whatsapp: prefix
    to_wa = to if to.startswith("whatsapp:") else f"whatsapp:{to}"
    from_wa = config.TWILIO_WHATSAPP_NUMBER

    msg = client.messages.create(
        from_=from_wa,
        to=to_wa,
        body=body,
    )
    logger.info("Text sent via Twilio SID=%s to=%s", msg.sid, to_wa[-4:])
    return {"sid": msg.sid, "status": msg.status}


async def send_audio_message(to: str, media_id_or_url: str) -> dict:
    """
    Send a WhatsApp audio message via Twilio.
    media_id_or_url: a publicly accessible URL to the OGG file.
    Twilio sandbox accepts media_url directly.
    """
    client = _get_twilio()
    to_wa = to if to.startswith("whatsapp:") else f"whatsapp:{to}"
    from_wa = config.TWILIO_WHATSAPP_NUMBER

    msg = client.messages.create(
        from_=from_wa,
        to=to_wa,
        media_url=[media_id_or_url],
    )
    logger.info("Audio sent via Twilio SID=%s to=%s", msg.sid, to_wa[-4:])
    return {"sid": msg.sid, "status": msg.status}


async def upload_audio(ogg_bytes: bytes) -> str:
    """
    Twilio needs a publicly accessible URL for media.
    We upload to a temp file endpoint or use a file host.
    For the sandbox demo we use file.io (free ephemeral file host).
    Returns a public URL string.
    """
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(
                "https://file.io",
                files={"file": ("voice.ogg", ogg_bytes, "audio/ogg; codecs=opus")},
                data={"expires": "1d", "maxDownloads": "1", "autoDelete": "true"},
            )
            resp.raise_for_status()
            data = resp.json()
            url = data.get("link", "")
            logger.info("Audio uploaded to file.io: %s", url)
            return url
    except Exception as e:
        logger.error("Audio upload failed: %s", e)
        return ""


async def get_media_url(media_id: str) -> str:
    """
    For Twilio, media URL comes directly in the webhook payload
    as MediaUrl0. This function is a passthrough.
    """
    return media_id


async def download_whatsapp_audio(media_url: str, token: str) -> bytes:
    """
    Download audio from Twilio media URL.
    Twilio requires Basic Auth using account SID + auth token.
    """
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(
            media_url,
            auth=(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN),
        )
        resp.raise_for_status()
        return resp.content


# ══════════════════════════════════════════════════════════════════════════════
#  META WHATSAPP CLOUD API — commented out, restore when ready
# ══════════════════════════════════════════════════════════════════════════════

# _META_BASE = "https://graph.facebook.com/v19.0"
#
# def _meta_headers() -> dict:
#     return {
#         "Authorization": f"Bearer {config.WHATSAPP_TOKEN}",
#         "Content-Type": "application/json",
#     }
#
# async def send_text_message_meta(to: str, body: str) -> dict:
#     payload = {
#         "messaging_product": "whatsapp",
#         "recipient_type": "individual",
#         "to": to,
#         "type": "text",
#         "text": {"preview_url": False, "body": body},
#     }
#     async with httpx.AsyncClient(timeout=15) as client:
#         resp = await client.post(
#             f"{_META_BASE}/{config.WHATSAPP_PHONE_NUMBER_ID}/messages",
#             headers=_meta_headers(),
#             json=payload,
#         )
#         resp.raise_for_status()
#         return resp.json()
#
# async def upload_audio_meta(ogg_bytes: bytes) -> str:
#     async with httpx.AsyncClient(timeout=30) as client:
#         resp = await client.post(
#             f"{_META_BASE}/{config.WHATSAPP_PHONE_NUMBER_ID}/media",
#             headers={"Authorization": f"Bearer {config.WHATSAPP_TOKEN}"},
#             files={
#                 "file": ("voice.ogg", ogg_bytes, "audio/ogg; codecs=opus"),
#                 "messaging_product": (None, "whatsapp"),
#                 "type": (None, "audio/ogg"),
#             },
#         )
#         resp.raise_for_status()
#         return resp.json()["id"]
#
# async def send_audio_message_meta(to: str, media_id: str) -> dict:
#     payload = {
#         "messaging_product": "whatsapp",
#         "recipient_type": "individual",
#         "to": to,
#         "type": "audio",
#         "audio": {"id": media_id},
#     }
#     async with httpx.AsyncClient(timeout=15) as client:
#         resp = await client.post(
#             f"{_META_BASE}/{config.WHATSAPP_PHONE_NUMBER_ID}/messages",
#             headers=_meta_headers(),
#             json=payload,
#         )
#         resp.raise_for_status()
#         return resp.json()
#
# async def get_media_url_meta(media_id: str) -> str:
#     async with httpx.AsyncClient(timeout=15) as client:
#         resp = await client.get(
#             f"{_META_BASE}/{media_id}",
#             headers={"Authorization": f"Bearer {config.WHATSAPP_TOKEN}"},
#         )
#         resp.raise_for_status()
#         return resp.json()["url"]
#
# async def download_whatsapp_audio_meta(media_url: str, token: str) -> bytes:
#     headers = {"Authorization": f"Bearer {token}"}
#     async with httpx.AsyncClient(timeout=30) as client:
#         resp = await client.get(media_url, headers=headers)
#         resp.raise_for_status()
#         return resp.content
