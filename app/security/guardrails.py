"""
Security guardrails:
- Input sanitisation and truncation
- Prompt injection detection
- Sensitive content blocking
- Output safety check
"""
import re
import logging

logger = logging.getLogger(__name__)

# ── Blocked input patterns ─────────────────────────────────────────────────────

_PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions",
    r"forget\s+(everything|all|your)\s+(you\s+know|instructions|context)",
    r"you\s+are\s+now\s+a?\s*different",
    r"new\s+persona",
    r"reveal\s+(your\s+)?(system\s+prompt|api\s+key|secret|password|instructions)",
    r"print\s+(your\s+)?(system\s+prompt|instructions|config)",
    r"disregard\s+(all\s+)?(previous|prior)\s+instructions",
    r"act\s+as\s+(a\s+)?(different|unrestricted|jailbreak)",
    r"jailbreak",
    r"DAN\s+mode",
    r"developer\s+mode",
]

_SENSITIVE_CREDENTIAL_PATTERNS = [
    r"\b\d{4}\s*\d{4}\s*\d{4}\b",          # partial Aadhaar-like numbers
    r"\botp\b",
    r"\bpassword\b",
    r"\bpin\b",
    r"\bcvv\b",
    r"\bcard\s+number\b",
    r"\bbank\s+account\s+number\b",
    r"\bifsc\b",
    r"\bnetbanking\s+password\b",
]

_BLOCKED_TOPICS = [
    r"\bdiagnos(e|is|ing)\b",
    r"\bmedical\s+(advice|treatment|prescription)\b",
    r"\blegal\s+advice\b",
    r"\binvest(ment)?\s+advice\b",
    r"\binvest\s+in\b",
    r"\bbuy\s+(stocks?|shares?|crypto)\b",
    r"\bhow\s+to\s+(make|build|create)\s+(bomb|weapon|explosive|drugs?)\b",
    r"\bsuicide\b",
    r"\bself.?harm\b",
]

_COMPILED_INJECTION = [re.compile(p, re.IGNORECASE) for p in _PROMPT_INJECTION_PATTERNS]
_COMPILED_CREDENTIAL = [re.compile(p, re.IGNORECASE) for p in _SENSITIVE_CREDENTIAL_PATTERNS]
_COMPILED_TOPICS = [re.compile(p, re.IGNORECASE) for p in _BLOCKED_TOPICS]

# ── Output safety ──────────────────────────────────────────────────────────────

_OUTPUT_LEAK_PATTERNS = [
    r"GEMINI_API_KEY",
    r"ELEVENLABS_API_KEY",
    r"WHATSAPP_TOKEN",
    r"WHATSAPP_APP_SECRET",
    r"system\s+prompt",
    r"sk_[a-zA-Z0-9]{20,}",   # ElevenLabs key pattern
    r"AQ\.[a-zA-Z0-9]{10,}",  # Gemini key pattern
]
_COMPILED_OUTPUT_LEAK = [re.compile(p, re.IGNORECASE) for p in _OUTPUT_LEAK_PATTERNS]

# ── Missing source attribution ─────────────────────────────────────────────────
# Responses about schemes must contain a URL pointing to an official source.
_OFFICIAL_URL_PATTERN = re.compile(
    r"https?://(pmkisan|pmjay|scholarships|nrega|pmayg|mudra|pmvishwakarma"
    r"|myscheme|india\.gov|scholarships\.karnataka|ashraya\.karnataka"
    r"|indiapost|mera\.pmjay)\.gov\.in",
    re.IGNORECASE,
)


class GuardrailError(Exception):
    """Raised when input violates a guardrail."""
    def __init__(self, message: str, safe_reply: str):
        super().__init__(message)
        self.safe_reply = safe_reply


def sanitise_input(text: str, max_chars: int = 2000) -> str:
    """Strip control characters and truncate."""
    # Remove null bytes and non-printable ASCII control chars (except newlines/tabs)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    text = text.strip()
    return text[:max_chars]


def check_input(text: str) -> None:
    """
    Raise GuardrailError if the input violates any policy.
    Call this on all user text before passing to the agent.
    """
    # Prompt injection
    for pattern in _COMPILED_INJECTION:
        if pattern.search(text):
            logger.warning("Prompt injection attempt blocked: %.80s", text)
            raise GuardrailError(
                "Prompt injection detected",
                (
                    "I can only help you find and apply for Indian government schemes. "
                    "Please tell me what kind of help you are looking for — "
                    "for example: farming support, housing, scholarship, or employment."
                ),
            )

    # Sensitive credential requests
    for pattern in _COMPILED_CREDENTIAL:
        if pattern.search(text):
            logger.warning("Sensitive credential request blocked: %.80s", text)
            raise GuardrailError(
                "Sensitive credential request",
                (
                    "I do not ask for or store passwords, PINs, card numbers, or banking details. "
                    "Please never share such information with anyone. "
                    "I can only help you with government scheme information and application steps."
                ),
            )

    # Blocked topics
    for pattern in _COMPILED_TOPICS:
        if pattern.search(text):
            logger.warning("Blocked topic request: %.80s", text)
            raise GuardrailError(
                "Blocked topic",
                (
                    "I'm not able to provide medical, legal, or financial investment advice. "
                    "I can only help you with information about Indian government welfare schemes. "
                    "What scheme are you looking for?"
                ),
            )


def check_output(response_text: str) -> str:
    """
    Scan the agent's output before sending it to the user.
    - Removes any accidental env var / key leakage.
    - Returns the cleaned response.
    """
    for pattern in _COMPILED_OUTPUT_LEAK:
        if pattern.search(response_text):
            logger.error("Output guardrail: credential leak detected — response suppressed.")
            return (
                "I'm sorry, I encountered an internal error. "
                "Please try again or visit https://www.myscheme.gov.in directly."
            )
    return response_text


def redact_phone(text: str) -> str:
    """Redact phone numbers from log strings."""
    return re.sub(r"\b(\+91|91)?[6-9]\d{9}\b", "[REDACTED_PHONE]", text)
