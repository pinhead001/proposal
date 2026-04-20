import json
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


@patch("app.api.routes.generation.stream_pipeline")
def test_stream_pipeline_endpoint(mock_stream):
    async def fake_stream(rfp_text, proposal_texts):
        yield {"type": "progress", "percent": 10, "message": "Analyzing..."}
        yield {"type": "section", "data": {"title": "Executive Summary", "content": "Test"}}
        yield {"type": "done"}

    mock_stream.return_value = fake_stream("test", None)

    response = client.post("/stream-pipeline", json={"rfp_text": "Test RFP content here"})

    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]

    lines = response.text.strip().split('\n')
    data_lines = [l for l in lines if l.startswith('data: ') and l.strip() != 'data: [DONE]']

    events = []
    for line in data_lines:
        raw = line[6:].strip()
        if raw:
            events.append(json.loads(raw))

    types = [e["type"] for e in events]
    assert "progress" in types
    assert "section" in types
    assert "done" in types


def test_stream_pipeline_missing_rfp():
    response = client.post("/stream-pipeline", json={})
    assert response.status_code == 422
