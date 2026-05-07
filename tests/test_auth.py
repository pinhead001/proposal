from unittest.mock import patch
from fastapi.testclient import TestClient


def test_no_auth_required_by_default():
    from app.main import app
    client = TestClient(app)
    response = client.get("/api/health")
    assert response.status_code == 200


@patch("app.core.auth.API_KEY", "test-secret-key")
def test_auth_rejects_missing_key():
    from app.main import app
    client = TestClient(app)
    response = client.get("/api/health")
    assert response.status_code == 401


@patch("app.core.auth.API_KEY", "test-secret-key")
def test_auth_accepts_valid_key():
    from app.main import app
    client = TestClient(app)
    response = client.get("/api/health", headers={"X-API-Key": "test-secret-key"})
    assert response.status_code == 200


@patch("app.core.auth.API_KEY", "test-secret-key")
def test_auth_rejects_wrong_key():
    from app.main import app
    client = TestClient(app)
    response = client.get("/api/health", headers={"X-API-Key": "wrong-key"})
    assert response.status_code == 401
