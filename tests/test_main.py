from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_serves_frontend():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Proposal AI" in response.text


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "running"
    assert "llm_provider" in data
