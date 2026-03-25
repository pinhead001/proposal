import importlib
import os
from unittest.mock import patch

import app.core.config as config_mod
import app.services.llm.client as client_mod


@patch.dict("os.environ", {"LLM_PROVIDER": "claude"})
def test_get_llm_client_returns_claude():
    importlib.reload(config_mod)
    importlib.reload(client_mod)
    client = client_mod.get_llm_client()
    assert client.__name__ == "call_claude"


@patch.dict("os.environ", {"LLM_PROVIDER": "azure"})
def test_get_llm_client_returns_azure():
    importlib.reload(config_mod)
    importlib.reload(client_mod)
    client = client_mod.get_llm_client()
    assert client.__name__ == "call_azure"


def test_get_llm_client_defaults_to_claude():
    os.environ.pop("LLM_PROVIDER", None)
    importlib.reload(config_mod)
    importlib.reload(client_mod)
    client = client_mod.get_llm_client()
    assert client.__name__ == "call_claude"
