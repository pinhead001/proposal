from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "running"
    assert "llm_provider" in data


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


@patch("app.api.routes.generation.run_pipeline")
def test_run_pipeline_without_proposals(mock_pipeline):
    mock_pipeline.return_value = {"sections": []}

    response = client.post("/run-pipeline", json={
        "rfp_text": "Sample RFP",
    })

    assert response.status_code == 200
    mock_pipeline.assert_called_once_with("Sample RFP", None)


def test_run_pipeline_missing_rfp():
    response = client.post("/run-pipeline", json={})
    assert response.status_code == 422


def test_run_pipeline_empty_rfp():
    response = client.post("/run-pipeline", json={"rfp_text": ""})
    assert response.status_code == 422


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
    response = client.post("/export", json={"sections": []})
    assert response.status_code == 422


def test_export_missing_fields():
    response = client.post("/export", json={})
    assert response.status_code == 422
