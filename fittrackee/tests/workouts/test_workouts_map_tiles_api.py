from typing import TYPE_CHECKING
from unittest.mock import patch

import requests
from requests.structures import CaseInsensitiveDict

from fittrackee.workouts.workouts import get_tile_response_headers

from ..mixins import ApiTestCaseMixin, ResponseMockMixin

if TYPE_CHECKING:
    from flask import Flask

HEADERS = CaseInsensitiveDict(
    {
        "content-type": "image/png",
        "Cache-Control": "max-age=86400, stale-while-revalidate=604800",
        "ETag": '"tile-etag"',
        "Expires": "Wed, 24 Jun 2026 16:46:03 GMT",
        "Last-Modified": "Tue, 23 Jun 2026 16:46:03 GMT",
        "Age": "3600",
        "Server": "upstream",
    }
)
URL_PARAMS = {
    "s": "a",
    "z": 14,
    "x": 8301,
    "y": 5637,
}


class TestGetTileResponseHeaders:
    @staticmethod
    def test_it_returns_cache_headers() -> None:

        response_headers = get_tile_response_headers(HEADERS)

        assert (
            response_headers["Cache-Control"]
            == "max-age=86400, stale-while-revalidate=604800"
        )
        assert response_headers["ETag"] == '"tile-etag"'
        assert response_headers["Expires"] == "Wed, 24 Jun 2026 16:46:03 GMT"
        assert (
            response_headers["Last-Modified"]
            == "Tue, 23 Jun 2026 16:46:03 GMT"
        )
        assert response_headers["Age"] == "3600"
        assert "content-type" not in response_headers
        assert "Server" not in response_headers


class TestGetMapTile(ApiTestCaseMixin, ResponseMockMixin):
    route = "/api/workouts/map_tile/{s}/{z}/{x}/{y}.png"

    def test_it_returns_400_when_provider_is_invalid(
        self, app: "Flask"
    ) -> None:
        client = app.test_client()

        response = client.get(
            f"{self.route.format(**URL_PARAMS)}?tile_provider=invalid"
        )

        self.assert_400(
            response, error_message="tile provider 'invalid' is not available"
        )

    def test_it_returns_400_when_provider_is_not_enabled(
        self, app: "Flask"
    ) -> None:
        client = app.test_client()

        response = client.get(
            f"{self.route.format(**URL_PARAMS)}?tile_provider=cyclosm"
        )

        self.assert_400(
            response, error_message="tile provider 'cyclosm' is not available"
        )

    def test_it_calls_requests_get_with_default_tile_provider_url(
        self, app_default_static_map: "Flask"
    ) -> None:
        tile_response = self.get_response({}, headers=HEADERS)
        client = app_default_static_map.test_client()

        with patch.object(
            requests, "get", return_value=tile_response
        ) as requests_get_mock:
            client.get(self.route.format(**URL_PARAMS))

        # called OSM (de)
        requests_get_mock.assert_called_once_with(
            "https://tile.openstreetmap.de/14/8301/5637.png",
            headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:88.0)"},
            timeout=30,
        )

    def test_it_calls_requests_get_with_provided_tile_provider_url(
        self, app_with_multiple_tile_servers_enabled: "Flask"
    ) -> None:
        tile_response = self.get_response({}, headers=HEADERS)
        client = app_with_multiple_tile_servers_enabled.test_client()

        with patch.object(
            requests, "get", return_value=tile_response
        ) as requests_get_mock:
            client.get(
                f"{self.route.format(**URL_PARAMS)}?tile_provider=cyclosm"
            )

        requests_get_mock.assert_called_once_with(
            "https://a.tile-cyclosm.openstreetmap.fr/cyclosm/14/8301/5637.png",
            headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:88.0)"},
            timeout=30,
        )

    def test_it_returns_tile_provider_response(
        self, app_default_static_map: "Flask"
    ) -> None:
        content = b"some text"
        tile_response = self.get_response(
            {}, headers=dict(HEADERS), content=content
        )
        client = app_default_static_map.test_client()

        with patch.object(requests, "get", return_value=tile_response):
            response = client.get(self.route.format(**URL_PARAMS))

        assert response.status_code == 200
        assert response.data == content
        assert response.content_type == "image/png"
        assert response.headers["Last-Modified"] == HEADERS["Last-Modified"]

    def test_it_returns_tile_provider_response_on_error(
        self, app_default_static_map: "Flask"
    ) -> None:
        tile_response = self.get_response(
            {}, headers=dict(HEADERS), status_code=401
        )
        client = app_default_static_map.test_client()

        with patch.object(requests, "get", return_value=tile_response):
            response = client.get(self.route.format(**URL_PARAMS))

        assert response.status_code == 401
