from unittest.mock import patch, MagicMock
from app.services.pipeline.proposal_pipeline import run_pipeline


@patch("app.services.pipeline.proposal_pipeline.get_llm_client")
def test_run_pipeline_calls_llm(mock_get_client):
    mock_llm = MagicMock(side_effect=[
        "analysis result",       # analyze call
        "outline result",        # outline call
        "exec summary content",  # Executive Summary section
        "tech approach content",  # Technical Approach section
    ])
    mock_get_client.return_value = mock_llm

    result = run_pipeline("RFP text", ["past proposal 1"])

    assert mock_llm.call_count == 4
    assert len(result["sections"]) == 2
    assert result["sections"][0]["title"] == "Executive Summary"
    assert result["sections"][0]["content"] == "exec summary content"
    assert result["sections"][1]["title"] == "Technical Approach"
    assert result["sections"][1]["content"] == "tech approach content"


@patch("app.services.pipeline.proposal_pipeline.get_llm_client")
def test_run_pipeline_passes_prompts_correctly(mock_get_client):
    mock_llm = MagicMock(return_value="mocked")
    mock_get_client.return_value = mock_llm

    run_pipeline("My RFP", ["proposal A", "proposal B"])

    # First call is analyze prompt - should contain proposal texts
    analyze_call = mock_llm.call_args_list[0]
    assert "proposal A" in analyze_call[0][0] or "proposal B" in analyze_call[0][0]

    # Second call is outline prompt - should contain RFP
    outline_call = mock_llm.call_args_list[1]
    assert "My RFP" in outline_call[0][0]
