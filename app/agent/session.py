"""
Per-user conversation session state — stored in memory.
Tracks language, last scheme, user profile, and pending question.
"""
from dataclasses import dataclass, field
from threading import Lock
from typing import Optional

_lock = Lock()
_sessions: dict[str, "UserSession"] = {}


@dataclass
class UserSession:
    user_id: str
    detected_language: str = "en"          # "en" | "hi" | "kn"
    last_scheme_name: Optional[str] = None
    last_scheme_record: Optional[dict] = None

    # User profile collected over conversation
    state: Optional[str] = None
    education_level: Optional[str] = None
    category: Optional[str] = None         # general / sc / st / obc
    income_range: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None

    pending_question: Optional[str] = None
    conversation_history: list[dict] = field(default_factory=list)


def get_session(user_id: str) -> UserSession:
    with _lock:
        if user_id not in _sessions:
            _sessions[user_id] = UserSession(user_id=user_id)
        return _sessions[user_id]


def update_session(user_id: str, **kwargs) -> UserSession:
    session = get_session(user_id)
    with _lock:
        for key, value in kwargs.items():
            if hasattr(session, key):
                setattr(session, key, value)
    return session


def append_history(user_id: str, role: str, content: str) -> None:
    """Keep last 10 turns to avoid token bloat."""
    session = get_session(user_id)
    with _lock:
        session.conversation_history.append({"role": role, "content": content})
        if len(session.conversation_history) > 20:
            session.conversation_history = session.conversation_history[-20:]
