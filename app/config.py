"""
Central config — loaded once at startup from environment variables.
"""
import os
from dotenv import load_dotenv

load_dotenv()


def _require(key: str) -> str:
    val = os.getenv(key, "").strip()
    if not val:
        raise RuntimeError(f"Missing required environment variable: {key}")
    return val


def _optional(key: str, default: str = "") -> str:
    return os.getenv(key, default).strip()


class Config:
    # LLM
    GEMINI_API_KEY: str = _require("GEMINI_API_KEY")

    # Voice
    ELEVENLABS_API_KEY: str = _require("ELEVENLABS_API_KEY")

    # ── Twilio (active) ────────────────────────────────────────────────────────
    TWILIO_ACCOUNT_SID: str = _optional("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN: str = _optional("TWILIO_AUTH_TOKEN")
    TWILIO_WHATSAPP_NUMBER: str = _optional("TWILIO_WHATSAPP_NUMBER", "whatsapp:+17372508034")

    # ── Meta WhatsApp (kept, fill when ready) ──────────────────────────────────
    WHATSAPP_TOKEN: str = _optional("WHATSAPP_TOKEN")
    WHATSAPP_PHONE_NUMBER_ID: str = _optional("WHATSAPP_PHONE_NUMBER_ID")
    WHATSAPP_APP_SECRET: str = _optional("WHATSAPP_APP_SECRET")
    WHATSAPP_VERIFY_TOKEN: str = _optional("WHATSAPP_VERIFY_TOKEN", "setu_verify_2024")

    # App
    APP_ENV: str = _optional("APP_ENV", "development")
    LOG_LEVEL: str = _optional("LOG_LEVEL", "INFO")

    # ChromaDB
    CHROMA_DB_PATH: str = _optional("CHROMA_DB_PATH", "./chroma_db")

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 10

    # Text limits
    MAX_INPUT_CHARS: int = 2000
    MAX_OUTPUT_CHARS: int = 3000


config = Config()
