from app.core.config import LLM_PROVIDER


def get_llm_client():
    if LLM_PROVIDER == "azure":
        from app.services.llm.azure_client import call_azure
        return call_azure
    else:
        from app.services.llm.claude_client import call_claude
        return call_claude
