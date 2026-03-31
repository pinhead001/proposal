import os
import threading
from anthropic import Anthropic
from app.core.config import LLM_MAX_TOKENS, LLM_TEMPERATURE

_client = None
_lock = threading.Lock()


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
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=LLM_MAX_TOKENS,
        temperature=LLM_TEMPERATURE,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text
