"""
Main agent orchestrator — ties together:
  STT → guardrails → RAG retrieval → LLM → output guardrail → TTS
"""
import logging

from app.agent.llm import detect_language, generate_response
from app.agent.session import get_session, update_session, append_history
from app.knowledge.vector_store import retrieve_schemes
from app.security.guardrails import (
    GuardrailError,
    sanitise_input,
    check_input,
    check_output,
)
from app.config import config

logger = logging.getLogger(__name__)


async def process_user_message(
    user_id: str,
    text: str,
) -> str:
    """
    Full pipeline for a text message (already transcribed if from voice).
    Returns the final response text ready to send.
    """
    # 1. Sanitise
    text = sanitise_input(text, max_chars=config.MAX_INPUT_CHARS)

    if not text:
        return "Please send me a message or voice note. I'm here to help you find government schemes."

    # 2. Input guardrails
    try:
        check_input(text)
    except GuardrailError as e:
        append_history(user_id, "user", "[BLOCKED INPUT]")
        append_history(user_id, "assistant", e.safe_reply)
        return e.safe_reply

    # 3. Session
    session = get_session(user_id)

    # 4. Detect language
    lang = detect_language(text)
    update_session(user_id, detected_language=lang)

    # 5. RAG retrieval — semantic search over scheme knowledge base
    retrieved = retrieve_schemes(text, n_results=3)

    # Update last_scheme_name from top result if found
    if retrieved:
        update_session(
            user_id,
            last_scheme_name=retrieved[0]["scheme_name"],
            last_scheme_record=retrieved[0],
        )

    # 6. LLM generation (grounded)
    session = get_session(user_id)  # re-fetch after updates
    response_text = await generate_response(text, retrieved, session)

    # 7. Output guardrail
    response_text = check_output(response_text)

    # Truncate if too long
    if len(response_text) > config.MAX_OUTPUT_CHARS:
        response_text = response_text[: config.MAX_OUTPUT_CHARS] + "…"

    # 8. Persist to conversation history
    append_history(user_id, "user", text)
    append_history(user_id, "assistant", response_text)

    return response_text
