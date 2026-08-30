import os

os.environ.setdefault("API_TOKEN", "test-token")
os.environ.setdefault("PRIVATE_PORTAL_PASSWORD", "test-password")

from fastapi.testclient import TestClient

from src.config import get_settings
from src.main import app


def test_health_is_public():
    response = TestClient(app).get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_private_portal_requires_basic_auth():
    response = TestClient(app).get("/private")
    assert response.status_code == 401


def test_docs_host_opens_swagger_at_root(monkeypatch):
    monkeypatch.setenv("DOCS_HOST", "docs.example.com")
    get_settings.cache_clear()
    response = TestClient(app).get("/", headers={"Host": "docs.example.com"}, auth=("admin", "test-password"))
    assert response.status_code == 200
    assert "swagger-ui" in response.text


def test_metrics_require_bearer_token():
    response = TestClient(app).get("/api/v1/metrics/system")
    assert response.status_code == 401


def test_analytics_rejects_invalid_date_range(monkeypatch):
    monkeypatch.setenv("API_TOKEN", "test-token")
    monkeypatch.setenv("GA_PROPERTY_ID", "123456")
    get_settings.cache_clear()
    response = TestClient(app).get(
        "/api/v1/metrics/analytics?start_date=2026-02-01&end_date=2026-01-01",
        headers={"Authorization": "Bearer test-token"},
    )
    assert response.status_code == 422