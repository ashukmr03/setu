"""
Incoming webhook handler.
Supports both Twilio (active) and Meta WhatsApp Cloud API (commented out).

Twilio sends form-encoded POST data.
Meta sends JSON POST data.

To switch to Meta: set USE_TWILIO=False in client.py and use handle_meta_event().
"""
import logging

from app.agent.orchestrator import process_user_message
from app.security.guardrails import redact_phone
from app.voice.pipeline import (
    transcribe_audio,
    synthesise_speech,
)
from app.whatsapp.client import (
    send_text_message,
    send_audio_message,
    upload_audio,
    download_whatsapp_audio,
    get_media_url,
)
from app.config import config

logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════════════
#  TWILIO HANDLER (active)
# ══════════════════════════════════════════════════════════════════════════════

async def handle_twilio_event(form_data: dict) -> None:
    """
    Parse incoming Twilio WhatsApp webhook (application/x-www-form-urlencoded).

    Key fields Twilio sends:
      From        — sender's WhatsApp number e.g. whatsapp:+919876543210
      Body        — text content (empty for voice/media)
      NumMedia    — number of attached media files
      MediaUrl0   — URL of first media file (voice note)
      MediaContentType0 — MIME type e.g. audio/ogg
    """
    from_number = form_data.get("From", "")
    body = form_data.get("Body", "").strip()
    num_media = int(form_data.get("NumMedia", "0"))

    logger.info(
        "Twilio message from=%s body_len=%d media=%d",
        redact_phone(from_number), len(body), num_media,
    )

    transcribed_text = ""
    is_voice = False

    if num_media > 0:
        # Voice note or media attachment
        media_url = form_data.get("MediaUrl0", "")
        media_type = form_data.get("MediaContentType0", "")

        if "audio" in media_type:
            is_voice = True
            try:
                audio_bytes = await download_whatsapp_audio(
                    media_url, config.TWILIO_AUTH_TOKEN
                )
                transcribed_text = transcribe_audio(audio_bytes, mime_type=media_type)
            except Exception as e:
                logger.error("Failed to process voice note: %s", e)
                await send_text_message(
                    from_number,
                    "Sorry, I could not process your voice note. Please try again or send a text.",
                )
                return

            if not transcribed_text:
                await send_text_message(
                    from_number,
                    "Sorry, I could not understand the voice note. Please speak clearly and try again.",
                )
                return
        else:
            # Image / video / document — not supported
            await send_text_message(
                from_number,
                "I can only process text messages and voice notes. Please send a voice note or type your question.",
            )
            return

    elif body:
        transcribed_text = body

    else:
        return

    # Run agent pipeline
    response_text = await process_user_message(from_number, transcribed_text)

    # Always send text reply
    await send_text_message(from_number, response_text)

    # If original was voice → also send voice reply
    if is_voice and config.ELEVENLABS_API_KEY:
        try:
            from app.agent.session import get_session
            session = get_session(from_number)
            ogg_bytes = synthesise_speech(response_text, language=session.detected_language)
            if ogg_bytes:
                public_url = await upload_audio(ogg_bytes)
                if public_url:
                    await send_audio_message(from_number, public_url)
        except Exception as e:
            logger.error("Voice reply failed (non-fatal): %s", e)
            # Text already sent — voice failure is acceptable


# ══════════════════════════════════════════════════════════════════════════════
#  META WHATSAPP CLOUD API HANDLER — commented out, restore when ready
# ══════════════════════════════════════════════════════════════════════════════

# async def handle_meta_event(payload: dict) -> None:
#     """Parse incoming Meta WhatsApp Cloud API webhook (JSON)."""
#     try:
#         entry = payload.get("entry", [])
#         for ent in entry:
#             for change in ent.get("changes", []):
#                 value = change.get("value", {})
#                 for msg in value.get("messages", []):
#                     await _process_meta_message(msg)
#     except Exception as e:
#         logger.error("Meta webhook handler error: %s", e)
#
# async def _process_meta_message(msg: dict) -> None:
#     from_number = msg.get("from", "")
#     msg_type = msg.get("type", "")
#     transcribed_text = ""
#     is_voice = False
#
#     if msg_type == "text":
#         transcribed_text = msg.get("text", {}).get("body", "").strip()
#     elif msg_type == "audio":
#         is_voice = True
#         media_id = msg.get("audio", {}).get("id", "")
#         media_url = await get_media_url(media_id)
#         audio_bytes = await download_whatsapp_audio(media_url, config.WHATSAPP_TOKEN)
#         transcribed_text = transcribe_audio(audio_bytes)
#     else:
#         await send_text_message(from_number, "Please send a voice note or text message.")
#         return
#
#     if not transcribed_text:
#         return
#
#     response_text = await process_user_message(from_number, transcribed_text)
#     await send_text_message(from_number, response_text)
#
#     if is_voice and config.ELEVENLABS_API_KEY:
#         try:
#             from app.agent.session import get_session
#             session = get_session(from_number)
#             ogg_bytes = synthesise_speech(response_text, language=session.detected_language)
#             if ogg_bytes:
#                 media_id = await upload_audio(ogg_bytes)
#                 await send_audio_message(from_number, media_id)
#         except Exception as e:
#             logger.error("Meta voice reply failed: %s", e)
