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
        "rfp_text": "Sample RFP text for testing",
        "proposal_texts": ["Past proposal"],
    })

    assert response.status_code == 200
    data = response.json()
    assert len(data["sections"]) == 1
    assert data["sections"][0]["title"] == "Executive Summary"
    mock_pipeline.assert_called_once_with("Sample RFP text for testing", ["Past proposal"], None)


@patch("app.api.routes.generation.run_pipeline")
def test_run_pipeline_without_proposals(mock_pipeline):
    mock_pipeline.return_value = {"sections": []}

    response = client.post("/run-pipeline", json={
        "rfp_text": "Sample RFP text for testing",
    })

    assert response.status_code == 200
    mock_pipeline.assert_called_once_with("Sample RFP text for testing", None, None)


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


@patch("app.api.routes.generation.regenerate_section")
def test_regenerate_section(mock_regen):
    mock_regen.return_value = {"title": "Executive Summary", "content": "Improved content"}

    response = client.post("/regenerate-section", json={
        "section_title": "Executive Summary",
        "rfp_text": "Sample RFP text for testing",
        "instructions": "Make it more concise",
        "current_content": "Original content",
    })

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Executive Summary"
    assert data["content"] == "Improved content"


def test_regenerate_section_missing_fields():
    response = client.post("/regenerate-section", json={})
    assert response.status_code == 422


def test_history_endpoint():
    response = client.get("/history")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@patch("app.api.routes.generation.save_to_history", return_value=1)
def test_save_proposal(mock_save):
    response = client.post("/save-proposal", json={
        "rfp_text": "Test RFP",
        "sections": [{"title": "Exec Summary", "content": "Content"}],
    })
    assert response.status_code == 200
    assert response.json()["id"] == 1
    mock_save.assert_called_once()


def test_save_proposal_missing_fields():
    response = client.post("/save-proposal", json={})
    assert response.status_code == 422


def test_save_proposal_empty_rfp():
    response = client.post("/save-proposal", json={
        "rfp_text": "",
        "sections": [{"title": "S", "content": "C"}],
    })
    assert response.status_code == 422


def test_save_proposal_invalid_sections():
    response = client.post("/save-proposal", json={
        "rfp_text": "Test RFP",
        "sections": [{"title": "Missing content field"}],
    })
    assert response.status_code == 422


def test_available_sections():
    response = client.get("/available-sections")
    assert response.status_code == 200
    data = response.json()
    assert "sections" in data
    assert len(data["sections"]) > 0
