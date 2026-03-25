from unittest.mock import patch
from app.services.pipeline.proposal_pipeline import run_pipeline


@patch("app.services.pipeline.proposal_pipeline.call_claude")
def test_run_pipeline_calls_claude(mock_claude):
    mock_claude.side_effect = [
        "analysis result",       # analyze call
        "outline result",        # outline call
        "exec summary content",  # Executive Summary section
        "tech approach content",  # Technical Approach section
    ]

    result = run_pipeline("RFP text", ["past proposal 1"])

    assert mock_claude.call_count == 4
    assert len(result["sections"]) == 2
    assert result["sections"][0]["title"] == "Executive Summary"
    assert result["sections"][0]["content"] == "exec summary content"
    assert result["sections"][1]["title"] == "Technical Approach"
    assert result["sections"][1]["content"] == "tech approach content"


@patch("app.services.pipeline.proposal_pipeline.call_claude")
def test_run_pipeline_passes_prompts_correctly(mock_claude):
    mock_claude.return_value = "mocked"

    run_pipeline("My RFP", ["proposal A", "proposal B"])

    # First call is analyze prompt - should contain proposal texts
    analyze_call = mock_claude.call_args_list[0]
    assert "proposal A" in analyze_call[0][0] or "proposal B" in analyze_call[0][0]

    # Second call is outline prompt - should contain RFP
    outline_call = mock_claude.call_args_list[1]
    assert "My RFP" in outline_call[0][0]
