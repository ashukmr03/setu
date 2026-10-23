"""
Simple in-memory per-user rate limiter (no Redis needed).
Allows N requests per 60-second sliding window per WhatsApp user ID.
"""
import time
import logging
from collections import defaultdict, deque
from threading import Lock

from app.config import config

logger = logging.getLogger(__name__)

_lock = Lock()
# Maps user_id -> deque of timestamps
_request_log: dict[str, deque] = defaultdict(deque)


def is_rate_limited(user_id: str) -> bool:
    """
    Returns True if the user has exceeded the rate limit.
    Sliding window of 60 seconds.
    """
    now = time.time()
    window = 60.0
    limit = config.RATE_LIMIT_PER_MINUTE

    with _lock:
        dq = _request_log[user_id]
        # Evict timestamps outside the window
        while dq and now - dq[0] > window:
            dq.popleft()

        if len(dq) >= limit:
            logger.warning("Rate limit exceeded for user %s", user_id)
            return True

        dq.append(now)
        return False
