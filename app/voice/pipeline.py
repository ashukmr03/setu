"""
Voice pipeline:
  WhatsApp audio URL → download → ElevenLabs STT → text
  text → ElevenLabs TTS → mp3 bytes → ogg/opus (WhatsApp native voice note)

ElevenLabs STT supports Hindi, Kannada, and English natively.
ElevenLabs TTS outputs MP3 which we convert to OGG OPUS so WhatsApp
renders it as a playable voice note instead of a file attachment.
"""
import io
import logging
import tempfile
import os

import httpx
from elevenlabs.client import ElevenLabs
try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False

from app.config import config

logger = logging.getLogger(__name__)

_eleven = ElevenLabs(api_key=config.ELEVENLABS_API_KEY)

# Multilingual voice — "Rachel" supports Hindi/Kannada/English well
# You can swap to any ElevenLabs voice ID from your dashboard
_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Rachel — multilingual
_TTS_MODEL = "eleven_multilingual_v2"
_STT_MODEL = "scribe_v1"


async def download_whatsapp_audio(media_url: str, whatsapp_token: str) -> bytes:
    """
    Download audio file from WhatsApp CDN.
    WhatsApp sends a media_id; the caller must first resolve it to a URL
    via the WhatsApp API (handled in whatsapp/client.py).
    """
    headers = {"Authorization": f"Bearer {whatsapp_token}"}
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(media_url, headers=headers)
        resp.raise_for_status()
        return resp.content


def transcribe_audio(audio_bytes: bytes, mime_type: str = "audio/ogg") -> str:
    """
    Send audio bytes to ElevenLabs STT (Scribe).
    Returns transcribed text string.
    """
    try:
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "voice.ogg"  # ElevenLabs needs a filename hint

        result = _eleven.speech_to_text.convert(
            file=audio_file,
            model_id=_STT_MODEL,
            tag_audio_events=False,
            diarize=False,
        )
        text = result.text.strip() if hasattr(result, "text") else str(result).strip()
        logger.info("STT transcription: %.100s", text)
        return text
    except Exception as e:
        logger.error("ElevenLabs STT error: %s", e)
        return ""


def synthesise_speech(text: str, language: str = "en") -> bytes:
    """
    Convert text to speech using ElevenLabs multilingual model.
    Returns OGG OPUS bytes ready to upload to WhatsApp.
    """
    try:
        # Generate MP3 audio
        audio_generator = _eleven.text_to_speech.convert(
            voice_id=_VOICE_ID,
            text=text,
            model_id=_TTS_MODEL,
            output_format="mp3_44100_128",
        )
        mp3_bytes = b"".join(audio_generator)

        # Convert MP3 → OGG OPUS (WhatsApp native voice note format)
        ogg_bytes = _mp3_to_ogg_opus(mp3_bytes)
        logger.info("TTS synthesised %d bytes of OGG audio.", len(ogg_bytes))
        return ogg_bytes
    except Exception as e:
        logger.error("ElevenLabs TTS error: %s", e)
        return b""


def _mp3_to_ogg_opus(mp3_bytes: bytes) -> bytes:
    """Convert MP3 bytes to OGG OPUS. Falls back to returning mp3 if pydub unavailable."""
    if not PYDUB_AVAILABLE:
        logger.warning("pydub not available — sending MP3 directly.")
        return mp3_bytes

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_mp3:
        tmp_mp3.write(mp3_bytes)
        tmp_mp3_path = tmp_mp3.name

    tmp_ogg_path = tmp_mp3_path.replace(".mp3", ".ogg")
    try:
        audio = AudioSegment.from_mp3(tmp_mp3_path)
        audio.export(
            tmp_ogg_path,
            format="ogg",
            codec="libopus",
            parameters=["-ar", "16000", "-ac", "1", "-b:a", "32k"],
        )
        with open(tmp_ogg_path, "rb") as f:
            return f.read()
    finally:
        os.unlink(tmp_mp3_path)
        if os.path.exists(tmp_ogg_path):
            os.unlink(tmp_ogg_path)
