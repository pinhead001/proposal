from unittest.mock import patch, MagicMock


@patch("app.services.pipeline.proposal_pipeline.load_analysis", return_value=None)
@patch("app.services.pipeline.proposal_pipeline.save_analysis")
@patch("app.services.pipeline.proposal_pipeline.load_proposals", return_value=[])
@patch("app.services.pipeline.proposal_pipeline.get_llm_client")
def test_run_pipeline(mock_get_client, mock_load_proposals, mock_save, mock_load_analysis):
    mock_llm = MagicMock(side_effect=[
        "analysis result",
        "outline result",
        "section 1 content",
        "section 2 content",
    ])
    mock_get_client.return_value = mock_llm

    from app.services.pipeline.proposal_pipeline import run_pipeline
    result = run_pipeline("RFP text", ["past proposal"], ["Exec Summary", "Tech Approach"])

    assert mock_llm.call_count == 4
    assert len(result["sections"]) == 2
    assert result["sections"][0]["title"] == "Exec Summary"
    assert result["sections"][1]["title"] == "Tech Approach"


@patch("app.services.pipeline.proposal_pipeline.load_analysis", return_value="cached analysis")
@patch("app.services.pipeline.proposal_pipeline.load_proposals", return_value=["stored proposal"])
@patch("app.services.pipeline.proposal_pipeline.get_llm_client")
def test_run_pipeline_uses_cached_analysis(mock_get_client, mock_load_proposals, mock_load_analysis):
    mock_llm = MagicMock(return_value="mocked")
    mock_get_client.return_value = mock_llm

    from app.services.pipeline.proposal_pipeline import run_pipeline
    result = run_pipeline("RFP text", section_titles=["Summary"])

    # Should skip the analyze call since analysis is cached
    # Calls: outline + 1 section = 2
    assert mock_llm.call_count == 2


@patch("app.services.pipeline.proposal_pipeline.load_analysis", return_value=None)
@patch("app.services.pipeline.proposal_pipeline.load_proposals", return_value=[])
@patch("app.services.pipeline.proposal_pipeline.get_llm_client")
def test_run_pipeline_no_proposals_raises(mock_get_client, mock_load_proposals, mock_load_analysis):
    mock_get_client.return_value = MagicMock()

    from app.services.pipeline.proposal_pipeline import run_pipeline
    import pytest
    with pytest.raises(ValueError, match="No proposal texts"):
        run_pipeline("RFP text")


@patch("app.services.pipeline.proposal_pipeline.load_analysis", return_value="analysis")
@patch("app.services.pipeline.proposal_pipeline.get_llm_client")
def test_regenerate_section(mock_get_client, mock_load_analysis):
    mock_llm = MagicMock(return_value="new content")
    mock_get_client.return_value = mock_llm

    from app.services.pipeline.proposal_pipeline import regenerate_section
    result = regenerate_section("Summary", "RFP text", instructions="Be concise")

    assert result["title"] == "Summary"
    assert result["content"] == "new content"
    mock_llm.assert_called_once()
