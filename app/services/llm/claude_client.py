import os
import time
import logging
import threading
from anthropic import Anthropic, APIError, APITimeoutError, RateLimitError
from app.core.config import LLM_MAX_TOKENS, LLM_TEMPERATURE

logger = logging.getLogger(__name__)

_client = None
_lock = threading.Lock()

MAX_RETRIES = 3
RETRY_BASE_DELAY = 2


def _get_client():
    global _client
    if _client is None:
        with _lock:
            if _client is None:
                api_key = os.environ.get("ANTHROPIC_API_KEY")
                if not api_key:
                    raise RuntimeError(
                        "ANTHROPIC_API_KEY environment variable is not set. "
                        "Get your key at https://console.anthropic.com/"
                    )
                _client = Anthropic(api_key=api_key)
    return _client


def call_claude(prompt: str):
    client = _get_client()

    for attempt in range(MAX_RETRIES + 1):
        try:
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=LLM_MAX_TOKENS,
                temperature=LLM_TEMPERATURE,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text
        except (APITimeoutError, RateLimitError) as e:
            if attempt == MAX_RETRIES:
                logger.error("Claude API failed after %d retries: %s", MAX_RETRIES, e)
                raise
            delay = RETRY_BASE_DELAY * (2 ** attempt)
            logger.warning("Claude API error (attempt %d/%d), retrying in %ds: %s", attempt + 1, MAX_RETRIES, delay, e)
            time.sleep(delay)
        except APIError as e:
            logger.error("Claude API error (non-retryable): %s", e)
            raise
