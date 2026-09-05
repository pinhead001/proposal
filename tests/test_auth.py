from unittest.mock import patch
from fastapi.testclient import TestClient


def test_no_auth_required_by_default():
    from app.main import app
    client = TestClient(app)
    response = client.get("/api/health")
    assert response.status_code == 200


def test_health_is_public_even_with_auth():
    """Health endpoint should be accessible without API key even when auth is configured."""
    from app.main import app
    client = TestClient(app)
    with patch("app.core.auth.API_KEY", "test-secret-key"):
        response = client.get("/api/health")
        assert response.status_code == 200


@patch("app.core.auth.API_KEY", "test-secret-key")
def test_auth_rejects_missing_key_on_protected_route():
    from app.main import app
    client = TestClient(app)
    response = client.get("/available-sections")
    assert response.status_code == 401


@patch("app.core.auth.API_KEY", "test-secret-key")
def test_auth_accepts_valid_key():
    from app.main import app
    client = TestClient(app)
    response = client.get("/available-sections", headers={"X-API-Key": "test-secret-key"})
    assert response.status_code == 200


@patch("app.core.auth.API_KEY", "test-secret-key")
def test_auth_rejects_wrong_key():
    from app.main import app
    client = TestClient(app)
    response = client.get("/available-sections", headers={"X-API-Key": "wrong-key"})
    assert response.status_code == 401
