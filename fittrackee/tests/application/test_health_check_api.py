import json

from flask import Flask


class TestHealthCheck:
    def test_it_returns_pong_on_health_check(self, app: Flask) -> None:
        """ => Ensure the /health_check route behaves correctly."""
        client = app.test_client()
        response = client.get('/api/ping')
        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'pong' in data['message']
        assert 'success' in data['status']
