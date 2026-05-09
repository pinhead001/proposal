import logging
import os
import threading
import time

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
                from openai import AzureOpenAI
                _client = AzureOpenAI(
                    api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
                    api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
                    azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT", ""),
                )
    return _client


def call_azure(prompt: str) -> str:
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
            if not response.choices:
                raise RuntimeError("Azure LLM returned empty response")
            return response.choices[0].message.content
        except RuntimeError:
            raise
        except Exception as e:
            if attempt == MAX_RETRIES:
                raise
            delay = RETRY_BASE_DELAY * (2 ** attempt)
            logger.warning("Azure call attempt %d failed (%s), retrying in %ds", attempt + 1, e, delay)
            time.sleep(delay)
