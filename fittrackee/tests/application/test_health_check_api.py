import json
from unittest.mock import patch

from flask import Flask

from fittrackee import db


class TestHealthCheck:
    def test_it_returns_pong_on_health_check(self, app: Flask) -> None:
        """=> Ensure the /health_check route behaves correctly."""
        client = app.test_client()

        response = client.get("/api/ping")

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "pong" in data["message"]
        assert "success" in data["status"]


class TestDbHealthCheck:
    route = "/api/check-db"

    def test_it_returns_200_when_db_is_available(self, app: Flask) -> None:
        client = app.test_client()

        response = client.get(self.route)

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["message"] == "db available"
        assert data["status"] == "success"

    def test_it_returns_500_when_db_is_not_available(self, app: Flask) -> None:
        client = app.test_client()

        with patch.object(db.session, "execute", side_effect=Exception()):
            response = client.get(self.route)

        assert response.status_code == 500
        data = json.loads(response.data.decode())
        assert data["message"] == "db unavailable"
        assert data["status"] == "error"
