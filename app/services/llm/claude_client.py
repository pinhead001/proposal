import logging
import os
import threading

from anthropic import Anthropic, APITimeoutError, RateLimitError

from app.core.config import LLM_MAX_TOKENS, LLM_TEMPERATURE
from app.services.llm.retry import with_retries

logger = logging.getLogger(__name__)

_client: Anthropic | None = None
_lock = threading.Lock()


def _get_client() -> Anthropic:
    global _client
    if _client is None:
        with _lock:
            if _client is None:
                _client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    return _client


def call_claude(prompt: str) -> str:
    client = _get_client()

    def _call() -> str:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=LLM_MAX_TOKENS,
            temperature=LLM_TEMPERATURE,
            messages=[{"role": "user", "content": prompt}],
        )
        if not response.content:
            raise RuntimeError("LLM returned empty response")
        return response.content[0].text

    return with_retries(_call, (APITimeoutError, RateLimitError), label="Claude")
