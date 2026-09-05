import json
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


@patch("app.api.routes.generation.stream_pipeline")
def test_stream_pipeline_success(mock_stream):
    async def mock_gen(*args, **kwargs):
        yield {"type": "progress", "percent": 50, "message": "Working..."}
        yield {"type": "section", "data": {"title": "Summary", "content": "Test"}}
        yield {"type": "done"}

    mock_stream.return_value = mock_gen()

    response = client.post("/stream-pipeline", json={"rfp_text": "Test RFP text here"})
    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]

    lines = [l for l in response.text.strip().split("\n") if l.startswith("data: ")]
    assert len(lines) >= 3

    progress = json.loads(lines[0].replace("data: ", ""))
    assert progress["type"] == "progress"

    section = json.loads(lines[1].replace("data: ", ""))
    assert section["type"] == "section"
    assert section["data"]["title"] == "Summary"

    done = json.loads(lines[2].replace("data: ", ""))
    assert done["type"] == "done"


@patch("app.api.routes.generation.stream_pipeline")
def test_stream_pipeline_error_handling(mock_stream):
    async def mock_gen(*args, **kwargs):
        raise ValueError("No proposal texts provided")
        yield  # noqa: unreachable - needed to make this an async generator

    mock_stream.return_value = mock_gen()

    response = client.post("/stream-pipeline", json={"rfp_text": "Test RFP text here"})
    assert response.status_code == 200

    lines = [l for l in response.text.strip().split("\n") if l.startswith("data: ")]
    error_line = [l for l in lines if "error" in l]
    assert len(error_line) > 0


def test_stream_pipeline_validation():
    response = client.post("/stream-pipeline", json={})
    assert response.status_code == 422


def test_stream_pipeline_empty_rfp():
    response = client.post("/stream-pipeline", json={"rfp_text": ""})
    assert response.status_code == 422
