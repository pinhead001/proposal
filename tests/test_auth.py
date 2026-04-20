from unittest.mock import patch
from fastapi.testclient import TestClient


def test_no_auth_required_when_key_unset():
    with patch("app.core.config.API_KEY", None), \
         patch("app.core.auth.API_KEY", None):
        from app.main import app
        client = TestClient(app)
        response = client.get("/api/health")
        assert response.status_code == 200


def test_auth_rejects_missing_key():
    with patch("app.core.auth.API_KEY", "secret123"):
        from app.main import app
        client = TestClient(app)
        response = client.get("/api/health")
        assert response.status_code == 401
        assert "Invalid or missing API key" in response.json()["detail"]


def test_auth_rejects_wrong_key():
    with patch("app.core.auth.API_KEY", "secret123"):
        from app.main import app
        client = TestClient(app)
        response = client.get("/api/health", headers={"X-API-Key": "wrongkey"})
        assert response.status_code == 401


def test_auth_accepts_correct_key():
    with patch("app.core.auth.API_KEY", "secret123"):
        from app.main import app
        client = TestClient(app)
        response = client.get("/api/health", headers={"X-API-Key": "secret123"})
        assert response.status_code == 200
