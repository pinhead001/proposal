import os
import time
import logging
import threading
from openai import AzureOpenAI, APITimeoutError, RateLimitError, APIError
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
                _client = AzureOpenAI(
                    api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
                    api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-02-01"),
                    azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT", ""),
                )
    return _client


def call_azure(prompt: str):
    client = _get_client()
    deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")

    for attempt in range(MAX_RETRIES + 1):
        try:
            response = client.chat.completions.create(
                model=deployment,
                max_tokens=LLM_MAX_TOKENS,
                temperature=LLM_TEMPERATURE,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content
        except (APITimeoutError, RateLimitError) as e:
            if attempt == MAX_RETRIES:
                logger.error("Azure API failed after %d retries: %s", MAX_RETRIES, e)
                raise
            delay = RETRY_BASE_DELAY * (2 ** attempt)
            logger.warning("Azure API error (attempt %d/%d), retrying in %ds: %s", attempt + 1, MAX_RETRIES, delay, e)
            time.sleep(delay)
        except APIError as e:
            logger.error("Azure API error (non-retryable): %s", e)
            raise
