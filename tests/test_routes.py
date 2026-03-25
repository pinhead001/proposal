from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


@patch("app.api.routes.generation.run_pipeline")
def test_run_pipeline_endpoint(mock_pipeline):
    mock_pipeline.return_value = {
        "sections": [
            {"title": "Executive Summary", "content": "Test content"},
        ]
    }

    response = client.post("/run-pipeline", json={
        "rfp_text": "Sample RFP",
        "proposal_texts": ["Past proposal"],
    })

    assert response.status_code == 200
    data = response.json()
    assert len(data["sections"]) == 1
    assert data["sections"][0]["title"] == "Executive Summary"
    mock_pipeline.assert_called_once_with("Sample RFP", ["Past proposal"])


def test_run_pipeline_missing_fields():
    client_no_raise = TestClient(app, raise_server_exceptions=False)
    response = client_no_raise.post("/run-pipeline", json={})
    assert response.status_code == 500


def test_export_endpoint():
    payload = {
        "sections": [
            {"title": "Summary", "content": "Some content"},
        ]
    }

    response = client.post("/export", json=payload)

    assert response.status_code == 200
    assert "application/vnd.openxmlformats" in response.headers["content-type"]
    assert "proposal.docx" in response.headers["content-disposition"]
    assert len(response.content) > 0


def test_export_empty_sections():
    payload = {"sections": []}
    response = client.post("/export", json=payload)
    assert response.status_code == 200
    assert len(response.content) > 0
