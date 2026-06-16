"""
TMS — E2E Tests: Health & Backend
Tests health check endpoint and API docs accessibility.
"""


class TestHealthEndpoint:
    def test_health_returns_200(self, client):
        """TC-API-001: Health endpoint returns 200 with correct body."""
        resp = client.get("/api/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert data["service"] == "TMS Backend"
        assert data["version"] == "1.0.0"

    def test_health_response_structure(self, client):
        """TC-API-002: Health response contains required keys."""
        resp = client.get("/api/health")
        data = resp.json()
        assert "status" in data
        assert "service" in data
        assert "version" in data


class TestAPIDocs:
    def test_swagger_docs_accessible(self, client):
        """TC-API-003: Swagger UI at /docs returns 200."""
        resp = client.get("/docs")
        assert resp.status_code == 200

    def test_redoc_accessible(self, client):
        """TC-API-004: ReDoc at /redoc returns 200."""
        resp = client.get("/redoc")
        assert resp.status_code == 200

    def test_openapi_json(self, client):
        """TC-API-005: OpenAPI JSON schema is valid."""
        resp = client.get("/openapi.json")
        assert resp.status_code == 200
        data = resp.json()
        assert "paths" in data
        assert "info" in data
        assert data["info"]["title"] == "TMS — Telemedicine Management System"
