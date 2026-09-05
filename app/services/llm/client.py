from typing import Callable

from app.core.config import LLM_PROVIDER


def get_llm_client() -> Callable[[str], str]:
    if LLM_PROVIDER == "azure":
        from app.services.llm.azure_client import call_azure
        return call_azure
    from app.services.llm.claude_client import call_claude
    return call_claude
