import os
from anthropic import Anthropic

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


def call_claude(prompt: str):
    response = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=1000,
        temperature=0.3,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text
