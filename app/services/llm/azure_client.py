import logging
import os
import threading

from app.core.config import LLM_MAX_TOKENS, LLM_TEMPERATURE
from app.services.llm.retry import with_retries

logger = logging.getLogger(__name__)

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
    from openai import APITimeoutError, RateLimitError, APIError

    client = _get_client()
    deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")

    def _call() -> str:
        response = client.chat.completions.create(
            model=deployment,
            max_tokens=LLM_MAX_TOKENS,
            temperature=LLM_TEMPERATURE,
            messages=[{"role": "user", "content": prompt}],
        )
        if not response.choices:
            raise RuntimeError("Azure LLM returned empty response")
        return response.choices[0].message.content

    return with_retries(
        _call, (APITimeoutError, RateLimitError, APIError), label="Azure",
    )
