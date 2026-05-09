import logging
import os
import threading
import time

from anthropic import APITimeoutError, RateLimitError

from app.core.config import LLM_MAX_TOKENS, LLM_TEMPERATURE

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
RETRY_BASE_DELAY = 2

_client = None
_lock = threading.Lock()


def _get_client():
    global _client
    if _client is None:
        with _lock:
            if _client is None:
                from anthropic import Anthropic
                _client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    return _client


def call_claude(prompt: str) -> str:
    client = _get_client()
    for attempt in range(MAX_RETRIES + 1):
        try:
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=LLM_MAX_TOKENS,
                temperature=LLM_TEMPERATURE,
                messages=[{"role": "user", "content": prompt}],
            )
            if not response.content:
                raise RuntimeError("LLM returned empty response")
            return response.content[0].text
        except (APITimeoutError, RateLimitError) as e:
            if attempt == MAX_RETRIES:
                raise
            delay = RETRY_BASE_DELAY * (2 ** attempt)
            logger.warning("LLM call attempt %d failed (%s), retrying in %ds", attempt + 1, e, delay)
            time.sleep(delay)
