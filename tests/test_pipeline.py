import pytest
from unittest.mock import patch, MagicMock
from app.services.pipeline.proposal_pipeline import run_pipeline, DEFAULT_SECTIONS


@patch("app.services.pipeline.proposal_pipeline.save_analysis")
@patch("app.services.pipeline.proposal_pipeline.load_analysis", return_value=None)
@patch("app.services.pipeline.proposal_pipeline.load_proposals", return_value=[])
@patch("app.services.pipeline.proposal_pipeline.get_llm_client")
def test_run_pipeline_calls_llm(mock_get_client, mock_load_p, mock_load_a, mock_save_a):
    # 1 analyze + 1 outline + 5 sections = 7 calls
    mock_llm = MagicMock(side_effect=[
        "analysis result",
        "outline result",
        *[f"content for {s}" for s in DEFAULT_SECTIONS],
    ])
    mock_get_client.return_value = mock_llm

    result = run_pipeline("RFP text", ["past proposal 1"])

    assert mock_llm.call_count == 7
    assert len(result["sections"]) == 5
    assert result["sections"][0]["title"] == "Executive Summary"
    assert result["sections"][1]["title"] == "Technical Approach"
    assert result["sections"][2]["title"] == "Staffing Plan"
    assert result["sections"][3]["title"] == "Past Performance"
    assert result["sections"][4]["title"] == "Cost Narrative"


@patch("app.services.pipeline.proposal_pipeline.save_analysis")
@patch("app.services.pipeline.proposal_pipeline.load_analysis", return_value=None)
@patch("app.services.pipeline.proposal_pipeline.load_proposals", return_value=[])
@patch("app.services.pipeline.proposal_pipeline.get_llm_client")
def test_run_pipeline_passes_prompts_correctly(mock_get_client, mock_load_p, mock_load_a, mock_save_a):
    mock_llm = MagicMock(return_value="mocked")
    mock_get_client.return_value = mock_llm

    run_pipeline("My RFP", ["proposal A", "proposal B"])

    # First call is analyze prompt - should contain proposal texts
    analyze_call = mock_llm.call_args_list[0]
    assert "proposal A" in analyze_call[0][0] or "proposal B" in analyze_call[0][0]

    # Second call is outline prompt - should contain RFP
    outline_call = mock_llm.call_args_list[1]
    assert "My RFP" in outline_call[0][0]


@patch("app.services.pipeline.proposal_pipeline.load_analysis", return_value="cached analysis")
@patch("app.services.pipeline.proposal_pipeline.load_proposals", return_value=[])
@patch("app.services.pipeline.proposal_pipeline.get_llm_client")
def test_run_pipeline_uses_cached_analysis(mock_get_client, mock_load_p, mock_load_a):
    # No analyze call needed, just outline + 5 sections = 6 calls
    mock_llm = MagicMock(return_value="mocked")
    mock_get_client.return_value = mock_llm

    run_pipeline("RFP text", ["past proposal"])

    assert mock_llm.call_count == 6  # skipped analysis


@patch("app.services.pipeline.proposal_pipeline.save_analysis")
@patch("app.services.pipeline.proposal_pipeline.load_analysis", return_value=None)
@patch("app.services.pipeline.proposal_pipeline.load_proposals", return_value=["stored proposal"])
@patch("app.services.pipeline.proposal_pipeline.get_llm_client")
def test_run_pipeline_uses_stored_proposals(mock_get_client, mock_load_p, mock_load_a, mock_save_a):
    mock_llm = MagicMock(return_value="mocked")
    mock_get_client.return_value = mock_llm

    run_pipeline("RFP text")

    # Analyze prompt should use stored proposal
    analyze_call = mock_llm.call_args_list[0]
    assert "stored proposal" in analyze_call[0][0]


@patch("app.services.pipeline.proposal_pipeline.load_analysis", return_value=None)
@patch("app.services.pipeline.proposal_pipeline.load_proposals", return_value=[])
def test_run_pipeline_no_proposals_raises(mock_load_p, mock_load_a):
    with pytest.raises(ValueError, match="No proposal texts provided"):
        run_pipeline("RFP text")
