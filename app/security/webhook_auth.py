"""
Webhook signature verification for both Twilio and Meta.
"""
import hashlib
import hmac
import base64
import logging
from urllib.parse import urlencode

from app.config import config

logger = logging.getLogger(__name__)


# ── Twilio signature verification ──────────────────────────────────────────────
def verify_twilio_signature(
    raw_body: bytes,
    twilio_signature: str,
    url: str,
) -> bool:
    """
    Twilio signs requests with HMAC-SHA1 of (url + sorted POST params).
    Docs: https://www.twilio.com/docs/usage/webhooks/webhooks-security
    """
    if not config.TWILIO_AUTH_TOKEN:
        logger.warning("TWILIO_AUTH_TOKEN not set — skipping Twilio signature check (dev mode).")
        return True

    if not twilio_signature:
        logger.warning("Missing X-Twilio-Signature header.")
        return False

    try:
        # Parse form body into sorted key=value string
        from urllib.parse import parse_qs
        params = {}
        for pair in raw_body.decode("utf-8").split("&"):
            if "=" in pair:
                k, v = pair.split("=", 1)
                from urllib.parse import unquote_plus
                params[unquote_plus(k)] = unquote_plus(v)

        # Twilio: concatenate url + sorted params
        s = url + "".join(f"{k}{v}" for k, v in sorted(params.items()))

        computed = base64.b64encode(
            hmac.new(
                key=config.TWILIO_AUTH_TOKEN.encode("utf-8"),
                msg=s.encode("utf-8"),
                digestmod=hashlib.sha1,
            ).digest()
        ).decode("utf-8")

        if not hmac.compare_digest(computed, twilio_signature):
            logger.warning("Twilio signature mismatch.")
            return False

        return True
    except Exception as e:
        logger.error("Twilio signature verification error: %s", e)
        return False


# ── Meta WhatsApp signature verification (kept for when Meta is ready) ─────────
def verify_webhook_signature(payload_bytes: bytes, signature_header: str | None) -> bool:
    """
    Verify X-Hub-Signature-256 from Meta.
    Returns True if valid.
    """
    if not config.WHATSAPP_APP_SECRET:
        logger.warning("WHATSAPP_APP_SECRET not set — skipping Meta signature check (dev mode).")
        return True

    if not signature_header:
        logger.warning("Missing X-Hub-Signature-256 header.")
        return False

    if not signature_header.startswith("sha256="):
        logger.warning("Malformed Meta signature header.")
        return False

    expected_sig = signature_header[len("sha256="):]
    computed_sig = hmac.new(
        key=config.WHATSAPP_APP_SECRET.encode("utf-8"),
        msg=payload_bytes,
        digestmod=hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(computed_sig, expected_sig):
        logger.warning("Meta webhook signature mismatch.")
        return False

    return True
