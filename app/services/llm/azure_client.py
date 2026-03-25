import os
from openai import AzureOpenAI

_client = None


def _get_client():
    global _client
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
    response = client.chat.completions.create(
        model=deployment,
        max_tokens=1000,
        temperature=0.3,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content
